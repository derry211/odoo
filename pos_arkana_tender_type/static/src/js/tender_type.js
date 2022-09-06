odoo.define("pos_arkana_tender_type.tender_type", function (require) {
  "use strict";

  var models = require("point_of_sale.models");
  var screens = require("point_of_sale.screens");
  var core = require("web.core");

  var QWeb = core.qweb;
  var _t = core._t;

  var TenderTypeButton = screens.ActionButtonWidget.extend({
    template: "TenderTypeButton",
    init: function (parent, options) {
      this._super(parent, options);

      this.pos.get("orders").bind(
        "add remove change",
        function () {
          this.renderElement();
        },
        this
      );

      this.pos.bind(
        "change:selectedOrder",
        function () {
          this.renderElement();
        },
        this
      );
    },
    button_click: function () {
      var self = this;

      var no_tender_type = [
        {
          label: _t("None"),
        },
      ];
      var tender_types = _.map(self.pos.tender_types, function (tender_type) {
        return {
          label: tender_type.name,
          item: tender_type,
        };
      });

      var selection_list = no_tender_type.concat(tender_types);
      self.gui.show_popup("selection", {
        title: _t("Select Tender Type"),
        list: selection_list,
        confirm: function (tender_type) {
          var order = self.pos.get_order();
          order.tender_type_id = tender_type;
          // This will trigger the recomputation of taxes on order lines.
          // It is necessary to manually do it for the sake of consistency
          // with what happens when changing a customer.
          // _.each(order.orderlines.models, function (line) {
          //     line.set_quantity(line.quantity);
          // });
          order.trigger("change");
        },
        is_selected: function (tender_type) {
          return tender_type === self.pos.get_order().tender_type_id;
        },
      });
    },
    get_current_tender_type_name: function () {
      var name = _t("Tender Type: None");
      var order = this.pos.get_order();

      if (order) {
        var tender_type = order.tender_type_id;

        if (tender_type) {
          name = tender_type.name;
        }
      }
      return name;
    },
  });

  screens.define_action_button({
    name: "tender_type",
    widget: TenderTypeButton,
    condition: function () {
      return true;
    },
  });

  models.load_fields("pos.order", "tender_type_id");

  // load model
  models.load_models({
    model: "pos.tender.type",
    fields: ["name"],
    //domain: function(self){ return [['pos_config_id','=',self.config.id]]; },
    loaded: function (self, tender_types) {
      self.tender_types = tender_types;
      self.tender_types_by_id = {};
      for (var i = 0; i < tender_types.length; i++) {
        self.tender_types_by_id[tender_types[i].id] = tender_types[i];
      }
    },
  });

  var _super = models.Order;
  models.Order = models.Order.extend({
    export_as_JSON: function () {
      var json = _super.prototype.export_as_JSON.apply(this, arguments);
      json.tender_type_id = this.tender_type_id
        ? this.tender_type_id.id
        : false;
      return json;
    },
  });
});
