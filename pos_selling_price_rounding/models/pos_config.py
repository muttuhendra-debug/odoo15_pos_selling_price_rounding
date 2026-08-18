from odoo import fields, models, api

class PosConfig(models.Model):
    _inherit = 'pos.config'

    enable_rounding_price = fields.Boolean(string='Enable Rounding Product Selling Price', default=False)
    rounding_value = fields.Float(string='Rounding Value', default=100.0)
    enable_cashier_rounding = fields.Boolean(string='Only Certain Cashiers Can Use Rounded Prices', default=False)
    rounding_cashier_ids = fields.Many2many(
        'res.users',
        'pos_config_rounding_cashier_rel',
        'config_id',
        'user_id',
        string='Rounding Cashiers'
    )

    @api.model
    def create(self, vals):
        # Sync global settings for new POS configurations
        ICP = self.env['ir.config_parameter'].sudo()
        if 'enable_rounding_price' not in vals:
            vals['enable_rounding_price'] = ICP.get_param('pos_selling_price_rounding.enable_rounding_price') == 'True'
        if 'rounding_value' not in vals:
            vals['rounding_value'] = float(ICP.get_param('pos_selling_price_rounding.rounding_value', 100.0))
        if 'enable_cashier_rounding' not in vals:
            vals['enable_cashier_rounding'] = ICP.get_param('pos_selling_price_rounding.enable_cashier_rounding') == 'True'
        if 'rounding_cashier_ids' not in vals:
            rounding_cashier_ids_str = ICP.get_param('pos_selling_price_rounding.rounding_cashier_ids', '')
            if rounding_cashier_ids_str:
                vals['rounding_cashier_ids'] = [(6, 0, [int(id) for id in rounding_cashier_ids_str.split(',') if id])]
        return super(PosConfig, self).create(vals)
