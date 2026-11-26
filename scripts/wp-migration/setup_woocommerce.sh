#!/usr/bin/env bash
# Install and do the baseline configuration of WooCommerce on the destination
# WordPress site (lesponctuelles.be). Run this on the server itself (SSH),
# in the WordPress install directory, with WP-CLI available.
#
# Usage: ./setup_woocommerce.sh
# Optional overrides: WC_COUNTRY, WC_CURRENCY (defaults below are for Belgium).

set -euo pipefail

WC_COUNTRY="${WC_COUNTRY:-BE}"
WC_CURRENCY="${WC_CURRENCY:-EUR}"

if ! command -v wp >/dev/null 2>&1; then
  echo "wp-cli (wp) not found on PATH. Install it first: https://wp-cli.org/#installing" >&2
  exit 1
fi

echo "== Installing and activating WooCommerce =="
wp plugin install woocommerce --activate

echo "== Base store settings (country: $WC_COUNTRY, currency: $WC_CURRENCY) =="
wp option update woocommerce_default_country "$WC_COUNTRY"
wp option update woocommerce_currency "$WC_CURRENCY"
wp option update woocommerce_currency_pos "left_space"
wp option update woocommerce_price_thousand_sep " "
wp option update woocommerce_price_decimal_sep ","
wp option update woocommerce_price_num_decimals 2
wp option update woocommerce_weight_unit kg
wp option update woocommerce_dimension_unit cm

echo "== Verifying WooCommerce pages (Shop/Cart/Checkout/My account) =="
wp option get woocommerce_shop_page_id
wp option get woocommerce_cart_page_id
wp option get woocommerce_checkout_page_id
wp option get woocommerce_myaccount_page_id

cat <<'EOF'

WooCommerce is installed and activated with base settings applied.

Still to do manually in wp-admin (WooCommerce > Settings):
  1. Set up a payment gateway (e.g. Mollie or Stripe are the common choices
     for Belgian shops; the plain "Bank transfer/Cheque" gateways are not
     enough for a live store).
  2. Set up shipping zones and rates for Belgium (and other zones if needed).
  3. Add tax rates (Belgian standard VAT is 21%, with reduced rates for
     specific categories) - Settings > Tax, after enabling taxes in
     Settings > General.
  4. Required legal pages for a Belgian webshop: mentions légales / conditions
     générales de vente, politique de confidentialité (RGPD), politique de
     cookies, and a clear statement of the 14-day right of withdrawal.
  5. Pick and configure a theme compatible with WooCommerce (Storefront is
     the safe default) if the current theme doesn't declare WooCommerce
     support.
  6. Add products (manually, via CSV import under WooCommerce > Products >
     Import, or via the WooCommerce REST API for bulk/automated creation).
EOF
