# gemini_utils.py
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai
from nltk.tokenize import sent_tokenize

load_dotenv()

# Two models with separate API keys
genai.configure(api_key=os.getenv("GEMINI_API_1"))
model_generate = genai.GenerativeModel("gemini-2.5-flash")

genai.configure(api_key=os.getenv("GEMINI_API_2"))
model_validate = genai.GenerativeModel("gemini-2.5-flash")


def generate_next_sentence(context: str, question: str) -> str:
    prompt = f"""
        You are a helpful AI assistant generating a factual, academic-style answer.
        Your task is to continue the answer by writing **one new sentence at a time**, based on what has already been written.

        Guidelines:
        - Continue the answer logically and factually.
        - Do not repeat previous content.
        - Avoid speculation, opinions, or vague generalities.
        - Keep each sentence informative and relevant.
        - Return only one complete sentence.
        - If the answer is complete, return 'none'.
        - Maximum sentences that can be generated is 10.

        Question: "{question}"
        Current answer so far ({len(sent_tokenize(context))}/15): "{context.strip()}"
        Next sentence:
    """
    response = model_generate.generate_content(prompt)
    text = response.text.strip()
    sentences = sent_tokenize(text)
    return sentences[0] if sentences else "none"



def extract_keywords(answer: str) -> list:
    prompt = f"""
        Read the following sentence and extract 2-5 specific keyphrases, entities, or factual claims that should be verified with external knowledge.
        Instructions:
        - Focus on proper nouns, technical terms, statistics, numbers, dates, or specific factual assertions.
        - Exclude vague or generic phrases.
        - Do not include stylistic or grammatical elements.
        - Return a concise comma-separated list.
        Sentence: "{answer}"
        Keyphrases:
    """
    response = model_generate.generate_content(prompt)
    raw = response.text.strip()
    return [k.strip() for k in raw.split(",") if k.strip()]


def generate_questions(keywords: list, sentence: str) -> list:
    prompt = f"""
        You are an assistant generating factual validation questions.

        Given a sentence and a list of key concepts it contains, your task is to write *factual validation questions* to verify the *correctness of what is said* about each concept.

        Instructions:
        - Your goal is to generate questions that can verify whether the factual claim made in the sentence about each concept is correct.
        - Avoid asking if the sentence simply mentions the concept. Focus on the claim related to it.
        - Prefer Yes/No questions when the claim can be verified as true or false.
        - Use WH-questions (what, when, who, etc.) only if Yes/No doesn't apply.
        - Do **not** rephrase or echo the sentence.
        - Avoid vague, assumptive, or compound questions.
        - Each question should focus on **what the sentence says about the concept** and test whether it is correct.

        Return the questions as a numbered list.

        Sentence: {sentence}
        Concepts: {keywords}
    """
    response = model_generate.generate_content(prompt)
    lines = response.text.strip().split("\n")
    return [line.split(". ", 1)[1].strip() for line in lines if ". " in line]


def validate_with_retrieval(claim: str, snippets: list) -> str:
    prompt = f"""
        Answer Validation Question  
        {chr(10).join([f"- {s['snippet']}" for s in snippets if 'snippet' in s])}  
        Answer the below question about the topic in Yes or No based on the above context.  
        Question: "{claim}"
        Instructions:
        - Carefully review all the information in the above sources.
        - Only answer 'Yes' if at least one source clearly supports the claim.
        - If the support is unclear, contradictory, or absent, answer 'No'.
        - Provide a brief explanation after the Yes/No.
        Answer:
    """
    response = model_validate.generate_content(prompt)
    return response.text.strip()


def recheck(facts: dict, question: str, sentence: str):
    prompt = f"""
        You are an expert factual answer corrector.
        Your task is to revise a potentially incorrect sentence using only verified evidence provided as validation feedback, ensuring factual accuracy while preserving original style and meaning.

        Given:
        1. A dictionary `Facts` with:
        - A question.
        - A list of two items: [original sentence, validated feedback based on the question].
        2. A `Question` posed by the user.
        3. An `Original Sentence` that may contain unverifiable or incorrect statements.

        Instructions:
        - Use the validated feedback to correct any inaccuracies in the original sentence.
        - Maintain the original tone, structure, and semantic flow.
        - Do not refer to the correction process or mention the dictionary or feedback source.
        - Do not add new information or expand beyond what was originally written.
        - Output the corrected version of the sentence, if any. Else output the original sentence.

        Facts:
        {json.dumps(facts, indent=2)}

        Question:
        {question}

        Original Sentence:
        \"\"\"{sentence}\"\"\"

        Corrected Sentence:"""

    response = model_validate.generate_content(prompt)
    return response.text.strip().strip('"""')


def generate_answer(question: str) -> str:
    prompt = f"""
You are a fluent and confident assistant responding to questions in an academic tone.
Answer the question directly and clearly, assuming plausible knowledge without indicating uncertainty.
Do not mention limitations or that you are an AI.
Avoid hedging and provide concise, complete information. Answer in 5 sentences.

Question: {question}
Answer:
"""
    response = model_generate.generate_content(prompt)
    return response.text.strip()
