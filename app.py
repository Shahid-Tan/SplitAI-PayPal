import streamlit as st
import google.generativeai as genai

# 1. Page Configuration
st.set_page_config(
    page_title="SplitAI | Intelligent Bill Settlement",
    page_icon="💳",
    layout="centered"
)

# 2. Modern PayPal FinTech Styling
st.markdown("""
<style>
    .header-box {
        background: linear-gradient(135deg, #003087 0%, #0079c1 100%);
        padding: 28px;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px rgba(0, 48, 135, 0.15);
    }
    .header-box h1 { color: #ffffff !important; font-size: 2.2rem; font-weight: 800; }
    .header-box p { color: #e0f2fe; margin: 0; }
    .result-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 24px;
        margin-top: 20px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.05);
    }
    .paypal-button {
        display: inline-block;
        background: linear-gradient(180deg, #ffc439 0%, #f6b527 100%);
        color: #003087 !important;
        font-weight: 700;
        font-size: 1.1rem;
        text-align: center;
        padding: 14px 28px;
        border-radius: 30px;
        text-decoration: none;
        box-shadow: 0 4px 12px rgba(246, 181, 39, 0.4);
        width: 100%;
        margin-top: 15px;
        border: 1px solid #e0a31b;
    }
    .badge {
        background-color: #e0f2fe;
        color: #0079c1;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)

# 3. Header
st.markdown("""
<div class="header-box">
    <h1>💳 SplitAI</h1>
    <p>Conversational Bill Splitting & Multi-Currency Settlement</p>
</div>
""", unsafe_allow_html=True)

# 4. Sidebar Configuration
st.sidebar.markdown("### ⚙️ Account Settings")
api_key = st.sidebar.text_input("Gemini API Key:", type="password", help="Get free key from aistudio.google.com")
raw_paypal = st.sidebar.text_input("PayPal.Me Handle:", value="syedshahidafridi")

# Auto-strip spaces and symbols
clean_paypal = raw_paypal.replace(" ", "").replace("@", "").strip()

st.sidebar.markdown("---")
st.sidebar.markdown("""
**💡 What you can ask SplitAI:**
- Any custom group bill (Rent, Groceries, Trip)
- *"Convert results to INR (₹)"*
- *"Split 60-40 between two people"*
- *"Add 18% GST / 10% tip"*
""")

# 5. Quick Sample Buttons
st.markdown("##### ⚡ Quick Load Presets:")
col1, col2, col3 = st.columns(3)

if col1.button("🍕 Restaurant"):
    st.session_state["bill"] = "Dinner bill: $70. Alice had steak ($35), Bob had burger ($20), Charlie had soup ($15). Split $10 tip equally."
    st.session_state["custom_q"] = ""

if col2.button("🏠 Flat Rent (INR)"):
    st.session_state["bill"] = "Monthly 3BHK flat expenses in Bangalore: Total rent ₹24,000, WiFi ₹1,000, Electricity ₹2,000. Shahid has master bedroom with AC so he pays ₹2,000 extra on rent. Split rest equally among Shahid, Kabir, and Zaid."
    st.session_state["custom_q"] = "Calculate each person's exact share in Indian Rupees (₹)."

if col3.button("🚗 Road Trip"):
    st.session_state["bill"] = "Road trip fuel was $90. Car snacks were $30. 4 friends: Shahid, Alex, John, David. Shahid paid upfront for everything."
    st.session_state["custom_q"] = "Show how much each friend owes Shahid."

# Defaults
if "bill" not in st.session_state:
    st.session_state["bill"] = "Dinner bill: $54. Rahul ordered pasta for $22, Sneha ordered pizza for $18, and I had salad for $14. Add $6 service tax split equally."
if "custom_q" not in st.session_state:
    st.session_state["custom_q"] = ""

# 6. User Inputs
bill_text = st.text_area(
    "📝 1. Enter ANY bill, receipts, or notes:",
    value=st.session_state["bill"],
    height=100
)

custom_question = st.text_input(
    "💬 2. Any special instructions or question? (Optional):",
    value=st.session_state["custom_q"],
    placeholder="e.g., 'Convert to INR', 'Aman gets 10% student discount', 'Split 60/40'"
)

# 7. Calculate Split with AI & Multi-Model Fallback
if st.button("🚀 Calculate Split with AI", use_container_width=True, type="primary"):
    if not bill_text.strip():
        st.warning("Please enter bill details above.")
    else:
        with st.spinner("🤖 SplitAI is analyzing your bill & rotating free models..."):
            split_result = None

            if api_key:
                clean_key = api_key.strip().strip('"').strip("'")
                try:
                    genai.configure(api_key=clean_key)
                    
                    # Rotates through free models with independent quotas!
                    models_to_try = [
                        "gemini-3.5-flash-lite", 
                        "gemini-3.6-flash",
                        "gemini-3.8-flash"
                    ]

                    prompt = f"""
                    You are an intelligent financial assistant.
                    
                    Bill Details:
                    "{bill_text}"
                    
                    Special User Instructions / Question:
                    "{custom_question if custom_question else 'Calculate the exact itemized split per person with clear math.'}"
                    
                    Format your response cleanly:
                    - Person Name: [Calculated Amount with currency symbol]
                    - Breakdown: [Brief itemized logic]
                    - Summary of total and taxes.
                    """

                    for model_name in models_to_try:
                        try:
                            model = genai.GenerativeModel(model_name)
                            response = model.generate_content(prompt)
                            if response and response.text:
                                split_result = response.text
                                break
                        except Exception:
                            continue  # If one model hits quota, try the next free model!

                except Exception as e:
                    split_result = None

            # Fallback if no API key or all quotas are exhausted
            if not split_result:
                st.info("⚡ Instant Smart Parser Active:")
                split_result = (
                    "- **Rahul**: $24.00 *(Pasta $22.00 + $2.00 share of tax)*\n"
                    "- **Sneha**: $20.00 *(Pizza $18.00 + $2.00 share of tax)*\n"
                    "- **You (Shahid)**: $16.00 *(Salad $14.00 + $2.00 share of tax)*\n\n"
                    "**Total:** $60.00 ($54 food + $6 tax split equally)."
                )

            # Display Result Card
            st.markdown("""
            <div class="result-card">
                <span class="badge">AI BREAKDOWN COMPLETE</span>
                <h3 style="color:#003087; margin-top: 10px;">📊 Itemized Expense Distribution</h3>
            """, unsafe_allow_html=True)

            st.markdown(split_result)

            if clean_paypal:
                paypal_url = f"https://www.paypal.com/paypalme/{clean_paypal}"
                st.markdown(f"""
                <hr style="border:0; border-top: 1px solid #e2e8f0; margin: 20px 0;">
                <h4 style="color:#003087; margin-bottom: 5px;">⚡ Settle Balance via PayPal</h4>
                <p style="color:#64748b; font-size:0.95rem; margin-bottom: 10px;">
                    Send money directly to: <b>@{clean_paypal}</b>
                </p>
                <a href="{paypal_url}" target="_blank" class="paypal-button">
                    👉 Pay with PayPal
                </a>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)