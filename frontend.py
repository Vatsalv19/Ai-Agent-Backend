import streamlit as st
import requests

st.set_page_config(page_title="Langraph Agent", layout="wide")
st.title("🤖 AI Agent")
st.write("Create and interact with the AI")

system_prompt = st.text_area(
    "Define your AI agent", 
    height=70, 
    placeholder="Define your AI agent's behavior and personality here..."
)

MODEL_NAMES_GROQ = ["llama3-70b-8192"]
MODEL_NAMES_OPENAI = ["gpt-4o-mini"]

provider = st.radio("Select Model Provider", ["groq", "openai"])  # Fixed: lowercase to match backend

if provider == "groq":  # Fixed: lowercase
    selected_model = st.selectbox("Select Model", MODEL_NAMES_GROQ)
else:
    selected_model = st.selectbox("Select Model", MODEL_NAMES_OPENAI)

allow_web_search = st.checkbox("Allow Web Search")

user_query = st.text_area(
    "Enter your query", 
    height=150, 
    placeholder="Type your question or request here..."
)

API_URL = "http://localhost:8000/chat"

if st.button("Ask Agent"):
    if user_query.strip():
        try:
            # Show loading spinner
            with st.spinner("Getting response from AI agent..."):
                payload = {
                    "model_name": selected_model,
                    "model_provider": provider,
                    "system_prompt": system_prompt,
                    "messages": [user_query],
                    "allow_search": allow_web_search
                }
                
                response = requests.post(API_URL, json=payload, timeout=30)
                
                if response.status_code == 200:
                    response_data = response.json()
                    
                    if "error" in response_data:
                        st.error(f"Error: {response_data['error']}")
                    else:
                        st.subheader("Response from AI Agent")
                        # Display the actual response content
                        if "response" in response_data:
                            st.markdown(response_data["response"])
                        else:
                            st.write(response_data)
                else:
                    st.error(f"HTTP Error {response.status_code}: {response.text}")
                        
        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to the API. Please make sure the backend server is running on http://localhost:8000")
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. The AI agent took too long to respond.")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Request failed: {str(e)}")
        except Exception as e:
            st.error(f"❌ Unexpected error: {str(e)}")
    else:
        st.warning("⚠️ Please enter a query before asking the agent.")

# Add sidebar with information
st.sidebar.header("ℹ️ Information")
st.sidebar.markdown("""
**Available Models:**
- **Groq**: llama3-70b-8192
- **OpenAI**: gpt-4o-mini

**Features:**
- Custom system prompts
- Web search capability
- Multiple model providers
""")

st.sidebar.markdown("---")
st.sidebar.markdown("**Backend Status:**")
try:
    health_response = requests.get("http://localhost:8000/", timeout=5)
    if health_response.status_code == 200:
        st.sidebar.success("✅ Backend is running")
    else:
        st.sidebar.error("❌ Backend is not responding")
except:
    st.sidebar.error("❌ Backend is not running")