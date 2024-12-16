import {
  LocationSelectorDialog
} from '@delivery/js/location_selector/location_selector_dialog/location_selector_dialog';
import { _t } from '@web/core/l10n/translation';
import { rpc } from '@web/core/network/rpc';
import publicWidget from '@web/legacy/js/public/public_widget';

publicWidget.registry.WebsiteSalePProviderDiscount = publicWidget.Widget.extend({
  selector: '#o_payment_form',
  events: {
    // Addresses
    'change [name="o_payment_radio"]': '_changePaymentMethod',
  },

  // #=== WIDGET LIFECYCLE ===#
  async _getDiscount(providerId) {
    let r = await rpc("/shop/get_provider_discount", { 'provider_id': providerId });
    return r;
  },

  async _changePaymentMethod(ev) {
    const discountElement = document.getElementById("provider_discount_span");
    const discountTotalElement = document.getElementById("provider_discount_access");

    let providerId = ev.target.getAttribute('data-provider-id');
    providerId = parseInt(providerId);
    if (!providerId) {
      return;
    } else {
      let discountFound = await this._getDiscount(providerId);
      if (discountElement && discountTotalElement) {
        if (discountFound) {
          // Calculate discount in base of the total
          if (discountFound.discountType == "fixed") {
            let txt = Math.min(discountFound.trueDiscount, parseFloat(discountTotalElement.innerHTML));
            discountElement.innerHTML = "-" + txt;
          } else {
            let total = parseFloat(discountTotalElement.innerHTML);
            let discount = discountFound.trueDiscount;
            let txt = (discount / 100) * total;
            discountElement.innerHTML = "-" + txt.toFixed(2);
          }
        } else {
          discountElement.innerHTML = "0";
        }

      }
    }
  },
});


console.log("JS loaded");
export default publicWidget.registry.WebsiteSalePProviderDiscount;
