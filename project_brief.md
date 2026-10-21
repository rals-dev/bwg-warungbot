# My agent: WarungBot

One-liner: A conversational agent that helps small coffee shop owners in Indonesia manage inventory, record sales, calculate profit margins in Rupiah, and generate marketing visuals with a catalog of coffee shop beverages, ingredients, and supplies.

Tool coverage:
- Memory: Remembers the coffee shop's brand style, tone of voice, visual aesthetic, and recurring promotion preferences across sessions.
- Tools: Check inventory levels, flag low-stock items, record sales transactions, deduct inventory stock, and query product and sales records.
- Catalog/UI: Coffee menu items and shop supplies (beans, dairy, syrups, packaging) rendered as rich A2UI product cards, low-stock alert badges, and sales summary tables.
- Image gen: Generates promotional posters and social media marketing banners for featured drinks and promotions using Imagen / Gemini image generation, uploaded to Cloud Storage.
- Sandbox: Computes total revenue, cost of goods sold (COGS), profit margins, and daily sales analytics in Indonesian Rupiah (IDR).

Recommended for every project: memory, storage, tools, image generation, A2UI
Agent-specific / stretch (pick what fits): Code sandbox for financial & profit margin calculations, Firestore for structured products and sales records, Cloud Storage for promotional poster assets.
