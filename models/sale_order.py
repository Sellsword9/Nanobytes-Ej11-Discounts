from odoo import models, fields, api
import logging

class SaleOrder(models.Model):
    _inherit = ['sale.order']

    #discount = fields.Float(related='transaction_ids.payment_provider.discount', string='Discount', readonly=True)
    payment_provider = fields.Many2one(related='transaction_ids.provider_id', string='Payment Provider', readonly=True)
    
    def calculate_percentaje_of_amount(self, discount_amount):
        # This method gets a number and returns the % that that number represents of the total amount of this order
        # If the % is greater than 100, it returns 100
        total = self.amount_total
        percentage = (discount_amount * 100) / total
        return min(percentage, 100)
    
    def update_based_on_provider_discount(self):
        _logger = logging.getLogger(__name__)
        _logger.info('Updating 1221')
        _logger.info('INFO: $ ---->' + str(self.payment_provider.discount_fixed_amount))
        _logger.info('INFO: % -->' + str(self.payment_provider.discount_percentage))
        has_discount = self.payment_provider.discount_fixed_amount or self.payment_provider.discount_percentage
        if has_discount:
            _logger.info('if entereed 1221 aksjdajsdoajdiajisjasiodaiosjaiosd')
            tmp_discount = 0.0
            if self.payment_provider.discount_type == 'fixed':
                tmp_discount = self.calculate_percentaje_of_amount(self.payment_provider.discount_fixed_amount)
                
            elif self.payment_provider.discount_type == 'percentage':
                tmp_discount = min(self.payment_provider.discount_percentage, 100)
            
            _logger.info('INFO  INFO: Discounting the sale order by ' + str(tmp_discount) + '% from a payment of ' + self.payment_provider.name)
            for line in self.order_line:
                line.discount = tmp_discount
            
        else:
            _logger.info('INFO: GHJGHJGHJ No discount found for the payment provider INFO: /n GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment provider /n GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment providerINFO: GHJGHJGHJ No discount found for the payment provider')
    
    @api.onchange('payment_provider', 'amount_total', 'state')
    def _onchange_payment_provider(self):
        _logger = logging.getLogger(__name__)
        _logger.info('Updating 999')
        if self.payment_provider:
            self.update_based_on_provider_discount()
            
    @api.model 
    def write(self, vals):
        _logger = logging.getLogger(__name__)
        _logger.info('Updating 888')
        res = super(SaleOrder, self).write(vals)
        self.update_based_on_provider_discount()
        return res