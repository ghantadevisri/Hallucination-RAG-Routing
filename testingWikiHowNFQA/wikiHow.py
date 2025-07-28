import os
import time
from gemini_utils import (
    generate_answer,
    generate_next_sentence,
    extract_keywords,
    generate_questions,
    validate_with_retrieval,
    recheck
)
from retrieval import search_google_cse
import google.generativeai as genai
from evaluate import load as load_metric
from bert_score import score as bert_score
import torch
from datasets import load_dataset

# Load metrics globally
rouge = load_metric("rouge")

# --- Hallucination mitigation pipeline ---
def active_generate(question: str, max_sentences=5):
    original_answer = ""
    improved_answer = ""
    print(f"\nQUESTION: {question}\n")

    for _ in range(max_sentences):
        sentence = generate_next_sentence(improved_answer, question)
        print(f"\n\nGenerated Sentence: {sentence}")
        time.sleep(3)

        if sentence.lower() == 'none':
            break

        original_answer += sentence + " "
        concepts = extract_keywords(sentence)
        print(f"\n→ Concepts: {concepts}")
        time.sleep(3)

        questions = generate_questions(concepts, sentence)
        print(f"\n→ Questions: {questions}")
        time.sleep(3)

        facts_collected = {}
        for q in questions:
            search_results = search_google_cse(q)
            if not search_results:
                print(f"  ✘ No results for: {q}")
                continue

            validation = validate_with_retrieval(q, search_results)
            print(f"  ✓ Validation for '{q}': {validation}")
            time.sleep(2)

            facts_collected[q] = [sentence, validation]

        updated_sentence = recheck(facts_collected, question, sentence)
        print(f"\nUpdated Sentence: {updated_sentence}")
        improved_answer += updated_sentence + " "

    return original_answer.strip(), improved_answer.strip()

# --- WikiHowQA Evaluation ---
def load_nfqa_subset(count=50):
    ds = load_dataset("Lurunchik/WikiHowNFQA", download_mode="force_redownload", split="test")
    return ds.select(range(count))

def load_nfqa_specific(index=1256, count=6):
    dataset = load_dataset("Lurunchik/WikiHowNFQA", split="test")
    indices = list(range(index, index + count))
    sample = dataset.select(indices)
    return sample

def evaluate_metrics(prediction, reference):
    rouge_score = rouge.compute(predictions=[prediction], references=[reference])["rougeL"]
    P, R, F1 = bert_score([prediction], [reference], lang="en", model_type="bert-base-uncased", device="cpu")

    return {
        "ROUGE-L": rouge_score,
        "BERTScore": F1[0].item()
    }

def posthoc_generate(question: str):
    print(f"\nQUESTION: {question}\n")

    response = generate_answer(question)
    print("\nInitial answer: \n", response)

    """ time.sleep(10)
    keywords = extract_keywords(response)
    time.sleep(10)
    questions = generate_questions(keywords)

    print("\nGenerated Validation Questions:")
    for q in questions:
        print(f"- {q}")

    facts = {}
    print("\nRetrieving info and validating...\n")
    for q in questions:
        time.sleep(10)
        results = search_google_cse(q)
        if results:
            time.sleep(10)
            explanation = validate_with_retrieval(q, results)
            print(f"Validation for '{q}':\n{explanation}\n")
            facts[q] = explanation
        else:
            print(f"No results found for '{q}'\n")

    time.sleep(10)
    updated_response = recheck(facts, question, response) """
    return response

def run_evaluation():
    samples = load_nfqa_specific()

    for i, sample in enumerate(samples):
        q = sample['question']
        ref = sample['answer']

        print(f"\n--- Sample {i+1} ---")
        print("Q:", q)

        before, after = active_generate(q)

        print("\nBefore (original):\n", before)         
        print("\nAfter (corrected):\n", after)
        print("\nReference Answer:\n", ref)

        before_score = evaluate_metrics(before, ref)
        after_score = evaluate_metrics(after, ref)

        print("\n→ Evaluation Metrics:")
        for metric in before_score:
            print(f"  - {metric} (Before): {before_score[metric]}")
            print(f"  - {metric} (After):  {after_score[metric]}")

# --- Entry Point ---
if __name__ == "__main__":  
  run_evaluation()