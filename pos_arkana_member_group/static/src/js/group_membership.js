odoo.define("pos_arkana_member_group.member_group", function (require) {
  "use strict";

  var models = require("point_of_sale.models");
  var screens = require("point_of_sale.screens");
  var core = require("web.core");

  var QWeb = core.qweb;
  var _t = core._t;

  var ClientListScreenWidget = screens.ClientListScreenWidget.include({
    save_changes: function () {
      var order = this.pos.get_order();
      // member ?
      var active_member_id = (this.new_client && this.new_client.active_member_id) ? this.new_client.active_member_id[0] : false;
      var member = (active_member_id) ? this.pos.member_by_id[this.new_client.active_member_id[0]] : undefined;
      if (member != undefined){
        // prevent using another disc type
        if (order.choose_disc != undefined && order.choose_disc != "membership") {
          return this.pos.gui.show_popup("error", {
            title: _t("Membership : Discount Already set another discount "),
            body: _t("Please return to the original settings Or Refresh"),
          });
        }
      }

      if (this.has_client_changed()) {
        var default_fiscal_position_id = _.findWhere(
          this.pos.fiscal_positions,
          { id: this.pos.config.default_fiscal_position_id[0] }
        );
        order.set_client(this.new_client);
        if (this.new_client) {
          if (this.new_client.property_account_position_id) {
            var client_fiscal_position_id = _.findWhere(
              this.pos.fiscal_positions,
              { id: this.new_client.property_account_position_id[0] }
            );
            order.fiscal_position =
              client_fiscal_position_id || default_fiscal_position_id;
          }

          order.set_pricelist(
            _.findWhere(this.pos.pricelists, {
              id: this.new_client.property_product_pricelist[0],
            }) || this.pos.default_pricelist
          );

          // check member & set choose disc
          // var active_member_id = (this.new_client.active_member_id) ? this.new_client.active_member_id[0] : false;
          // var member = (active_member_id) ? this.pos.member_by_id[this.new_client.active_member_id[0]] : undefined;

          //perlu lagi?
          // if (member == undefined){
          //   order.set_choose_disc(order.choose_disc); //order.choose_disc
          // } else {
          //   order.set_choose_disc("membership");
          // }
        } 
        else {
          if (default_fiscal_position_id) {
            order.fiscal_position = default_fiscal_position_id;
          }
          order.set_pricelist(this.pos.default_pricelist);
          // set non undefined choose disc or existing choice
          if (order.disc_type || order.name_bank_disc) {
            order.set_choose_disc(order.choose_disc);
          } else {
            order.set_choose_disc(undefined);
          }
        }
      }

    },
  });

  // Override
  var _super = models.Order.prototype;
  models.Order = models.Order.extend({
    export_as_JSON: function () {
      var json = _super.export_as_JSON.apply(this, arguments);
      json.choose_disc = this.choose_disc ? this.choose_disc : "";
      return json;
    },
    set_choose_disc: function (choose_disc) {
      this.choose_disc = choose_disc;
      this.trigger("change", this);
    },
    set_pricelist: function (pricelist) {
      var self = this;
      var order = this.pos.get_order();
      var client = this.pos.get_client();

      // Validasi Matching With Pricelist
      if (pricelist.is_member) {
        if (client) {
          var member = this.pos.member_by_id[client.active_member_id[0]];

          // member different pricelist
          if (member && member.pricelist_id[0] != pricelist.id) {
            return self.pos.gui.show_popup("error", {
              title: _t("Error: 'Member Not Match With Pricelist'"),
              body: _t(
                "Pricelist is not for this member, Please select another Pricelist"
              ),
            });
          // non-member
          } else if (member == undefined) {
            return self.pos.gui.show_popup("error", {
                  title: _t("Error: 'Pricelist Not For Customer'"),
                  body: _t(
                    "Pricelist is not for customer, Please select another Pricelist"
                  ),
                });
          // member
          } else {
            // set to membership
            if (order) {
              order.set_choose_disc('membership');
            }
          }
          
        } else {
          // not allow for non member / non client
          return self.pos.gui.show_popup("error", {
                title: _t("Error: 'Pricelist Not For Non Customer'"),
                body: _t(
                  "Pricelist is not for non customer, Please select another Pricelist"
                ),
              });
        }
      } 
      else {
        // non-member pricelist
        // set to undefined
        if (order) {
          // set non undefined choose disc or existing choice
          if (order.disc_type || order.name_bank_disc) {
            order.set_choose_disc(order.choose_disc);
          } else {
            order.set_choose_disc(undefined);
          }
        }
      }

      this.pricelist = pricelist;

      var lines_to_recompute = _.filter(this.get_orderlines(), function (line) {
        return !line.price_manually_set;
      });
      _.each(lines_to_recompute, function (line) {
        line.set_unit_price(
          line.product.get_price(self.pricelist, line.get_quantity())
        );
        self.fix_tax_included_price(line);
      });

      this.trigger("change");
    },
  });

  // Load Field
  models.load_fields("res.partner", "active_member_id");
  models.load_fields("product.pricelist", "is_member");

  // load model
  models.load_models({
    model: "res.partner.member",
    fields: ["name", "pricelist_id"],
    loaded: function (self, members) {
      self.members = members;
      self.member_by_id = {};
      self.member_icon_by_id = {};
      for (var i = 0; i < members.length; i++) {
        self.member_by_id[members[i].id] = members[i];
        self.member_icon_by_id[members[i].id] =
          "/web/image?model=res.partner.member&id=" +
          members[i].id +
          "&field=icon";
      }
    },
  });
});
