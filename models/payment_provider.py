from odoo import models, fields, api


class PaymentProvider(models.Model):
    _inherit = ['payment.provider']

    # Used as a quick way of seeing if a record has a discount
    discount = fields.Float('Discount', compute='_compute_discount', store=True, readonly=True)
    
    
    discount_type = fields.Selection([
        ('fixed', 'Fixed'),
        ('percentage', 'Percentage'),
    ], string='Discount Type', readonly=False, default='percentage')
    discount_percentage = fields.Float('Discount Percentage')
    discount_fixed_amount = fields.Float('Discount Fixed Amount')
    
    def get_discount(self):
        if self.discount_type == 'fixed':
            return self.discount_fixed_amount
        elif self.discount_type == 'percentage':
            return self.discount_percentage
        return 0.0
    
    @api.depends('discount_percentage', 'discount_fixed_amount')
    def _compute_discount(self):
        for record in self:
            record.discount = record.get_discount()
    
    _sql_constraints = [
        ('discount_percentage_check',
         'CHECK(discount_percentage < 100 AND discount_percentage >= 0)',
         'The discount percentage must be less than 100 and greater than or equal to 0.'),
        
        ('discount_fixed_amount_check',
         'CHECK(discount_fixed_amount >= 0)',
         'The discount fixed amount must be greater than or equal to 0.'),
        
        ('no_both_discount',
         'CHECK((discount_percentage = 0 AND discount_fixed_amount > 0) OR (discount_percentage > 0 AND discount_fixed_amount = 0))',
         'You cannot have both a discount percentage and fixed amount.')
    ]
