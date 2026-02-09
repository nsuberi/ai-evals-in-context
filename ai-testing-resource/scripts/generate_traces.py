#!/usr/bin/env python3
"""Generate trace data programmatically from knowledge base docs.

Produces ~20 traces per version (v1, v2, v3) = ~60 total.
- v1: Verbose (300+ words), length_violation annotations
- v2: Concise (~80 words) but with hallucinations
- v3: Concise (~80 words), accurate, with sources
"""
import json
import random
from pathlib import Path

random.seed(42)

V1_PROMPT = (
    "You are a helpful customer support agent for Acme Widgets Inc.\n\n"
    "Provide comprehensive, detailed answers of at least 300 words. Be thorough "
    "and cover all aspects of the customer's question. Include relevant background "
    "information and context to ensure the customer fully understands the topic.\n\n"
    "Always maintain a professional and friendly tone."
)

V2_PROMPT = (
    "You are a helpful customer support agent for Acme Widgets Inc.\n\n"
    "Provide concise answers of approximately 80 words. Be direct and helpful.\n\n"
    "You have knowledge of Acme's products, pricing, return policies, and "
    "shipping options. Answer questions confidently based on your knowledge of the company."
)

V3_PROMPT_TEMPLATE = (
    "You are a helpful customer support agent for Acme Widgets Inc.\n\n"
    "Provide concise answers of approximately 80 words. Be direct and helpful.\n\n"
    "Use ONLY the information provided in the context below to answer questions. "
    "If the context doesn't contain relevant information, say \"I don't have "
    'specific information about that, but I can help you contact our support team."\n\n'
    "Context:\n[{doc_title}]\n{doc_content}"
)

# ─────────────────────────────────────────────
# Question / response definitions per topic
# ─────────────────────────────────────────────

QUESTIONS = [
    # Return policy questions (1-5)
    {
        "question": "What is your return policy?",
        "kb_doc": "return_policy",
        "kb_title": "Acme Widgets Return Policy",
        "v1_response": "Thank you for your inquiry about our return policy at Acme Widgets Inc.! We take great pride in ensuring complete customer satisfaction and have developed a comprehensive return policy that addresses various scenarios you might encounter during your shopping experience with us.\n\nOur standard return policy allows customers a generous 30-day return window starting from the delivery date. During this period, you can return any item that meets our return conditions for a full refund to your original payment method. The items must be unused and remain in their original packaging to qualify for a standard return. We understand that sometimes products may not meet your expectations, and we want to make the return process as smooth as possible.\n\nFor defective products, we offer an extended 90-day warranty period. If you receive a defective item within this timeframe, we will either replace it completely free of charge or provide you with a full refund, whichever you prefer. In these cases, we cover all return shipping costs because we believe you shouldn't have to pay for manufacturing defects.\n\nFor change-of-mind returns where the product is not defective, there is a flat rate return shipping fee of $8.95. Please note that certain items are non-returnable, including customized or personalized widgets, clearance items marked as \"Final Sale,\" and items that have been damaged due to customer misuse.\n\nRefunds are typically processed within 5-7 business days after we receive your returned item at our warehouse. While original shipping charges are non-refundable, we do offer a store credit option that adds a 10% bonus value to your credit amount, which many customers find attractive.\n\nIf you have any additional questions about our return policy or need assistance with a specific return, please don't hesitate to reach out to our customer support team. We're here to help ensure your complete satisfaction with every Acme Widgets purchase!",
        "v2_response": "Our return policy offers a 30-day window for returns. Items must be unused and in original packaging for a full refund. Defective items can be returned within 90 days with free shipping. For non-defective returns, there's a $9.99 shipping fee. Customized items and final sale products cannot be returned. Refunds are processed within 3-5 business days after we receive your return.",
        "v2_hallucinations": [
            {
                "text": "The shipping fee is stated as $9.99, but the actual fee is $8.95.",
                "span_text": "$9.99 shipping fee",
            },
            {
                "text": "Refund processing time is stated as 3-5 days, but it's actually 5-7 business days.",
                "span_text": "3-5 business days",
            },
        ],
        "v3_response": 'We offer a 30-day return window from delivery date. Items must be unused and in original packaging for a full refund. Defective products have a 90-day warranty with free return shipping. For change-of-mind returns, there\'s an $8.95 flat shipping fee. Note that customized items and "Final Sale" clearance products cannot be returned. Refunds are processed within 5-7 business days of receiving your return.',
        "v3_accuracies": [
            {
                "text": "Correctly states 30-day return window from the knowledge base.",
                "span_text": "30-day return window from delivery date",
            },
            {
                "text": "Correctly states $8.95 shipping fee matching knowledge base.",
                "span_text": "$8.95 flat shipping fee",
            },
            {
                "text": "Correctly states 5-7 business days refund processing time.",
                "span_text": "5-7 business days",
            },
        ],
    },
    {
        "question": "Can I return a defective widget?",
        "kb_doc": "return_policy",
        "kb_title": "Acme Widgets Return Policy",
        "v1_response": "Absolutely! At Acme Widgets Inc., we stand behind the quality of our products and have a comprehensive defective product return policy designed to make things right if something goes wrong with your purchase. We understand how frustrating it can be to receive a product that doesn't work as expected, and we want to ensure the process is as smooth as possible for you.\n\nOur defective product warranty covers all widgets for a full 90 days from the date of delivery. This is three times longer than our standard 30-day return window, because we recognize that manufacturing defects may not always be immediately apparent. During this 90-day warranty period, you have two options available to you: you can either receive a complete free replacement of the defective widget, or you can opt for a full refund to your original payment method.\n\nOne of the most important aspects of our defective product policy is that we cover all return shipping costs for defective items. You won't have to pay a single penny to send back a defective widget. This is different from our change-of-mind return policy, where customers are responsible for the $8.95 flat rate shipping fee. We believe that if our product fails to meet quality standards, you shouldn't bear any of the cost.\n\nBefore sending your defective widget back, please contact our customer support team to obtain an RMA (Return Merchandise Authorization) number. This helps us track your return efficiently and ensures faster processing of your replacement or refund. Our support team can also help troubleshoot the issue to confirm it's a defect rather than a usage issue.\n\nOnce we receive the defective item at our warehouse, if you chose a refund, it will typically be processed within 5-7 business days. If you opted for a replacement, we'll ship the new widget to you at no additional charge, usually within 2-3 business days of receiving your return. We truly value your trust in Acme Widgets!",
        "v2_response": "Yes, defective widgets can be returned within 60 days for a free replacement or full refund. We cover return shipping costs for all defective items. Just contact us for a return label and we'll process everything within 2-3 business days. Make sure to include the original receipt with your return for faster processing.",
        "v2_hallucinations": [
            {
                "text": "Warranty period stated as 60 days, but actual warranty is 90 days.",
                "span_text": "60 days",
            },
            {
                "text": "Processing time stated as 2-3 business days, actual refund processing is 5-7 business days.",
                "span_text": "2-3 business days",
            },
            {
                "text": "Receipt requirement is fabricated; actual policy requires an RMA number from support.",
                "span_text": "original receipt",
            },
        ],
        "v3_response": "Yes! Defective widgets are covered under our 90-day warranty. You can choose between a free replacement or a full refund. We cover all return shipping costs for defective items. Before sending it back, contact our support team to get an RMA number. Refunds are processed within 5-7 business days of receiving the return.",
        "v3_accuracies": [
            {
                "text": "Correctly states 90-day warranty period.",
                "span_text": "90-day warranty",
            },
            {
                "text": "Correctly states free replacement or full refund options.",
                "span_text": "free replacement or a full refund",
            },
            {
                "text": "Correctly states RMA number requirement.",
                "span_text": "RMA number",
            },
        ],
    },
    {
        "question": "What items cannot be returned?",
        "kb_doc": "return_policy",
        "kb_title": "Acme Widgets Return Policy",
        "v1_response": "Thank you for asking about our non-returnable items policy at Acme Widgets Inc. We want to be completely transparent about which items fall outside our standard return policy so you can make informed purchasing decisions. While we strive to make our return process as accommodating as possible, there are certain categories of items that we cannot accept for returns.\n\nThe first category of non-returnable items is customized or personalized widgets. When you order a widget that has been specifically configured, engraved, or modified to your personal specifications, we are unable to accept it for return. This is because customized items are made specifically for each individual customer and cannot be resold to other customers. The unique nature of these products means they have no resale value once they've been personalized.\n\nThe second category is clearance items that are marked as \"Final Sale.\" These products are offered at significantly reduced prices, and part of the agreement when purchasing a Final Sale item is that it cannot be returned or exchanged. We clearly mark these items on our website and in our stores so customers are aware before making their purchase. The deep discounts on Final Sale items are possible specifically because we do not accept returns on them.\n\nThe third category is items that have been damaged due to customer misuse. While we absolutely stand behind our products when there are manufacturing defects, we cannot accept returns for items that have been damaged through improper use, neglect, or accidents. This includes physical damage from drops, water damage on non-water-resistant models, or damage from using the widget in ways not described in the user manual.\n\nFor all other items in good condition, our standard 30-day return window applies. Items must be unused and in their original packaging to qualify. If you're unsure whether your specific situation qualifies for a return, please don't hesitate to contact our customer support team for personalized assistance. We're always happy to help!",
        "v2_response": 'There are three categories of non-returnable items: customized or personalized widgets since they\'re made to order, clearance items marked "Final Sale" due to deep discounting, and items damaged through customer misuse. Additionally, any widget opened more than 14 days ago may be subject to a restocking fee of 15%.',
        "v2_hallucinations": [
            {
                "text": "The 14-day opening period and 15% restocking fee are fabricated; no such policy exists.",
                "span_text": "opened more than 14 days ago may be subject to a restocking fee of 15%",
            },
        ],
        "v3_response": 'Three categories of items cannot be returned: customized or personalized widgets, clearance items marked "Final Sale," and items damaged due to customer misuse. Everything else follows our standard 30-day return window. Items must be unused and in original packaging to qualify. If you\'re unsure about your situation, contact our support team.',
        "v3_accuracies": [
            {
                "text": "Correctly lists all three non-returnable categories.",
                "span_text": 'customized or personalized widgets, clearance items marked "Final Sale," and items damaged due to customer misuse',
            },
            {
                "text": "Correctly states 30-day return window.",
                "span_text": "30-day return window",
            },
        ],
    },
    {
        "question": "How long does it take to get a refund?",
        "kb_doc": "return_policy",
        "kb_title": "Acme Widgets Return Policy",
        "v1_response": "Thank you for your question about our refund processing timeline at Acme Widgets Inc. We understand that when you're waiting for a refund, every day feels longer, and we want to give you a thorough understanding of what to expect throughout the entire process so you can plan accordingly.\n\nOnce we receive your returned item at our warehouse, refunds are typically processed within 5-7 business days. This processing period begins from the date we physically receive and inspect your returned product, not from the date you ship it. During this time, our quality assurance team examines the returned item to verify it meets our return conditions, and our finance team initiates the refund to your original payment method.\n\nIt's important to note that after we process the refund on our end, it may take an additional 3-5 business days for the refund to appear in your account, depending on your bank or credit card company. Some financial institutions process refunds faster than others, so the exact timeline can vary. We always recommend checking with your bank if you haven't seen the refund after the expected processing period.\n\nRegarding your refund amount, please be aware that original shipping charges are non-refundable. The refund will cover the full purchase price of the item, but not the initial shipping cost you paid when ordering. However, we do offer an attractive alternative: you can choose to receive store credit instead of a direct refund. When you opt for store credit, we add a 10% bonus value to your credit amount, which many of our customers find to be a great deal.\n\nFor example, if your refund amount would be $100, choosing store credit would give you $110 in credit to use on future purchases. This bonus is our way of thanking you for your continued loyalty and trust in Acme Widgets. The store credit never expires and can be used on any products in our catalog.\n\nIf you have any concerns about your refund status or would like to check on a pending return, please contact our customer support team with your order number and we'll be happy to provide an update.",
        "v2_response": "Refunds are processed within 3-5 business days after we receive your return. The amount goes back to your original payment method. Note that original shipping charges are non-refundable. You can also choose store credit which gives you a 5% bonus on the refund amount.",
        "v2_hallucinations": [
            {
                "text": "Refund timeline stated as 3-5 days, but actual is 5-7 business days.",
                "span_text": "3-5 business days",
            },
            {
                "text": "Store credit bonus stated as 5%, but actual bonus is 10%.",
                "span_text": "5% bonus",
            },
        ],
        "v3_response": "Refunds are processed within 5-7 business days after we receive your return at our warehouse. The refund goes to your original payment method. Note that original shipping charges are non-refundable. Alternatively, you can opt for store credit, which adds a 10% bonus value to your refund amount.",
        "v3_accuracies": [
            {
                "text": "Correctly states 5-7 business days processing time.",
                "span_text": "5-7 business days",
            },
            {
                "text": "Correctly states 10% store credit bonus.",
                "span_text": "10% bonus value",
            },
        ],
    },
    {
        "question": "Do you offer store credit for returns?",
        "kb_doc": "return_policy",
        "kb_title": "Acme Widgets Return Policy",
        "v1_response": "Yes, we absolutely do offer store credit as an alternative to traditional refunds at Acme Widgets Inc., and many of our customers find it to be an excellent option! We've designed our store credit program to reward customers who choose to keep their money within the Acme Widgets ecosystem, and it comes with a very attractive bonus that makes it worth considering.\n\nWhen you return an item and choose store credit instead of a refund to your original payment method, we add a 10% bonus value to your credit amount. This means that if your return qualifies for a $100 refund, you would receive $110 in store credit. For a $50 return, you'd get $55 in store credit. This bonus applies regardless of the item being returned or the reason for the return, as long as the return itself qualifies under our standard return policy.\n\nThe store credit is applied to your Acme Widgets account immediately upon processing, which typically happens within 5-7 business days of receiving your returned item. Unlike a traditional refund, where you might have to wait additional time for your bank to process the return, store credit is available for use as soon as it's applied to your account.\n\nYour store credit never expires and can be used on any products in our catalog, including new releases, seasonal collections, and even some promotional items. You can use partial credit on a purchase and save the rest for later, giving you complete flexibility in how you spend it. Many customers appreciate that the 10% bonus effectively gives them a discount on their next purchase.\n\nPlease keep in mind that while store credit offers the bonus value, it cannot be converted back to cash once it's been issued. If you think you might want a cash refund in the future, it's best to choose the standard refund option at the time of return. Our customer support team can help you weigh the options if you're unsure which choice is best for your situation.",
        "v2_response": "Yes! We offer store credit as an alternative to cash refunds. When you choose store credit, you receive a 15% bonus on top of your refund amount. So a $100 return would give you $115 in store credit. The credit is applied immediately and never expires. It's a popular choice among our regular customers.",
        "v2_hallucinations": [
            {
                "text": "Store credit bonus stated as 15%, but actual bonus is 10%.",
                "span_text": "15% bonus",
            },
            {
                "text": "The $115 example is wrong; it should be $110 (10% of $100 = $10 bonus).",
                "span_text": "$115 in store credit",
            },
        ],
        "v3_response": "Yes! We offer a store credit option as an alternative to refunding your original payment method. When you choose store credit, we add a 10% bonus value to your refund amount. Refunds are processed within 5-7 business days. Original shipping charges remain non-refundable regardless of which option you choose.",
        "v3_accuracies": [
            {
                "text": "Correctly states 10% bonus value for store credit.",
                "span_text": "10% bonus value",
            },
            {
                "text": "Correctly states 5-7 business days processing.",
                "span_text": "5-7 business days",
            },
        ],
    },
    # Pricing questions (6-10)
    {
        "question": "How much does the Starter plan cost?",
        "kb_doc": "pricing_tiers",
        "kb_title": "Acme Widgets Pricing Tiers",
        "v1_response": "Thank you for your interest in our Starter plan at Acme Widgets Inc.! I'm happy to provide you with a comprehensive overview of this entry-level tier, which is designed for individuals and small businesses who are just beginning their widget journey and want to explore our platform without a large commitment.\n\nThe Starter plan is priced at just $49 per month, making it our most affordable option and a great way to get started with Acme Widgets. Despite being our entry-level tier, it still packs plenty of value to help you get up and running quickly and efficiently.\n\nWith the Starter plan, you receive up to 100 widgets per month, which is more than enough for most individual users and small teams. You also get access to email support with a 48-hour response time. While this isn't as fast as our higher-tier support options, our support team is knowledgeable and thorough in their responses, ensuring you get the help you need.\n\nThe plan includes a basic analytics dashboard that gives you visibility into your widget usage patterns, performance metrics, and key statistics. While it doesn't include the advanced analytics and export features available in our Professional and Enterprise plans, it provides everything you need to monitor your widget operations effectively.\n\nThe Starter plan comes with 1 user seat, making it ideal for solo practitioners or individual contributors. If you need additional seats, you might want to consider upgrading to our Professional plan, which offers 5 user seats.\n\nLike all our plans, the Starter plan includes a 14-day free trial so you can test everything before committing. If you opt for annual billing instead of monthly, you'll save 20% on the regular price. We believe this makes our Starter plan one of the best values in the widget industry for beginners!",
        "v2_response": "The Starter plan costs $59 per month and includes up to 100 widgets, email support with 24-hour response time, basic analytics, and 2 user seats. It's perfect for individuals getting started. All plans include a 14-day trial and you can save 10% with annual billing.",
        "v2_hallucinations": [
            {
                "text": "Price stated as $59/month, but actual price is $49/month.",
                "span_text": "$59 per month",
            },
            {
                "text": "Response time stated as 24-hour, but Starter plan has 48-hour response.",
                "span_text": "24-hour response time",
            },
            {
                "text": "User seats stated as 2, but Starter plan has 1 user seat.",
                "span_text": "2 user seats",
            },
            {
                "text": "Annual discount stated as 10%, but actual is 20%.",
                "span_text": "10% with annual billing",
            },
        ],
        "v3_response": "The Starter plan costs $49 per month and includes up to 100 widgets per month, email support with 48-hour response time, a basic analytics dashboard, and 1 user seat. Like all plans, it includes a 14-day free trial. You can save 20% by choosing annual billing.",
        "v3_accuracies": [
            {"text": "Correctly states $49/month price.", "span_text": "$49 per month"},
            {
                "text": "Correctly states 48-hour response time.",
                "span_text": "48-hour response time",
            },
            {"text": "Correctly states 20% annual savings.", "span_text": "20%"},
        ],
    },
    {
        "question": "How much does the Enterprise plan cost?",
        "kb_doc": "pricing_tiers",
        "kb_title": "Acme Widgets Pricing Tiers",
        "v1_response": "Thank you for your interest in our Enterprise plan at Acme Widgets Inc.! I'm excited to share the details of our most comprehensive offering, which is designed specifically for organizations that need maximum flexibility and support for their widget operations.\n\nThe Enterprise plan is priced at $299 per month, making it our premium tier offering. This plan is perfect for larger organizations or businesses that require unlimited widgets and dedicated support. Let me break down everything that's included in this exceptional package.\n\nWith the Enterprise plan, you get unlimited widgets per month, which means you can scale your operations without worrying about hitting any caps or limits. This is particularly valuable for growing businesses or those with fluctuating demand. Additionally, you receive phone and email support with an industry-leading 4-hour response time, ensuring that any issues you encounter are addressed promptly by our expert team.\n\nThe plan includes custom analytics and reporting features, allowing you to gain deep insights into your widget usage and performance metrics. You'll have unlimited user seats, so your entire team can access the platform without additional per-user fees. Each Enterprise customer also receives a dedicated account manager who serves as your primary point of contact and ensures you get the most value from our services.\n\nWe also offer custom integrations with Enterprise plans, meaning we can work with your existing systems and workflows to create a seamless experience. The plan comes with an SLA guarantee of 99.9% uptime, giving you peace of mind that our service will be reliable when you need it most.\n\nIf you're interested in annual billing, you can save 20% on the monthly rate. We also offer a 14-day free trial so you can experience all the Enterprise features before committing. Would you like me to help you get started with a trial, or do you have any other questions about the Enterprise plan?",
        "v2_response": "Our Enterprise plan costs $349 per month and includes unlimited widgets, priority support with 2-hour response time, custom integrations, and a dedicated account manager. You get unlimited user seats and advanced analytics. Annual plans receive a 15% discount. The Enterprise plan also includes our premium SLA with 99.95% uptime guarantee.",
        "v2_hallucinations": [
            {
                "text": "Price stated as $349/month, but actual price is $299/month.",
                "span_text": "$349 per month",
            },
            {
                "text": "Response time stated as 2-hour, but actual is 4-hour response time.",
                "span_text": "2-hour response time",
            },
            {
                "text": "Annual discount stated as 15%, but actual discount is 20%.",
                "span_text": "15% discount",
            },
            {
                "text": "Uptime stated as 99.95%, but actual SLA is 99.9%.",
                "span_text": "99.95% uptime guarantee",
            },
        ],
        "v3_response": "The Enterprise plan costs $299 per month and includes unlimited widgets, phone and email support with 4-hour response time, custom analytics, unlimited user seats, a dedicated account manager, custom integrations, and a 99.9% uptime SLA guarantee. You can save 20% with annual billing. All plans include a 14-day free trial.",
        "v3_accuracies": [
            {
                "text": "Correctly states $299/month price from knowledge base.",
                "span_text": "$299 per month",
            },
            {
                "text": "Correctly states 4-hour response time.",
                "span_text": "4-hour response time",
            },
            {
                "text": "Correctly states 99.9% uptime SLA.",
                "span_text": "99.9% uptime SLA guarantee",
            },
            {
                "text": "Correctly states 20% annual discount.",
                "span_text": "20% with annual billing",
            },
        ],
    },
    {
        "question": "What does the Professional plan include?",
        "kb_doc": "pricing_tiers",
        "kb_title": "Acme Widgets Pricing Tiers",
        "v1_response": "Thank you for asking about our Professional plan at Acme Widgets Inc.! The Professional plan is our mid-tier offering and represents the best balance of features and value for growing businesses and teams that need more than what our Starter plan provides but don't yet require the full Enterprise experience.\n\nThe Professional plan is priced at $149 per month and is designed to support teams of up to 5 people with robust analytics and API capabilities. Let me walk you through everything that's included in this popular plan.\n\nFirst, the Professional plan provides up to 500 widgets per month, a significant upgrade from the Starter plan's 100-widget limit. This higher allocation is perfect for teams with moderate to high widget usage who need room to grow without immediately jumping to the unlimited Enterprise tier.\n\nYou'll receive priority email support with a 24-hour response time, which is twice as fast as the Starter plan's 48-hour response time. Our priority support queue ensures that Professional plan customers get faster resolution of their issues and questions.\n\nThe plan includes advanced analytics with export functionality. Unlike the basic analytics dashboard in the Starter plan, the Professional tier gives you detailed insights, custom date ranges, and the ability to export your data in multiple formats for further analysis. This is invaluable for teams that need to share reports with stakeholders or integrate analytics data into other tools.\n\nWith 5 user seats included, your entire team can collaborate on the platform without additional per-seat charges. This makes the Professional plan significantly more cost-effective than purchasing multiple Starter plans for team use.\n\nThe Professional plan also includes full API access, allowing you to integrate Acme Widgets into your existing workflows, automate processes, and build custom solutions on top of our platform.\n\nAs with all our plans, you get a 14-day free trial and can save 20% with annual billing.",
        "v2_response": "The Professional plan is $179 per month and includes up to 500 widgets, email support with 12-hour response time, advanced analytics, 3 user seats, and API access. It's our most popular plan for growing teams. Annual billing saves you 20%.",
        "v2_hallucinations": [
            {
                "text": "Price stated as $179/month, but actual is $149/month.",
                "span_text": "$179 per month",
            },
            {
                "text": "Response time stated as 12-hour, but actual is 24-hour for Professional.",
                "span_text": "12-hour response time",
            },
            {
                "text": "User seats stated as 3, but actual is 5 user seats.",
                "span_text": "3 user seats",
            },
        ],
        "v3_response": "The Professional plan costs $149/month and includes up to 500 widgets per month, priority email support with 24-hour response time, advanced analytics with exports, 5 user seats, and API access. Like all our plans, it includes a 14-day free trial, and you save 20% with annual billing.",
        "v3_accuracies": [
            {"text": "Correctly states $149/month price.", "span_text": "$149/month"},
            {
                "text": "Correctly states 24-hour response time.",
                "span_text": "24-hour response time",
            },
            {"text": "Correctly states 5 user seats.", "span_text": "5 user seats"},
        ],
    },
    {
        "question": "Can you compare all your pricing plans?",
        "kb_doc": "pricing_tiers",
        "kb_title": "Acme Widgets Pricing Tiers",
        "v1_response": "I'd be happy to provide a comprehensive comparison of all our pricing plans at Acme Widgets Inc.! We offer three distinct tiers designed to meet the needs of individuals, growing teams, and large organizations. Let me walk you through each plan in detail so you can make the best choice for your situation.\n\nOur Starter plan at $49 per month is the perfect entry point. It includes up to 100 widgets per month, email support with a 48-hour response time, a basic analytics dashboard, and 1 user seat. This plan is ideal for individuals or solo practitioners who are just getting started with widgets and want to explore the platform at a comfortable pace.\n\nThe Professional plan at $149 per month is our most popular option for growing businesses. It offers up to 500 widgets per month (5x the Starter plan), priority email support with a faster 24-hour response time, advanced analytics with data export capabilities, 5 user seats for team collaboration, and full API access for custom integrations and automation. This represents a significant step up in both capacity and capabilities.\n\nOur Enterprise plan at $299 per month is the ultimate package for organizations that demand the best. It includes unlimited widgets with no monthly caps, phone and email support with an industry-leading 4-hour response time, custom analytics and reporting tailored to your needs, unlimited user seats for your entire organization, a dedicated account manager, custom integrations, and an SLA guarantee of 99.9% uptime.\n\nAll three plans include a 14-day free trial so you can test the features before committing. Additionally, all plans offer a 20% discount when you choose annual billing instead of monthly. This means the Starter plan drops to about $39/month, the Professional to about $119/month, and the Enterprise to about $239/month on annual billing. Choose the plan that best fits your current needs, knowing you can always upgrade as your requirements grow!",
        "v2_response": "We have three plans: Starter at $49/month with 100 widgets and basic features, Professional at $149/month with 500 widgets and API access, and Enterprise at $349/month with unlimited everything. All include a 14-day trial. Professional has 5 seats, Enterprise has unlimited. Annual billing saves 20%.",
        "v2_hallucinations": [
            {
                "text": "Enterprise price stated as $349/month, but actual is $299/month.",
                "span_text": "$349/month with unlimited",
            },
        ],
        "v3_response": "We offer three tiers: Starter ($49/month) with 100 widgets, email support (48hr), basic analytics, 1 seat. Professional ($149/month) with 500 widgets, priority email (24hr), advanced analytics, 5 seats, API access. Enterprise ($299/month) with unlimited widgets, phone+email (4hr), custom analytics, unlimited seats, dedicated account manager, 99.9% SLA. All include a 14-day trial; annual billing saves 20%.",
        "v3_accuracies": [
            {
                "text": "Correctly states all three plan prices.",
                "span_text": "Starter ($49/month)",
            },
            {
                "text": "Correctly states Enterprise at $299/month.",
                "span_text": "Enterprise ($299/month)",
            },
            {
                "text": "Correctly states 14-day trial and 20% annual savings.",
                "span_text": "14-day trial; annual billing saves 20%",
            },
        ],
    },
    {
        "question": "Do you offer a free trial?",
        "kb_doc": "pricing_tiers",
        "kb_title": "Acme Widgets Pricing Tiers",
        "v1_response": "Yes, absolutely! At Acme Widgets Inc., we firmly believe that you should be able to experience our platform fully before making a financial commitment, which is why we offer a generous free trial program for all of our pricing plans. Let me provide you with all the details about our trial offering.\n\nAll three of our plans — Starter ($49/month), Professional ($149/month), and Enterprise ($299/month) — include a 14-day free trial period. During these 14 days, you have full access to all the features included in whichever plan you choose to try. This means you can truly test the platform under real-world conditions before deciding whether to continue with a paid subscription.\n\nDuring the trial period, there are no restrictions on the features available to you. If you're trying the Enterprise plan, for example, you'll have access to unlimited widgets, phone and email support, custom analytics, unlimited user seats, and even a temporary dedicated account manager to help you get the most out of your trial experience.\n\nAt the end of the 14-day trial, you can choose to continue with the plan and begin paying the monthly rate, switch to a different plan that better fits your needs, or cancel without any charges. We don't require a credit card to start your trial, so there's absolutely no risk involved.\n\nAdditionally, I want to mention that if you decide to continue with any plan after your trial, you can save 20% by choosing annual billing instead of monthly. This makes our already competitive pricing even more attractive. Many customers find that after experiencing the full capabilities during their trial, the annual commitment is a no-brainer.\n\nWe're confident that once you try Acme Widgets, you'll see the value our platform brings to your operations. Would you like to start a trial today?",
        "v2_response": "Yes! All our plans include a 7-day free trial with full access to all features. No credit card required to start. After the trial, you can choose to subscribe monthly or annually. Annual billing saves you 20% off the regular monthly price.",
        "v2_hallucinations": [
            {
                "text": "Trial period stated as 7 days, but actual trial is 14 days.",
                "span_text": "7-day free trial",
            },
        ],
        "v3_response": "Yes! All plans include a 14-day free trial with full access to the features of your chosen tier. After the trial, you can continue with monthly billing or save 20% with annual billing. Our three plans are Starter ($49/month), Professional ($149/month), and Enterprise ($299/month).",
        "v3_accuracies": [
            {
                "text": "Correctly states 14-day free trial.",
                "span_text": "14-day free trial",
            },
            {
                "text": "Correctly states 20% annual savings.",
                "span_text": "20% with annual billing",
            },
        ],
    },
    # Product specs questions (11-15)
    {
        "question": "What are the specs of Widget Pro X2?",
        "kb_doc": "product_specs",
        "kb_title": "Acme Widget Product Specifications",
        "v1_response": "Thank you for your interest in the Widget Pro X2, one of our most popular products at Acme Widgets Inc.! The X2 represents the sweet spot in our product lineup, offering premium features at a mid-range price point. Let me provide you with a complete rundown of everything this impressive widget has to offer.\n\nStarting with the physical specifications, the Widget Pro X2 measures 5 inches by 5 inches by 2.5 inches, making it compact enough for portable use while still providing a substantial form factor for comfortable handling. It weighs 12 ounces, which strikes a good balance between portability and build quality. The X2 is constructed from carbon fiber composite material, which provides exceptional durability while keeping the weight manageable.\n\nThe power system is impressive — the X2 features a 3500mAh lithium-ion battery that provides up to 12 hours of continuous use on a single charge. This is a significant upgrade from the X1's 8-hour battery life, making the X2 ideal for all-day use without needing to worry about charging.\n\nIn terms of connectivity, the Widget Pro X2 comes equipped with Bluetooth 5.0, WiFi 6, and NFC capabilities. The addition of NFC over the X1 model opens up possibilities for quick pairing, contactless interactions, and integration with other NFC-enabled devices.\n\nOne of the standout features of the X2 is its IP67 water resistance rating. This means it can withstand being submerged in up to 1 meter of water for 30 minutes, making it suitable for use in wet conditions, outdoor environments, and situations where exposure to water or dust is a concern.\n\nThe Widget Pro X2 is priced at $129.99, positioning it between our entry-level X1 ($79.99) and our industrial-grade Enterprise E1 ($249.99). For most users, the X2 offers the best combination of features, performance, and value. It's truly the workhorse of our product lineup!",
        "v2_response": "The Widget Pro X2 features a 4.5-inch display, weighs 10 oz, and is made with premium aluminum alloy. It has a 3000mAh battery providing 10 hours of use, Bluetooth 5.0 and WiFi connectivity, and IP65 water resistance. Priced at $149.99, it's our mid-range option perfect for everyday use.",
        "v2_hallucinations": [
            {
                "text": 'Dimensions wrong: stated 4.5-inch but X2 is 5" x 5" x 2.5".',
                "span_text": "4.5-inch display",
            },
            {
                "text": "Weight wrong: stated 10 oz but actual weight is 12 oz.",
                "span_text": "10 oz",
            },
            {
                "text": "Material wrong: stated aluminum alloy but actual is carbon fiber composite.",
                "span_text": "aluminum alloy",
            },
            {
                "text": "Battery wrong: stated 3000mAh/10 hours but actual is 3500mAh/12 hours.",
                "span_text": "3000mAh battery providing 10 hours",
            },
            {
                "text": "Water resistance wrong: stated IP65 but actual is IP67.",
                "span_text": "IP65 water resistance",
            },
            {
                "text": "Price wrong: stated $149.99 but actual price is $129.99.",
                "span_text": "$149.99",
            },
        ],
        "v3_response": 'The Widget Pro X2 measures 5" x 5" x 2.5" and weighs 12 oz. It\'s made with carbon fiber composite material. The 3500mAh lithium-ion battery provides 12 hours of life. Connectivity includes Bluetooth 5.0, WiFi 6, and NFC. It has IP67 water resistance for durability. Priced at $129.99.',
        "v3_accuracies": [
            {"text": "Correctly states dimensions.", "span_text": '5" x 5" x 2.5"'},
            {"text": "Correctly states weight.", "span_text": "12 oz"},
            {
                "text": "Correctly states carbon fiber composite material.",
                "span_text": "carbon fiber composite",
            },
            {
                "text": "Correctly states battery specs.",
                "span_text": "3500mAh lithium-ion battery provides 12 hours",
            },
            {"text": "Correctly states IP67 rating.", "span_text": "IP67"},
            {"text": "Correctly states $129.99 price.", "span_text": "$129.99"},
        ],
    },
    {
        "question": "Tell me about the Widget Pro X1.",
        "kb_doc": "product_specs",
        "kb_title": "Acme Widget Product Specifications",
        "v1_response": "I'd be delighted to tell you all about the Widget Pro X1, our entry-level widget at Acme Widgets Inc.! The X1 is where many of our customers begin their Acme Widgets journey, and despite being our most affordable option, it's packed with quality features that make it a fantastic choice for everyday use.\n\nThe Widget Pro X1 has dimensions of 4 inches by 4 inches by 2 inches, making it the most compact widget in our product lineup. At just 8 ounces, it's incredibly lightweight and easy to carry with you throughout the day. The X1 is constructed from aircraft-grade aluminum, which provides excellent durability and a premium feel while keeping the weight minimal.\n\nPowering the X1 is a 2000mAh lithium-ion battery that delivers up to 8 hours of continuous use. While this is less than the X2's 12-hour battery, 8 hours is more than sufficient for a full workday of widget operations. The battery charges quickly and maintains its capacity well over hundreds of charge cycles.\n\nFor connectivity, the X1 comes equipped with Bluetooth 5.0 and WiFi 6, giving you reliable wireless connections for data transfer and communication. While it doesn't include the NFC capability found in the X2, the Bluetooth and WiFi combination covers the vast majority of connectivity needs.\n\nIt's worth noting that unlike the X2, the X1 does not have a water resistance rating. This means you'll want to keep it protected from moisture and use it primarily in dry environments. For outdoor or wet-condition use, we'd recommend upgrading to the X2 with its IP67 rating.\n\nThe Widget Pro X1 is priced at just $79.99, making it our most accessible widget. It's an excellent choice for beginners, casual users, or anyone who values portability and simplicity. Many customers start with the X1 and later upgrade to the X2 as their needs grow!",
        "v2_response": 'The Widget Pro X1 is our entry-level model at $89.99. It measures 4" x 4" x 2", weighs 8 oz, and features aircraft-grade aluminum construction. It has a 2500mAh battery for 10 hours of use, Bluetooth 5.0 and WiFi 6 connectivity. Great for beginners and casual users.',
        "v2_hallucinations": [
            {
                "text": "Price stated as $89.99, but actual is $79.99.",
                "span_text": "$89.99",
            },
            {
                "text": "Battery stated as 2500mAh/10 hours, but actual is 2000mAh/8 hours.",
                "span_text": "2500mAh battery for 10 hours",
            },
        ],
        "v3_response": 'The Widget Pro X1 is our entry-level model at $79.99. It measures 4" x 4" x 2" and weighs 8 oz. Made with aircraft-grade aluminum, it features a 2000mAh lithium-ion battery with 8-hour life. Connectivity includes Bluetooth 5.0 and WiFi 6. It\'s compact and lightweight, perfect for everyday use.',
        "v3_accuracies": [
            {"text": "Correctly states $79.99 price.", "span_text": "$79.99"},
            {
                "text": "Correctly states 2000mAh battery with 8-hour life.",
                "span_text": "2000mAh lithium-ion battery with 8-hour life",
            },
            {
                "text": "Correctly states aircraft-grade aluminum.",
                "span_text": "aircraft-grade aluminum",
            },
        ],
    },
    {
        "question": "What is the Widget Enterprise E1?",
        "kb_doc": "product_specs",
        "kb_title": "Acme Widget Product Specifications",
        "v1_response": "Excellent question! The Widget Enterprise E1 is our industrial-grade, professional widget at Acme Widgets Inc., designed specifically for demanding business environments and commercial applications. Let me give you a thorough overview of this impressive piece of equipment.\n\nThe Enterprise E1 is our largest and most robust widget, measuring 6 inches by 6 inches by 3 inches. At 18 ounces, it's heavier than our consumer models, but that weight comes from its industrial steel housing that provides exceptional durability and protection. This widget is built to last in challenging environments where other products might fail.\n\nUnlike our Pro X1 and X2 models which run on batteries, the Enterprise E1 is a wired device that plugs directly into a power source. This design decision was intentional — in industrial settings, constant power is typically available and more reliable than battery operation. It eliminates the need for charging and ensures the E1 is always ready for operation.\n\nThe E1 offers comprehensive connectivity options including Ethernet, WiFi 6, and Bluetooth 5.0. The inclusion of Ethernet connectivity sets it apart from our consumer models and is essential for enterprise environments where wired network connections provide the most reliable and secure data transfer.\n\nOne of the most impressive specifications of the E1 is its operating temperature range of -20 degrees Celsius to 60 degrees Celsius. This extreme temperature tolerance makes it suitable for use in warehouses, outdoor installations, manufacturing facilities, cold storage environments, and other challenging locations where standard electronics might not function properly.\n\nThe Widget Enterprise E1 is priced at $249.99, with bulk discounts available for organizations purchasing multiple units. This makes it cost-effective for large-scale deployments across offices, factories, or distributed operations. Contact our sales team to discuss volume pricing for your specific needs.\n\nIf your business requires reliable, always-on widget operations in challenging environments, the Enterprise E1 is the clear choice!",
        "v2_response": 'The Widget Enterprise E1 is our industrial-grade model at $299.99. It measures 6" x 6" x 3" and weighs 16 oz with a stainless steel housing. It\'s a wired device with Ethernet, WiFi 6, and Bluetooth connectivity. It operates from -10C to 50C. Bulk pricing is available for organizations.',
        "v2_hallucinations": [
            {
                "text": "Price stated as $299.99, but actual is $249.99.",
                "span_text": "$299.99",
            },
            {
                "text": "Weight stated as 16 oz, but actual is 18 oz.",
                "span_text": "16 oz",
            },
            {
                "text": "Material stated as stainless steel, but actual is industrial steel housing.",
                "span_text": "stainless steel housing",
            },
            {
                "text": "Temperature range stated as -10C to 50C, but actual is -20C to 60C.",
                "span_text": "-10C to 50C",
            },
        ],
        "v3_response": 'The Widget Enterprise E1 is our industrial-grade model at $249.99 (bulk discounts available). It measures 6" x 6" x 3", weighs 18 oz, and has an industrial steel housing. It\'s wired (no battery), with Ethernet, WiFi 6, and Bluetooth 5.0. Operating temperature range is -20C to 60C, making it ideal for demanding environments.',
        "v3_accuracies": [
            {
                "text": "Correctly states $249.99 with bulk discounts.",
                "span_text": "$249.99 (bulk discounts available)",
            },
            {"text": "Correctly states 18 oz weight.", "span_text": "18 oz"},
            {
                "text": "Correctly states -20C to 60C operating range.",
                "span_text": "-20C to 60C",
            },
        ],
    },
    {
        "question": "How do the Widget Pro X1 and X2 compare?",
        "kb_doc": "product_specs",
        "kb_title": "Acme Widget Product Specifications",
        "v1_response": 'Great question! Comparing the Widget Pro X1 and X2 is something many of our customers ask about, as these two models represent the core of our consumer product lineup at Acme Widgets Inc. Let me provide a detailed side-by-side comparison so you can make the best choice for your needs.\n\nStarting with physical dimensions, the X1 is our more compact option at 4" x 4" x 2" and weighing just 8 ounces, while the X2 is slightly larger at 5" x 5" x 2.5" and weighing 12 ounces. If portability is your top priority, the X1 has the edge, but the X2\'s larger size provides a more comfortable form factor for extended use.\n\nThe materials differ significantly between the two models. The X1 uses aircraft-grade aluminum, which is lightweight and durable. The X2 steps up to carbon fiber composite, which offers an even better strength-to-weight ratio and a more premium feel. Both materials are excellent, but the carbon fiber composite in the X2 is the more advanced choice.\n\nBattery life is a major differentiator. The X1\'s 2000mAh lithium-ion battery provides 8 hours of use, which is solid for a typical workday. The X2 nearly doubles this with a 3500mAh lithium-ion battery that delivers 12 hours of continuous use. If you need all-day battery life without recharging, the X2 is the clear winner.\n\nConnectivity is another area where the X2 pulls ahead. Both models include Bluetooth 5.0 and WiFi 6, but the X2 adds NFC capability, enabling quick pairing and contactless features that the X1 lacks.\n\nThe X2 also includes IP67 water resistance, meaning it can handle submersion in water up to 1 meter for 30 minutes. The X1 has no water resistance rating, making it less suitable for outdoor or wet environments.\n\nPricing reflects these differences: the X1 is $79.99 while the X2 is $129.99. The $50 premium for the X2 gets you better battery, better materials, NFC, and water resistance. For most users, the X2 represents better long-term value, but the X1 remains excellent for budget-conscious buyers!',
        "v2_response": 'The X1 ($79.99) is our entry model: 4" x 4" x 2", 8 oz, aluminum build, 2000mAh battery (8 hours), Bluetooth and WiFi. The X2 ($139.99) upgrades to: 5" x 5" x 2.5", 12 oz, carbon fiber, 3500mAh battery (12 hours), adds NFC and IP67 water resistance. The X2 is worth the extra for the battery and water resistance alone.',
        "v2_hallucinations": [
            {
                "text": "X2 price stated as $139.99, but actual is $129.99.",
                "span_text": "$139.99",
            },
        ],
        "v3_response": 'The X1 ($79.99) offers 4"x4"x2", 8 oz, aircraft-grade aluminum, 2000mAh/8hr battery, Bluetooth 5.0 + WiFi 6. The X2 ($129.99) upgrades to 5"x5"x2.5", 12 oz, carbon fiber composite, 3500mAh/12hr battery, adds NFC and IP67 water resistance. The X2 adds significantly more battery life, water resistance, and NFC connectivity.',
        "v3_accuracies": [
            {"text": "Correctly states both prices.", "span_text": "X1 ($79.99)"},
            {
                "text": "Correctly compares battery specs.",
                "span_text": "3500mAh/12hr battery",
            },
            {
                "text": "Correctly identifies X2 additions.",
                "span_text": "NFC and IP67 water resistance",
            },
        ],
    },
    {
        "question": "Is the Widget Pro X2 waterproof?",
        "kb_doc": "product_specs",
        "kb_title": "Acme Widget Product Specifications",
        "v1_response": "Great question about the water resistance capabilities of the Widget Pro X2! This is one of the standout features that differentiates the X2 from other models in our product lineup at Acme Widgets Inc., and I'm happy to provide a thorough explanation of what the water resistance rating means for your daily use.\n\nThe Widget Pro X2 carries an IP67 water resistance rating. Let me break down what that means in practical terms. The \"IP\" stands for Ingress Protection, which is an international standard for measuring how well electronic devices are sealed against the intrusion of dust and water. The first digit (6) indicates complete protection against dust — no dust particles can enter the device at all. The second digit (7) indicates the device can withstand temporary submersion in water up to 1 meter deep for up to 30 minutes.\n\nIn practical everyday terms, this means the Widget Pro X2 can handle situations like being splashed with water, being used in the rain, being accidentally dropped in a puddle, or even brief submersion if it falls into a sink or shallow water. You can confidently use it in damp environments, during outdoor activities, or in industrial settings where moisture is present.\n\nHowever, it's important to note that IP67 is technically \"water-resistant\" rather than truly \"waterproof.\" While it can handle temporary submersion and everyday water exposure, it's not designed for prolonged underwater use or exposure to high-pressure water jets. Swimming with it or using it in a shower with direct high-pressure water would not be recommended.\n\nIt's also worth mentioning that neither our entry-level Widget Pro X1 nor our industrial Widget Enterprise E1 carries a water resistance rating. The X2 is unique in our lineup for this capability. If water resistance is important to your use case, the X2 is your best option.\n\nThe X2's carbon fiber composite construction also contributes to its environmental resilience, as carbon fiber naturally resists moisture absorption better than the aluminum used in the X1. At $129.99, it's a solid investment for users who need that extra protection!",
        "v2_response": "The Widget Pro X2 has an IP65 water resistance rating, which means it's protected against low-pressure water jets and dust. It can handle rain and splashes but shouldn't be submerged. The carbon fiber body adds extra moisture protection. At $129.99, it's the only water-resistant model in our lineup.",
        "v2_hallucinations": [
            {
                "text": "Water resistance stated as IP65, but actual rating is IP67.",
                "span_text": "IP65 water resistance rating",
            },
            {
                "text": "IP65 description is wrong; IP67 allows submersion up to 1m for 30 min.",
                "span_text": "protected against low-pressure water jets",
            },
        ],
        "v3_response": "The Widget Pro X2 has an IP67 water resistance rating, meaning it's fully dust-proof and can withstand temporary submersion in up to 1 meter of water for 30 minutes. It handles rain, splashes, and accidental drops in water. Note that neither the X1 nor the Enterprise E1 has a water resistance rating. Priced at $129.99.",
        "v3_accuracies": [
            {
                "text": "Correctly states IP67 rating.",
                "span_text": "IP67 water resistance rating",
            },
            {"text": "Correctly states $129.99 price.", "span_text": "$129.99"},
        ],
    },
    # Shipping questions (16-20)
    {
        "question": "What shipping options do you offer?",
        "kb_doc": "shipping_info",
        "kb_title": "Acme Widgets Shipping Information",
        "v1_response": "Thank you for asking about our shipping options at Acme Widgets Inc.! We offer a variety of shipping methods to accommodate different needs and timelines, whether you're looking for the most economical option or need your order as quickly as possible. Let me walk you through all of our available shipping options in detail.\n\nFor domestic shipping within the United States, we offer three distinct tiers. Our Standard Shipping option delivers your order within 5-7 business days at a cost of just $5.95. However, if your order total exceeds $50, standard shipping is completely free! This is our most popular shipping option as it offers great value, especially when customers combine items to meet the free shipping threshold.\n\nOur Express Shipping option delivers within 2-3 business days at a cost of $12.95. This is an excellent middle-ground option for customers who need their items sooner but don't require overnight delivery. Many business customers choose Express for time-sensitive orders.\n\nFor the most urgent needs, we offer Overnight Shipping that delivers by the next business day for $24.95. To qualify for overnight delivery, orders must be placed before 2:00 PM Eastern Standard Time. Orders placed after this cutoff will ship the following business day.\n\nWe also offer International Shipping to over 50 countries worldwide. International deliveries typically take 7-14 business days, and shipping costs are calculated at checkout based on the destination country and package weight. Please note that customs duties and taxes for international orders are the buyer's responsibility.\n\nRegarding order processing, all orders placed before 2:00 PM EST are shipped the same business day. You'll receive a tracking number via email within 24 hours of your order shipping. For added security, we require a signature for any orders valued over $200.\n\nWe're committed to getting your Acme Widgets to you quickly and safely, no matter where you are!",
        "v2_response": "We offer Standard (7-10 days, $4.95, free over $75), Express (2-3 days, $14.95), and Overnight (next day before 3 PM EST, $29.95) shipping for domestic orders. International shipping to 30+ countries takes 10-21 days with costs at checkout. Tracking is provided for all orders. Signature required for orders over $150.",
        "v2_hallucinations": [
            {
                "text": "Standard delivery stated as 7-10 days, actual is 5-7 business days.",
                "span_text": "7-10 days",
            },
            {
                "text": "Standard cost stated as $4.95, actual is $5.95.",
                "span_text": "$4.95",
            },
            {
                "text": "Free threshold stated as $75, actual is $50.",
                "span_text": "free over $75",
            },
            {
                "text": "Overnight cutoff stated as 3 PM, actual is 2 PM EST.",
                "span_text": "3 PM EST",
            },
            {
                "text": "Overnight price stated as $29.95, actual is $24.95.",
                "span_text": "$29.95",
            },
            {
                "text": "International to 30+ countries, actual is 50+.",
                "span_text": "30+ countries",
            },
            {
                "text": "Signature threshold stated as $150, actual is $200.",
                "span_text": "over $150",
            },
        ],
        "v3_response": "We offer three domestic options: Standard (5-7 days, $5.95, free over $50), Express (2-3 days, $12.95), and Overnight (next business day, $24.95, order by 2 PM EST). International shipping to 50+ countries takes 7-14 days with costs calculated at checkout. Orders before 2 PM EST ship same day. Tracking provided within 24 hours.",
        "v3_accuracies": [
            {
                "text": "Correctly states standard shipping details.",
                "span_text": "Standard (5-7 days, $5.95, free over $50)",
            },
            {
                "text": "Correctly states express shipping.",
                "span_text": "Express (2-3 days, $12.95)",
            },
            {
                "text": "Correctly states overnight shipping.",
                "span_text": "Overnight (next business day, $24.95, order by 2 PM EST)",
            },
        ],
    },
    {
        "question": "How much is express shipping?",
        "kb_doc": "shipping_info",
        "kb_title": "Acme Widgets Shipping Information",
        "v1_response": "Thank you for asking about our Express Shipping option at Acme Widgets Inc.! I'm happy to provide you with a complete overview of our express delivery service, including pricing, delivery times, and how it compares to our other shipping options so you can make the best choice for your needs.\n\nOur Express Shipping is priced at $12.95 per order and provides delivery within 2-3 business days. This is a great option for customers who need their widgets relatively quickly but don't require the urgency of overnight delivery. The 2-3 business day window means that in most cases, you'll receive your order within a few days, which is significantly faster than our Standard Shipping's 5-7 business day timeline.\n\nTo put this in context with our other shipping options: Standard Shipping costs $5.95 and takes 5-7 business days (and is free on orders over $50), while Overnight Shipping costs $24.95 and delivers by the next business day when ordered before 2:00 PM EST. Express Shipping at $12.95 fits right in the middle, offering a good balance between speed and cost.\n\nAll of our shipping options, including Express, benefit from our same-day processing commitment. If you place your order before 2:00 PM Eastern Standard Time, your order will ship the same business day. This means an Express order placed at 1:00 PM EST on a Monday would ship that same Monday and typically arrive by Wednesday or Thursday.\n\nYou'll receive a tracking number via email within 24 hours of your order shipping, so you can monitor your package's progress in real-time. For orders over $200, a signature will be required upon delivery for added security, regardless of the shipping method chosen.\n\nExpress Shipping is available for all domestic orders within the United States. For international deliveries, shipping times and costs are calculated separately at checkout based on the destination country.",
        "v2_response": "Express shipping costs $14.95 and delivers within 1-2 business days. It's available for all domestic orders. Orders placed before 3 PM EST ship the same day. You'll get tracking via email within 48 hours of shipment.",
        "v2_hallucinations": [
            {
                "text": "Express price stated as $14.95, actual is $12.95.",
                "span_text": "$14.95",
            },
            {
                "text": "Express delivery stated as 1-2 days, actual is 2-3 business days.",
                "span_text": "1-2 business days",
            },
            {
                "text": "Same-day cutoff stated as 3 PM, actual is 2 PM EST.",
                "span_text": "3 PM EST",
            },
            {
                "text": "Tracking stated as 48 hours, actual is within 24 hours.",
                "span_text": "48 hours",
            },
        ],
        "v3_response": "Express shipping costs $12.95 and delivers within 2-3 business days. Orders placed before 2 PM EST ship the same day. You'll receive a tracking number via email within 24 hours. For comparison, Standard is $5.95 (5-7 days, free over $50) and Overnight is $24.95 (next business day).",
        "v3_accuracies": [
            {"text": "Correctly states $12.95 express price.", "span_text": "$12.95"},
            {
                "text": "Correctly states 2-3 business days.",
                "span_text": "2-3 business days",
            },
            {"text": "Correctly states 2 PM EST cutoff.", "span_text": "2 PM EST"},
        ],
    },
    {
        "question": "Do you ship internationally?",
        "kb_doc": "shipping_info",
        "kb_title": "Acme Widgets Shipping Information",
        "v1_response": "Yes, absolutely! Acme Widgets Inc. is proud to offer international shipping to customers around the world. We understand that our widgets are in demand globally, and we've established shipping partnerships to serve customers in numerous countries. Let me provide you with all the details about our international shipping program.\n\nWe currently ship to over 50 countries worldwide, covering major markets across North America, Europe, Asia, South America, Africa, and Oceania. Our international shipping network continues to grow as we expand our global reach, so even if your country isn't currently on our list, it may be added in the future.\n\nInternational deliveries typically take between 7 and 14 business days, depending on the destination country and local postal service efficiency. Some countries may experience slightly longer delivery times due to customs processing or remote geographic locations. We work with reliable international carriers to ensure your package arrives safely and in good condition.\n\nShipping costs for international orders are calculated at checkout based on several factors including the destination country, package weight, and package dimensions. We present the exact shipping cost before you complete your purchase so there are no surprises. We strive to offer competitive international shipping rates by working with multiple carrier partners.\n\nOne important thing to note is that customs duties, import taxes, and any other fees levied by the destination country's customs authority are the buyer's responsibility. These charges vary by country and are determined by local customs regulations, not by Acme Widgets. We recommend checking your country's import regulations before placing an order so you know what additional costs to expect.\n\nJust like our domestic orders, international orders placed before 2:00 PM EST will be shipped the same business day. You'll receive a tracking number via email within 24 hours of shipment. Please note that international tracking may have less frequent updates compared to domestic tracking, especially once the package enters the destination country's postal system.\n\nWe're committed to making our widgets available to customers everywhere!",
        "v2_response": "Yes! We ship to over 40 countries internationally. Delivery takes 10-21 business days with costs starting at $19.95 based on destination. Customs and import duties are included in the shipping price. International orders over $100 receive free expedited shipping. Tracking is available for all international shipments.",
        "v2_hallucinations": [
            {
                "text": "Country count stated as 40+, actual is 50+.",
                "span_text": "40 countries",
            },
            {
                "text": "Delivery stated as 10-21 days, actual is 7-14 business days.",
                "span_text": "10-21 business days",
            },
            {
                "text": "Customs stated as included, but actual policy says buyer's responsibility.",
                "span_text": "included in the shipping price",
            },
            {
                "text": "Free expedited shipping claim is fabricated; no such policy exists.",
                "span_text": "free expedited shipping",
            },
        ],
        "v3_response": "Yes! We ship to 50+ countries internationally. Delivery takes 7-14 business days, with shipping costs calculated at checkout based on destination. Important: customs duties and import taxes are the buyer's responsibility. Like domestic orders, international orders placed before 2 PM EST ship the same day with tracking provided within 24 hours.",
        "v3_accuracies": [
            {"text": "Correctly states 50+ countries.", "span_text": "50+ countries"},
            {
                "text": "Correctly states 7-14 business days.",
                "span_text": "7-14 business days",
            },
            {
                "text": "Correctly states customs are buyer's responsibility.",
                "span_text": "customs duties and import taxes are the buyer's responsibility",
            },
        ],
    },
    {
        "question": "Is there free shipping?",
        "kb_doc": "shipping_info",
        "kb_title": "Acme Widgets Shipping Information",
        "v1_response": "Great question! At Acme Widgets Inc., we do indeed offer free shipping, and I'd like to give you a complete overview of how it works along with all of our shipping options so you can plan your purchases to maximize value.\n\nYes, we offer free Standard Shipping on all domestic orders over $50! This is one of our most popular benefits and a great way to save on shipping costs. When your order total reaches $50 or more, the $5.95 standard shipping fee is automatically waived at checkout. Many of our customers strategically combine items in their orders to reach the free shipping threshold.\n\nTo put this in perspective, our Standard Shipping normally costs $5.95 and delivers within 5-7 business days. So by spending $50 or more, you save that $5.95 fee while still getting reliable delivery within a week. This applies to all domestic orders within the United States.\n\nIf you need your items faster, our Express Shipping ($12.95, 2-3 business days) and Overnight Shipping ($24.95, next business day by ordering before 2:00 PM EST) are available at their standard rates regardless of order size. The free shipping benefit specifically applies to Standard Shipping only.\n\nFor international orders, shipping costs are always calculated at checkout based on the destination country and are not eligible for the free shipping promotion. International shipping to over 50 countries takes 7-14 business days, and customs duties are the buyer's responsibility.\n\nA few more helpful details about our shipping: all orders placed before 2:00 PM EST ship the same business day, you'll receive tracking via email within 24 hours, and orders over $200 require a signature upon delivery.\n\nSo to summarize: spend $50 or more on your domestic order and enjoy free Standard Shipping! It's just one of the ways we try to make shopping with Acme Widgets as pleasant and affordable as possible.",
        "v2_response": "Yes! We offer free standard shipping on all domestic orders over $75. Standard shipping takes 5-7 business days. If your order is under $75, standard shipping costs $5.95. Express and overnight options are available at additional cost for faster delivery.",
        "v2_hallucinations": [
            {
                "text": "Free shipping threshold stated as $75, actual is $50.",
                "span_text": "over $75",
            },
            {
                "text": "Repeated wrong threshold: under $75 should be under $50.",
                "span_text": "under $75",
            },
        ],
        "v3_response": "Yes! Standard shipping is free on domestic orders over $50. Below that threshold, standard shipping costs $5.95 and delivers in 5-7 business days. Express ($12.95, 2-3 days) and overnight ($24.95, next day) options are also available. International shipping costs are calculated at checkout.",
        "v3_accuracies": [
            {
                "text": "Correctly states free shipping threshold of $50.",
                "span_text": "free on domestic orders over $50",
            },
            {
                "text": "Correctly states $5.95 standard shipping cost.",
                "span_text": "$5.95",
            },
        ],
    },
    {
        "question": "When will my order ship?",
        "kb_doc": "shipping_info",
        "kb_title": "Acme Widgets Shipping Information",
        "v1_response": "Thank you for asking about our order processing and shipping timeline at Acme Widgets Inc.! We know that when you place an order, you want to know exactly when to expect it. Let me provide you with a thorough explanation of our shipping process from the moment you click \"Place Order\" to when your package arrives at your door.\n\nThe great news is that Acme Widgets offers same-day shipping for orders placed before our daily cutoff time of 2:00 PM Eastern Standard Time. This means if you place your order at any point before 2:00 PM EST on a business day (Monday through Friday), your order will be processed, packed, and shipped that very same day. This is one of the fastest order processing commitments in the widget industry.\n\nIf you place your order after 2:00 PM EST, or on a weekend or holiday, your order will be processed and shipped on the next business day. For example, an order placed at 3:00 PM EST on a Friday would ship on the following Monday (assuming Monday is a regular business day).\n\nOnce your order ships, you'll receive a tracking number via email within 24 hours. This tracking number allows you to monitor your package's progress in real-time through our carrier's website. You'll be able to see when it's been picked up, when it's in transit, and when it's out for delivery.\n\nThe total delivery time depends on which shipping method you selected: Standard Shipping delivers within 5-7 business days from the ship date, Express Shipping delivers within 2-3 business days, and Overnight Shipping delivers by the next business day. For international orders, delivery takes 7-14 business days after shipping.\n\nFor your security, we require a signature upon delivery for any order valued over $200. This helps ensure that high-value packages are safely received by the intended recipient. The carrier will make multiple delivery attempts if you're not available to sign.\n\nWe take great care in packaging your widgets to ensure they arrive in perfect condition!",
        "v2_response": "Orders placed before 3 PM EST on business days ship the same day. After that cutoff, they ship the next business day. You'll receive tracking info via email within 48 hours. Delivery time depends on your shipping method: Standard (5-7 days), Express (2-3 days), or Overnight. Signature required for orders over $100.",
        "v2_hallucinations": [
            {
                "text": "Cutoff stated as 3 PM EST, actual is 2 PM EST.",
                "span_text": "3 PM EST",
            },
            {
                "text": "Tracking email stated as within 48 hours, actual is within 24 hours.",
                "span_text": "48 hours",
            },
            {
                "text": "Signature threshold stated as $100, actual is $200.",
                "span_text": "over $100",
            },
        ],
        "v3_response": "Orders placed before 2 PM EST ship the same business day. After that, they ship the next business day. You'll receive a tracking number via email within 24 hours of shipment. Delivery depends on your chosen method: Standard (5-7 days), Express (2-3 days), or Overnight (next day). Signature is required for orders over $200.",
        "v3_accuracies": [
            {"text": "Correctly states 2 PM EST cutoff.", "span_text": "2 PM EST"},
            {
                "text": "Correctly states tracking within 24 hours.",
                "span_text": "within 24 hours",
            },
            {
                "text": "Correctly states $200 signature threshold.",
                "span_text": "over $200",
            },
        ],
    },
]


def find_span(text, substring):
    """Find span_start and span_end for a substring in text."""
    idx = text.find(substring)
    if idx == -1:
        return None, None
    return idx, idx + len(substring)


def build_v1_trace(idx, q):
    response = q["v1_response"]
    word_count = len(response.split())
    annotations = [
        {
            "type": "length_violation",
            "severity": "warning",
            "text": f"Response is {word_count} words, far exceeding the target of ~80 words. Users prefer concise answers.",
            "span_start": None,
            "span_end": None,
        },
        {
            "type": "prompt_issue",
            "severity": "info",
            "text": "The system prompt requests 'at least 300 words', causing verbose responses that hurt user experience.",
            "span_start": None,
            "span_end": None,
        },
    ]

    return {
        "id": f"v1-trace-{idx:03d}",
        "version": "v1",
        "question": q["question"],
        "prompt": V1_PROMPT,
        "response": response,
        "latency_ms": random.randint(2200, 3200),
        "tokens": {"prompt": 92, "completion": word_count + random.randint(-5, 15)},
        "sources": [],
        "annotations": annotations,
    }


def build_v2_trace(idx, q):
    response = q["v2_response"]
    word_count = len(response.split())
    annotations = []

    for h in q["v2_hallucinations"]:
        start, end = find_span(response, h["span_text"])
        annotations.append(
            {
                "type": "hallucination",
                "severity": "error",
                "text": h["text"],
                "span_start": start,
                "span_end": end,
            }
        )

    annotations.append(
        {
            "type": "missing_source",
            "severity": "warning",
            "text": "No sources cited. User cannot verify accuracy of the information provided.",
            "span_start": None,
            "span_end": None,
        }
    )

    return {
        "id": f"v2-trace-{idx:03d}",
        "version": "v2",
        "question": q["question"],
        "prompt": V2_PROMPT,
        "response": response,
        "latency_ms": random.randint(1000, 1400),
        "tokens": {"prompt": 72, "completion": word_count + random.randint(-3, 5)},
        "sources": [],
        "annotations": annotations,
    }


def build_v3_span_trace(idx, q):
    """Generate simulated RAG pipeline spans for v3 traces."""
    spans = []
    current_time = 0

    # Span 1: Query Embedding
    embedding_duration = random.randint(40, 60)
    spans.append(
        {
            "span_id": f"v3-trace-{idx:03d}-span-1",
            "name": "Query Embedding",
            "span_type": "embedding",
            "start_time": current_time,
            "duration_ms": embedding_duration,
            "input": {"text": q["question"]},
            "output": {"dimensions": 384, "preview": "[0.123, -0.456, 0.789, ...]"},
            "metadata": {"model": "all-MiniLM-L6-v2"},
        }
    )
    current_time += embedding_duration

    # Span 2: ChromaDB Retrieval
    retrieval_duration = random.randint(100, 150)
    kb_content_preview = (
        "Acme Widgets Return Policy..."
        if "return" in q["kb_doc"]
        else (
            "Pricing: Starter ($49)..."
            if "pricing" in q["kb_doc"]
            else (
                "Product Specs..."
                if "product" in q["kb_doc"]
                else "Shipping Information..."
            )
        )
    )
    spans.append(
        {
            "span_id": f"v3-trace-{idx:03d}-span-2",
            "name": "ChromaDB Retrieval",
            "span_type": "retrieval",
            "start_time": current_time,
            "duration_ms": retrieval_duration,
            "input": {"embedding_dim": 384, "n_results": 3},
            "output": {
                "documents": [
                    {
                        "id": q["kb_doc"],
                        "title": q["kb_title"],
                        "distance": round(random.uniform(0.2, 0.4), 3),
                        "content_preview": kb_content_preview,
                    }
                ]
            },
            "metadata": {"collection": "acme_knowledge_base"},
        }
    )
    current_time += retrieval_duration

    # Span 3: Context Building
    context_duration = random.randint(5, 15)
    kb_dir = Path(__file__).parent.parent / "data" / "knowledge_base"
    kb_path = kb_dir / f"{q['kb_doc']}.md"
    kb_content = kb_path.read_text() if kb_path.exists() else ""
    context_preview = kb_content[:100] + "..." if len(kb_content) > 100 else kb_content
    spans.append(
        {
            "span_id": f"v3-trace-{idx:03d}-span-3",
            "name": "Context Building",
            "span_type": "context",
            "start_time": current_time,
            "duration_ms": context_duration,
            "input": {"doc_count": 1},
            "output": {
                "context_length": len(kb_content),
                "preview": f"[{q['kb_title']}]\n{context_preview}",
            },
            "metadata": {"separator": "\\n\\n---\\n\\n"},
        }
    )
    current_time += context_duration

    # Span 4: Prompt Construction
    prompt_duration = random.randint(5, 10)
    prompt_full = V3_PROMPT_TEMPLATE.format(
        doc_title=q["kb_title"], doc_content=kb_content
    )
    prompt_preview = prompt_full[:100] + "..."
    spans.append(
        {
            "span_id": f"v3-trace-{idx:03d}-span-4",
            "name": "Prompt Construction",
            "span_type": "prompt",
            "start_time": current_time,
            "duration_ms": prompt_duration,
            "input": {"template": "V3_SYSTEM_PROMPT"},
            "output": {"prompt_length": len(prompt_full), "preview": prompt_preview},
            "metadata": {"template_version": "v3"},
        }
    )
    current_time += prompt_duration

    # Span 5: Claude API Call
    api_duration = random.randint(1800, 2500)
    response_preview = q["v3_response"][:100] + "..."
    word_count = len(q["v3_response"].split())
    prompt_tokens = len(prompt_full.split()) + random.randint(350, 450)
    completion_tokens = word_count + random.randint(-3, 5)
    spans.append(
        {
            "span_id": f"v3-trace-{idx:03d}-span-5",
            "name": "Claude API Call",
            "span_type": "llm",
            "start_time": current_time,
            "duration_ms": api_duration,
            "input": {
                "model": "claude-sonnet-4-20250514",
                "max_tokens": 512,
                "message_preview": q["question"],
            },
            "output": {
                "response_preview": response_preview,
                "usage": {
                    "input_tokens": prompt_tokens,
                    "output_tokens": completion_tokens,
                },
                "stop_reason": "end_turn",
            },
            "metadata": {"api_version": "2023-06-01"},
        }
    )
    current_time += api_duration

    return spans, current_time


def build_v3_trace(idx, q):
    response = q["v3_response"]
    word_count = len(response.split())

    # Build prompt with context
    kb_dir = Path(__file__).parent.parent / "data" / "knowledge_base"
    kb_path = kb_dir / f"{q['kb_doc']}.md"
    kb_content = kb_path.read_text() if kb_path.exists() else ""
    prompt = V3_PROMPT_TEMPLATE.format(doc_title=q["kb_title"], doc_content=kb_content)

    annotations = []
    for a in q["v3_accuracies"]:
        start, end = find_span(response, a["span_text"])
        annotations.append(
            {
                "type": "accurate_answer",
                "severity": "success",
                "text": a["text"],
                "span_start": start,
                "span_end": end,
            }
        )

    annotations.append(
        {
            "type": "correct_retrieval",
            "severity": "success",
            "text": f"Retrieved relevant {q['kb_doc']} document for the query.",
            "span_start": None,
            "span_end": None,
        }
    )

    # Generate RAG pipeline spans
    spans, total_latency = build_v3_span_trace(idx, q)

    return {
        "id": f"v3-trace-{idx:03d}",
        "version": "v3",
        "question": q["question"],
        "prompt": prompt,
        "response": response,
        "latency_ms": total_latency,
        "tokens": {
            "prompt": len(prompt.split()) + random.randint(350, 450),
            "completion": word_count + random.randint(-3, 5),
        },
        "sources": [{"id": q["kb_doc"], "title": q["kb_title"]}],
        "annotations": annotations,
        "spans": spans,
    }


def main():
    output_dir = Path(__file__).parent.parent / "data" / "traces"
    output_dir.mkdir(parents=True, exist_ok=True)

    v1_traces = []
    v2_traces = []
    v3_traces = []

    for idx, q in enumerate(QUESTIONS, start=1):
        v1_traces.append(build_v1_trace(idx, q))
        v2_traces.append(build_v2_trace(idx, q))
        v3_traces.append(build_v3_trace(idx, q))

    for version, traces in [("v1", v1_traces), ("v2", v2_traces), ("v3", v3_traces)]:
        path = output_dir / f"{version}_traces.json"
        with open(path, "w") as f:
            json.dump(traces, f, indent=2)
        print(f"{version}: {len(traces)} traces written to {path}")

    # Validate spans
    errors = 0
    for traces in [v1_traces, v2_traces, v3_traces]:
        for t in traces:
            for ann in t["annotations"]:
                if ann["span_start"] is not None and ann["span_end"] is not None:
                    span_text = t["response"][ann["span_start"]:ann["span_end"]]
                    if not span_text:
                        print(f"  WARNING: Empty span in {t['id']}: {ann['text']}")
                        errors += 1

    if errors:
        print(f"\n{errors} span errors found!")
    else:
        print("\nAll spans validated successfully.")


if __name__ == "__main__":
    main()
