<<<<<<< HEAD
# Active RAG Chat with Hallucination Mitigation

## Project Overview

This project presents an "Active Retrieval-Augmented Generation (RAG)" chat application built with Streamlit, specifically designed to address and mitigate the challenge of hallucination in Large Language Model (LLM) responses. Inspired by the methodology outlined in the research paper "[Active Retrieval Augmented Generation](https://arxiv.org/abs/2307.03987)", this implementation extends the RAG paradigm by introducing a dynamic, iterative self-correction mechanism.

The core idea is to enhance the factual accuracy and reliability of LLM-generated answers by integrating real-time validation against external knowledge sources. The application provides a transparent view into this "thinking process," allowing users to observe the AI's internal validation steps. Alongside the interactive chat, an accompanying evaluation script is included to quantitatively assess the effectiveness of this active hallucination mitigation strategy.

## Features

* **Interactive Chat Interface:** A responsive front-end built with Streamlit.
* **Active RAG Pipeline:** Implements a novel, multi-step iterative process for generating and validating LLM responses.
* **Hallucination Mitigation:** Significantly reduces the generation of factually incorrect or unverified information by the LLM.
* **Transparent Thinking Process:** Users can expand a dedicated section within each AI response to view the detailed steps of sentence generation, keyword extraction, validation question formulation, external retrieval, and rechecking.
* **External Knowledge Integration:** Utilizes Google Custom Search Engine (CSE) for real-time information retrieval and factual validation.
* **LLM Backbone:** Powered by `gemini-2.0-flash-lite` for both content generation and validation tasks.

## How It Works: The Active RAG Pipeline

The heart of this project is a sophisticated, iterative RAG pipeline designed to build and validate answers sentence by sentence. This process involves multiple interactions with the LLM and an external search engine:

1.  **Sentence-by-Sentence Generation:** The LLM (`gemini-2.0-flash-lite`) is prompted to generate the answer to the user's question one sentence at a time, building upon the previously generated context.
2.  **Keyword and Concept Extraction:** From each newly generated sentence, the LLM identifies and extracts 2-5 main topics, keyphrases, or factual claims that require verification.
3.  **Validation Question Generation:** The LLM then formulates specific, relevant questions around these identified concepts. These questions are designed to be answerable by an external search and to help determine the factual correctness of the original generated sentence.
4.  **External Retrieval (Google CSE):** The generated validation questions are used to query a Google Custom Search Engine (CSE). The search results (snippets) provide external evidence.
5.  **LLM-based Validation:** Another instance of the LLM (`gemini-2.0-flash-lite`, potentially configured with a separate API key for clear separation of roles) takes the validation question and the retrieved snippets. It then determines whether the original claim in the generated sentence is supported by the external evidence, providing a "Yes" or "No" and a brief explanation.
6.  **Sentence Correction/Refinement:** Finally, the LLM uses these validation results to "recheck" and, if necessary, correct the original generated sentence. If a claim is found to be unverified or incorrect, the sentence is revised to ensure factual accuracy before being added to the final answer.

This iterative process continues until the LLM indicates the answer is complete or a maximum number of sentences is reached.

## Evaluation and Results

The effectiveness of this active RAG method was rigorously tested using a subset of the **WikiHowNFQA dataset**. The `wikiHow.py` script automates this evaluation, comparing the original LLM responses (before correction) and the actively corrected responses against reference answers using ROUGE-L and BERTScore metrics.

The evaluation, conducted on **1036 questions** from the dataset (limited by time and API rate constraints), yielded the following insights:

* **27.89%** of responses exhibited improvement in *both* ROUGE-L and BERTScore, highlighting a substantial positive impact on factual accuracy and semantic similarity.
* **25.90%** of responses showed improvement in *either* ROUGE-L or BERTScore, demonstrating partial but significant enhancement in quality.
* **30.98%** of responses remained factually consistent, indicating the initial generation was already accurate and required no correction.

These results underscore the potential of active RAG methods in enhancing LLM reliability, while also pointing to the ongoing challenges in achieving perfect factual consistency.

## Setup and Installation

Follow these steps to set up and run the application locally.

### Prerequisites

* Python 3.8+
* `pip` (Python package installer)
* `git` (for cloning the repository)
* **Google Cloud Project & API Keys:**
    * You'll need atleast two Google Cloud Project with the **Gemini API** enabled . Or you can use just one but you will run out of the daily requests quota very soon.
    * Generate **two separate API keys** for the Gemini API. These will be used for `model_generate` and `model_validate` respectively (e.g., `GEMINI_API_1` and `GEMINI_API_2`).
    * **Google Custom Search Engine (CSE) API Key & Search Engine ID:**
        * Create a Custom Search Engine (CSE) at [Programmable Search Engine](https://programmablesearchengine.google.com/control/overview).
        * Obtain your **Search Engine ID (CX)** (`GOOGLE_CX_ID`).
        * Enable the **Custom Search API** in your Google Cloud Project.
        * Generate an API key for the Custom Search API (e.g., `GOOGLE_SEARCH_API`).

### Installation Steps

1.  **Clone the Repository:**
    ```bash
    git clone [https://github.com/r1thk4/hallucination-mitigator]
    cd hallucination-mitigator
    ```

2.  **Create a Virtual Environment (Recommended):**
    ```bash
    python -m venv venv
    ```

3.  **Activate the Virtual Environment:**
    * **On macOS/Linux:**
        ```bash
        source venv/bin/activate
        ```
    * **On Windows:**
        ```bash
        .\venv\Scripts\activate
        ```

4.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

5.  **Set Environment Variables:**
    Create a `.env` file in the root directory of your project (same level as `app.py`) and add your API keys and CSE details:

    ```
    GEMINI_API_1="YOUR_GEMINI_API_KEY_FOR_GENERATION"
    GEMINI_API_2="YOUR_GEMINI_API_KEY_FOR_VALIDATION"
    GOOGLE_SEARCH_API="YOUR_GOOGLE_CUSTOM_SEARCH_API_KEY"
    GOOGLE_CX_ID="YOUR_GOOGLE_CUSTOM_SEARCH_ENGINE_ID"
    ```
    **Important:** Do not commit your `.env` file to GitHub. It's crucial for security and is typically ignored by Git (via `.gitignore`).

## Running the Application

1.  **Activate your virtual environment** (if not already active).
2.  **Navigate to the project's root directory** (where `app.py` is located):
    ```bash
    cd your-github-repo-name
    ```
3.  **Run the Streamlit app:**
    ```bash
    streamlit run app.py
    ```
    This command will open the application in your default web browser.

## Running the Evaluation Script

To replicate the evaluation of the Active RAG pipeline:

1.  **Activate your virtual environment**.
2.  **Navigate to the project's root directory** (`your-github-repo-name/`).
3.  **Execute the script as a Python module:**
    ```bash
    python -m testingWikiHowNFQA.wikiHow
    ```
    This script will load a subset of the WikiHowNFQA dataset, run the `active_generate` pipeline for each question, and print evaluation metrics (ROUGE-L, BERTScore) comparing the original and corrected answers against the reference answers. Be aware of potential rate limits from API calls during extensive evaluation.
=======
# Hallucination-RAG-Routing
Complexity-based validation routing layer for hallucination correction — IIIT Nagpur internship
>>>>>>> 528991dfde8b8885af9a0e80601ea6400bfe387d
