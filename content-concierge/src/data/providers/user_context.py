from __future__ import annotations

from core.schemas.user_context import (
    AccountProfile,
    ActivityHistory,
    ExperienceLevel,
    Goals,
    Goal,
    Holding,
    HoldingCategory,
    NotificationMethod,
    Portfolio,
    Preferences,
    UserContext,
    WealthSummary,
)

from data.relational.repo import RelationalRepo


class UserContextProvider:
    """
    Loads canonical UserContext from Postgres (latest snapshots).
    """

    def __init__(self, repo: RelationalRepo):
        self.repo = repo

    def load(self, customer_id: str) -> UserContext:
        user = self.repo.get_user(customer_id)
        wealth = self.repo.get_latest_wealth(customer_id)
        holdings = self.repo.get_latest_holdings(customer_id)
        goals = self.repo.get_goals(customer_id)
        activity = self.repo.get_activity_summary(customer_id)
        prefs = self.repo.get_preferences(customer_id)

        wealth_model = WealthSummary(
            total_investable_assets=float(wealth.total_investable_assets) if wealth and wealth.total_investable_assets is not None else None,
            checking_balance=float(wealth.checking_balance) if wealth and wealth.checking_balance is not None else None,
            savings_balance=float(wealth.savings_balance) if wealth and wealth.savings_balance is not None else None,
            brokerage_balance=float(wealth.brokerage_balance) if wealth and wealth.brokerage_balance is not None else None,
            external_accounts_linked=wealth.external_accounts_linked if wealth else 0,
        )

        holdings_models: list[Holding] = []
        for h in holdings:
            cost_basis = float(h.cost_basis) if h.cost_basis is not None else None
            mv = float(h.current_market_value) if h.current_market_value is not None else None
            unreal = (mv - cost_basis) if (mv is not None and cost_basis is not None) else None

            # Category normalization: keep DB values, but map into enum when possible
            try:
                cat = HoldingCategory(h.category)
            except Exception:
                cat = HoldingCategory.other

            holdings_models.append(
                Holding(
                    name=h.name,
                    ticker=h.ticker,
                    category=cat,
                    units=float(h.units) if h.units is not None else None,
                    current_market_value=mv,
                    cost_basis=cost_basis,
                    unrealized_gain_loss=unreal,
                    dividend_reinvestment_enabled=h.dividend_reinvestment_enabled,
                    recent_dividend_payments=float(h.recent_dividend_payments) if h.recent_dividend_payments is not None else None,
                    dividend_yield_pct=float(h.dividend_yield_pct) if h.dividend_yield_pct is not None else None,
                )
            )

        goals_model = Goals(
            goals=[
                Goal(
                    goal_type=g.goal_type,
                    target_amount=float(g.target_amount) if g.target_amount is not None else None,
                    progress_pct=float(g.progress_pct) if g.progress_pct is not None else None,
                    estimated_goal_date=g.estimated_goal_date,
                )
                for g in goals
            ]
        )

        activity_model = ActivityHistory(
            last_login_at=activity.last_login_at if activity else None,
            login_frequency_30d=activity.login_frequency_30d if activity else None,
            engagement_score=float(activity.engagement_score) if activity and activity.engagement_score is not None else None,
            inactivity_flag=activity.inactivity_flag if activity else False,
        )

        pref_model = Preferences(
            preferred_insight_format=(prefs.preferred_insight_format if prefs else "text"),
        )

        # Enum casting with fallbacks
        try:
            notif = NotificationMethod(user.preferred_notification_method)
        except Exception:
            notif = NotificationMethod.unknown

        try:
            exp = ExperienceLevel(user.investment_experience_level)
        except Exception:
            exp = ExperienceLevel.unknown

        return UserContext(
            profile=AccountProfile(
                customer_id=user.customer_id,
                full_name=user.full_name,
                date_of_birth=user.date_of_birth,
                retirement_goal_date=user.retirement_goal_date,
                preferred_notification_method=notif,
                investment_experience_level=exp,
            ),
            wealth=wealth_model,
            portfolio=Portfolio(holdings=holdings_models),
            goals=goals_model,
            activity=activity_model,
            preferences=pref_model,
        )
