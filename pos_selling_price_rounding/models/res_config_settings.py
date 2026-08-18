from odoo import fields, models, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    pos_enable_rounding_price = fields.Boolean(
        string="Enable Rounding Product Selling Price",
        config_parameter='pos_selling_price_rounding.enable_rounding_price'
    )
    pos_rounding_value = fields.Float(
        string="Rounding Value",
        config_parameter='pos_selling_price_rounding.rounding_value',
        default=100.0
    )
    pos_enable_cashier_rounding = fields.Boolean(
        string="Only Certain Cashiers Can Use Rounded Prices",
        config_parameter='pos_selling_price_rounding.enable_cashier_rounding'
    )
    pos_rounding_cashier_ids = fields.Many2many(
        'res.users',
        'res_config_rounding_cashier_rel',
        'config_id',
        'user_id',
        string="Rounding Cashiers"
    )

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        # Synchronize global settings to all POS configurations
        pos_configs = self.env['pos.config'].sudo().search([])
        pos_configs.write({
            'enable_rounding_price': self.pos_enable_rounding_price,
            'rounding_value': self.pos_rounding_value,
            'enable_cashier_rounding': self.pos_enable_cashier_rounding,
            'rounding_cashier_ids': [(6, 0, self.pos_rounding_cashier_ids.ids)],
        })
        # Store Many2many in config_parameter as a string of IDs
        self.env['ir.config_parameter'].sudo().set_param(
            'pos_selling_price_rounding.rounding_cashier_ids',
            ','.join(map(str, self.pos_rounding_cashier_ids.ids))
        )

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        ICP = self.env['ir.config_parameter'].sudo()
        rounding_cashier_ids_str = ICP.get_param('pos_selling_price_rounding.rounding_cashier_ids', '')
        if rounding_cashier_ids_str:
            res.update(
                pos_rounding_cashier_ids=[(6, 0, [int(id) for id in rounding_cashier_ids_str.split(',') if id])],
            )
        return res
