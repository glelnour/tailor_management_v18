# Copyright 2019 Tecnativa - Ernesto Tejeda
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    pack_line_ids = fields.One2many(
        "product.pack.line",
        "parent_product_id",
        string="Pack Products",
        help="Products that are part of this pack.",
    )
    used_in_pack_line_ids = fields.One2many(
        "product.pack.line",
        "product_id",
        string="Found in Packs",
        help="Packs where this product is used.",
    )

    def get_pack_lines(self):
        """Return all pack lines of this product (if it's a pack)."""
        return self.mapped("pack_line_ids")

    def split_pack_products(self):
        # Just check if the product has pack lines → treat it as a pack
        packs = self.filtered(lambda p: p.pack_line_ids)
        return packs, (self - packs)

    # def _price_compute(self, price_type, uom=False, currency=False, company=False, date=False):
    #     packs, no_packs = self.split_pack_products()
    #     prices = super(ProductProduct, no_packs)._price_compute(
    #         price_type, uom, currency, company
    #     )
    #     for product in packs.sudo():
    #         pack_price = 0.0
    #         for pack_line in product.pack_line_ids:
    #             pack_price += pack_line.get_price()
    #         pricelist_id_or_name = self._context.get("pricelist")
    #         if pricelist_id_or_name:
    #             if isinstance(pricelist_id_or_name, list):
    #                 pricelist_id_or_name = pricelist_id_or_name[0]
    #             if isinstance(pricelist_id_or_name, str):
    #                 pricelist_name_search = self.env["product.pricelist"].name_search(
    #                     pricelist_id_or_name, operator="=", limit=1
    #                 )
    #                 if pricelist_name_search:
    #                     pricelist = self.env["product.pricelist"].browse(
    #                         pricelist_name_search[0][0]
    #                     )
    #             elif isinstance(pricelist_id_or_name, int):
    #                 pricelist = self.env["product.pricelist"].browse(pricelist_id_or_name)
    #             if pricelist and pricelist.currency_id != product.currency_id:
    #                 pack_price = pricelist.currency_id._convert(
    #                     pack_price,
    #                     product.currency_id,
    #                     self.env.company,
    #                     fields.Date.today(),
    #                 )
    #         prices[product.id] = pack_price
    #     return prices

    @api.depends("list_price", "price_extra")
    def _compute_product_lst_price(self):
        packs, no_packs = self.split_pack_products()
        ret_val = super(ProductProduct, no_packs)._compute_product_lst_price()
        uom = self._context.get("uom", False)
        if uom:
            uom = self.env["uom.uom"].browse([uom])
        for product in packs:
            list_price = product._price_compute("list_price").get(product.id)
            if uom:
                list_price = product.uom_id._compute_price(list_price, uom)
            product.lst_price = list_price + product.price_extra
        return ret_val

    def compute_cost_from_pack(self):
        """Compute the cost from pack components."""
        for rec in self:
            if rec.pack_line_ids:
                total_cost = sum(rec.pack_line_ids.mapped('total_cost'))
                rec.standard_price = total_cost
