// odoo.define("pos_arkana_discount_bank.discount", function (require) {
//   "use strict";

//   var models = require("point_of_sale.models");
//   var screens = require("point_of_sale.screens");
//   var utils = require('web.utils');

//   var core = require("web.core");
//   var round_pr = utils.round_precision;
//   var round_di = utils.round_decimals;

//   var QWeb = core.qweb;
//   var _t = core._t;

//   // Bank Discount
//   var DiscountBankButton = screens.ActionButtonWidget.extend({
//     template: "DiscountBankButton",

//     init: function (parent, options) {
//       this._super(parent, options);

//       this.pos.get("orders").bind(
//         "add remove change",
//         function () {
//           this.renderElement();
//         },
//         this
//       );

//       this.pos.bind(
//         "change:selectedOrder",
//         function () {
//           this.renderElement();
//         },
//         this
//       );
//     },
//     button_click: function () {
//       var self = this;

//       var no_bank_discount = [
//         {
//           label: _t("None"),
//         },
//       ];
//       var bank_discounts = _.map(
//         self.pos.bank_discounts,
//         function (bank_discount) {
//           return {
//             label: bank_discount.name,
//             item: bank_discount,
//           };
//         }
//       );

//       var selection_list = no_bank_discount.concat(bank_discounts);
//       self.gui.show_popup("selection", {
//         title: _t("Select Bank Discount"),
//         list: selection_list,
//         confirm: function (bank_discount) {
//           var order = self.pos.get_order();
//           order.bank_discount_id = bank_discount;

//           if (
//             order.choose_disc != undefined &&
//             order.choose_disc != "disc_bank"
//           ) {
//             self.gui.show_popup("error", {
//               title: _t(
//                 "Bank Discount : Discount Already set another discount "
//               ),
//               body: _t("Please return to the original settings Or Refresh"),
//             });
//             return;
//           }

//           order.set_bank_disc();

//           order.set_choose_disc("disc_bank");

//           var lines = order.get_orderlines();

//           if (lines <= 0) {
//             self.gui.show_popup("error", {
//               title: _t("Bank Discount : Shopping cart is empty"),
//               body: _t(
//                 "Please fill in the Bank discount after entering the shopping cart"
//               ),
//             });
//             return;
//           }

//           order.trigger("change");
//         },
//         is_selected: function (bank_discount) {
//           return bank_discount === self.pos.get_order().bank_discount_id;
//         },
//       });
//     },
//     get_current_bank_discount_name: function () {
//       var name = _t("Bank Discount: None");
//       var order = this.pos.get_order();

//       if (order) {
//         var bank_discount = order.bank_discount_id;

//         if (bank_discount) {
//           name = bank_discount.name;
//         }
//       }

//       if (order.choose_disc != "disc_bank") {
//         name = _t("Bank Discount: None");
//       }

//       return name;
//     },
//   });

//   screens.define_action_button({
//     name: "bank_discount",
//     widget: DiscountBankButton,
//     condition: function () {
//       return true;
//     },
//   });

//   // load model
//   models.load_models({
//     model: "pos.discount.bank",
//     fields: [
//       "name",
//       "product_disc_bank_id",
//       "min_amount",
//       "max_amount",
//       "disc_amount",
//       "disc_percent",
//     ],
//     //domain: function(self){ return [['pos_config_id','=',self.config.id]]; },
//     loaded: function (self, bank_discounts) {
//       self.bank_discounts = bank_discounts;
//       self.bank_discounts_by_id = {};
//       for (var i = 0; i < bank_discounts.length; i++) {
//         self.bank_discounts_by_id[bank_discounts[i].id] = bank_discounts[i];
//       }
//     },
//   });

//   var _super_order = models.Order.prototype;
//   models.Order = models.Order.extend({
//     initialize: function () {
//       _super_order.initialize.apply(this, arguments);
//       // fix
//       if (!this.disc_bank_amount) {
//         this.disc_bank_amount = this.pos.disc_bank_amount;
//       }

//       this.save_to_db();
//     },
//     export_as_JSON: function () {
//       var json = _super_order.export_as_JSON.apply(this, arguments);
//       json.bank_discount_id = this.bank_discount_id ? this.bank_discount_id.id : false;
//       json.disc_bank_amount = this.disc_bank_amount ? this.disc_bank_amount : undefined;
//       json.choose_disc = this.choose_disc ? this.choose_disc : "";
//       return json;
//     },
//     set_choose_disc: function (choose_disc) {
//       this.choose_disc = choose_disc;
//       this.trigger("change", this);
//     },
//     calculate_bank_disc_line: function(){
//       var order = this.pos.get_order();

//       var orderLines = this.get_orderlines();
//       var summary_price = this.summary_for_bank_disc();
//       // console.log(summary_price, "summary")


//       var nilai_pos = order.get_total_with_tax();
//       // console.log(nilai_pos);
//       var min_trans = this.pos.get_order().bank_discount_id.min_amount;
//       // console.log(min_trans);
//       var max_trans = this.pos.get_order().bank_discount_id.max_amount;
//       // console.log(max_trans);
//       if (nilai_pos < min_trans) {
//         order.set_choose_disc(undefined);
//         this.pos.gui.show_popup("error", {
//           title: _t("Transaction cannot be continued"),
//           body: _t("Please Change Discount Bank"),
//         });
//         return;
//       }

//       if (min_trans < nilai_pos && nilai_pos < max_trans) {
//         var disc_bank_percernt = this.pos.get_order().bank_discount_id
//           .disc_percent;
//           this.disc_bank_amount = (disc_bank_percernt / 100.0) * nilai_pos;
//         // console.log(this.disc_bank_amount, "percent");
//       }

//       if (nilai_pos > max_trans) {
//         this.disc_bank_amount = this.pos.get_order().bank_discount_id.disc_amount;
//         // console.log(this.disc_bank_amount, "rp");
//       }

//       for (var i = 0; i < orderLines.length; i++){
//         var line = orderLines[i];

//         var bank_disc_line = 0;

//         var price = line.get_price_with_tax();
        
//         bank_disc_line = (price / summary_price) * this.disc_bank_amount;

//         // console.log(this.disc_bank_amount);

//         // console.log(bank_disc_line);

//         line.set_bank_disc_line(bank_disc_line);
//       }

//     },
//     summary_for_bank_disc: function () {
//       return round_pr(this.orderlines.reduce((function(sum, orderLine) {
//         return sum + orderLine.get_price_with_tax();
//       }), 0), this.pos.currency.rounding);
//     },
//     get_disc_bank_amount: function() {
//       return this.get_disc_bank_amount;
//     },
//     set_bank_disc: function () {
//       this.calculate_bank_disc_line();
//     }
//   });

//   var _super_orderline = models.Orderline.prototype;
//   models.Orderline = models.Orderline.extend({
//     initialize: function (attr, options) {
//       _super_orderline.initialize.call(this, attr, options);
//       this.flag_disc = this.flag_disc;
//       this.bank_disc_line = this.bank_disc_line;
//     },
//     get_flag_disc: function () {
//       return this.flag_disc;
//     },
//     get_bank_disc_line: function () {
//       return this.bank_disc_line;
//     },
//     get_unit_price_disc_bank: function(){
//       var digits = this.pos.dp['Product Price'];
//       // round and truncate to mimic _symbol_set behavior
//       var disc_bank = this.get_bank_disc_line();
      
//       if(disc_bank == undefined){
//         var unit_price = parseFloat(round_di(this.price || 0, digits).toFixed(digits));
//       }else{
//         var unit_price = parseFloat(round_di(this.price || 0, digits).toFixed(digits) - (disc_bank / this.get_quantity()));
//       } 
//       return unit_price;
//     },
//     get_all_prices: function(){
//       var disc_bank = this.get_bank_disc_line();

//       if(disc_bank == undefined){
//         var price_unit = this.get_unit_price()  * (1.0 - (this.get_discount() / 100.0));
//       }else{
//         var price_unit = this.get_unit_price_disc_bank()   * (1.0 - (this.get_discount() / 100.0));
//       }
//       // console.log(price_unit)
//       var taxtotal = 0;

//       var product =  this.get_product();
//       var taxes_ids = product.taxes_id;
//       var taxes =  this.pos.taxes;
//       var taxdetail = {};
//       var product_taxes = [];

//       _(taxes_ids).each(function(el){
//           product_taxes.push(_.detect(taxes, function(t){
//               return t.id === el;
//           }));
//       });

//       var all_taxes = this.compute_all(product_taxes, price_unit, this.get_quantity(), this.pos.currency.rounding);
//       _(all_taxes.taxes).each(function(tax) {
//           taxtotal += tax.amount;
//           taxdetail[tax.id] = tax.amount;
//       });

//       return {
//           "priceWithTax": all_taxes.total_included,
//           "priceWithoutTax": all_taxes.total_excluded,
//           "tax": taxtotal,
//           "taxDetails": taxdetail,
//       };
//     },
//     get_base_price: function(){
//       var disc_bank = this.get_bank_disc_line();
//       var rounding = this.pos.currency.rounding;
      
      
//       if (disc_bank == undefined){
//         var base_price = round_pr(this.get_unit_price() * this.get_quantity() * (1 - this.get_discount()/100), rounding);
//       }else {
//         var base_price = round_pr(this.get_unit_price_disc_bank() * this.get_quantity() * (1 - this.get_discount()/100), rounding);
//       }
//       return base_price;
//     },
//     get_display_price_without_disc_bank: function(){
//       var disc_bank = this.get_bank_disc_line();

//       if(disc_bank == undefined){
//         if (this.pos.config.iface_tax_included === 'total') {
//           return this.get_price_with_tax();
//         } else {
//           return this.get_base_price();
//         }
//       }else{
//         if (this.pos.config.iface_tax_included === 'total') {
//           return this.get_price_with_tax() + (disc_bank / this.get_quantity());
//         } else {
//           return this.get_base_price() + (disc_bank / this.get_quantity());
//         }
//       }
//     },
//     set_bank_disc_line: function(bank_disc_line) {
//       this.bank_disc_line = bank_disc_line;
//       this.trigger("change", this);
//     },
//     export_as_JSON: function () {
//       var json = _super_orderline.export_as_JSON.call(this);
//       json.flag_disc = this.flag_disc;
//       json.bank_disc_line = this.bank_disc_line;
//       return json;
//     },
//     init_from_JSON: function (json) {
//       _super_orderline.init_from_JSON.apply(this, arguments);
//       this.flag_disc = json.flag_disc;
//       this.bank_disc_line = json.bank_disc_line; 
//     },
//   });

//   screens.OrderWidget.include({
//     update_summary: function () {
//       this._super();
//       var order = this.pos.get_order();
      
//       if(order.disc_bank_amount == undefined){
//         return this.format_currency(0);
//       }

//       this.el.querySelector('.summary .total .disc_bank .value').textContent =  this.format_currency(order.disc_bank_amount);

//     },
//   });

// });
