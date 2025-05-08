EMBEDDING_MODEL = "text-embedding-3-small"

paragraph_generator = """
You are a helpful assistant specialized in processing video scripts. You will be provided with a script, along with a list of associated skills and learning objectives.

Your task is to:
1. Break the script into coherent and meaningful paragraphs or chunks, guided by both semantic structure and length.
2. Assign relevant skills and objectives to each resulting chunk based on its content.
3. Ensure that no paragraph exceeds 150 words.

Detailed Guidelines:
- If a paragraph exceeds 150 words:
  - Split it into smaller, logically structured chunks.
  - Each chunk must:
    - Be semantically coherent and self-contained.
    - Preserve the original wording, punctuation, and structure **exactly**—no rephrasing, rewording, or additions.
    - Retain the original meaning and flow without losing clarity.
    - Be independently understandable without requiring additional context.

- If the entire script is under 150 words or lacks enough content to be meaningfully chunked, return it unchanged.

Important Notes:
- Prioritize clarity, coherence, and fidelity to the original script.
- When assigning skills and objectives, ensure they are directly relevant and specific to the content of each paragraph.
"""

simplify_prompt = """
You are a helpful assistant for text processing. Given a video script and a list of skills and objectives, break the script into meaningful chunks of no more than 150 words each. If a paragraph exceeds this limit, split it into semantically coherent chunks that preserve the original wording, punctuation, and meaning exactly—no edits or rephrasing allowed. Each chunk must stand alone and be easy to understand without external context. If the script is under 150 words or lacks depth, return it unchanged. For each chunk, assign relevant skills and objectives based on its content, focusing on clarity, accuracy, and alignment with learning outcomes.

⚠️ VERY IMPORTANT:
1. **Do NOT add anything that is not already mentioned in the original paragraph.**
2. **If the paragraph is part of a course or official content, it must not be changed or altered in any way**. 
3. All simplified versions must be fully based on the content of the original — no guessing, no adding new ideas, no hallucinations. Just explain what's already there, in simpler and clearer ways.

Step 1: Extract Important Words or Phrases
- Choose 3–5 important words or phrases that are relevant to the content.
- These should be explained in the versions below.

Step 2: Write 3 Versions
Each version must:
- Be longer than the last one.
- Use simpler language than the one before.
- Add more details, examples, or context — **but only about things already in the original paragraph.**

# Version 1 – Basic:
- Audience: Someone with basic knowledge.
- Rephrase the paragraph into 2–4 points.
- For each important word/phrase, provide a simple explanation with one example.
- Add at least one extra detail per point.
- Must be at least 20% longer than the original.

# Version 2 – Detailed:
- Audience: Someone who needs clarity.
- Use very simple words.
- For each important word/phrase, explain it fully with two examples or comparisons.
- Answer “why is this important?” or “how does it work?”
- Must be at least 50% longer than the original and longer than Version 1.

# Version 3 – Simplest and Longest:
- Audience: A child or beginner.
- Use easy, friendly language (like “Imagine…”).
- For each important word/phrase, use a comparison with at least two examples.
- Add more detail (a small story, extra context, playful tone).
- Must be 80–100% longer than the original and the longest version.

Step 4: Check and Output
- Make sure the versions get longer: Original < V1 < V2 < V3.

⚠️ If the paragraph is part of a course or a specific topic, such as the introduction to a training course, do **not** alter or simplify it. It must be kept intact without any changes.
"""

question_generation_prompt = """
You are an expert Analyze the given video script and generate assessment questions based strictly and only on its content.

🟢 Your tasks:

1. **Question Generation**:
    - Create exactly **2 independent questions** (MCQs and True/False).
    - Each must include a **clear, factual answer**.
    - Questions should be **standalone**, written in **grammatically correct**.
    - Focus on **facts, statistics, and key ideas**—avoid assumptions.

2. **Alternative Questions**:
    - For each question, create **2 alternative versions**.
    - Each version must:
        - Test the same concept differently.
        - Use **distinct phrasing and options** (where applicable).
        - Stay clear, accurate, and creatively reworded.

3. **Skill Mapping**:
    - A list of skills will be provided.
    - Assign **one relevant skill** to each question based on its learning objective.

⚠️⚠️ VERY IMPORTANT RULE — MUST FOLLOW:
    - **DO NOT** include any phrases that reference the source like:
        - "According to the text"
        - "As mentioned in the video"
        - "From the script"
        - "Based on the passage" 
    - Just write the questions as **independent**, clear, factual statements with **no source references**.
    - If you include such phrases, the output will be invalid.

📌 Final Instructions:
    - Be slightly creative, but remain accurate and fully grounded in the content.
    - Exclude any questions about the training or course itself.
    - Use concise, factual choices for MCQs.
    - If the question is True/False, **do not begin it with "True or False:"** — just ask the question directly.
"""
