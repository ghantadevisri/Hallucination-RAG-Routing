import streamlit as st
import time
from gemini_utils import (
    generate_next_sentence,
    extract_keywords,
    generate_questions,
    validate_with_retrieval,
    recheck
)
from retrieval import search_google_cse

import re

def compute_complexity(sentence):
    words = sentence.split()
    word_score = len(words) / 30
    claim_words = ["is", "was", "are", "were", "percent",
                   "million", "billion", "founded", "invented",
                   "discovered", "born", "died"]
    claim_count = sum(1 for w in words if w.lower() in claim_words)
    claim_score = claim_count / 5
    score = min(0.6 * word_score + 0.4 * claim_score, 1.0)
    return score

def has_risky_pattern(sentence):
    has_number = bool(re.search(r'\b\d+\b', sentence))
    words = sentence.split()
    has_proper_noun = any(
        w[0].isupper() for i, w in enumerate(words) if i > 0 and w.strip('.,!?').isalpha()
    )
    return has_number or has_proper_noun

def assign_tier(sentence):
    score = compute_complexity(sentence)
    risky = has_risky_pattern(sentence)
    if score < 0.3:
        tier = "light"
    elif score < 0.6:
        tier = "medium"
    else:
        tier = "heavy"
    if risky and tier == "light":
        tier = "medium"
    return tier, score, risky

# --- Page Configuration ---
st.set_page_config(
    page_title="Complexity-Routed RAG",
    page_icon="🧠",
    layout="centered"
)

# --- CSS for Styling the Permanent Log ---
st.markdown("""
<style>
    /* Add padding to the bottom of the main chat container */
    .main .block-container {
        padding-bottom: 8rem;
    }
    div[data-testid="stChatInput"] {
        padding-left: 2rem;
        padding-right: 2rem;
    }
    [data-testid="stChatMessage"] {
        overflow-wrap: break-word;
    } 
    details {
        border: 1px solid #262730;
        border-radius: 0.5rem;
        padding: 0.5rem 1rem;
        margin-bottom: 1rem; 
    }
    summary {
        cursor: pointer;
        font-weight: bold;
    }
    .final-answer-box {
        white-space: normal;          
        overflow-wrap: break-word;    
        background-color: #ffffff;
        color: #000000;
        padding: 1rem;                
        border-radius: 0.5rem;        
        margin-top: 1rem;             
    }
    /* CSS classes to mimic st.info, st.success, st.error */
    .st-box {
        border-left: 5px solid;
        padding: 1rem;
        border-radius: 0.25rem;
        margin-bottom: 1rem;
    }
    .st-info-box {
        padding: 1rem;
        border-color: #007bff; 
        background-color: rgba(0, 123, 255, 0.1);
    }
    .st-success-box {
        padding: 1rem;
        border-color: #28a745; 
        background-color: rgba(40, 167, 69, 0.1);
    }
    .st-error-box {
        padding: 1rem;
        border-color: #dc3545; 
        background-color: rgba(220, 53, 69, 0.1);
    }
    .st-warning-box {
        padding: 1rem;
        border-color: #ffc107; 
        background-color: rgba(255, 193, 7, 0.1);
    }
</style>
""", unsafe_allow_html=True)


# --- App Title and Description ---
st.title("Complexity-Routed RAG")
st.markdown("Enter a question below. The AI will provide a validated answer. You can expand the dropdown in its response to see how it 'thinks'.")
st.divider()


# --- Session State Initialization ---
if "messages" not in st.session_state:
    st.session_state.messages = []


# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"], unsafe_allow_html=True)


# --- Main Generation Logic ---
def run_generation_pipeline(question, placeholder):
    """
    Shows a live thinking process in the placeholder, and returns the final
    answer and the completed log for permanent storage.
    """
    final_answer = ""
    thinking_log = ""
    api_call_count = 0
    
    with placeholder.expander("Thinking process...", expanded=True):
        live_log_area = st.empty() 
        live_log_area.markdown("⚙️ *Starting thinking process...*")

        for i in range(3): # Keeping 3 iterations for demonstration
            thinking_log += f"\nStep {i+1}\n\n" 
            
            time.sleep(10) 
            sentence = generate_next_sentence(final_answer, question)
            api_call_count += 1
            if sentence.lower() == "none":
                thinking_log += "<div class='st-success-box'>✅ Answer generation complete.</div>"
                live_log_area.markdown(thinking_log, unsafe_allow_html=True)
                break
            tier, score, risky = assign_tier(sentence)
            thinking_log += f"<div class='st-info-box'>ℹ️ <b>Generated:</b> \"{sentence}\"<br><b>Tier:</b> {tier} | <b>Score:</b>        {score:.2f} | <b>Risky:</b> {risky}</div>"
            live_log_area.markdown(thinking_log + "⚙️ *Processing...*", unsafe_allow_html=True)

            time.sleep(10)
            concepts = extract_keywords(sentence)
            api_call_count += 1
            thinking_log += f"<b>Concepts:</b> `{', '.join(concepts)}`\n\n" 
            live_log_area.markdown(thinking_log + "⚙️ *Processing...*", unsafe_allow_html=True)
            
            time.sleep(10)
            if tier == "light":
              concepts = concepts[:1]
            elif tier == "medium":
              concepts = concepts[:3]
            questions = generate_questions(concepts, sentence)
            api_call_count += 1
            thinking_log += "<b>Validation Questions:</b>\n"
            for q in questions:
                thinking_log += f"- _{q}_\n"
            thinking_log += "\n---\n"
            live_log_area.markdown(thinking_log + "⚙️ *Processing...*", unsafe_allow_html=True)

            facts_collected = {}
            for q in questions:
                time.sleep(10)
                search_results = search_google_cse(q)
                api_call_count += 1
                
                if search_results:
                    validation = validate_with_retrieval(q, search_results)
                    facts_collected[q] = [sentence, validation]
                    if "Yes" in validation:
                        thinking_log += f"<div class='st-success-box'>✓ <b>Verified:</b> {q}<br><b>Reason:</b> {validation}</div>"
                    else:
                        thinking_log += f"<div class='st-error-box'>✗ <b>Unverified:</b> {q}<br><b>Reason:</b> {validation}</div>"
                else:
                    thinking_log += f"<div class='st-warning-box'>? <b>No Results:</b> {q}</div>"
                live_log_area.markdown(thinking_log + "⚙️ *Processing...*", unsafe_allow_html=True)
            
            time.sleep(10)
            updated_sentence = recheck(facts_collected, question, sentence)
            api_call_count += 1
            final_answer += updated_sentence + " "
            live_log_area.markdown(thinking_log + "⚙️ *Processing...*", unsafe_allow_html=True)
    
    thinking_log += f"<div class='st-success-box'>📊 <b>Total API calls used: {api_call_count}</b></div>"
    return final_answer.strip(), thinking_log


# --- Input Handling ---
if prompt := st.chat_input("Ask your question..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        placeholder = st.empty()
        final_answer, thinking_log = run_generation_pipeline(prompt, placeholder)
        
        placeholder.empty()

        assistant_response_content = f"""
        <details>
            <summary>Show the thinking process...</summary>
            <div class="thinking-process-log">
                {thinking_log}
            </div>
        </details>
        <h3>Final Answer:</h3>
        <div class="final-answer-box">{final_answer}</div>
        """
        st.markdown(assistant_response_content, unsafe_allow_html=True)
    
    st.session_state.messages.append({"role": "assistant", "content": assistant_response_content})
    st.rerun()
