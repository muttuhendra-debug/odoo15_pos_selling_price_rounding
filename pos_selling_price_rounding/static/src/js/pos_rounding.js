odoo.define('pos_selling_price_rounding.pos_rounding', function (require) {
    "use strict";

    var models = require('point_of_sale.models');
    const Orderline = require('point_of_sale.Orderline');
    const Registries = require('point_of_sale.Registries');

    // Ensure our new fields are loaded into the POS configuration
    models.load_fields('pos.config', ['enable_rounding_price', 'rounding_value', 'enable_cashier_rounding', 'rounding_cashier_ids']);

    var _orderline_proto = models.Orderline.prototype;
    models.Orderline = models.Orderline.extend({
        initialize: function(attr, options) {
            _orderline_proto.initialize.apply(this, arguments);
            this.is_rounding_enabled = options && options.is_rounding_enabled !== undefined ? options.is_rounding_enabled : true;
            this.raw_discount = options && options.raw_discount !== undefined ? options.raw_discount : 0;
        },
        export_as_JSON: function() {
            var json = _orderline_proto.export_as_JSON.apply(this, arguments);
            json.is_rounding_enabled = this.is_rounding_enabled;
            json.raw_discount = this.raw_discount;
            return json;
        },
        init_from_JSON: function(json) {
            _orderline_proto.init_from_JSON.apply(this, arguments);
            this.is_rounding_enabled = json.is_rounding_enabled !== undefined ? json.is_rounding_enabled : true;
            this.raw_discount = json.raw_discount !== undefined ? json.raw_discount : 0;
        },
        set_discount: function (discount) {
            if (!this._is_rounding) {
                this.raw_discount = parseFloat(discount) || 0;
            }

            var config = this.pos.config;

            // If the feature is not enabled or line rounding is disabled, use standard behavior
            if (!config.enable_rounding_price || config.rounding_value <= 0 || this._is_rounding || this.is_rounding_enabled === false) {
                _orderline_proto.set_discount.apply(this, arguments);
                return;
            }

            // Check if cashier rounding restriction is enabled
            if (config.enable_cashier_rounding) {
                var cashier = this.pos.get_cashier();
                var cashier_id = cashier ? (cashier.user_id ? cashier.user_id[0] : cashier.id) : null;
                if (!cashier_id || !config.rounding_cashier_ids.includes(cashier_id)) {
                    _orderline_proto.set_discount.apply(this, arguments);
                    return;
                }
            }

            var disc = Math.min(Math.max(parseFloat(discount) || 0, 0), 100);
            if (disc === 0) {
                _orderline_proto.set_discount.apply(this, arguments);
                return;
            }

            this._is_rounding = true;
            try {
                // Use the current unit price as base (respects manual price changes/pricelists)
                var base_price = this.get_unit_price();
                if (base_price <= 0) {
                    _orderline_proto.set_discount.apply(this, arguments);
                } else {
                    var price_after_discount = base_price * (1 - disc / 100);
                    var rounding = config.rounding_value;
                    var rounded_price = Math.ceil(price_after_discount / rounding) * rounding;

                    // Ensure we don't round above the base price
                    if (rounded_price > base_price) {
                        rounded_price = base_price;
                    }

                    // Recalculate effective discount to match rounded price exactly
                    var effective_disc = (1 - rounded_price / base_price) * 100;

                    // Apply the adjusted discount percentage.
                    _orderline_proto.set_discount.call(this, effective_disc);
                }
            } finally {
                this._is_rounding = false;
            }
        },
        toggle_rounding: function () {
            this.is_rounding_enabled = !this.is_rounding_enabled;
            var disc_to_apply = this.raw_discount !== undefined ? this.raw_discount : (this.get_discount() || 0);
            this.set_discount(disc_to_apply);
            this.trigger('change', this);
        },
    });

    const PosRoundingOrderline = Orderline => class extends Orderline {
        onToggleRounding(ev) {
            ev.stopPropagation();
            this.props.line.toggle_rounding();
        }
    };

    Registries.Component.extend(Orderline, PosRoundingOrderline);

    return PosRoundingOrderline;
});
