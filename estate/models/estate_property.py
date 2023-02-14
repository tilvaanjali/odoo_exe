from odoo import models, fields, api
from odoo.exceptions import UserError, ValidationError
from odoo.tools import float_compare, float_is_zero
from dateutil.relativedelta import relativedelta


class EstateModel(models.Model):
    _name = "estate.model"
    _description = "Estate Model"
    _order = "id desc"

    def _default_date_availability(self):
        return fields.Date.context_today(self) + relativedelta(months=3)

    name = fields.Char(string='Name', required=True)
    last_seen = fields.Datetime("Last Seen", default=lambda self: fields.Datetime.now())

    description = fields.Text(string='Description')
    postcode = fields.Float(string='PostCode')
    date_availability = fields.Date(string='Date Availability', copy=False)
    expected_price = fields.Float(string='Expected Price', required=True)
    selling_price = fields.Float(string='Selling Price', copy=False, default=False)
    bedrooms = fields.Integer(string='Bedrooms', default=1)
    living_area = fields.Integer(string='Living Area')
    facades = fields.Integer(string='Facades')
    garage = fields.Boolean(string='Garage')
    other_info = fields.Text(string='Other Info')
    garden = fields.Boolean(string='Garden')
    active = fields.Boolean(string='Active', default=False)
    garden_area = fields.Integer(string='Garden Area')
    garden_orientation = fields.Selection(string='Garden Orientation',
                                          selection=[('north', 'North'), ('south', 'South'), ('east', 'East'),
                                                     ('west', 'West')])
    state = fields.Selection(selection=[
        ('new', 'New'),
        ('offer_received', 'Offer Received'),
        ('offer_accepted', 'Offer Accepted'),
        ('sold', 'Sold'),
        ('canceled', 'Canceled')], copy=False, string='Status', default='new')

    buyer = fields.Many2one("res.partner", string="Buyer ", copy=False)
    seller = fields.Many2one("res.partner", string="Seller")
    property_type_id = fields.Many2one("property.model", string="Property Type")
    salesperson = fields.Many2one("res.users", string="Sales Person", default=lambda self: self.env.user)
    tag_ids = fields.Many2many("tag.model", string="Tag")
    offer_ids = fields.One2many("offer.model", "property_id", string="Offer")
    total_area = fields.Integer(string="Total Area", compute="_compute_total_area", store=True)
    best_price = fields.Float("Best Offer", compute="_compute_best_price")

    _sql_constraints = [
        ("check_expected_price", "CHECK(expected_price >= 0)", "The expected price must be strictly positive"),
        ("check_selling_price", "CHECK(selling_price >= 0)", "The offer price must be positive"),
    ]

    # Compute Methods:
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for prop_total in self:
            prop_total.total_area = prop_total.living_area + prop_total.garden_area

    @api.depends("offer_ids.price")
    def _compute_best_price(self):
        for prop_offer in self:

            if prop_offer.offer_ids:
                prop_offer.best_price = max(prop_offer.offer_ids.mapped("price"))

            else:
                prop_offer.best_price = 0.0

            print(prop_offer.best_price)

        # constraints:

        @api.constrains("expected_price", "selling_price")
        def _check_price_difference(self):
            for prop in self:
                if (
                        not float_is_zero(prop.selling_price, precision_rounding=0.01)
                        and float_compare(prop.selling_price, prop.expected_price * 90.0 / 100.0,
                                          precision_rounding=0.01) < 0
                ):
                    raise ValidationError(
                        "The selling price must be at least 90% of the expected price! "
                        + "You must reduce the expected price if you want to accept this offer."
                    )
    # onchange Method:

    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
            self.garden_orientation = "north"
        else:
            self.garden_area = 0
            self.garden_orientation = False

    # CRUD method:

    def unlink(self):
        if not set(self.mapped("state")) <= {"new", "canceled"}:
            raise UserError("Only new and canceled properties can be deleted.")
        return super().unlink()

    # Cancel and sold button:

    def action_sold(self):
        if "canceled" in self.mapped("state"):
            raise UserError("Canceled properties cannot be sold.")
        return self.write({"state": "sold"})

    def action_cancel(self):
        if "sold" in self.mapped("state"):
            raise UserError("Sold properties cannot be canceled.")
        return self.write({"state": "sold"})



    # # Hide Buttons
    #
    # def action_sold(self):
    #     for rec in self:
    #         rec.state = "sold"
    #
    # def action_cancel(self):
    #     for rec in self:
    #         rec.state = "canceled"
