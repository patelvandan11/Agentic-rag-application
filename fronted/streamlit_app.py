import streamlit as st
import requests

API_URL = "http://localhost:8000/research"

st.set_page_config(page_title="AI Research Assistant", layout="wide")

st.title("🧠 AI Research Assistant (Agentic RAG)")
st.write("Ask a research question and let agents do the work.")

query = st.text_input(
    "Enter your research question",
    placeholder="Compare CNN vs Vision Transformers for medical imaging"
)

if st.button("Run Research"):
    if not query:
        st.warning("Please enter a question")
    else:
        with st.spinner("Agents are working..."):
            response = requests.post(API_URL, params={"query": query})

        if response.status_code == 200:
            data = response.json()

            st.subheader("📌 Planner Output")
            st.text(data["plan"])

            st.subheader("📄 Retrieved Papers")
            for p in data["papers"]:
                st.markdown(f"**{p['title']}** ({p['source']})")
                st.write(p["summary"])

            st.subheader("🧠 Agent Analysis")
            st.write(data["analysis"])

            st.subheader("✅ Final Summary")
            st.success(data["summary"])
        else:
            st.error("Backend error occurred")
