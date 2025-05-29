import streamlit as st
import google.generativeai as genai
import PyPDF2
import io
import random
import json
from typing import List, Dict
import time

# Page configuration
st.set_page_config(
    page_title="✨ Flashcard Generator",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 20px;
        margin-bottom: 2rem;
        text-align: center;
        color: white;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.9;
        font-weight: 300;
    }
    
    .flashcard {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        border-radius: 20px;
        padding: 2rem;
        margin: 1rem 0;
        box-shadow: 0 10px 30px rgba(240, 147, 251, 0.3);
        transition: all 0.3s ease;
        border: none;
        color: white;
    }
    
    .flashcard:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(240, 147, 251, 0.4);
    }
    
    .flashcard-question {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        color: white;
        font-weight: 500;
        font-size: 1.1rem;
    }
    
    .flashcard-answer {
        background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
        border-radius: 15px;
        padding: 1.5rem;
        color: white;
        font-weight: 400;
        line-height: 1.6;
    }
    
    .stats-card {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        color: white;
        margin: 0.5rem;
        box-shadow: 0 5px 15px rgba(250, 112, 154, 0.3);
    }
    
    .control-panel {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 20px;
        padding: 2rem;
        margin: 2rem 0;
    }
    
    .success-message {
        background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%);
        border-radius: 10px;
        padding: 1rem;
        color: white;
        text-align: center;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    .error-message {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        border-radius: 10px;
        padding: 1rem;
        color: white;
        text-align: center;
        font-weight: 500;
        margin: 1rem 0;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.75rem 2rem;
        border-radius: 50px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(102, 126, 234, 0.4);
    }
    
    .shuffle-button > button {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%) !important;
        color: white !important;
        font-size: 1.1rem !important;
        padding: 1rem 2rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'flashcards' not in st.session_state:
    st.session_state.flashcards = []
if 'current_card' not in st.session_state:
    st.session_state.current_card = 0
if 'show_answer' not in st.session_state:
    st.session_state.show_answer = False
if 'gemini_api_key' not in st.session_state:
    st.session_state.gemini_api_key = ""

def configure_gemini(api_key: str):
    """Configure Gemini AI with the provided API key"""
    try:
        genai.configure(api_key=api_key)
        return True
    except Exception as e:
        st.error(f"Error configuring Gemini: {str(e)}")
        return False

def extract_text_from_pdf(pdf_file) -> str:
    """Extract text from uploaded PDF file"""
    try:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() + "\n"
        return text
    except Exception as e:
        st.error(f"Error reading PDF: {str(e)}")
        return ""

def generate_flashcards(text: str, num_cards: int = 10) -> List[Dict[str, str]]:
    """Generate flashcards using FREE Gemini AI"""
    try:
        # Debug: Show what we're doing
        st.write("🔍 **Debug Info:**")
        st.write(f"- Text length: {len(text)} characters")
        st.write(f"- Requested cards: {num_cards}")
        
        # Try different model names in order of preference
        model_names = ['gemini-1.5-flash', 'gemini-1.0-pro', 'gemini-pro']
        model = None
        
        for model_name in model_names:
            try:
                st.write(f"- Trying model: {model_name}")
                model = genai.GenerativeModel(model_name)
                break
            except Exception as e:
                st.write(f"- Model {model_name} failed: {str(e)}")
                continue
        
        if not model:
            st.error("❌ No working Gemini model found!")
            return []
        
        # Simplified prompt that's more likely to work
        prompt = f"""
        Create {num_cards} flashcards from this text. 
        
        Use this EXACT format for each flashcard:
        Q: [question here]
        A: [answer here]
        
        Text to use: {text[:3000]}
        
        Make {num_cards} flashcards now:
        """
        
        st.write("- Sending request to Gemini...")
        response = model.generate_content(prompt)
        st.write("- Got response from Gemini!")
        
        if not response or not response.text:
            st.error("❌ Empty response from Gemini")
            return []
        
        st.write(f"- Response length: {len(response.text)} characters")
        
        # Show the raw response for debugging
        with st.expander("🔍 Raw AI Response (for debugging)"):
            st.text(response.text[:500] + "..." if len(response.text) > 500 else response.text)
        
        # Parse the response
        flashcards = []
        lines = response.text.strip().split('\n')
        current_question = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('Q:'):
                current_question = line.replace('Q:', '').strip()
            elif line.startswith('A:') and current_question:
                answer = line.replace('A:', '').strip()
                flashcards.append({
                    'question': current_question,
                    'answer': answer
                })
                current_question = None
        
        st.write(f"- Parsed {len(flashcards)} flashcards")
        
        if len(flashcards) == 0:
            # Fallback: create simple flashcards
            st.warning("⚠️ Couldn't parse AI response, creating sample flashcards...")
            sample_cards = [
                {"question": "What is the main topic of this text?", "answer": f"The text discusses: {text[:100]}..."},
                {"question": "What are the key points mentioned?", "answer": "Based on the provided text, the key points include the main concepts and ideas presented."},
                {"question": "How would you summarize this content?", "answer": "This content covers important information that can be studied through these flashcards."}
            ]
            return sample_cards[:num_cards]
        
        return flashcards[:num_cards]
            
    except Exception as e:
        st.error(f"❌ Error generating flashcards: {str(e)}")
        
        # Show detailed error info
        import traceback
        with st.expander("🔍 Detailed Error Info"):
            st.code(traceback.format_exc())
        
        # Return sample flashcards as fallback
        st.info("📝 Returning sample flashcards as fallback...")
        return [
            {"question": "Sample Question 1", "answer": "This is a sample answer to test the flashcard functionality."},
            {"question": "Sample Question 2", "answer": "Another sample answer to verify everything is working."}
        ]

def shuffle_flashcards():
    """Shuffle the current flashcards"""
    if st.session_state.flashcards:
        random.shuffle(st.session_state.flashcards)
        st.session_state.current_card = 0
        st.session_state.show_answer = False
        st.success("🔀 Flashcards shuffled!")

# Main header
st.markdown("""
<div class="main-header">
    <h1>🧠 AI Flashcard Generator</h1>
    <p>Transform any text or PDF into interactive flashcards with Gemini AI</p>
</div>
""", unsafe_allow_html=True)

# Sidebar for API key and controls
with st.sidebar:
    st.markdown("### 🔐 FREE Gemini API")
    st.info("💡 Get your FREE API key from Google AI Studio - no payment required!")
    api_key = st.text_input(
        "Gemini API Key", 
        type="password", 
        value=st.session_state.gemini_api_key,
        help="Get your FREE API key from ai.google.dev - completely free!"
    )
    
    if api_key != st.session_state.gemini_api_key:
        st.session_state.gemini_api_key = api_key
    
    st.markdown("### 📊 Statistics")
    if st.session_state.flashcards:
        st.metric("Total Cards", len(st.session_state.flashcards))
        st.metric("Current Card", f"{st.session_state.current_card + 1}")
        progress = (st.session_state.current_card + 1) / len(st.session_state.flashcards)
        st.progress(progress)

# Main content tabs
tab1, tab2 = st.tabs(["📄 PDF Upload", "✍️ Text Input"])

with tab1:
    st.markdown("### Upload PDF Document")
    uploaded_file = st.file_uploader(
        "Choose a PDF file", 
        type="pdf",
        help="Upload any PDF document to generate flashcards"
    )
    
    if uploaded_file:
        with st.spinner("📖 Extracting text from PDF..."):
            extracted_text = extract_text_from_pdf(uploaded_file)
        
        if extracted_text:
            st.markdown('<div class="success-message">✅ PDF text extracted successfully!</div>', 
                       unsafe_allow_html=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown(f'<div class="stats-card"><h3>{len(extracted_text)}</h3><p>Characters</p></div>', 
                           unsafe_allow_html=True)
            with col2:
                st.markdown(f'<div class="stats-card"><h3>{len(extracted_text.split())}</h3><p>Words</p></div>', 
                           unsafe_allow_html=True)
            
            with st.expander("📝 Preview Extracted Text"):
                st.text_area("Extracted Content", extracted_text[:1000] + "..." if len(extracted_text) > 1000 else extracted_text, height=200)
            
            num_cards = st.slider("Number of flashcards to generate", 5, 20, 10)
            
            if st.button("🚀 Generate Flashcards from PDF", key="pdf_generate"):
                if not api_key:
                    st.markdown('<div class="error-message">❌ Please enter your Gemini API key in the sidebar</div>', 
                               unsafe_allow_html=True)
                else:
                    configure_gemini(api_key)
                    with st.spinner("🤖 AI is creating your flashcards..."):
                        flashcards = generate_flashcards(extracted_text, num_cards)
                    
                    if flashcards:
                        st.session_state.flashcards = flashcards
                        st.session_state.current_card = 0
                        st.session_state.show_answer = False
                        st.balloons()
                        st.markdown('<div class="success-message">🎉 Flashcards generated successfully!</div>', 
                                   unsafe_allow_html=True)

with tab2:
    st.markdown("### Enter Your Text")
    user_text = st.text_area(
        "Paste your text here",
        height=300,
        placeholder="Enter the text you want to create flashcards from..."
    )
    
    if user_text:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f'<div class="stats-card"><h3>{len(user_text)}</h3><p>Characters</p></div>', 
                       unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="stats-card"><h3>{len(user_text.split())}</h3><p>Words</p></div>', 
                       unsafe_allow_html=True)
        
        num_cards = st.slider("Number of flashcards to generate", 5, 20, 10, key="text_slider")
        
        if st.button("🚀 Generate Flashcards from Text", key="text_generate"):
            if not api_key:
                st.markdown('<div class="error-message">❌ Please enter your Gemini API key in the sidebar</div>', 
                           unsafe_allow_html=True)
            else:
                configure_gemini(api_key)
                with st.spinner("🤖 AI is creating your flashcards..."):
                    flashcards = generate_flashcards(user_text, num_cards)
                
                if flashcards:
                    st.session_state.flashcards = flashcards
                    st.session_state.current_card = 0
                    st.session_state.show_answer = False
                    st.balloons()
                    st.markdown('<div class="success-message">🎉 Flashcards generated successfully!</div>', 
                               unsafe_allow_html=True)

# Flashcard Display and Controls
if st.session_state.flashcards:
    st.markdown("---")
    st.markdown("## 🎴 Study Your Flashcards")
    
    # Control buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("⬅️ Previous", disabled=(st.session_state.current_card == 0)):
            st.session_state.current_card -= 1
            st.session_state.show_answer = False
    
    with col2:
        if st.button("➡️ Next", disabled=(st.session_state.current_card >= len(st.session_state.flashcards) - 1)):
            st.session_state.current_card += 1
            st.session_state.show_answer = False
    
    with col3:
        if st.button("🔀 Shuffle", key="shuffle_main"):
            shuffle_flashcards()
    
    with col4:
        if st.button("🔄 Reset"):
            st.session_state.current_card = 0
            st.session_state.show_answer = False
    
    # Current flashcard
    current_flashcard = st.session_state.flashcards[st.session_state.current_card]
    
    # Always show the question
    st.markdown(f"""
    <div class="flashcard">
        <div class="flashcard-question">
            <h3>❓ Question {st.session_state.current_card + 1}</h3>
            <p>{current_flashcard['question']}</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Show/Hide answer button
    if not st.session_state.show_answer:
        if st.button("👁️ Show Answer", key="btn_show_answer"):
            st.session_state.show_answer = True
            st.rerun()
    else:
        # Show the answer when revealed
        st.markdown(f"""
        <div class="flashcard">
            <div class="flashcard-answer">
                <h3>💡 Answer</h3>
                <p>{current_flashcard['answer']}</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🙈 Hide Answer", key="btn_hide_answer"):
            st.session_state.show_answer = False
            st.rerun()

# Tips and Instructions
with st.expander("💡 Tips for Better Flashcards"):
    st.markdown("""
    **For best results:**
    - Use clear, well-structured text
    - Include key concepts and definitions
    - Ensure your text has enough content for multiple flashcards
    - Review and edit flashcards as needed
    
    **Study Tips:**
    - Use the shuffle feature to test yourself randomly
    - Try to answer before revealing the answer
    - Review cards you find difficult more frequently
    - Take breaks between study sessions
    """)

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; padding: 2rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 15px; color: white; margin-top: 2rem;">
    <h4>🆓 Powered by FREE Gemini AI</h4>
    <p>Created with ❤️ using Streamlit • Get your FREE API key at <a href="https://ai.google.dev/" style="color: #ffd700;">ai.google.dev</a></p>
    <p><strong>100% FREE - No payment required!</strong></p>
</div>
""", unsafe_allow_html=True)