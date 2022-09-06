odoo.define("pos_arkana_discount.discount", function (require) {
  "use strict";

  var models = require("point_of_sale.models");
  var gui = require("point_of_sale.gui");
  var screens = require("point_of_sale.screens");
  var PopupWidget = require("point_of_sale.popups");
  var utils = require('web.utils');


  var core = require("web.core");
  var round_pr = utils.round_precision;
  var round_di = utils.round_decimals;


  var QWeb = core.qweb;
  var _t = core._t;


  // Global Disc
  // ---------------------------
  var JavaraGlobalDiscountWidget = PopupWidget.extend({
    template: "JavaraGlobalDiscountWidget",

    show: function (options) {
      this._super(options);
    },

    click_confirm: function () {
      var value = this.$("#disc_type").val();
      var value1 = this.$("#global_disc").val();

      this.gui.close_popup();
      if (this.options.confirm) {
        this.options.confirm.call(this, value, value1);
      }
    },
  });

  gui.define_popup({
    name: "javara_global_discount_widget",
    widget: JavaraGlobalDiscountWidget,
  });

  var GlobalDiscountButton = screens.ActionButtonWidget.extend({
    template: "GlobalDiscountButton",
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

      self.gui.show_popup("javara_global_discount_widget", {
        title: _t("Add Global Discount"),
        confirm: function (disc_type, global_disc) {
          var order = self.pos.get_order();
          var lines = order.get_orderlines();


          if (
            order.choose_disc != undefined &&
            order.choose_disc != "global_disc"
          ) {
            self.gui.show_popup("error", {
              title: _t(
                "Global Discount : Discount Already set another discount "
              ),
              body: _t("Please return to the original settings Or Refresh"),
            });
            return;
          }

          order.set_choose_disc("global_disc");

          if (order.disc_type == "") {
            order.set_choose_disc(undefined);
          }

          if (lines <= 0) {
            order.set_choose_disc(undefined);
            self.gui.show_popup("error", {
              title: _t("Global Discount : Shopping cart is empty"),
              body: _t(
                "Please fill in the Global discount after entering the shopping cart"
              ),
            });
            return;
          }


          order.set_global_disc(global_disc, disc_type);

          order.trigger("change");
        },
      });
    },

    get_current_disc_type_name: function () {
      var name_disc_type = _t("Global Disc:");
      var order_disc_type = this.pos.get_order();

      if (order_disc_type) {
        var disc_type_name = order_disc_type.disc_type;

        if (disc_type_name) {
          name_disc_type = disc_type_name;
        }
      }

      return name_disc_type;
    },
    get_current_global_disc_name: function () {
      var name_global_disc = _t(" None");
      var order_global_disc = this.pos.get_order();

      if (order_global_disc) {
        var global_disc_name = order_global_disc.global_disc;

        if (global_disc_name) {
          name_global_disc = global_disc_name;
        }
      }

      return name_global_disc;
    },
  });

  screens.define_action_button({
    name: "global_discount_button",
    widget: GlobalDiscountButton,
    condition: function () {
      return true;
    },
  });


  // Bank Disc 
  // -------------------------------------------
  var DiscountBankButton = screens.ActionButtonWidget.extend({
    template: "DiscountBankButton",

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

      var no_bank_discount = [
        {
          label: _t("None"),
        },
      ];

      if(self.pos.bank_discounts == undefined){
        return{
          label: _t("None"),
        }
      }

      var bank_discounts = _.map(
        self.pos.bank_discounts,
        function (bank_discount) {
            return {
              label: bank_discount.name, 
              item: bank_discount 
            };
        }
      );

      var selection_list = no_bank_discount.concat(bank_discounts);
      self.gui.show_popup("selection", {
        title: _t("Select Bank Discount"),
        list: selection_list,
        confirm: function (bank_discount) {
          var order = self.pos.get_order();
          order.bank_discount_id = bank_discount;

          if (
            order.choose_disc != undefined &&
            order.choose_disc != "disc_bank"
          ) {
            self.gui.show_popup("error", {
              title: _t(
                "Bank Discount : Discount Already set another discount "
              ),
              body: _t("Please return to the original settings Or Refresh"),
            });
            return;
          }

          var lines = order.get_orderlines();

          if (lines <= 0) {
            self.gui.show_popup("error", {
              title: _t("Bank Discount : Shopping cart is empty"),
              body: _t(
                "Please fill in the Bank discount after entering the shopping cart"
              ),
            });
            return;
          }

          if (bank_discount != undefined){
            order.set_choose_disc("disc_bank");
            order.set_name_bank_disc(bank_discount.name);
          }else{
            order.set_choose_disc(undefined);
            order.set_name_bank_disc(undefined);
          }

          order.set_bank_disc();

          order.trigger("change");
        },
        is_selected: function (bank_discount) {
          return bank_discount === self.pos.get_order().bank_discount_id;
        },
      });
    },
    get_current_bank_discount_name: function () {
      var name_display_bank = _t("Bank Discount: None");
      var order = this.pos.get_order();

      if (order) {
        var bank_discount = order.bank_discount_id;

        if (bank_discount) {
          name_display_bank = bank_discount.name;
        }
      }
      return name_display_bank;
    
    },
  });

  screens.define_action_button({
    name: "bank_discount",
    widget: DiscountBankButton,
    condition: function () {
      return true;
    },
  });

  // load model
  models.load_models({
    model: "pos.discount.bank",
    fields: [
      "name",
      "product_disc_bank_id",
      "min_amount",
      "max_amount",
      "disc_amount",
      "disc_percent",
    ],
    //domain: function(self){ return [['pos_config_id','=',self.config.id]]; },
    loaded: function (self, bank_discounts) {
      self.bank_discounts = bank_discounts;
      self.bank_discounts_by_id = {};
      for (var i = 0; i < bank_discounts.length; i++) {
        self.bank_discounts_by_id[bank_discounts[i].id] = bank_discounts[i];
      }
    },
  });


  // Order 
  // ------------------------------
  var _super_order = models.Order.prototype;
  models.Order = models.Order.extend({
    initialize: function () {
      _super_order.initialize.apply(this, arguments);
      if (!this.disc_type) {
        this.disc_type = this.pos.disc_type;
      }

      // % atau fix
      if (!this.global_disc) {
        this.global_disc = this.pos.global_disc;
      }

      // fix
      if (!this.global_disc_amount) {
        this.global_disc_amount = this.pos.global_disc_amount;
      }

      if (!this.choose_disc) {
        this.choose_disc = this.pos.choose_disc;
      }

      if (!this.name_bank_disc) {
        this.name_bank_disc = this.pos.name_bank_disc;
      }

      if (!this.disc_bank_amount) {
        this.disc_bank_amount = this.pos.disc_bank_amount;
      }

      this.save_to_db();
    },
    // Global Disc
    // -------------------------------------------
    calculate_gloal_disc_line: function (global_disc, disc_type) {
      this.global_disc = global_disc;
      this.disc_type = disc_type;

      var orderLines = this.get_orderlines();
      var summary_price = this.summary_for_global_disc();

      if (this.disc_type != "fix") {
        this.global_disc_amount = (summary_price * this.global_disc) / 100;
      } else {
        // force integer
        this.global_disc_amount = parseInt(this.global_disc);
      }

      for (var i = 0; i < orderLines.length; i++) {
        var line = orderLines[i];

        var global_disc_line = 0;
        var price = line.get_price_with_tax(); //sudah apply discount line
        
        global_disc_line = (price / summary_price) * this.global_disc_amount;
        
        line.set_global_disc_line(global_disc_line);
      }
    },
    get_global_disc_amount: function (){
      return this.global_disc_amount;
    },
    summary_for_global_disc:function() {
      return round_pr(this.orderlines.reduce((function(sum, orderLine) {
        return sum + orderLine.get_price_with_tax();
      }), 0), this.pos.currency.rounding);
    },
    export_as_JSON: function () {
      var json = _super_order.export_as_JSON.apply(this, arguments);
      json.disc_type = this.disc_type ? this.disc_type : "";
      json.global_disc = this.global_disc ? this.global_disc : "";
      json.global_disc_amount = this.global_disc_amount
        ? this.global_disc_amount
        : undefined;
      json.choose_disc = this.choose_disc ? this.choose_disc : "";
      json.bank_discount_id = this.bank_discount_id ? this.bank_discount_id.id : false;
      json.name_bank_disc = this.name_bank_disc ? this.name_bank_disc : undefined;
      json.disc_bank_amount = this.disc_bank_amount ? this.disc_bank_amount : undefined;
      return json;
    },
    init_from_JSON: function (json) {
      _super_order.init_from_JSON.apply(this, arguments);
      this.disc_type = this.pos.disc_type;
      this.global_disc = this.pos.global_disc;
      this.global_disc_amount = this.pos.global_disc_amount;
      this.choose_disc = this.choose_disc;
    },
    export_for_printing: function () {
      var json = _super_order.export_for_printing.apply(this, arguments);
      json.disc_type = this.disc_type ? this.disc_type : "";
      json.global_disc = this.global_disc ? this.global_disc : "";
      json.global_disc_amount = this.global_disc_amount
        ? this.global_disc_amount
        : undefined;
      json.choose_disc = this.choose_disc ? this.choose_disc : "";
      return json;
    },
    set_choose_disc: function (choose_disc) {
      this.choose_disc = choose_disc;
      this.trigger("change", this);
    },
    set_name_bank_disc: function (name_bank){
      this.name_bank_disc = name_bank;
      this.trigger("change", this);
    },
    get_total_with_tax_and_global_bank: function() {
      if (this.get_global_disc_amount() == undefined && this.get_disc_bank_amount() == undefined){
        return 0;
      }
      if (this.get_global_disc_amount() != undefined){
        return this.get_total_without_tax() + this.get_total_tax() + this.get_global_disc_amount();
      }
      if (this.get_disc_bank_amount() != undefined){
        return this.get_total_without_tax() + this.get_total_tax() + this.get_disc_bank_amount();
      }
      
    },
    set_global_disc: function (global_disc, disc_type) {
      this.calculate_gloal_disc_line(global_disc, disc_type);
    },
    reset_global_disc: function () {
      this.calculate_gloal_disc_line(0, "");
    },
    set_choose_disc: function (choose_disc) {
      this.choose_disc = choose_disc;
      this.trigger("change", this);
    },
    // Disc Bank 
    // ------------------------------------
    calculate_bank_disc_line: function(){
      var order = this.pos.get_order();

      var orderLines = this.get_orderlines();
      var summary_price = this.summary_for_bank_disc();
      
      if(order.bank_discount_id != undefined){

        var nilai_pos = order.get_total_with_tax();
        
        var min_trans = this.pos.get_order().bank_discount_id.min_amount;
        
        var max_trans = this.pos.get_order().bank_discount_id.max_amount;
    
        if (nilai_pos < min_trans) {
          order.set_choose_disc(undefined);
          this.pos.gui.show_popup("error", {
            title: _t("Transaction cannot be continued"),
            body: _t("Please Change Discount Bank"),
          });
          return;
        }
  
        if (min_trans < nilai_pos && nilai_pos < max_trans) {
          var disc_bank_percernt = this.pos.get_order().bank_discount_id
            .disc_percent;
            this.disc_bank_amount = (disc_bank_percernt / 100.0) * nilai_pos;
        }
  
        if (nilai_pos > max_trans) {
          this.disc_bank_amount = this.pos.get_order().bank_discount_id.disc_amount;
        }
  
        for (var i = 0; i < orderLines.length; i++){
          var line = orderLines[i];
  
          var bank_disc_line = 0;
  
          var price = line.get_price_with_tax();
          
          bank_disc_line = (price / summary_price) * this.disc_bank_amount;
  
          line.set_bank_disc_line(bank_disc_line);
        }
      }else{
  
        for (var i = 0; i < orderLines.length; i++){
          var line = orderLines[i];
  
  
          line.set_bank_disc_line(0);
        }

        order.disc_bank_amount = 0;
        order.set_choose_disc(undefined);
      }
    },
    summary_for_bank_disc: function () {
      return round_pr(this.orderlines.reduce((function(sum, orderLine) {
        return sum + orderLine.get_price_with_tax();
      }), 0), this.pos.currency.rounding);
    },
    get_disc_bank_amount: function() {
      return this.disc_bank_amount;
    },
    set_bank_disc: function () {
      this.calculate_bank_disc_line();
    }
  });


  // Orderline 
  // -------------------------------------
  var _super_orderline = models.Orderline.prototype;
  models.Orderline = models.Orderline.extend({
    initialize: function (attr, options) {
      _super_orderline.initialize.call(this, attr, options);
      this.global_disc_line = this.global_disc_line;
      this.flag_disc = this.flag_disc;
      this.bank_disc_line = this.bank_disc_line;
    },
    set_global_disc_line: function (global_disc_line) {
      this.global_disc_line = global_disc_line;
      this.trigger("change", this);
    },

    // Global Disc 
    // ---------------------------
    get_global_disc_line: function () {
      return this.global_disc_line;
    },
    
    // Disc Bank 
    // ---------------------------
    get_flag_disc: function () {
      return this.flag_disc;
    },
    get_bank_disc_line: function () {
      return this.bank_disc_line;
    },
    get_unit_price_disc_bank_global: function(){
      var digits = this.pos.dp['Product Price'];
      var disc_bank = this.get_bank_disc_line();
      var disc_global = this.get_global_disc_line();
      
      if(disc_bank == undefined && disc_global == undefined){
        var unit_price = parseFloat(round_di(this.price || 0, digits).toFixed(digits));
      }
      
      if(disc_bank != undefined){
        var unit_price = parseFloat(round_di(this.price || 0, digits).toFixed(digits) - (disc_bank / this.get_quantity()));
      }

      if(disc_global != undefined){
        var unit_price = parseFloat(round_di(this.price || 0, digits).toFixed(digits) - (disc_global / this.get_quantity()));
      }


      return unit_price;
    },
    get_all_prices: function(){
      var disc_bank = this.get_bank_disc_line();
      var disc_global = this.get_global_disc_line();

      if(disc_bank == undefined && disc_global == undefined){
        var price_unit = this.get_unit_price()  * (1.0 - (this.get_discount() / 100.0));
      }

      if(disc_bank != undefined){
        var price_unit = this.get_unit_price_disc_bank_global()   * (1.0 - (this.get_discount() / 100.0));
      }

      if(disc_global != undefined){
        var price_unit = this.get_unit_price_disc_bank_global()   * (1.0 - (this.get_discount() / 100.0));
      }      
      
      var taxtotal = 0;

      var product =  this.get_product();
      var taxes_ids = product.taxes_id;
      var taxes =  this.pos.taxes;
      var taxdetail = {};
      var product_taxes = [];

      _(taxes_ids).each(function(el){
          product_taxes.push(_.detect(taxes, function(t){
              return t.id === el;
          }));
      });

      var all_taxes = this.compute_all(product_taxes, price_unit, this.get_quantity(), this.pos.currency.rounding);
      _(all_taxes.taxes).each(function(tax) {
          taxtotal += tax.amount;
          taxdetail[tax.id] = tax.amount;
      });

      return {
          "priceWithTax": all_taxes.total_included,
          "priceWithoutTax": all_taxes.total_excluded,
          "tax": taxtotal,
          "taxDetails": taxdetail,
      };
    },
    get_base_price: function(){
      var disc_bank = this.get_bank_disc_line();
      var disc_global = this.get_global_disc_line();

      var rounding = this.pos.currency.rounding;
      
      
      if (disc_bank == undefined && disc_global == undefined){
        var base_price = round_pr(this.get_unit_price() * this.get_quantity() * (1 - this.get_discount()/100), rounding);
      }
      if(disc_bank != undefined){
        var base_price = round_pr(this.get_unit_price_disc_bank_global() * this.get_quantity() * (1 - this.get_discount()/100), rounding);
      }

      if(disc_global != undefined){
        var base_price = round_pr(this.get_unit_price_disc_bank_global() * this.get_quantity() * (1 - this.get_discount()/100), rounding);
      }


      return base_price;
    },
    get_display_price_without_disc_bank_global: function(){
      var disc_bank = this.get_bank_disc_line();
      var disc_global = this.get_global_disc_line();


      if(disc_bank == undefined && disc_global == undefined){
        if (this.pos.config.iface_tax_included === 'total') {
          return this.get_price_with_tax();
        } else {
          return this.get_base_price();
        }
      }
      if(disc_bank != undefined){
        if (this.pos.config.iface_tax_included === 'total') {
          return this.get_price_with_tax() + disc_bank;
        } else {
          return this.get_base_price() + disc_bank;
        }
      }
      if(disc_global != undefined){
        if (this.pos.config.iface_tax_included === 'total') {
          return this.get_price_with_tax() + disc_global;
        } else {
          return this.get_base_price() + disc_global;
        }
      }
      
    },
    set_bank_disc_line: function(bank_disc_line) {
      this.bank_disc_line = bank_disc_line;
      this.trigger("change", this);
    },

    export_as_JSON: function () {
      var json = _super_orderline.export_as_JSON.call(this);
      json.global_disc_line = this.global_disc_line;
      json.flag_disc = this.flag_disc;
      json.bank_disc_line = this.bank_disc_line;
      return json;
    },
    init_from_JSON: function (json) {
      _super_orderline.init_from_JSON.apply(this, arguments);
      this.global_disc_line = json.global_disc_line;
      this.flag_disc = json.flag_disc;
      this.bank_disc_line = json.bank_disc_line; 
    },
  });

  // Screen POS
  // -----
  screens.OrderWidget.include({
    update_summary: function () {
      this._super();
      var order = this.pos.get_order();
      
      if(!order.get_orderlines().length){
        return;
      }

      var global = order.global_disc_amount ? order.global_disc_amount : 0;
      var bank = order.disc_bank_amount ? order.disc_bank_amount: 0;
       

      this.el.querySelector('.summary .total .global_disc .value').textContent =  this.format_currency(global);

      this.el.querySelector('.summary .total .disc_bank .value').textContent =  this.format_currency(bank);

    },
  });
});
