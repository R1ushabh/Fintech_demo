import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import random

# Configure page
st.set_page_config(
    page_title="ArthGuru - Financial Coach",
    page_icon="🧘",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header { font-size: 3rem; font-weight: 700; color: #1f1f1f; text-align: center; margin-bottom: 1rem; }
    .sub-header { font-size: 1.2rem; color: #666; text-align: center; margin-bottom: 2rem; }
    .insight-box { background-color: #fff3cd; border: 1px solid #ffc107; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; color: #856404; }
    .warning-box { background-color: #f8d7da; border: 1px solid #f5c6cb; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; color: #721c24; }
    .success-box { background-color: #d4edda; border: 1px solid #c3e6cb; padding: 1rem; border-radius: 8px; margin: 0.5rem 0; color: #155724; }
</style>
""", unsafe_allow_html=True)

# ================== UTILITY FUNCTIONS ==================
def generate_suggested_questions(analysis):
    questions = ["Summarize my financial health.", "What is my top priority?"]
    top_expense = analysis['expense_by_category'].idxmax()
    questions.append(f"How can I reduce my spending on {top_expense}?")
    if analysis['savings_rate'] < 15:
        questions.append("Give me 3 ways to improve my savings rate.")
    return random.sample(questions, min(len(questions), 4))

def create_visualizations(data, analysis):
    data['date'] = pd.to_datetime(data['date'])
    monthly_data = data.groupby(data['date'].dt.to_period('M')).agg({
        'income': 'sum',
        'spending': 'sum'
    }).reset_index()
    monthly_data['date'] = monthly_data['date'].astype(str)
    fig1 = go.Figure()
    fig1.add_trace(go.Bar(x=monthly_data['date'], y=monthly_data['income'], name='Income', marker_color='#667eea'))
    fig1.add_trace(go.Bar(x=monthly_data['date'], y=monthly_data['spending'], name='Expenses', marker_color='#f093fb'))
    fig1.update_layout(title='Monthly Income vs Expenses', barmode='group', height=400)
    expense_data = analysis['expense_by_category']
    fig2 = px.pie(values=expense_data.values, names=expense_data.index, title='Expense Breakdown by Category', height=400)
    return fig1, fig2

def load_sample_data():
    dates = pd.date_range(start='2025-04-01', end='2025-09-30', freq='D')
    data = []
    for month in range(4, 10):
        income_date = f"2025-{month:02d}-01"
        income = random.uniform(40000, 50000)
        data.append({'date': income_date, 'income': income, 'spending': 0, 'category': 'Salary'})
    expense_categories = {
        'Food': (150, 600, 0.8), 'Housing': (800, 1500, 0.3), 'Transportation': (50, 300, 0.4),
        'Entertainment': (200, 1200, 0.3), 'Bills': (500, 2500, 0.2), 'Healthcare': (300, 1500, 0.1),
        'Clothing': (800, 3000, 0.05), 'Misc': (100, 800, 0.2)
    }
    for date in dates:
        for category, (min_val, max_val, freq) in expense_categories.items():
            if random.random() < freq:
                expense = random.uniform(min_val, max_val)
                data.append({'date': date.strftime('%Y-%m-%d'), 'income': 0, 'spending': expense, 'category': category})
    return pd.DataFrame(data)

# ================== SIMULATED AGENT CLASSES ==================
class FinancialAnalyzerAgent:
    def analyze(self, data):
        data['date'] = pd.to_datetime(data['date'])
        total_income = data['income'].sum()
        total_expenses = data['spending'].sum()
        net_savings = total_income - total_expenses
        savings_rate = (net_savings / total_income * 100) if total_income > 0 else 0
        monthly_income = data[data['income'] > 0].groupby(data['date'].dt.to_period('M'))['income'].sum()
        income_std = monthly_income.std()
        income_mean = monthly_income.mean()
        expense_by_category = data[data['spending'] > 0].groupby('category')['spending'].sum()
        return {
            'total_income': total_income, 'total_expenses': total_expenses, 'net_savings': net_savings,
            'savings_rate': savings_rate, 'avg_monthly_income': income_mean,
            'expense_by_category': expense_by_category
        }

class FinancialPlannerAgent:
    def __init__(self, analysis_results):
        self.analysis = analysis_results
    def create_plan(self):
        analysis_results = self.analysis
        recommendations = []
        goals = []
        if analysis_results['savings_rate'] < 10:
            recommendations.append({
                'type': 'critical', 'title': 'Low Savings Rate Detected',
                'message': f"Your savings rate is {analysis_results['savings_rate']:.1f}%. Target at least 15-20% for financial stability."
            })
            goals.append("Increase savings rate to 15% within 3 months")
        else:
             recommendations.append({
                'type': 'success', 'title': 'Excellent Savings Rate',
                'message': f"Great job! Your {analysis_results['savings_rate']:.1f}% savings rate is above average."
            })
        top_expense_cat = analysis_results['expense_by_category'].idxmax()
        if (analysis_results['expense_by_category'][top_expense_cat] / analysis_results['total_income'] * 100) > 15:
             recommendations.append({
                'type': 'warning', 'title': f'High {top_expense_cat} Spending',
                'message': f"{top_expense_cat} spending is {(analysis_results['expense_by_category'][top_expense_cat] / analysis_results['total_income'] * 100):.1f}% of income. Consider reducing to 10%."
            })
             goals.append(f"Reduce {top_expense_cat} spending by 30%")
        return {'recommendations': recommendations, 'goals': goals}

class FinancialAdvisorAgent:
    def __init__(self, analysis, plan):
        self.analysis = analysis
        self.plan = plan
    def generate_advice(self, query):
        query_lower = query.lower()
        if 'summarize' in query_lower or 'health' in query_lower:
            return f"Your overall financial health is fair. You have a savings rate of {self.analysis['savings_rate']:.1f}% and a net savings of ₹{self.analysis['net_savings']:,.0f}. Your main challenge is a low savings rate, but you have a stable income. Focusing on reducing non-essential spending will significantly improve your financial standing."
        if 'savings' in query_lower or 'save' in query_lower:
            return f"Based on your current financial data, you're saving {self.analysis['savings_rate']:.1f}% of your income. The recommended savings rate is 15-20%. I suggest setting up automatic transfers to a savings account right after you receive income."
        elif 'spending' in query_lower or 'expenses' in query_lower:
            top_expense = self.analysis['expense_by_category'].idxmax()
            top_amount = self.analysis['expense_by_category'].max()
            return f"Your highest expense category is {top_expense} at ₹{top_amount:,.0f}. I recommend reviewing this category for potential savings."
        else:
            return "I can answer questions about savings, spending, and your financial plan. What would you like to know?"

# ================== MAIN APP ==================
def main():
    st.markdown('<div class="main-header">🧘 ArthGuru: Financial Coach</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">AI-Powered Agentic System for Financial Health Management</div>', unsafe_allow_html=True)

    with st.sidebar:
        st.header("📊 Data Source")
        data_option = st.radio("Choose data source:", ["Use Sample Data", "Upload CSV"])
        if data_option == "Upload CSV":
            uploaded_file = st.file_uploader("Upload your financial CSV", type=['csv'])
            if uploaded_file:
                st.session_state.financial_data = pd.read_csv(uploaded_file)
                for key in ['step', 'analysis', 'plan', 'advisor', 'chat_history', 'suggested_questions']:
                    if key in st.session_state: del st.session_state[key]
        else:
            if st.button("Load Sample Data"):
                st.session_state.financial_data = load_sample_data()
                for key in ['step', 'analysis', 'plan', 'advisor', 'chat_history', 'suggested_questions']:
                    if key in st.session_state: del st.session_state[key]

    if st.session_state.get('financial_data') is not None:
        data = st.session_state.financial_data
        required_columns = {'date', 'income', 'spending', 'category'}
        if not required_columns.issubset(data.columns):
            st.error(f"Your data is missing required columns: {list(required_columns - set(data.columns))}. Please fix the file and try again.")
            return

        if 'step' not in st.session_state:
            st.session_state.step = 0

        st.markdown("### 🤖 Agentic Workflow Demo")
        agent_expander = st.expander("Follow the AI agents as they collaborate", expanded=True)
        with agent_expander:
            if st.session_state.step == 0:
                st.info("Agents are idle. Click below to start the financial analysis.")
                if st.button("▶️ Start Analysis"):
                    st.session_state.step = 1
                    st.rerun()
            if st.session_state.step >= 1:
                st.markdown("**1. 🕵️‍♂️ Analyzer Agent: Active**")
                if 'analysis' not in st.session_state:
                    with st.spinner("Processing financial data..."):
                        analyzer = FinancialAnalyzerAgent()
                        st.session_state.analysis = analyzer.analyze(data)
                        time.sleep(1.5)
                analysis = st.session_state.analysis
                st.success("Analysis Complete!")
                st.write({k: (f"{v:.1f}%" if 'rate' in k else f"₹{v:,.0f}") for k, v in analysis.items() if k not in ['expense_by_category', 'avg_monthly_income']})
            if st.session_state.step == 1:
                if st.button("🤝 Send to Planner Agent"):
                    st.session_state.step = 2
                    st.rerun()
            if st.session_state.step >= 2:
                st.markdown("**2. 📝 Planner Agent: Active**")
                if 'plan' not in st.session_state:
                    with st.spinner("Generating recommendations and goals..."):
                        planner = FinancialPlannerAgent(st.session_state.analysis)
                        st.session_state.plan = planner.create_plan()
                        time.sleep(1.5)
                plan = st.session_state.plan
                st.success("Planning Complete!")
                st.write("**Generated Goals:**")
                for goal in plan['goals']:
                    st.markdown(f"- {goal}")
                st.write("**Detailed Recommendations:**")
                for rec in plan['recommendations']:
                    st.markdown(f"- **{rec['title']}**: {rec['message']}")
            if st.session_state.step == 2:
                if st.button("🗣️ Activate Advisor Agent"):
                    st.session_state.step = 3
                    st.rerun()
            if st.session_state.step >= 3:
                st.markdown("**3. 👨‍🏫 Advisor Agent: Ready**")
                if 'advisor' not in st.session_state:
                    st.session_state.advisor = FinancialAdvisorAgent(st.session_state.analysis, st.session_state.plan)
                st.success("Advisor is now online and ready to chat.")

        if st.session_state.step == 3:
            analysis = st.session_state.analysis
            plan = st.session_state.plan
            advisor = st.session_state.advisor
            st.markdown("---_## ✅ Final Report_---")
            st.markdown("### 📈 Recommendations & Goals")
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("**AI-Generated Recommendations**")
                for rec in plan['recommendations']:
                    if rec['type'] == 'critical':
                        st.markdown(f'<div class="warning-box"><b>⚠️ {rec["title"]}</b><br>{rec["message"]}</div>', unsafe_allow_html=True)
                    else:
                        st.markdown(f'<div class="insight-box"><b>💡 {rec["title"]}</b><br>{rec["message"]}</div>', unsafe_allow_html=True)
            with col2:
                st.markdown("**Your Financial Goals**")
                for i, goal in enumerate(plan['goals'], 1):
                    st.markdown(f"{i}. {goal}")

            st.markdown("### 📊 Visualizations")
            fig1, fig2 = create_visualizations(data, analysis)
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(fig1, use_container_width=True)
            with col2:
                st.plotly_chart(fig2, use_container_width=True)

            st.markdown("### 💬 Chat with Your Financial Coach")
            if 'chat_history' not in st.session_state:
                st.session_state.chat_history = []
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
            
            if 'suggested_questions' not in st.session_state:
                st.session_state.suggested_questions = generate_suggested_questions(analysis)
            
            if st.session_state.get('suggested_questions'):
                st.markdown("**Here are some questions you could ask:**")
                cols = st.columns(len(st.session_state.suggested_questions))
                for i, question in enumerate(st.session_state.suggested_questions):
                    with cols[i]:
                        if st.button(question, key=f"suggestion_{i}"):
                            st.session_state.chat_history.append({"role": "user", "content": question})
                            if 'suggested_questions' in st.session_state:
                                del st.session_state.suggested_questions
                            st.rerun()

            if prompt := st.chat_input("Ask about savings, spending, budget, or investments..."):
                if 'suggested_questions' in st.session_state:
                    del st.session_state.suggested_questions
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                st.rerun()

            if st.session_state.chat_history and st.session_state.chat_history[-1]["role"] == "user":
                user_question = st.session_state.chat_history[-1]["content"]
                with st.chat_message("assistant"):
                    response = advisor.generate_advice(user_question)
                    st.markdown(response)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})

    else:
        st.info("👈 Please upload your financial CSV or load sample data to begin analysis.")

if __name__ == "__main__":
    main()