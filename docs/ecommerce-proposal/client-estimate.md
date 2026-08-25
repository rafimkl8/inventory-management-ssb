# Website Development Proposal — Sani Shwapno Bazar

**Prepared for:** Sani Shwapno Bazar (Facebook page store)
**Prepared by:** [Your name]
**Date:** August 25, 2026
**Validity:** This estimate is valid for 14 days from the date above.

---

## 1. Project Overview

A customer-facing online storefront for Sani Shwapno Bazar's existing product catalog (currently 66 products / 90 size-variants across Shampoo, Soap, Perfume, Body Spray, Chocolate, Biscuit, Powdered Milk, and Tang — sourced from Saudi Arabia, UAE, Egypt, Germany, and other countries). The store connects to the same inventory system already tracking stock, batches, and expiry dates, so products and stock levels stay accurate automatically.

Customers will be able to browse products by category, add items to a cart, and check out using:
- **Cash on Delivery (default)** — no payment needed until the order arrives.
- **bKash or Nagad in advance** — customer can choose to pay the full order amount ahead of time.
- **Advance delivery charge for larger orders** — to reduce fake/abandoned COD orders, orders above a set value require a small non-refundable advance before dispatch (see confirmation needed below).

Every order is manually reviewed and confirmed by the shop owner (checking their bKash/Nagad app for reported transactions) before being shipped — there's no automated payment processing risk to manage.

---

## 2. Two Build Options

| | **Tier A — Recommended** | **Tier B — Future upgrade** |
|---|---|---|
| Payment | COD + manually-verified bKash/Nagad | + Automatic online bKash/Nagad/card payments |
| Requires trade license? | No | Yes (needed to open a payment gateway merchant account) |
| Price | ৳30,000 – ৳45,000 | ৳60,000 – ৳90,000 |
| Timeline | 3–5 weeks | +2–3 weeks on top of Tier A |

**Recommendation:** Start with Tier A. It fits your current stage as a 1-month-old page with manual payment handling, and it's fully upgradable to Tier B later once you have the business paperwork for a payment gateway account.

---

## 3. Tier A — Cash-on-Delivery Storefront

### Included
- Public storefront: home page, category pages, product detail pages, built from your existing product catalog and images.
- Shopping cart (add/update/remove items).
- Checkout with:
  - Cash on Delivery as the default option.
  - Option to pay in advance via bKash or Nagad (customer enters their Transaction ID; shop owner verifies it manually).
  - **Tiered advance delivery charge** for larger orders *(pending your confirmation — see Section 7)*:
    - Orders above ৳3,000 → ৳130 advance required
    - Orders above ৳5,000 → ৳200 advance required
- Order notification sent directly to your WhatsApp/Messenger with full order details.
- Admin dashboard (extension of your existing inventory system) to view, confirm, and manage orders.
- Mobile-responsive design — most Facebook shop customers order from their phones, so this is treated as a requirement, not an extra.
- Product image support.
- Basic on-page SEO (page titles, descriptions) so products are findable via Google search.
- Performance optimizations: compressed/optimized images, fast-loading pages, no server "sleep" delays (see Section 5 for why this matters).

### Not included in Tier A (available as add-ons — Section 6)
- Automatic online payment processing (Tier B).
- Product photography or ad copywriting.
- Paid advertising/marketing setup.
- Ongoing content updates after launch (new product uploads are already possible via the existing admin panel by the shop owner directly).

### Price: **৳35,000** (flat quote within ৳30,000–45,000 range)
### Timeline: **3–5 weeks**

---

## 4. Tier B — Full Online Payment Storefront (Future Upgrade)

Adds real-time, automatic bKash/Nagad/card payments at checkout via a licensed payment gateway (e.g. SSLCommerz), removing the need for manual transaction verification on advance/full payments.

**Requirement before this tier is possible:** a registered trade license and business bank account, needed to open a merchant account with the payment gateway provider. Most 1-month-old Facebook pages don't have this yet — confirm with the client before quoting this tier as immediately available.

### Price: **৳65,000** flat (range ৳60,000–90,000)
- If upgrading later from an existing Tier A build: **৳35,000–45,000** additional (cheaper than building fresh, since the catalog/cart/UI already exists).
### Timeline: **+2–3 weeks** on top of Tier A

---

## 5. Recurring / Third-Party Costs

These are paid by the client directly to the providers — not included in the build fee above, and not marked up unless the client asks you to manage renewals for them (Section 6).

| Item | Estimated Cost | Notes |
|---|---|---|
| Domain (.com) | ৳900 – ৳1,500 / year | One-time-per-year registration |
| Frontend hosting | ৳0 / year to start | Free tier (Vercel/Netlify/Cloudflare Pages) is sufficient at current order volume |
| Backend/API hosting | ৳0 – ৳7,000 / year | Free tier may be enough initially; a small paid tier avoids any slow/cold-start requests as traffic grows |
| Database | ৳0 / year | Free tier (Supabase/Neon Postgres) sufficient at this scale |
| Image hosting/CDN | ৳0 / year | Free tier (Cloudinary) covers a catalog this size |
| SSL certificate | ৳0 | Included free with all hosting providers above |
| Payment gateway (Tier B only) | No fixed fee — **~2.5% per transaction** | Only applies once Tier B is active; no cost while on Tier A |

**Estimated total recurring cost: ~৳900 – ৳8,500 / year**, almost entirely just the domain if free tiers are used, or including a small backend hosting fee if you want to guarantee zero slow-loading requests as the shop grows.

---

## 6. Optional Add-ons (quoted separately if wanted)

| Add-on | Estimated Price |
|---|---|
| Monthly maintenance & support retainer (updates, fixes, new feature requests) | ৳1,500 – ৳3,000 / month |
| Managing domain/hosting renewals on the client's behalf | Small service fee, agreed separately |
| Product photography cleanup / re-shoots | Quoted separately, not a developer service |
| SEO improvements / Facebook catalog sync | Quoted separately if requested |

---

## 7. Information Needed From the Client Before Starting

1. **Confirm the advance delivery charge rule exactly:** Orders above ৳3,000 → ৳130 advance, orders above ৳5,000 → ৳200 advance, orders below ৳3,000 → no advance (pure COD). *(Please confirm this is correct, or correct it.)*
2. The bKash and/or Nagad number(s) customers should send advance payments to.
3. The WhatsApp/phone number order notifications should be sent to.
4. Product photos (existing Facebook photos can be reused if quality is acceptable) or confirmation to proceed with what's already in the inventory system.
5. Preferred domain name (e.g. sanishwapnobazar.com), if not already purchased.

---

## 8. Payment Terms

- **50% advance** to begin work, **50% on delivery/launch.**
- **2 rounds of revisions** included after the first working version is shared; additional revision rounds billed separately at an hourly/flat rate to be agreed.
- Domain and hosting must be set up under the client's own accounts (recommended for their ownership and control) — support provided to set these up together.

---

## 9. Disclaimer

This is an estimate based on the current catalog size (66 products / 90 variants) and stated requirements. Significant scope changes (e.g. major new features, multi-language support, large catalog growth) may require a revised quote.
