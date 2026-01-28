Scope Document: Content Concierge MVP 1 — Personalized Engagement for Inactive Wealth Users

1. Business Context & Objective

The Content Concierge solution is designed to re-engage inactive users of the bank’s Wealth Management platform by delivering hyper-personalized financial insights and learning resources (videos, audio, bullet summaries) on the account homepage, tailored to the user’s unique portfolio. The ultimate aim is to encourage renewed activity and help clients on their financial journey, deepening their engagement with the bank's products and services.

Target Audience for MVP 1
    - Inactive Wealth Management Users: Defined as clients with wealth accounts (e.g., 250K+ invested, 1M+ total assets across platforms) who have not engaged in key activities (e.g., trades, check-ins, consultations) beyond a set threshold (to be defined in implementation).
    - Example Persona: “Alex,” a 50-year-old professional building for retirement, with $250K invested.

2. Scope of MVP 1

In-Scope

    - Use Case 1: Proactively re-engage inactive users at login/account home with curated, relevant, and actionable content.
    - *Use Cases 2 and 3* (for “Everyday” and “Advanced” users) are not in scope for MVP 1 but are roadmap items.

Key Features

1. Personalized Investment Insights Module (Front-End)
    - Appear prominently on account summary/homepage for targeted inactive users.
    - Display 2–3 key insights per session (e.g., “You’re 71% of the way to retirement goal!” or “Dividend-growth stocks are trending”).
    - Each insight includes a call-to-action *plus* links to further learning in the user’s preferred format:
    - Short video
    - Audio clip
    - 3-bullet summary

2. Educational Content Delivery
    - Curated financial literacy materials, tactical guides, and news *directly related* to user’s portfolio/gaps.
    - Multi-format support (video/audio/bullet).

3. Backend Personalization Pipeline
    - AI agent queries relational database for user’s up-to-date portfolio, holdings, goal progress, and recent actions.
    - AI agent scrapes/browses approved web sources (plus proprietary content if available) for:
    - Market news or portfolio-relevant updates
    - Articles/tutorials explaining relevant strategies (e.g., impact of asset allocation changes, trending funds)
    - AI agent generates context-aware, explainable SQL queries to retrieve pertinent user information.

4. Insight Curation & Delivery
    - Backend combines user context, scraped content, and pre-authorized learning assets.
    - Generates concise, high-value, engaging insight modules with *attribution to original sources or further reading*.
    - Links to click-through educational items based on the user's engagement and preference history.

5. User Activity & Feedback Tracking
    - Track which insights and educational assets users interact with, for ongoing learning-path refinement.


3. Requirements

Functional Requirements

    - User Authentication & Segmentation:
    - Identify inactive users at login; flag them for targeted content.
    - Personalized Dashboard:
    - Dynamically populate content modules with insights at login based on live/near-real-time data.
    - Content Engine:
    - LLMS dynamically generates SQL to get up-to-date portfolio and activity data per user.
    - Automatically scrape new content from designated sources.
    - Map educational content to each insight for various formats.
    - Personalization/curation logic must be explainable, traceable for audit/regulatory needs.
    - Frontend Integration:
    - Easy-to-read, modular widgets for: insights, video/audio player, bullet-point summaries.
    - Click-through & Interaction Analytics:
    - Robust tracking to gauge what content resonates/activates user (type, length, style).

Non-Functional Requirements

    - Performance: Content modules must load within X seconds of account login (specific SLA to be defined).
    - Security/Privacy: Only the authenticated user’s data accessed; all bank/internal policies rigorously applied.
    - Compliance: Content selection, storage, and display must be auditable; must filter for suitability/compliance.
    - Extensibility: Architecture should allow easy onboarding of new user segments (Use Cases 2/3) and content types.


4. Workflows & Data Flows

User Journey

1. Login:
    - User logs into Wealth Management portal/app.
2. Detection:
    - System checks for inactivity criteria; flags user for Concierge pilot.
3. Content Assembly:
    - Backend queries user data via LLMS-generated SQL, fetches up-to-date portfolio/goals/status.
    - AI agent scrapes approved web pages for current news/trends aligning to user’s needs.
    - Agent selects/curates matching educational assets in chosen formats.
    - Module generated with 2–3 insights + educational links.
4. Presentation:
    - Personalized insight modules displayed in user’s “Investment Summary” or home.
    - User can read summary, watch video, or listen to a concise audio.
5. Tracking:
    - Each interaction logged for future refinement.

Backend Data Flow

User Log-in	User Status Determination	Data Fetch (RDBMS via SQL)	Content Scraping & Mapping	Insight Generation & Curation	Frontend Display & Analytics Logging


5. Out of Scope for MVP 1

    - "Everyday" and "Advanced" user segments (future releases).
    - Portfolio action nudges or trade execution recommendations.
    - Deep third-party integrations beyond web scraping.


6. Success Criteria & KPIs

    - Adoption: % of flagged inactive users interacting with the insight modules.
    - Engagement: Avg number of insights/learning assets consumed per session.
    - Activation Rate: % of previously inactive users performing key actions post-exposure.
    - User Feedback: Qualitative feedback on clarity, relevance, utility of insights.


7. Assumptions & Dependencies

    - Timely access to anonymized portfolio/activity data.
    - Pre-approved list of compliant educational resources and web sources.
    - Alignment on inactivity definition and engagement metrics.


8. Illustrative Example (from Screenshot)

> User Alex (persona):
> Sees: “You’re 71% of the way to your 2032 retirement goal! 60/40 portfolio can replace 80% of paycheck. Continue investing to remain on track.”
> Also sees: “Dividend-growth stocks trending (🔼 40% chatter, 🔼 25% ETF volume). Learn how a 5% shift to Dividend-Aristocrat ETF could lift your yield.”
> Each is clickable: “Watch a 2-min video” or “See 3-bullet summary.”
====================================================================================================================

E.g:
Alex opens the X app to personalized investment insights on the Investment Summary page, tailored to his goals and financial profile (e.g., “You’re 71 % of the way to your 2032 retirement goal: a 60/40 portfolio that can replace 80% of your paycheck. Continue investing to stay on track”) as well as dynamic market insights (e.g., “Dividend-growth stocks are trending (⇧ 40 % chatter, ⇧ 25 % ETF volume). Learn how a 5 % shift to a Dividend-Aristocrat ETF could lift your yield.” Each insight links to educational content in his preferred format (e.g., video, audio-clip, 3 bullet summary). 



PERSONALIZED INVESTMENT INSIGHTS ​

Agent continuously tracks Alex’s progress toward his goals, generating tailored updates.​

Selects and surfaces relevant educational articles and resources linked to each insight.​

Personalizes insights and links based on activity, preferences, and knowledge gaps.​

Auto-tunes content based on engagement ​


==============

Inputs from Relational Source: [Assumptions - For initial POC build]
 
A. Account & Personal Profile
 
Customer ID (system identifier)
Full Name
Date of Birth / Age (e.g., 50-year-old professional)
Retirement Goal Date (e.g., 2032)
Preferred Contact/Notification Method
Investment Experience Level (if available)
 
B. Total Wealth & Asset Aggregation
 
Total Investable Assets (sum across all linked accounts, e.g., $1M)
Account Balances (segmented by checking, savings, brokerage)
External Accounts Linked (other banks/brokerages, if supported)
 
C. Investment Portfolio Details
 
Portfolio Asset Mix / Allocation
 
Asset Classes (percent breakdown: equities/stocks, fixed income/bonds, cash, alternatives, ETFs, mutual funds, etc.)
Holding Categories (domestic stocks, international stocks, US Treasuries, REITs, etc.)
 
 
Individual Holdings (per security/fund/ETF)
 
Security/Fund/ETF Name
Ticker Symbol
Number of Shares/Units
Current Market Value
Cost Basis / Purchase Price
Acquisition Date
Dividend/Reinvestment Election Status
Recent Dividend Payments & Yield
Unrealized Gain/Loss
 
 
D. Goals & Progress
 
Defined Financial Goals
 
Goal Type (retirement, home purchase, education, etc.)
Target Amount
Progress-to-Goal % (calculated field, e.g., 71%)
Estimated Goal Date
 
 
Contribution History/Schedule (recurring or lump-sum investments)
E. Activity/Behavioral History
Latest Trades/Transactions
Login Frequency / Last Accessed
Recent Interactions (e.g., tutorial videos watched)
Engagement Score / Activity Level Flag (how “inactive” is determined)
F. Preferences and Personalization
Preferred Insight Format (video/audio/bullet/text)
Prior Content Consumed
Feedback/Thumbs-up/down on insights


======================

You are a wealth management insights assistant and your mission is to re-engage inactive clients by surfacing smart, actionable investment insights tied to their actual portfolio status, recent market events, and preferred learning format.
Always personalize your response with the user’s context and attach an educational resource in their preferred format (e.g., video, audio-clip, or concise 3-bullet summary) for each insight, using only the provided educational library or trusted content feeds.
 
USER PROFILE
 
Name: [User Name]
Age: [User Age]
Inactivity duration: [Number of days/weeks inactive]
Investment Goals: [Goal description; target $ and date, e.g., "Retire by 2032 with $1M"]
Progress to Goal: [Current % to goal; summary (e.g., 71%)]
Preferred Content Format: [video | audio-clip | 3-bullet summary | combination, as indicated by user/app engagement]
 
PORTFOLIO SNAPSHOT
 
Total Investable Assets: [$ Amount]
Asset Mix: [e.g., 60% US Stocks, 30% Bonds, 10% ETFs]
Key Holdings:
 
[Name (Ticker): $Value, Shares, Asset Class, Cost Basis, Unrealized Gains/Losses]
 
 
Recent Dividend/Income Activity: [e.g., "$320 in dividends paid since last visit"]
Recent Transactions: [any important buys/sells or inactivity]
 
MARKET & NEWS SIGNALS
 
Major market news relevant to holdings:
[e.g., "Dividend-growth stocks trending—up 8% per Benzinga; ETF X sees 25% higher volume"]
Trending topics in user’s asset categories:
[e.g., “Dividend Aristocrat ETF”, “60/40 portfolio”, etc.]
 
EDUCATIONAL CONTENT LIBRARY
(all items pre-matched and curated from Benzinga, MT Newswire, or trusted internal sources)
 
For each market topic or portfolio opportunity above, provide:
 
Video: [Title, 1-sentence description, URL/ID]
Audio-clip: [Title, 1-sentence description, URL/ID]
3-bullet summary: [Bulleted key takeaways or summary, URL/ID]
 
 
Always use the user’s preferred content format for linking educational action steps.
 
 
Instructions to LLM:
 
In 2–3 clear, neutral, and encouraging sentences:
 
Acknowledge the user’s inactivity duration and any missed events/opportunities (market movement, dividends, etc.) since their last login.
Highlight a personalized action opportunity or insight relevant to their holdings or goals, referencing current market/news context.
Conclude with a direct educational call-to-action in the user’s preferred format, linking the resource for deeper learning.
 
Example: “Learn more in a quick 3-bullet summary here: [title/link],” or “Watch this 2-minute video to explore the strategy: [title/link]”, or “Listen to a 30-second audio clip: [title/link]”.
 
 
Always cite the source for any news or data (e.g., “as reported by Benzinga”).
Never provide investment advice—present information for consideration, exploration, or learning only.
If no educational content exists in the user’s preferred format, fall back to the next best available option.
