import os
from typing import Optional, Tuple

import streamlit as st
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

st.set_page_config(page_title="Holiday Assistant AI", page_icon="🏖️", layout="centered")

# Small, simple styles: a clean white page, subtle dividers, and readable buttons.
st.markdown(
    """
    <style>
      .block-container {max-width: 950px; padding-top: 2rem; padding-bottom: 2.5rem;}
      h1, h2, h3 {color: #173b55;}
      div.stButton > button {border-radius: 8px; min-height: 2.6rem; font-weight: 600;}
      div.stButton > button[kind="primary"] {background: #177e89; border-color: #177e89;}
      div.stButton > button[kind="primary"]:hover {background: #116670; border-color: #116670;}
      .small-note {color: #64748b; font-size: .9rem;}
    </style>
    """,
    unsafe_allow_html=True,
)

API_KEY = os.getenv("GEMINI_API_KEY", "").strip()
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite").strip()


@st.cache_resource(show_spinner=False)
def create_client(api_key: str):
    return genai.Client(
        api_key=api_key,
        http_options=types.HttpOptions(
            timeout=20000,
            retry_options=types.HttpRetryOptions(attempts=1),
        ),
    )


def ask_gemini(prompt: str, max_tokens: int = 550) -> Tuple[Optional[str], Optional[str]]:
    if not API_KEY:
        return None, "Gemini API key not found. Add GEMINI_API_KEY to your .env file, or use Sample Demo."

    try:
        client = create_client(API_KEY)
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
            config=types.GenerateContentConfig(
                temperature=0.4,
                max_output_tokens=max_tokens,
            ),
        )
        answer = (response.text or "").strip()
        if not answer:
            return None, "The AI returned an empty response. Please try again."
        return answer, None
    except Exception as exc:
        message = str(exc)
        lower = message.lower()
        if "503" in lower or "unavailable" in lower or "high demand" in lower:
            return None, "Gemini is temporarily busy (503). Try again later, or use Sample Demo for your presentation."
        if "429" in lower or "resource_exhausted" in lower or "quota" in lower:
            return None, "The Gemini API quota/rate limit was reached. Check your API usage or use Sample Demo."
        if "401" in lower or "403" in lower or "api key" in lower or "permission" in lower:
            return None, "Gemini rejected the API key. Check the key in .env and confirm the Gemini API is enabled."
        if "timeout" in lower or "timed out" in lower:
            return None, "The request timed out. Check the internet connection or use Sample Demo."
        return None, f"The Gemini request failed. Try again or use Sample Demo. Details: {message[:180]}"


def load_sample_demo() -> None:
    st.session_state["beach_results"] = """### Coastal places to consider around Chennai

**Marina Beach** — A well-known city beach for a seaside walk. *Tip:* Visit during cooler hours and follow local notices.

**Elliot's Beach** — A popular seaside area in Besant Nagar. *Tip:* Check local conditions before entering the water.

**Covelong / Kovalam coast** — A coastal area south of Chennai. *Tip:* Confirm activity availability and safety guidance locally.

**Mahabalipuram shore** — A coastal outing that can be paired with heritage sightseeing. *Tip:* Check local access and weather before travelling.

*Sample content for demonstration only; confirm current conditions before travelling.*"""
    st.session_state["hotel_results"] = """### Hotel-planning checklist

| Area option | What to compare | Amenities to check | Price guidance |
|---|---|---|---|
| Near Besant Nagar | Access to your chosen destination | Wi-Fi, parking, breakfast | Check current rates directly |
| Central Chennai | Transport links and journey time | Air conditioning, reception hours, cancellation policy | Compare official listings |
| Southern coastal area | Access to planned activities | Restaurant, family rooms, local transport | Confirm taxes and fees |

**Nearby essentials:** food, public transport/taxis, pharmacy and medical facilities.

*This is a planning example, not a live list of verified hotels or prices.*"""
    st.session_state["review_results"] = """### Hotel summary checklist

**Overview**  
Check the hotel's official website for its location, room types, and policies.

**Amenities to verify**  
Wi-Fi, air conditioning, breakfast, parking, lift access, and check-in hours.

**Questions before booking**
- What is the final cost including taxes and fees?
- Is the room available for your dates?
- What is the cancellation policy?
- How far is it from the attraction, and what is the travel time?

*This is an illustrative template, not a verified review of a real hotel.*"""
    st.session_state["demo_mode"] = True


for key in ("beach_results", "hotel_results", "review_results"):
    st.session_state.setdefault(key, "")
st.session_state.setdefault("demo_mode", False)

st.title("🏖️ Holiday Assistant AI")
st.write("Plan a trip with beach ideas, hotel-planning guidance, and hotel-summary checklists.")
st.caption("AI-generated information may be inaccurate. Check official sources before making travel or booking decisions.")

with st.sidebar:
    st.subheader("Project status")
    st.write("**Gemini API key:** " + ("Detected" if API_KEY else "Not found"))
    st.write(f"**Model:** `{MODEL_NAME}`")
    st.divider()
    if st.button("Load Sample Demo", use_container_width=True):
        load_sample_demo()
        st.rerun()
    if st.button("Clear Results", use_container_width=True):
        for key in ("beach_results", "hotel_results", "review_results"):
            st.session_state[key] = ""
        st.session_state["demo_mode"] = False
        st.rerun()
    st.caption("Sample Demo does not call the AI API.")

if st.session_state["demo_mode"]:
    st.info("Sample Demo is active. The displayed examples are pre-written and are not live Gemini results.")

with st.container():
    st.subheader("Trip details")
    col1, col2 = st.columns(2)
    with col1:
        location = st.text_input("Destination / city", value="Chennai", placeholder="e.g. Chennai")
    with col2:
        travel_style = st.selectbox("Travel style", ["Any traveller", "Family trip", "Solo travel", "Couple getaway", "Friends trip"])
    budget = st.selectbox("Budget preference", ["Not specified", "Budget friendly", "Mid-range", "Premium"])

tab_beach, tab_hotels, tab_review = st.tabs(["🌊 Beach suggestions", "🏨 Hotels & amenities", "📝 Hotel summary"])

with tab_beach:
    st.subheader("Find coastal places")
    st.write("Get beach suggestions and a practical visitor tip for each place.")
    if st.button("Generate beach suggestions", type="primary", key="make_beaches"):
        if not location.strip():
            st.warning("Enter a destination first.")
        else:
            prompt = f"You are a cautious travel assistant. Destination: {location.strip()}. Travel style: {travel_style}. Budget: {budget}. Suggest up to 5 relevant beaches or coastal spots. For each give a short description and one visitor tip. If inland, say so and suggest scenic alternatives. Do not claim live verification or current conditions. Keep the answer concise."
            with st.spinner("Generating suggestions…"):
                answer, error = ask_gemini(prompt, 500)
            if error:
                st.error(error)
            else:
                st.session_state["beach_results"] = answer
                st.session_state["demo_mode"] = False
    if st.session_state["beach_results"]:
        st.markdown(st.session_state["beach_results"])

with tab_hotels:
    st.subheader("Plan hotels and nearby amenities")
    st.write("Get a checklist for comparing accommodation options around a chosen area.")
    area = st.text_input("Beach / neighbourhood / area", placeholder="e.g. Besant Nagar", key="hotel_area")
    if st.button("Generate hotel guide", type="primary", key="make_hotels"):
        if not location.strip() or not area.strip():
            st.warning("Enter both a destination and an area.")
        else:
            prompt = f"Help a {travel_style.lower()} traveller with a {budget.lower()} preference research accommodation around {area.strip()}, in or near {location.strip()}. Give a concise planning table with columns: area or option type, what to compare, amenities to check, price guidance. Do not invent specific verified hotel names, exact current prices, ratings, availability, or distances. Then list nearby amenity types to check such as food, transport, and medical facilities. State this is not live booking data."
            with st.spinner("Preparing hotel guide…"):
                answer, error = ask_gemini(prompt, 600)
            if error:
                st.error(error)
            else:
                st.session_state["hotel_results"] = answer
                st.session_state["demo_mode"] = False
    if st.session_state["hotel_results"]:
        st.markdown(st.session_state["hotel_results"])

with tab_review:
    st.subheader("Create a hotel summary")
    st.write("Generate a cautious summary and a checklist of details to verify before booking.")
    hotel_name = st.text_input("Hotel name", placeholder="Enter a hotel name", key="review_hotel_name")
    if st.button("Generate hotel summary", type="primary", key="make_review"):
        if not location.strip() or not hotel_name.strip():
            st.warning("Enter a destination and hotel name.")
        else:
            prompt = f"Create a cautious travel research summary for the hotel named {hotel_name.strip()} in or near {location.strip()}. Traveller type: {travel_style}; budget: {budget}. Use headings: Overview, Amenities to Verify, Suitability for This Traveller, Questions Before Booking. Do not pretend to have checked live bookings or verified customer reviews. Do not invent exact prices, ratings, policies, or specific amenities. Tell the user to verify with official hotel or booking sources. Keep concise."
            with st.spinner("Preparing hotel summary…"):
                answer, error = ask_gemini(prompt, 550)
            if error:
                st.error(error)
            else:
                st.session_state["review_results"] = answer
                st.session_state["demo_mode"] = False
    if st.session_state["review_results"]:
        st.markdown(st.session_state["review_results"])

st.divider()
st.caption("Built with Python, Streamlit, and Google Gemini AI. Sample content is illustrative and not verified travel data.")
