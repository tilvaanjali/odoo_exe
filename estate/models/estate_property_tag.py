from odoo import models, fields, api


class TagModel(models.Model):
    _name = "tag.model"
    _description = "Tag Model"
    _order = "name"

    name = fields.Char(string='Name', required=True)
    color = fields.Integer("Color Index")

    _sql_constraints = [
        ("check_name", "UNIQUE(name)", "The name must be unique"),
    ]
