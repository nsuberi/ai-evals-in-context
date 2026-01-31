"""Test fixtures - Sample questions and expected answers"""

SAMPLE_QUESTIONS = [
    {
        'question': "What is your return policy?",
        'expected_keywords': ['30', 'day', 'return'],
        'category': 'returns'
    },
    {
        'question': "How much does the Enterprise plan cost?",
        'expected_keywords': ['299', 'month'],
        'category': 'pricing'
    },
    {
        'question': "What are the specs of Widget Pro X2?",
        'expected_keywords': ['5"', 'IP67', '129'],
        'category': 'products'
    },
    {
        'question': "How long does standard shipping take?",
        'expected_keywords': ['5-7', 'business', 'day'],
        'category': 'shipping'
    },
    {
        'question': "How much does express shipping cost?",
        'expected_keywords': ['12.95'],
        'category': 'shipping'
    },
]

GROUND_TRUTH = {
    'enterprise_price': '$299/month',
    'starter_price': '$49/month',
    'return_window': '30 days',
    'express_shipping': '$12.95',
    'widget_x2_price': '$129.99',
    'standard_shipping_time': '5-7 business days',
    'overnight_shipping': '$24.95',
}

EDGE_CASE_QUESTIONS = [
    "What is your cryptocurrency payment policy?",  # Not in KB
    "Can I return a customized widget?",  # Non-returnable
    "What's the warranty period?",  # 90 days
]
