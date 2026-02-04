# Architecture Overview

## System Architecture

```
+-------------------------------------------------------------+
|                     WEB INTERFACE                           |
|  Customer types question -> Displays response + sources     |
+-----------------------------+-------------------------------+
                              |
                              v
+-------------------------------------------------------------+
|                    CHATBOT SERVICE                          |
|  1. Receives question                                       |
|  2. Retrieves relevant documents from KB                    |
|  3. Constructs prompt with context                          |
|  4. Calls AI model                                          |
|  5. Returns response with sources                           |
+-----------------------------+-------------------------------+
                              |
              +---------------+---------------+
              v                               v
+--------------------------+    +--------------------------+
|    KNOWLEDGE BASE        |    |       AI MODEL           |
|    (Chroma Vector DB)    |    |    (Claude Sonnet)       |
|                          |    |                          |
|  - pricing_tiers.md      |    |  - Concise responses     |
|  - product_specs.md      |    |  - Grounded in context   |
|  - return_policy.md      |    |  - Source attribution    |
|  - shipping_info.md      |    |                          |
+--------------------------+    +--------------------------+
```

The architecture follows a standard RAG (Retrieval-Augmented Generation) pattern where user questions are first matched against the knowledge base, then relevant context is included in the prompt to the AI model.
