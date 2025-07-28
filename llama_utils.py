import json
import re
from nltk.tokenize import sent_tokenize
from transformers import AutoTokenizer, AutoModelForCausalLM, pipeline

# Load the LLaMA 2 model and tokenizer
MODEL_NAME = "meta-llama/Llama-2-7b-chat-hf"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, use_auth_token=True)
model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    device_map="auto",
    torch_dtype="auto"
)

llm = pipeline("text-generation", model=model, tokenizer=tokenizer, max_new_tokens=200)

def _call_llama(prompt: str) -> str:
    try:
        response = llm(prompt)[0]['generated_text']
        return response.strip()
    except Exception as e:
        print("LLaMA Error:", e)
        return "none"

def generate_next_sentence(context: str, question: str) -> str:
    prompt = f"""
        You are generating a factual answer to the question below. Generate **only the next sentence** of the answer.
        If you doubt that there is no next sentence, then return none.
        Question: "{question}"
        Current answer so far: "{context.strip()}"
        Next factual sentence:
    """
    text = _call_llama(prompt)
    sentences = sent_tokenize(text)
    return sentences[0] if sentences else "none"

def extract_keywords(answer: str) -> list:
    prompt = f"""
        Identify all the important keyphrases from the above sentence and return a comma separated list.
        If the sentence is not given or is 'none', then skip.
        Sentence: "{answer}"
        List only 2-3 concise concepts (names, events, numbers, dates, or claims).
        Output format: [concept1, concept2, ...]
    """
    raw = _call_llama(prompt)
    return [k.strip() for k in raw.split(",") if k.strip()]

def generate_questions(keywords: list) -> list:
    prompt = f"""
        For each concept, generate exactly one validation question. The questions should be simple and made to check facts about the concept given.
        - Use Yes/No if verifying a fact (e.g., “Was X true?”). 
        - You can also generate 'wh' questions (what/where/when/who/how) if it is more appropriate.
        - If no concept provided, then skip.
        Return questions as a numbered list.
        Concept={keywords}
    """
    text = _call_llama(prompt)
    lines = text.split("\n")
    return [line.split(". ", 1)[1].strip() for line in lines if ". " in line]

def validate_with_retrieval(claim: str, snippets: list) -> str:
    sources = '\n'.join([f"- {s['snippet']}" for s in snippets if 'snippet' in s])
    prompt = f"""
        You are a fact checker. Check if the following claim is supported by any of the texts below.
        Claim: "{claim}"
        Sources:
        {sources}
        Does any source support the claim? Answer 'Yes' or 'No' and explain briefly.
    """
    return _call_llama(prompt)

def recheck(facts: dict, current_ans: str):
    prompt = f"""
        You are a factual consistency checker. For each item in the dictionary below, determine if the explanation supports the original sentence.
        If the explanation supports the sentence, return the sentence as-is.
        If not, rewrite the sentence based on the explanation, as the next sentence to the current answer.
        Return just the final, corrected sentence. Do not return the dictionary or any code.
        Facts: {facts}
        Current Answer: {current_ans}
    """
    return _call_llama(prompt)

def generate_answer(question: str) -> str:
    prompt = f"""
        You are a confident and fluent assistant. Your job is to answer questions clearly and completely without verifying or checking for accuracy. 
        Even if you're not sure, guess based on what seems plausible. Avoid saying you're unsure. Just sound convincing.
        Question: {question}
        Answer:
    """
    return _call_llama(prompt)

def estimate_hallucination(text: str):
    prompt = f"""
        You are a factuality evaluator.
        Read the following academic-style response and assess whether it contains any hallucinations (i.e., false or unverifiable factual claims). 
        You must:
        1. Give a hallucination score from 0 to 5  
        - 0 = No hallucinations  
        - 5 = Extremely hallucinated
        2. List each suspected hallucinated claim and briefly explain why.
        Return your output **only** in this JSON format:
        {{
        "score": <number>,
        "hallucinations": [
            "Claim 1: <statement> — Explanation.",
            "Claim 2: <statement> — Explanation."
        ]
        }}
        Text:
        \"\"\"{text}\"\"\"
    """
    raw = _call_llama(prompt)
    try:
        json_str = re.search(r'\{.*\}', raw, re.DOTALL).group(0)
        data = json.loads(json_str)
        return data["score"], data["hallucinations"]
    except Exception as e:
        print("Parsing error. Fallback to raw text.\n", raw)
        return -1, [f"Could not parse: {raw}"]
