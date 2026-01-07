# Agentic Commerce: Going Big with Small Businesses

Here is the application proposed by our team for the **Stripe Challenge** at the 2025 edition of HackItAll.

Team Name: Stack Overhacked

Members:

- Alexia Florete [@alexia29florete](https://github.com/alexia29florete)
- Maria Ungurean [@MariaUng](https://github.com/MariaUng)
- Daniel Dinu [@danieldinu2030](https://github.com/danieldinu2030)

## The Challenge

Participants are invited to build an AI-driven "Agentic Commerce" solution. The goal is to create an intelligent interface that bridges the gap between intent and purchase, specifically favoring small, local (specifically in Romania),, or specialized businesses.
Instead of browsing endless catalogs, users should be able to express a complex intent (e.g., "I need a 100% cotton orange t-shirt from a local maker," or "Build a grocery cart from three different local bakeries and farm shops"), and the Agent should handle the rest.

### Core Requirements & Mechanics

Teams should focus on a pipeline that moves beyond a simple chatbot. The solution should demonstrate:
Intent Understanding: Parsing complex user prompts (e.g., differentiating between a generic request and a specific material/location requirement).

- The "Agent" Layer: The system must act as an agent, not just a text generator. It should utilize tools/APIs to:
  - Query multiple data sources
  - Filter results
  - Aggregate options into a cohesive view
- Iterative UX:
  - Some sort of app UI that encompasses the idea
  - A conversational interface where the user can refine results

### Suggested Use Cases (Inspiration)

- The Hyper-Local Hunter: An agent that finds specific clothing items or crafts within a 5-mile radius of the user.
- The Aggregated Cart: An agent that takes a shopping list, finds the best local vendors for each item, and combines them into a single payment flow ("One click, three shops").
- The Ethical Filter: An agent that explicitly filters out mass-produced items to surface products with high "social value."

### Judging Criteria

#### 1. Technical Implementation & "Agentic" Capabilities

- Complexity: Does the solution utilize actual agentic workflows (function calling, API integrations) rather than just standard LLM text generation?
- Accuracy: Does the agent respect constraints (e.g., "100% cotton") or does it hallucinate products?

#### 2. Social Impact & "Small Business" Alignment

- Value Proposition: Does this genuinely help small businesses compete with giants?
- Quality Filtering: How well does the system distinguish between high-value local businesses and low-quality products?
- Community: Does the solution foster a connection between the buyer and the local seller?

#### 3. Product Viability & Startup Potential

- Monetization: Is there a clear business model? (e.g., a fee on the "single checkout" convenience, or a SaaS model for shops).
- Scalability: Can this expand beyond the demo?
- Pitch: Is the presentation convincing? Does it answer the question: "Is this a good startup?"

#### 4. User Experience (UX) & Innovation

- "Click Less, Get More": Does the interface actually reduce the friction of shopping?
- Feedback Loops: Does the system capture user feedback (e.g., "This isn't what I wanted") to improve future searches?

## Running the App

You should be using a virtual environment. Run these commands:

```bash
    sudo apt install virtualenv
    virtualenv .venv
    source .venv/bin/activate
    pip install -r requirements.txt
    python app.py
```
