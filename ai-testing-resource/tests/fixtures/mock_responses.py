"""Mock AI responses for testing without API calls"""

MOCK_RESPONSES = {
    'v1': {
        'return_policy': {
            'text': """Thank you for your inquiry about our return policy! At Acme Widgets Inc., we take great pride in ensuring customer satisfaction and have developed a comprehensive return policy that addresses various scenarios you might encounter.

Our standard return policy allows customers a generous 30-day return window starting from the delivery date. During this period, you can return any item that meets our return conditions for a full refund to your original payment method. The items must be unused and in their original packaging to qualify for a return.

For defective products, we offer an extended 90-day warranty period. If you receive a defective item, we will either replace it completely free of charge or provide you with a full refund. In these cases, we cover all return shipping costs.

For change-of-mind returns, there is a flat rate return shipping fee of $8.95. Please note that certain items are non-returnable, including customized or personalized widgets, clearance items marked as "Final Sale," and items that have been damaged due to misuse.

Refunds are typically processed within 5-7 business days after we receive your returned item. While original shipping charges are non-refundable, we do offer a store credit option that adds a 10% bonus value to your credit amount.

If you have any additional questions about our return policy, please don't hesitate to reach out to our customer support team.""",
            'sources': [],
            'metadata': {
                'latency_ms': 2500,
                'prompt_tokens': 85,
                'completion_tokens': 280,
                'total_tokens': 365
            }
        }
    },
    'v2': {
        'return_policy': {
            'text': """Our return policy offers a 30-day window for returns. Items must be unused and in original packaging. You'll receive a full refund to your original payment method. For defective items, we provide free return shipping. Change-of-mind returns have a $8.95 shipping fee. Refunds are processed within 5-7 business days.""",
            'sources': [],
            'metadata': {
                'latency_ms': 1200,
                'prompt_tokens': 65,
                'completion_tokens': 75,
                'total_tokens': 140
            }
        }
    },
    'v3': {
        'return_policy': {
            'text': """We offer a 30-day return window from delivery date. Items must be unused and in original packaging for a full refund. Defective products have a 90-day warranty with free returns. Change-of-mind returns cost $8.95 for shipping. Note that customized items and "Final Sale" clearance items cannot be returned. Refunds process in 5-7 business days.""",
            'sources': [
                {'id': 'return_policy', 'title': 'Acme Widgets Return Policy'}
            ],
            'metadata': {
                'latency_ms': 1800,
                'prompt_tokens': 450,
                'completion_tokens': 85,
                'total_tokens': 535
            }
        }
    }
}
