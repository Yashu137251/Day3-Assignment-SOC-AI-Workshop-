import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path
from datetime import date
import uuid


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Yaswanth Finance",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# PROJECT PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent

DATA_DIR = BASE_DIR / "data"
DATA_FILE = DATA_DIR / "expenses.csv"

CSS_FILE = BASE_DIR / "assets" / "style.css"


# ============================================================
# CONSTANTS
# ============================================================

COLUMNS = [
    "id",
    "date",
    "type",
    "title",
    "category",
    "amount",
    "payment_method",
    "description"
]

EXPENSE_CATEGORIES = [
    "Food",
    "Transport",
    "Shopping",
    "Bills",
    "Entertainment",
    "Education",
    "Health",
    "Travel",
    "Subscriptions",
    "Other"
]

INCOME_CATEGORIES = [
    "Salary",
    "Freelance",
    "Business",
    "Investment",
    "Gift",
    "Other"
]

PAYMENT_METHODS = [
    "Cash",
    "UPI",
    "Debit Card",
    "Credit Card",
    "Bank Transfer",
    "Other"
]


# ============================================================
# LOAD CUSTOM CSS
# ============================================================

if CSS_FILE.exists():

    with open(
        CSS_FILE,
        "r",
        encoding="utf-8"
    ) as css_file:

        st.html(
            f"<style>{css_file.read()}</style>"
        )


# ============================================================
# HTML HELPER
# ============================================================

def render_html(html_content):
    """
    Render custom HTML using Streamlit's native HTML renderer.
    This prevents HTML from appearing as code blocks.
    """

    st.html(html_content)


# ============================================================
# DATA FILE SETUP
# ============================================================

def ensure_data_file():

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    if not DATA_FILE.exists():

        empty_df = pd.DataFrame(
            columns=COLUMNS
        )

        empty_df.to_csv(
            DATA_FILE,
            index=False
        )


# ============================================================
# LOAD DATA
# ============================================================

def load_data():

    ensure_data_file()

    try:

        df = pd.read_csv(
            DATA_FILE
        )

        if df.empty:

            return pd.DataFrame(
                columns=COLUMNS
            )

        for column in COLUMNS:

            if column not in df.columns:

                df[column] = ""

        df = df[COLUMNS]

        df["amount"] = pd.to_numeric(
            df["amount"],
            errors="coerce"
        ).fillna(0)

        df["date"] = pd.to_datetime(
            df["date"],
            errors="coerce"
        )

        df["type"] = df["type"].replace(
            "",
            "Expense"
        )

        df["title"] = df["title"].fillna("")

        df["category"] = df["category"].fillna("Other")

        df["payment_method"] = (
            df["payment_method"]
            .fillna("Other")
        )

        df["description"] = (
            df["description"]
            .fillna("")
        )

        return df

    except Exception:

        return pd.DataFrame(
            columns=COLUMNS
        )


# ============================================================
# SAVE DATA
# ============================================================

def save_data(df):

    save_df = df.copy()

    if not save_df.empty:

        save_df["date"] = pd.to_datetime(
            save_df["date"],
            errors="coerce"
        ).dt.strftime(
            "%Y-%m-%d"
        )

    save_df.to_csv(
        DATA_FILE,
        index=False
    )


# ============================================================
# SESSION STATE
# ============================================================

if "transactions" not in st.session_state:

    st.session_state.transactions = load_data()


if "page" not in st.session_state:

    st.session_state.page = "Dashboard"


if "edit_id" not in st.session_state:

    st.session_state.edit_id = None


if "budget" not in st.session_state:

    st.session_state.budget = 20000.0


if "currency" not in st.session_state:

    st.session_state.currency = "₹"


if "notifications" not in st.session_state:

    st.session_state.notifications = True


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def money(value):

    return (
        f"{st.session_state.currency}"
        f"{float(value):,.2f}"
    )


def get_totals(df):

    if df.empty:

        return 0.0, 0.0, 0.0

    income = df.loc[
        df["type"] == "Income",
        "amount"
    ].sum()

    expenses = df.loc[
        df["type"] == "Expense",
        "amount"
    ].sum()

    savings = income - expenses

    return (
        income,
        expenses,
        savings
    )


def validate_transaction(
    title,
    amount,
    transaction_type
):

    if not title.strip():

        return (
            False,
            "Please enter a transaction title."
        )

    if len(title.strip()) > 100:

        return (
            False,
            "Transaction title must be under 100 characters."
        )

    if amount <= 0:

        return (
            False,
            "Amount must be greater than ₹0."
        )

    if transaction_type not in [
        "Income",
        "Expense"
    ]:

        return (
            False,
            "Invalid transaction type."
        )

    return True, ""


# ============================================================
# CREATE TRANSACTION
# ============================================================

def add_transaction(
    transaction_date,
    transaction_type,
    title,
    category,
    amount,
    payment_method,
    description
):

    new_record = {

        "id": str(
            uuid.uuid4()
        ),

        "date": pd.Timestamp(
            transaction_date
        ),

        "type": transaction_type,

        "title": title.strip(),

        "category": category,

        "amount": float(amount),

        "payment_method": payment_method,

        "description": description.strip()
    }

    st.session_state.transactions = pd.concat(
        [
            st.session_state.transactions,
            pd.DataFrame(
                [new_record]
            )
        ],
        ignore_index=True
    )

    save_data(
        st.session_state.transactions
    )


# ============================================================
# UPDATE TRANSACTION
# ============================================================

def update_transaction(
    transaction_id,
    transaction_date,
    transaction_type,
    title,
    category,
    amount,
    payment_method,
    description
):

    mask = (
        st.session_state.transactions["id"]
        == transaction_id
    )

    st.session_state.transactions.loc[
        mask,
        "date"
    ] = pd.Timestamp(
        transaction_date
    )

    st.session_state.transactions.loc[
        mask,
        "type"
    ] = transaction_type

    st.session_state.transactions.loc[
        mask,
        "title"
    ] = title.strip()

    st.session_state.transactions.loc[
        mask,
        "category"
    ] = category

    st.session_state.transactions.loc[
        mask,
        "amount"
    ] = float(amount)

    st.session_state.transactions.loc[
        mask,
        "payment_method"
    ] = payment_method

    st.session_state.transactions.loc[
        mask,
        "description"
    ] = description.strip()

    save_data(
        st.session_state.transactions
    )


# ============================================================
# DELETE TRANSACTION
# ============================================================

def delete_transaction(transaction_id):

    st.session_state.transactions = (
        st.session_state.transactions[
            st.session_state.transactions["id"]
            != transaction_id
        ]
        .reset_index(drop=True)
    )

    save_data(
        st.session_state.transactions
    )


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    # --------------------------------------------------------
    # BRAND
    # --------------------------------------------------------

    render_html(
        """
        <div class="sidebar-brand">
            <span class="brand-icon">💰</span>
            <span>Yaswanth Finance</span>
        </div>

        <div class="sidebar-caption">
            Personal Finance Management
        </div>
        """
    )

    st.divider()

    # --------------------------------------------------------
    # NAVIGATION
    # --------------------------------------------------------

    render_html(
        """
        <div class="nav-section-title">
            MAIN MENU
        </div>
        """
    )

    navigation = [
        ("⌂", "Dashboard"),
        ("▤", "Transactions"),
        ("＋", "Add Transaction"),
        ("◈", "Budget Management"),
        ("◒", "Analytics"),
        ("⇩", "Export Data"),
        ("⚙", "Settings")
    ]

    navigation_labels = [
        f"{icon}  {name}"
        for icon, name in navigation
    ]

    current_label = next(
        (
            f"{icon}  {name}"
            for icon, name in navigation
            if name == st.session_state.page
        ),
        navigation_labels[0]
    )

    selected_navigation = st.radio(
        "Main Navigation",
        navigation_labels,
        index=navigation_labels.index(
            current_label
        ),
        label_visibility="collapsed",
        key="main_navigation"
    )

    selected_page = navigation[
        navigation_labels.index(
            selected_navigation
        )
    ][1]

    st.session_state.page = selected_page

    st.divider()

    # --------------------------------------------------------
    # QUICK OVERVIEW
    # --------------------------------------------------------

    sidebar_df = st.session_state.transactions

    sidebar_income, sidebar_expenses, sidebar_savings = (
        get_totals(
            sidebar_df
        )
    )

    render_html(
        f"""
        <div class="quick-overview">

            <div class="quick-overview-title">
                💡 Quick Overview
            </div>

            <div class="quick-stat">
                <span class="quick-stat-label">
                    Current Balance
                </span>

                <span class="quick-stat-value">
                    {money(sidebar_savings)}
                </span>
            </div>

            <div class="quick-stat">
                <span class="quick-stat-label">
                    Transactions
                </span>

                <span class="quick-stat-value">
                    {len(sidebar_df)}
                </span>
            </div>

        </div>
        """
    )

    st.divider()

    # --------------------------------------------------------
    # BUDGET NOTIFICATION
    # --------------------------------------------------------

    if st.session_state.notifications:

        current_time = pd.Timestamp.today()

        if not sidebar_df.empty:

            month_df = sidebar_df[
                (
                    sidebar_df["date"].dt.month
                    == current_time.month
                )
                &
                (
                    sidebar_df["date"].dt.year
                    == current_time.year
                )
            ]

            current_expenses = month_df.loc[
                month_df["type"] == "Expense",
                "amount"
            ].sum()

            if current_expenses > st.session_state.budget:

                st.warning(
                    "⚠️ Monthly budget exceeded."
                )

            elif (
                current_expenses
                >= st.session_state.budget * 0.8
            ):

                st.warning(
                    "⚠️ You are approaching your budget."
                )

    # --------------------------------------------------------
    # REFRESH
    # --------------------------------------------------------

    if st.button(
        "↻  Refresh Data",
        use_container_width=True
    ):

        st.session_state.transactions = load_data()

        st.rerun()


# ============================================================
# DASHBOARD
# ============================================================

if st.session_state.page == "Dashboard":

    render_html(
        """
        <div class="main-title">
            💰 Yaswanth Finance Dashboard
        </div>

        <div class="subtitle">
            A professional overview of your personal finances.
        </div>
        """
    )

    df = st.session_state.transactions.copy()

    income, expenses, savings = get_totals(
        df
    )

    # --------------------------------------------------------
    # CURRENT MONTH
    # --------------------------------------------------------

    today = pd.Timestamp.today()

    if not df.empty:

        month_df = df[
            (
                df["date"].dt.month
                == today.month
            )
            &
            (
                df["date"].dt.year
                == today.year
            )
        ]

        month_income = month_df.loc[
            month_df["type"] == "Income",
            "amount"
        ].sum()

        month_expenses = month_df.loc[
            month_df["type"] == "Expense",
            "amount"
        ].sum()

    else:

        month_income = 0.0

        month_expenses = 0.0

    # --------------------------------------------------------
    # KPI CARDS
    # --------------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    cards = [
        (
            "TOTAL BALANCE",
            savings,
            "balance"
        ),
        (
            "TOTAL INCOME",
            income,
            "income"
        ),
        (
            "TOTAL EXPENSES",
            expenses,
            "expense"
        ),
        (
            "SAVINGS",
            savings,
            "savings"
        )
    ]

    for column, card_data in zip(
        [col1, col2, col3, col4],
        cards
    ):

        title, value, card_type = card_data

        with column:

            render_html(
                f"""
                <div class="kpi-card {card_type}">

                    <div class="kpi-title">
                        {title}
                    </div>

                    <div class="kpi-value">
                        {money(value)}
                    </div>

                </div>
                """
            )

    st.write("")

    # --------------------------------------------------------
    # MONTHLY CARDS
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        render_html(
            f"""
            <div class="glass-card mini-finance-card">

                <span>
                    📅 Current Month Expenses
                </span>

                <strong>
                    {money(month_expenses)}
                </strong>

            </div>
            """
        )

    with col2:

        render_html(
            f"""
            <div class="glass-card mini-finance-card">

                <span>
                    💵 Current Month Income
                </span>

                <strong>
                    {money(month_income)}
                </strong>

            </div>
            """
        )

    # --------------------------------------------------------
    # BUDGET OVERVIEW
    # --------------------------------------------------------

    st.markdown(
        "### 🎯 Budget Overview"
    )

    budget = st.session_state.budget

    budget_percentage = (
        (
            month_expenses
            / budget
        )
        * 100
        if budget > 0
        else 0
    )

    st.progress(
        min(
            budget_percentage / 100,
            1.0
        )
    )

    st.caption(
        f"{money(month_expenses)} used of "
        f"{money(budget)} monthly budget "
        f"({budget_percentage:.1f}%)"
    )

    if budget_percentage >= 100:

        st.error(
            "🚨 You have exceeded your monthly budget."
        )

    elif budget_percentage >= 80:

        st.warning(
            "⚠️ You are approaching your monthly budget."
        )

    else:

        st.success(
            "✅ You are currently within your budget."
        )

    # --------------------------------------------------------
    # RECENT TRANSACTIONS
    # --------------------------------------------------------

    st.markdown(
        "### 🧾 Recent Transactions"
    )

    if df.empty:

        st.info(
            "No transactions yet. Add your first transaction."
        )

    else:

        recent = (
            df.sort_values(
                "date",
                ascending=False
            )
            .head(6)
            .copy()
        )

        recent_display = recent[
            [
                "date",
                "type",
                "title",
                "category",
                "amount"
            ]
        ].copy()

        recent_display["date"] = (
            recent_display["date"]
            .dt.strftime(
                "%d-%m-%Y"
            )
        )

        recent_display["amount"] = (
            recent_display["amount"]
            .apply(
                money
            )
        )

        st.dataframe(
            recent_display,
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # SAVINGS TREND
    # --------------------------------------------------------

    st.markdown(
        "### 📈 Savings Trend"
    )

    if not df.empty:

        trend = df.copy()

        trend["month"] = (
            trend["date"]
            .dt.to_period("M")
            .astype(str)
        )

        monthly = (
            trend.groupby(
                [
                    "month",
                    "type"
                ]
            )["amount"]
            .sum()
            .reset_index()
        )

        pivot = monthly.pivot(
            index="month",
            columns="type",
            values="amount"
        ).fillna(0)

        if "Income" not in pivot.columns:

            pivot["Income"] = 0

        if "Expense" not in pivot.columns:

            pivot["Expense"] = 0

        pivot["Savings"] = (
            pivot["Income"]
            - pivot["Expense"]
        )

        pivot = pivot.reset_index()

        fig = px.line(
            pivot,
            x="month",
            y="Savings",
            markers=True,
            title="Monthly Savings"
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(
                color="#e2e8f0"
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

    else:

        st.info(
            "Add transactions to display your savings trend."
        )

    # --------------------------------------------------------
    # FINANCIAL INSIGHTS
    # --------------------------------------------------------

    st.markdown(
        "### 🧠 Financial Insights"
    )

    if not df.empty:

        expense_df = df[
            df["type"] == "Expense"
        ]

        if not expense_df.empty:

            category_totals = (
                expense_df
                .groupby(
                    "category"
                )["amount"]
                .sum()
                .sort_values(
                    ascending=False
                )
            )

            top_category = (
                category_totals.index[0]
            )

            top_amount = (
                category_totals.iloc[0]
            )

            render_html(
                f"""
                <div class="insight-card">

                    <div class="insight-icon">
                        💡
                    </div>

                    <div>
                        <div class="insight-title">
                            Highest Spending Category
                        </div>

                        <div class="insight-text">
                            Your highest spending category
                            is <strong>{top_category}</strong>
                            with
                            <strong>{money(top_amount)}</strong>.
                        </div>
                    </div>

                </div>
                """
            )

        if income > 0:

            saving_rate = (
                savings
                / income
            ) * 100

            render_html(
                f"""
                <div class="insight-card">

                    <div class="insight-icon">
                        📊
                    </div>

                    <div>
                        <div class="insight-title">
                            Savings Rate
                        </div>

                        <div class="insight-text">
                            Your overall savings rate is
                            <strong>
                                {saving_rate:.1f}%
                            </strong>.
                        </div>
                    </div>

                </div>
                """
            )

    else:

        st.info(
            "Add transactions to generate financial insights."
        )


# ============================================================
# ADD TRANSACTION
# ============================================================

elif st.session_state.page == "Add Transaction":

    render_html(
        """
        <div class="main-title">
            ➕ Add Transaction
        </div>

        <div class="subtitle">
            Record income or expenses in your finance tracker.
        </div>
        """
    )

    with st.form(
        "transaction_form",
        clear_on_submit=True
    ):

        col1, col2 = st.columns(2)

        with col1:

            transaction_type = st.selectbox(
                "Transaction Type",
                [
                    "Expense",
                    "Income"
                ]
            )

            transaction_date = st.date_input(
                "Transaction Date",
                value=date.today()
            )

            title = st.text_input(
                "Transaction Title",
                placeholder="Example: Monthly Salary"
            )

        with col2:

            amount = st.number_input(
                "Amount (₹)",
                min_value=0.0,
                step=100.0,
                format="%.2f"
            )

            if transaction_type == "Expense":

                category = st.selectbox(
                    "Category",
                    EXPENSE_CATEGORIES
                )

            else:

                category = st.selectbox(
                    "Category",
                    INCOME_CATEGORIES
                )

            payment_method = st.selectbox(
                "Payment Method",
                PAYMENT_METHODS
            )

        description = st.text_area(
            "Description",
            placeholder="Add additional details..."
        )

        submitted = st.form_submit_button(
            "💾 Save Transaction"
        )

        if submitted:

            valid, message = validate_transaction(
                title,
                amount,
                transaction_type
            )

            if not valid:

                st.error(
                    message
                )

            else:

                add_transaction(
                    transaction_date,
                    transaction_type,
                    title,
                    category,
                    amount,
                    payment_method,
                    description
                )

                st.success(
                    "✅ Transaction added successfully!"
                )

                st.rerun()


# ============================================================
# TRANSACTIONS
# ============================================================

elif st.session_state.page == "Transactions":

    render_html(
        """
        <div class="main-title">
            📋 Transaction Management
        </div>

        <div class="subtitle">
            Search, view, update and delete your transactions.
        </div>
        """
    )

    df = st.session_state.transactions.copy()

    if df.empty:

        st.info(
            "No transactions available."
        )

    else:

        col1, col2, col3 = st.columns(3)

        with col1:

            search = st.text_input(
                "🔎 Search",
                placeholder="Search transaction..."
            )

        with col2:

            type_filter = st.selectbox(
                "Transaction Type",
                [
                    "All",
                    "Income",
                    "Expense"
                ]
            )

        with col3:

            category_filter = st.selectbox(
                "Category",
                [
                    "All"
                ]
                +
                sorted(
                    df["category"]
                    .dropna()
                    .unique()
                    .tolist()
                )
            )

        filtered = df.copy()

        if search:

            filtered = filtered[
                filtered["title"]
                .str.contains(
                    search,
                    case=False,
                    na=False
                )
            ]

        if type_filter != "All":

            filtered = filtered[
                filtered["type"]
                == type_filter
            ]

        if category_filter != "All":

            filtered = filtered[
                filtered["category"]
                == category_filter
            ]

        st.markdown(
            "### 📊 Transaction Table"
        )

        display = filtered.copy()

        display["date"] = (
            display["date"]
            .dt.strftime(
                "%d-%m-%Y"
            )
        )

        display["amount"] = (
            display["amount"]
            .apply(
                money
            )
        )

        display = display[
            [
                "date",
                "type",
                "title",
                "category",
                "amount",
                "payment_method",
                "description"
            ]
        ]

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True
        )

        if not filtered.empty:

            st.markdown(
                "### ✏️ Manage Transaction"
            )

            transaction_options = []

            for _, row in filtered.iterrows():

                transaction_options.append(
                    f"{row['title']} | "
                    f"{row['type']} | "
                    f"{money(row['amount'])}"
                )

            selected = st.selectbox(
                "Select Transaction",
                transaction_options
            )

            selected_index = (
                transaction_options.index(
                    selected
                )
            )

            selected_row = filtered.iloc[
                selected_index
            ]

            selected_id = selected_row["id"]

            col1, col2 = st.columns(2)

            with col1:

                if st.button(
                    "✏️ Edit Transaction",
                    use_container_width=True
                ):

                    st.session_state.edit_id = (
                        selected_id
                    )

                    st.rerun()

            with col2:

                if st.button(
                    "🗑️ Delete Transaction",
                    use_container_width=True
                ):

                    delete_transaction(
                        selected_id
                    )

                    st.success(
                        "Transaction deleted successfully."
                    )

                    st.rerun()

        # ----------------------------------------------------
        # EDIT TRANSACTION
        # ----------------------------------------------------

        if st.session_state.edit_id:

            rows = (
                st.session_state.transactions[
                    st.session_state.transactions["id"]
                    == st.session_state.edit_id
                ]
            )

            if not rows.empty:

                row = rows.iloc[0]

                st.divider()

                st.markdown(
                    "### ✏️ Edit Transaction"
                )

                current_type = (
                    row["type"]
                    if row["type"]
                    in [
                        "Income",
                        "Expense"
                    ]
                    else "Expense"
                )

                with st.form(
                    "edit_form"
                ):

                    edit_type = st.selectbox(
                        "Transaction Type",
                        [
                            "Expense",
                            "Income"
                        ],
                        index=[
                            "Expense",
                            "Income"
                        ].index(
                            current_type
                        )
                    )

                    edit_date = st.date_input(
                        "Date",
                        value=pd.to_datetime(
                            row["date"]
                        ).date()
                    )

                    edit_title = st.text_input(
                        "Title",
                        value=str(
                            row["title"]
                        )
                    )

                    category_list = (
                        EXPENSE_CATEGORIES
                        if edit_type
                        == "Expense"
                        else INCOME_CATEGORIES
                    )

                    current_category = (
                        row["category"]
                        if row["category"]
                        in category_list
                        else category_list[-1]
                    )

                    edit_category = st.selectbox(
                        "Category",
                        category_list,
                        index=category_list.index(
                            current_category
                        )
                    )

                    edit_amount = st.number_input(
                        "Amount",
                        min_value=0.0,
                        value=float(
                            row["amount"]
                        ),
                        step=100.0
                    )

                    current_payment = (
                        row["payment_method"]
                        if row["payment_method"]
                        in PAYMENT_METHODS
                        else "Other"
                    )

                    edit_payment = st.selectbox(
                        "Payment Method",
                        PAYMENT_METHODS,
                        index=PAYMENT_METHODS.index(
                            current_payment
                        )
                    )

                    edit_description = st.text_area(
                        "Description",
                        value=str(
                            row["description"]
                        )
                    )

                    save_button = (
                        st.form_submit_button(
                            "💾 Save Changes"
                        )
                    )

                    if save_button:

                        valid, message = (
                            validate_transaction(
                                edit_title,
                                edit_amount,
                                edit_type
                            )
                        )

                        if not valid:

                            st.error(
                                message
                            )

                        else:

                            update_transaction(
                                st.session_state.edit_id,
                                edit_date,
                                edit_type,
                                edit_title,
                                edit_category,
                                edit_amount,
                                edit_payment,
                                edit_description
                            )

                            st.session_state.edit_id = None

                            st.success(
                                "Transaction updated successfully."
                            )

                            st.rerun()


# ============================================================
# BUDGET MANAGEMENT
# ============================================================

elif st.session_state.page == "Budget Management":

    render_html(
        """
        <div class="main-title">
            🎯 Budget Management
        </div>

        <div class="subtitle">
            Set your monthly spending limit and monitor your progress.
        </div>
        """
    )

    new_budget = st.number_input(
        "Monthly Budget",
        min_value=0.0,
        value=float(
            st.session_state.budget
        ),
        step=1000.0
    )

    if st.button(
        "💾 Save Budget",
        use_container_width=True
    ):

        st.session_state.budget = (
            new_budget
        )

        st.success(
            "Monthly budget updated successfully."
        )

    df = st.session_state.transactions

    today = pd.Timestamp.today()

    if not df.empty:

        month_expenses = df[
            (
                df["type"]
                == "Expense"
            )
            &
            (
                df["date"].dt.month
                == today.month
            )
            &
            (
                df["date"].dt.year
                == today.year
            )
        ]["amount"].sum()

    else:

        month_expenses = 0.0

    st.markdown(
        "### 📊 Budget Status"
    )

    percentage = (
        month_expenses
        / new_budget
        * 100
        if new_budget > 0
        else 0
    )

    st.progress(
        min(
            percentage / 100,
            1
        )
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Monthly Budget",
            money(new_budget)
        )

    with col2:

        st.metric(
            "Amount Spent",
            money(month_expenses)
        )

    with col3:

        remaining = (
            new_budget
            - month_expenses
        )

        st.metric(
            "Remaining",
            money(remaining)
        )

    if percentage >= 100:

        st.error(
            "🚨 Monthly budget exceeded."
        )

    elif percentage >= 80:

        st.warning(
            "⚠️ You have used more than 80% of your budget."
        )

    else:

        st.success(
            "✅ Budget is currently under control."
        )


# ============================================================
# ANALYTICS
# ============================================================

elif st.session_state.page == "Analytics":

    render_html(
        """
        <div class="main-title">
            📊 Financial Analytics
        </div>

        <div class="subtitle">
            Interactive visual analysis of your financial activity.
        </div>
        """
    )

    df = st.session_state.transactions.copy()

    if df.empty:

        st.info(
            "Add transactions to see financial analytics."
        )

    else:

        # ----------------------------------------------------
        # MONTHLY INCOME VS EXPENSE
        # ----------------------------------------------------

        monthly = (
            df.assign(
                month=(
                    df["date"]
                    .dt.to_period("M")
                    .astype(str)
                )
            )
            .groupby(
                [
                    "month",
                    "type"
                ]
            )["amount"]
            .sum()
            .reset_index()
        )

        fig = px.bar(
            monthly,
            x="month",
            y="amount",
            color="type",
            barmode="group",
            title="Income vs Expenses"
        )

        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(
                color="#e2e8f0"
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )

        # ----------------------------------------------------
        # EXPENSE ANALYSIS
        # ----------------------------------------------------

        expense_df = df[
            df["type"]
            == "Expense"
        ]

        if not expense_df.empty:

            category_data = (
                expense_df
                .groupby(
                    "category"
                )["amount"]
                .sum()
                .reset_index()
                .sort_values(
                    "amount",
                    ascending=False
                )
            )

            col1, col2 = st.columns(2)

            with col1:

                fig = px.pie(
                    category_data,
                    names="category",
                    values="amount",
                    hole=0.5,
                    title="Expense Distribution"
                )

                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(
                        color="#e2e8f0"
                    )
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

            with col2:

                fig = px.bar(
                    category_data,
                    x="category",
                    y="amount",
                    title="Category Spending"
                )

                fig.update_layout(
                    template="plotly_dark",
                    paper_bgcolor="rgba(0,0,0,0)",
                    plot_bgcolor="rgba(0,0,0,0)",
                    font=dict(
                        color="#e2e8f0"
                    )
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        # ----------------------------------------------------
        # PAYMENT METHOD ANALYSIS
        # ----------------------------------------------------

        payment_data = (
            expense_df
            .groupby(
                "payment_method"
            )["amount"]
            .sum()
            .reset_index()
        )

        if not payment_data.empty:

            fig = px.bar(
                payment_data,
                x="payment_method",
                y="amount",
                title="Spending by Payment Method"
            )

            fig.update_layout(
                template="plotly_dark",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(
                    color="#e2e8f0"
                )
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


# ============================================================
# EXPORT DATA
# ============================================================

elif st.session_state.page == "Export Data":

    render_html(
        """
        <div class="main-title">
            📥 Export Data Management
        </div>

        <div class="subtitle">
            Download your financial records for backup and reporting.
        </div>
        """
    )

    df = st.session_state.transactions.copy()

    if df.empty:

        st.info(
            "There is no financial data available to export."
        )

    else:

        export_df = df.copy()

        export_df["date"] = (
            export_df["date"]
            .dt.strftime(
                "%Y-%m-%d"
            )
        )

        csv_data = (
            export_df
            .to_csv(
                index=False
            )
            .encode("utf-8")
        )

        st.download_button(
            "📥 Download Complete CSV",
            data=csv_data,
            file_name="yaswanth_financial_data.csv",
            mime="text/csv",
            use_container_width=True
        )

        st.markdown(
            "### 📊 Export Summary"
        )

        income, expenses, savings = (
            get_totals(
                df
            )
        )

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Total Income",
                money(income)
            )

        with col2:

            st.metric(
                "Total Expenses",
                money(expenses)
            )

        with col3:

            st.metric(
                "Total Savings",
                money(savings)
            )

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )


# ============================================================
# SETTINGS
# ============================================================

elif st.session_state.page == "Settings":

    render_html(
        """
        <div class="main-title">
            ⚙️ Settings
        </div>

        <div class="subtitle">
            Configure your personal finance dashboard.
        </div>
        """
    )

    # --------------------------------------------------------
    # CURRENCY
    # --------------------------------------------------------

    st.markdown(
        "### 💱 Currency"
    )

    currency_options = [
        "₹",
        "$",
        "€",
        "£"
    ]

    selected_currency = st.selectbox(
        "Currency Symbol",
        currency_options,
        index=currency_options.index(
            st.session_state.currency
        )
    )

    if st.button(
        "💾 Save Currency",
        use_container_width=True
    ):

        st.session_state.currency = (
            selected_currency
        )

        st.success(
            "Currency setting updated."
        )

        st.rerun()

    st.divider()

    # --------------------------------------------------------
    # NOTIFICATIONS
    # --------------------------------------------------------

    st.markdown(
        "### 🔔 Notifications"
    )

    notifications = st.toggle(
        "Enable budget notifications",
        value=st.session_state.notifications
    )

    st.session_state.notifications = (
        notifications
    )

    if notifications:

        st.success(
            "Budget notifications are enabled."
        )

    else:

        st.info(
            "Budget notifications are disabled."
        )

    st.divider()

    # --------------------------------------------------------
    # SECURITY
    # --------------------------------------------------------

    st.markdown(
        "### 🔐 Security & Validation"
    )

    st.info(
        "Your financial data is stored locally in "
        "data/expenses.csv. Avoid storing highly sensitive "
        "credentials or banking information in this application."
    )

    render_html(
        """
        <div class="security-card">

            <div class="security-item">
                <span>✓</span>
                Required transaction validation
            </div>

            <div class="security-item">
                <span>✓</span>
                Positive amount validation
            </div>

            <div class="security-item">
                <span>✓</span>
                Transaction type validation
            </div>

            <div class="security-item">
                <span>✓</span>
                Safe CSV storage
            </div>

            <div class="security-item">
                <span>✓</span>
                Local data management
            </div>

        </div>
        """
    )

    st.divider()

    # --------------------------------------------------------
    # DATA MANAGEMENT
    # --------------------------------------------------------

    st.markdown(
        "### ⚠️ Data Management"
    )

    confirm_delete = st.checkbox(
        "I understand that deleting all data cannot be undone."
    )

    if st.button(
        "🗑️ Delete All Financial Data",
        use_container_width=True
    ):

        if confirm_delete:

            st.session_state.transactions = (
                pd.DataFrame(
                    columns=COLUMNS
                )
            )

            save_data(
                st.session_state.transactions
            )

            st.session_state.edit_id = None

            st.success(
                "All financial data has been deleted."
            )

            st.rerun()

        else:

            st.warning(
                "Please confirm the deletion first."
            )


# ============================================================
# PROFESSIONAL FOOTER
# ============================================================

render_html(
    """
    <div class="footer">

        <div class="footer-brand">
            💰 Yaswanth Finance
        </div>

        <div class="footer-description">
            Professional Personal Finance Management
        </div>

        <div class="footer-line"></div>

        <div class="footer-tech">
            Built with Python • Streamlit • Pandas • Plotly
        </div>

    </div>
    """
)