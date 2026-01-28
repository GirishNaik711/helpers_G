"""Streamlit UI for Financial Insights POC."""
import streamlit as st
import pandas as pd
import requests
from io import BytesIO
from datetime import datetime, timedelta

# --- Configuration ---
API_BASE_URL = "http://localhost:8000"
INACTIVE_THRESHOLD_DAYS = 180  # 6 months

st.set_page_config(
    page_title="Financial Insights",
    page_icon="📊",
    layout="centered"
)

# --- Custom CSS ---
st.markdown("""
<style>
    .insight-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 12px;
        color: white;
        margin: 10px 0;
    }
    .suggestion-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #667eea;
        margin: 8px 0;
    }
    .ticker-badge {
        background: #667eea;
        color: white;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: bold;
        display: inline-block;
        margin-right: 8px;
    }
    .change-positive { color: #28a745; font-weight: bold; }
    .change-negative { color: #dc3545; font-weight: bold; }
    .inactive-badge {
        background: #dc3545;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        margin-left: 8px;
    }
    .active-badge {
        background: #28a745;
        color: white;
        padding: 4px 10px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: bold;
        margin-left: 8px;
    }
</style>
""", unsafe_allow_html=True)


def is_inactive(last_activity_date) -> bool:
    """Check if account is inactive (>6 months since last activity)."""
    if pd.isna(last_activity_date) or last_activity_date is None:
        return False

    try:
        if isinstance(last_activity_date, datetime):
            last_dt = last_activity_date
        elif isinstance(last_activity_date, str):
            last_dt = datetime.fromisoformat(last_activity_date.replace("Z", "+00:00"))
        else:
            last_dt = pd.to_datetime(last_activity_date)

        # Make both datetimes naive for comparison
        if last_dt.tzinfo is not None:
            last_dt = last_dt.replace(tzinfo=None)

        threshold = datetime.now() - timedelta(days=INACTIVE_THRESHOLD_DAYS)
        return last_dt < threshold
    except Exception:
        return False


def get_inactive_months(last_activity_date) -> int | None:
    """Calculate months of inactivity."""
    if pd.isna(last_activity_date) or last_activity_date is None:
        return None

    try:
        if isinstance(last_activity_date, datetime):
            last_dt = last_activity_date
        elif isinstance(last_activity_date, str):
            last_dt = datetime.fromisoformat(last_activity_date.replace("Z", "+00:00"))
        else:
            last_dt = pd.to_datetime(last_activity_date)

        if last_dt.tzinfo is not None:
            last_dt = last_dt.replace(tzinfo=None)

        days = (datetime.now() - last_dt).days
        return max(1, days // 30)
    except Exception:
        return None


def parse_excel(uploaded_file) -> pd.DataFrame:
    """Parse uploaded Excel file."""
    return pd.read_excel(BytesIO(uploaded_file.read()))


def get_account_data(df: pd.DataFrame, account_id: str) -> dict:
    """Extract data for a specific account."""
    row = df[df["account_id"] == account_id].iloc[0]
    last_activity = row.get("last_activity_date")
    return {
        "account_id": row["account_id"],
        "current_balance": float(row["current_balance"]) if pd.notna(row["current_balance"]) else 0,
        "tickers": row["tickers"] if pd.notna(row.get("tickers")) else None,
        "last_activity_date": str(last_activity) if pd.notna(last_activity) else None,
        "is_inactive": is_inactive(last_activity),
        "inactive_months": get_inactive_months(last_activity)
    }


def call_generate_api(account_id: str, tickers: list[str]) -> dict:
    """Call /generate endpoint for users with holdings."""
    response = requests.post(
        f"{API_BASE_URL}/generate",
        json={"account_id": account_id, "tickers": tickers},
        timeout=60
    )
    response.raise_for_status()
    return response.json()


def call_zero_balance_api(account_id: str, last_activity_date: str | None) -> dict:
    """Call /zero_balance_suggestion endpoint."""
    response = requests.post(
        f"{API_BASE_URL}/zero_balance_suggestion",
        json={"account_id": account_id, "last_activity_date": last_activity_date},
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def display_insight(data: dict):
    """Display personalized insight in a nice format."""
    st.markdown("### Your Personalized Insight")

    # Headline card
    st.markdown(f"""
    <div class="insight-card">
        <h3 style="margin:0; color:white;">📈 {data['headline']}</h3>
    </div>
    """, unsafe_allow_html=True)

    # Explanation
    st.markdown("#### What's Happening")
    st.info(data['explanation'])

    # Personal relevance
    st.markdown("#### Why This Matters to You")
    st.success(data['personal_relevance'])


def display_zero_balance_suggestions(data: dict):
    """Display suggestions for zero-balance users."""
    st.markdown("### Welcome Back!")
    st.markdown(f"*{data['message']}*")

    st.markdown("---")
    st.markdown("#### Top Performing Stocks")

    for suggestion in data['suggestions']:
        change = suggestion.get('change', '')
        change_class = "change-positive" if '+' in change else "change-negative"

        st.markdown(f"""
        <div class="suggestion-card">
            <span class="ticker-badge">{suggestion['symbol']}</span>
            <strong>{suggestion['name']}</strong>
            <span class="{change_class}" style="float:right;">{change}</span>
            <br><small style="color:#666;">{suggestion['note']}</small>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    st.info("💡 If you'd like, we can add these to a watchlist or send you a short market note to help you reach your goals.")


# --- Main App ---
st.title("📊 Financial Insights")
st.markdown("Upload your account data to get personalized financial insights.")

# File upload
uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx", "xls"])

if uploaded_file:
    try:
        df = parse_excel(uploaded_file)

        # Filter valid accounts
        valid_accounts = df[df["account_id"].notna()]["account_id"].tolist()

        if not valid_accounts:
            st.error("No valid accounts found in the file.")
        else:
            st.success(f"Found {len(valid_accounts)} accounts")

            # Build account display with inactive flag
            def format_account_option(account_id):
                row = df[df["account_id"] == account_id].iloc[0]
                last_activity = row.get("last_activity_date")
                if is_inactive(last_activity):
                    return f"{account_id} [INACTIVE]"
                return account_id

            # Account selector
            selected_account = st.selectbox(
                "Select Account ID",
                options=valid_accounts,
                format_func=format_account_option
            )

            if selected_account:
                account_data = get_account_data(df, selected_account)

                # Display inactive warning if applicable
                if account_data['is_inactive']:
                    months = account_data['inactive_months']
                    month_label = "months" if months > 1 else "month"
                    st.markdown(f"""
                    <div style="background: #fff3cd; border: 1px solid #ffc107; border-radius: 8px; padding: 12px; margin-bottom: 15px;">
                        <span class="inactive-badge">INACTIVE</span>
                        <strong style="margin-left: 8px;">This account has been inactive for ~{months} {month_label}</strong>
                        <br><small style="color: #856404; margin-left: 58px;">Last activity: {account_data['last_activity_date']}</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: #d4edda; border: 1px solid #28a745; border-radius: 8px; padding: 12px; margin-bottom: 15px;">
                        <span class="active-badge">ACTIVE</span>
                        <strong style="margin-left: 8px;">This account is active</strong>
                    </div>
                    """, unsafe_allow_html=True)

                # Display account info
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Current Balance", f"${account_data['current_balance']:,.2f}")
                with col2:
                    tickers_display = account_data['tickers'] if account_data['tickers'] else "None"
                    st.metric("Holdings", tickers_display)

                st.markdown("---")

                # Generate insights button
                if st.button("Generate Insights", type="primary", use_container_width=True):
                    with st.spinner("Generating insights..."):
                        try:
                            if account_data['current_balance'] == 0:
                                # Zero balance - use static suggestions
                                result = call_zero_balance_api(
                                    account_data['account_id'],
                                    account_data['last_activity_date']
                                )
                                display_zero_balance_suggestions(result)
                            else:
                                # Has balance - generate personalized insight
                                if not account_data['tickers']:
                                    st.warning("This account has a balance but no ticker holdings recorded.")
                                else:
                                    tickers = [t.strip() for t in account_data['tickers'].split(',')]
                                    result = call_generate_api(account_data['account_id'], tickers)
                                    display_insight(result)
                        except requests.exceptions.ConnectionError:
                            st.error("Cannot connect to API. Make sure the FastAPI server is running on port 8000.")
                        except Exception as e:
                            st.error(f"Error: {str(e)}")

    except Exception as e:
        st.error(f"Error reading file: {str(e)}")

# Footer
st.markdown("---")
st.markdown("<small style='color:#888;'>Financial Insights POC | Educational purposes only</small>", unsafe_allow_html=True)
