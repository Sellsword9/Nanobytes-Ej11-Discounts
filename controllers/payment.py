from odoo import _
from odoo.http import request, route
from odoo.tools import float_compare

# Logger import
import logging

from odoo.addons.website_sale.controllers import payment as payment_portal

logger = logging.getLogger(__name__)

class PaymentPortal(payment_portal.PaymentPortal):
    inherit = ['website_sale.payment']
    
    def _validate_transaction_for_order(self, transaction, sale_order): 
        
        logger.info("the quick brown fox jumps over the lazy dog")
        logger.info(sale_order)
        logger.info(transaction)
        logger.info(sale_order.amount_total)
        logger.info(sale_order.reference)
        logger.info("the quick brown fox jumps over the lazy dog")
        # Payment now has a new field called discount so if we have product then we should apply
        # discount to the order
        product = sale_order.reference

        total = sale_order.amount_total
        if product:
            discount = transaction.payment_provider_id.get_discount()
            if discount:
                logger.info("Discount is applied")
        return 
