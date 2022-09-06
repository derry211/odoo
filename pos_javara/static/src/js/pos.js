odoo.define("pos_javara.PosModel", function(require) {
    "use strict";

    var rpc = require("web.rpc");
    var models = require("point_of_sale.models");
    var screens = require("point_of_sale.screens");
    var models = require("point_of_sale.models");
    var core = require("web.core");
    var _t = core._t;

    // menampilkan qty available
    var PosModelSuper = models.PosModel.prototype;
    models.PosModel = models.PosModel.extend({
        load_server_data: function() {
            var self = this;

            var loaded = PosModelSuper.load_server_data.call(this);

            var prod_model = _.find(this.models, function(model) {
                return model.model === "product.product";
            });
            if (prod_model) {
                prod_model.fields.push("qty_available", "type");
                var context_super = prod_model.context;
                prod_model.context = function(that) {
                    var ret = context_super(that);
                    ret.location = that.config.stock_location_id[0];
                    return ret;
                };
                var loaded_super = prod_model.loaded;
                prod_model.loaded = function(that, products) {
                    loaded_super(that, products);
                    self.db.product_qtys = products;
                };
                return loaded;
            }

            return loaded.then(function() {
                return rpc
                    .query({
                        model: "product.product",
                        method: "search_read",
                        args: [],
                        fields: ["qty_available", "type"],
                        domain: [
                            ["sale_ok", "=", false],
                            ["available_in_pos", "=", true],
                        ],
                        context: {location: self.config.stock_location_id[0]},
                    })
                    .then(function(products) {
                        self.db.product_qtys = products;
                    });
            });
        },
        set_product_qty_available: function(product, qty) {
            product.qty_available = qty;
            this.refresh_qty_available(product);
        },
        update_product_qty_from_order_lines: function(order) {
            var self = this;
            order.orderlines.each(function(line) {
                var product = line.get_product();
                product.qty_available -= line.get_quantity();
                self.refresh_qty_available(product);
            });
            // Compatibility with pos_multi_session
            order.trigger("new_updates_to_send");
        },
        after_load_server_data: function() {
            var self = this;
            var res = PosModelSuper.after_load_server_data.apply(this, arguments);
//            _.each(this.db.product_qtys, function(v) {
//                _.extend(self.db.get_product_by_id(v.id), v);
//            });
            return res;
        },
        refresh_qty_available: function(product) {
            var $elem = $("[data-product-id='" + product.id + "'] .qty-tag");
            $elem.html(product.qty_available);
            if (product.qty_available <= 0 && !$elem.hasClass("not-available")) {
                $elem.addClass("not-available");
            }
        },
        push_order: function(order, opts) {
            var pushed = PosModelSuper.push_order.call(this, order, opts);
            if (order) {
                this.update_product_qty_from_order_lines(order);
            }
            return pushed;
        },
        push_and_invoice_order: function(order) {
            var invoiced = PosModelSuper.push_and_invoice_order.call(this, order);

            if (order && order.get_client() && order.orderlines) {
                this.update_product_qty_from_order_lines(order);
            }

            return invoiced;
        },
    });

    var OrderlineSuper = models.Orderline;
    models.Orderline = models.Orderline.extend({
        export_as_JSON: function() {
            var data = OrderlineSuper.prototype.export_as_JSON.apply(this, arguments);
            data.qty_available = this.product.qty_available;
            return data;
        },
        // Compatibility with pos_multi_session
        apply_ms_data: function(data) {
            if (OrderlineSuper.prototype.apply_ms_data) {
                OrderlineSuper.prototype.apply_ms_data.apply(this, arguments);
            }
            var product = this.pos.db.get_product_by_id(data.product_id);
            if (product.qty_available !== data.qty_available) {
                this.pos.set_product_qty_available(product, data.qty_available);
            }

        },
    });

    // block stock negative
    screens.PaymentScreenWidget.include({
        validate_order: function(force_validation) {
            var self = this;
            var _super = this._super;
            var order = this.pos.get_order();
            var orderlines = order.get_orderlines();
            var has_negative_product = false;
            for (var i = 0; i < orderlines.length; i++) {
                if (
                    orderlines[i].product.type == 'product' &&
                    orderlines[i].product.qty_available < orderlines[i].quantity
                ) {
                    has_negative_product = true;
                    self.gui
                        .show_popup('alert',{
                            'title': _t('Can Not Validate Order'),
                            'body': _t('Order has out-of-stock product'),
                        });
                }
            }
            if (!has_negative_product) {
                this._super(force_validation);
            }
        },
    });

    screens.ProductListWidget.include({
        init: function(parent, options) {
            var self = this;
            this._super(parent, options);
            var click_product_handler_super = this.click_product_handler;
            this.click_product_handler = function() {
                var product = self.pos.db.get_product_by_id(this.dataset.productId);
                if (product.type == 'product' && product.qty_available <= 0) {
                    return self.gui.show_popup("alert", {
                        title: _t("The Product is Out of Stock"),
                        body: _t("It's unavailable to add the product"),
                    });
                }
                _.bind(click_product_handler_super, this)();
            };
        },
    });
});