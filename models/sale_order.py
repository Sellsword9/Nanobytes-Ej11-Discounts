from odoo import models, fields, api
import logging

class SaleOrder(models.Model):
    _inherit = ['sale.order']

    #discount = fields.Float(related='transaction_ids.payment_provider.discount', string='Discount', readonly=True)
    payment_provider = fields.Many2one(related='transaction_ids.provider_id', string='Payment Provider', readonly=True)
    provider_discount = fields.Float('Provider Discount', readonly=True, default=0.0, compute='_compute_provider_discount')
    
    @api.depends('payment_provider')
    def _compute_provider_discount(self):
        self.provider_discount = self.payment_provider.get_discount()
    
    def calculate_percentaje_of_amount(self, discount_amount):
        total = self.amount_total
        percentage = (discount_amount / total) * 100
        return min(percentage, 100)
    def calculate_fraction_of_amount(self, discount_amount):
        total = self.amount_total
        fraction = discount_amount / total
        return min(fraction, 1)
    
    def update_based_on_provider_discount(self):
        _logger = logging.getLogger(__name__)
        #_logger.info("Fixed amount: " + str(self.payment_provider.discount_fixed_amount))
        lines_has_no_discount_yet = True
        _logger.info('Checking if lines have discounts')
        for line in self.order_line:
            if line.discount > 0:
                lines_has_no_discount_yet = False
                break
        if lines_has_no_discount_yet:
            _logger.info('Applying discount')
            tmp_discount = 0.0
            _logger.info('Discount type: ' + str(self.payment_provider.discount_type))
            if self.payment_provider.discount_type == 'fixed':
                tmp_discount = self.calculate_percentaje_of_amount(self.payment_provider.discount_fixed_amount)
                #_logger = logging.getLogger(__name__)
                #_logger.info('Fixed discount for provider at: %s', tmp_discount)
                
            elif self.payment_provider.discount_type == 'percentage':
                tmp_discount = min(self.payment_provider.discount_percentage, 100)
            
            if tmp_discount > 0:
                _logger.info('Discounting ' + str(tmp_discount) + '%')
                for line in self.order_line:
                    line.discount = tmp_discount

    @api.onchange('payment_provider', 'amount_total', 'state')
    def _onchange_payment_provider(self):
        if self.payment_provider:
            self.update_based_on_provider_discount()
    
    def check_payment_provider_discount(self):
        return self.payment_provider.discount_fixed_amount or self.payment_provider.discount_percentage
    
    
    @api.model 
    def write(self, vals):
        res = super(SaleOrder, self).write(vals)
        if self.check_payment_provider_discount():
            self.update_based_on_provider_discount()
        return res

   
    # @api.model
    # @api.depends('order_line.price_subtotal', 'currency_id', 'company_id', 'payment_provider')
    def not_compute_amounts(self):
        has_provider_discount = self.check_payment_provider_discount()
        mult_discount = 1 # If not changed multiply by 1 so it doesnt make differences
        if has_provider_discount:
            if self.payment_provider.discount_type == 'fixed':
                mult_discount = 1 - self.calculate_fraction_of_amount(self.payment_provider.discount_fixed_amount)
            elif self.payment_provider.discount_type == 'percentage':
                mult_discount = 1 - (self.payment_provider.discount_percentage / 100)
            mult_discount = max(mult_discount, 0)
            mult_discount = min(mult_discount, 1)
            
            
        # Overriden code with the multiplication of the discount
        AccountTax = self.env['account.tax']
        for order in self:
            order_lines = order.order_line.filtered(lambda x: not x.display_type)
            base_lines = [line._prepare_base_line_for_taxes_computation() for line in order_lines]
            AccountTax._add_tax_details_in_base_lines(base_lines, order.company_id)
            AccountTax._round_base_lines_tax_details(base_lines, order.company_id)
            tax_totals = AccountTax._get_tax_totals_summary(
                base_lines=base_lines,
                currency=order.currency_id or order.company_id.currency_id,
                company=order.company_id,
            )
            order.amount_untaxed = tax_totals['base_amount_currency'] * mult_discount
            order.amount_tax = tax_totals['tax_amount_currency'] * mult_discount
            order.amount_total = tax_totals['total_amount_currency'] * mult_discount
