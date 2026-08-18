{
    'name': 'POS Selling Price Rounding',
    'version': '15.0.1.0.0',
    'category': 'Point of Sale',
    'summary': 'Rounding Product Selling Prices in POS',
    'description': 'This module allows rounding product selling prices in POS after discount is applied.',
    'author': 'Jules',
    'depends': ['point_of_sale'],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'assets': {
        'point_of_sale.assets': [
            'pos_selling_price_rounding/static/src/js/pos_rounding.js',
            'pos_selling_price_rounding/static/src/xml/Orderline.xml',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
