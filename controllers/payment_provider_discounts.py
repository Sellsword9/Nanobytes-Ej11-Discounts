from odoo import http
from odoo.http import request
import logging
from odoo import _
from odoo.exceptions import AccessError, MissingError, ValidationError
from odoo.fields import Command
from odoo.http import request, route
from odoo.tools import float_compare

from odoo.addons.payment.controllers import portal as payment_portal

class WebsiteSale(http.Controller):

    @http.route('/shop/get_provider_discount', type='json', auth='public', website=True)
    def get_provider_discount(self, provider_id):
        # Default
        discount = 0.0
        self.updateCart()
        
        
        #_logger = logging.getLogger(__name__)
        # _logger.info('Provider id: %s', provider_id)
       
        
        provider = request.env['payment.provider'].sudo().browse(provider_id)
        
        #_logger.info('Provider found: %s', provider)
        #_logger.info('Provider discount: %s', provider.get_discount())
        discountNumeric = provider.get_discount()
        
        discountType = "error"
        if provider.discount_type == 'fixed':
            discount = str(provider.discount_fixed_amount) + ""
            discountType = "fixed"
        elif provider.discount_type == 'percentage':
            discount = str(provider.discount_percentage) + '%'
            discountType = "percentage"
        
        
        value = {
            'discountText': discount,
            'discountType': discountType,
            'trueDiscount': discountNumeric
        }
        return value
    
    def updateCart(self):
        _logger = logging.getLogger(__name__)
        _logger.info('Updating cart')
        order = request.website.sale_get_order()
        order.update_based_on_provider_discount()

# Override payment transaction to force applying discount before paying 
class PaymentPortal(payment_portal.PaymentPortal):
    @http.route('/shop/payment/transaction/<int:order_id>', type='json', auth='public', website=True)
    def shop_payment_transaction(self, order_id, access_token, **kwargs):
        """ Create a draft transaction and return its processing values.

        :param int order_id: The sales order to pay, as a `sale.order` id
        :param str access_token: The access token used to authenticate the request
        :param dict kwargs: Locally unused data passed to `_create_transaction`
        :return: The mandatory values for the processing of the transaction
        :rtype: dict
        :raise: ValidationError if the invoice id or the access token is invalid
        """
        # Check the order id and the access token
        try:
            order_sudo = self._document_check_access('sale.order', order_id, access_token)
        except MissingError:
            raise
        except AccessError as e:
            raise ValidationError(_("The access token is invalid.")) from e

        if order_sudo.state == "cancel":
            raise ValidationError(_("The order has been cancelled."))
        
        # Apply discount before paying
        order_sudo.update_based_on_provider_discount()

        order_sudo._check_cart_is_ready_to_be_paid()

        self._validate_transaction_kwargs(kwargs)
        kwargs.update({
            'partner_id': order_sudo.partner_invoice_id.id,
            'currency_id': order_sudo.currency_id.id,
            'sale_order_id': order_id,  # Include the SO to allow Subscriptions to tokenize the tx
        })
        if not kwargs.get('amount'):
            kwargs['amount'] = order_sudo.amount_total

        if float_compare(kwargs['amount'], order_sudo.amount_total, precision_rounding=order_sudo.currency_id.rounding):
            raise ValidationError(_("The cart has been updated. Please refresh the page."))

        tx_sudo = self._create_transaction(
            custom_create_values={'sale_order_ids': [Command.set([order_id])]}, **kwargs,
        )

        # Store the new transaction into the transaction list and if there's an old one, we remove
        # it until the day the ecommerce supports multiple orders at the same time.
        request.session['__website_sale_last_tx_id'] = tx_sudo.id

        self._validate_transaction_for_order(tx_sudo, order_sudo)

        return tx_sudo._get_processing_values()
