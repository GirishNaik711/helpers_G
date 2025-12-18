from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0001_init"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("customer_id", sa.Text(), primary_key=True),
        sa.Column("full_name", sa.Text(), nullable=False),
        sa.Column("date_of_birth", sa.Date(), nullable=True),
        sa.Column("retirement_goal_date", sa.Date(), nullable=True),
        sa.Column("preferred_notification_method", sa.String(length=32), nullable=False, server_default="unknown"),
        sa.Column("investment_experience_level", sa.String(length=32), nullable=False, server_default="unknown"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "wealth_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("customer_id", sa.Text(), sa.ForeignKey("users.customer_id", ondelete="CASCADE"), nullable=False),
        sa.Column("as_of", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("total_investable_assets", sa.Numeric(18, 2), nullable=True),
        sa.Column("checking_balance", sa.Numeric(18, 2), nullable=True),
        sa.Column("savings_balance", sa.Numeric(18, 2), nullable=True),
        sa.Column("brokerage_balance", sa.Numeric(18, 2), nullable=True),
        sa.Column("external_accounts_linked", sa.Integer(), nullable=False, server_default="0"),
    )
    op.create_index("ix_wealth_customer_asof", "wealth_snapshots", ["customer_id", "as_of"])

    op.create_table(
        "holdings_snapshots",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("customer_id", sa.Text(), sa.ForeignKey("users.customer_id", ondelete="CASCADE"), nullable=False),
        sa.Column("as_of", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("ticker", sa.String(length=16), nullable=True),
        sa.Column("category", sa.String(length=64), nullable=False, server_default="other"),
        sa.Column("units", sa.Numeric(20, 6), nullable=True),
        sa.Column("current_market_value", sa.Numeric(18, 2), nullable=True),
        sa.Column("cost_basis", sa.Numeric(18, 2), nullable=True),
        sa.Column("dividend_reinvestment_enabled", sa.Boolean(), nullable=True),
        sa.Column("recent_dividend_payments", sa.Numeric(18, 2), nullable=True),
        sa.Column("dividend_yield_pct", sa.Numeric(8, 4), nullable=True),
    )
    op.create_index("ix_holdings_customer_asof", "holdings_snapshots", ["customer_id", "as_of"])
    op.create_index("ix_holdings_ticker", "holdings_snapshots", ["ticker"])

    op.create_table(
        "goals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("customer_id", sa.Text(), sa.ForeignKey("users.customer_id", ondelete="CASCADE"), nullable=False),
        sa.Column("goal_type", sa.String(length=64), nullable=False),
        sa.Column("target_amount", sa.Numeric(18, 2), nullable=True),
        sa.Column("progress_pct", sa.Numeric(6, 2), nullable=True),
        sa.Column("estimated_goal_date", sa.Date(), nullable=True),
    )

    op.create_table(
        "activity_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("customer_id", sa.Text(), sa.ForeignKey("users.customer_id", ondelete="CASCADE"), nullable=False),
        sa.Column("event_type", sa.String(length=64), nullable=False),
        sa.Column("event_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("event_metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
    )
    op.create_index("ix_activity_customer_eventat", "activity_events", ["customer_id", "event_at"])

    op.create_table(
        "activity_summary",
        sa.Column("customer_id", sa.Text(), sa.ForeignKey("users.customer_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("last_login_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("login_frequency_30d", sa.Integer(), nullable=True),
        sa.Column("engagement_score", sa.Numeric(8, 4), nullable=True),
        sa.Column("inactivity_flag", sa.Boolean(), nullable=False, server_default=sa.text("false")),
    )

    op.create_table(
        "preferences",
        sa.Column("customer_id", sa.Text(), sa.ForeignKey("users.customer_id", ondelete="CASCADE"), primary_key=True),
        sa.Column("preferred_insight_format", sa.String(length=32), nullable=False, server_default="text"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )

    op.create_table(
        "content_consumption",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("customer_id", sa.Text(), sa.ForeignKey("users.customer_id", ondelete="CASCADE"), nullable=False),
        sa.Column("content_id", sa.Text(), nullable=False),
        sa.Column("provider", sa.String(length=64), nullable=False, server_default="unknown"),
        sa.Column("consumed_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )
    op.create_index("ix_consumption_customer_time", "content_consumption", ["customer_id", "consumed_at"])

    op.create_table(
        "insight_feedback",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("customer_id", sa.Text(), sa.ForeignKey("users.customer_id", ondelete="CASCADE"), nullable=False),
        sa.Column("insight_id", sa.Text(), nullable=False),
        sa.Column("feedback", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("insight_feedback")
    op.drop_index("ix_consumption_customer_time", table_name="content_consumption")
    op.drop_table("content_consumption")
    op.drop_table("preferences")
    op.drop_table("activity_summary")
    op.drop_index("ix_activity_customer_eventat", table_name="activity_events")
    op.drop_table("activity_events")
    op.drop_table("goals")
    op.drop_index("ix_holdings_ticker", table_name="holdings_snapshots")
    op.drop_index("ix_holdings_customer_asof", table_name="holdings_snapshots")
    op.drop_table("holdings_snapshots")
    op.drop_index("ix_wealth_customer_asof", table_name="wealth_snapshots")
    op.drop_table("wealth_snapshots")
    op.drop_table("users")
