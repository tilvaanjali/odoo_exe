from odoo import models, fields, api

class ResModel(models.Model):

    _inherit = "res.users"

    property_ids = fields.One2many(
        "estate.model", "salesperson", string="Properties", domain=[("state", "in", ["new", "offer_received"])]
    )