
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from groq import RateLimitError
import time


def get_llm():
    return ChatGroq(
        model="qwen/qwen3.8-27b",
        temperature=0.2,
        max_tokens=500
    )


def build_chain(system_prompt: str):

    llm = get_llm()

    return (
        RunnablePassthrough()
        | RunnableLambda(lambda x: {"text": x})
        | ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{text}")
        ])
        | llm
        | StrOutputParser()
    )


def invoke_with_retry(chain, transcript: str, retries=3):

    for attempt in range(retries):

        try:
            return chain.invoke(transcript)

        except RateLimitError:

            if attempt == retries - 1:
                raise

            wait_time = 5 * (2 ** attempt)


            time.sleep(wait_time)


def extract_action_items(transcript: str) -> str:

    chain = build_chain(
        "You are an expert meeting analyst. From the meeting transcript, "
        "extract all action items. For each provide:\n"
        "- Task description\n"
        "- Owner (who is responsible)\n"
        "- Deadline (if mentioned, else write 'Not specified')\n\n"
        "Format as a numbered list. If none found say 'No action items found.' but try to infer action items from context if possible."
    )

    return invoke_with_retry(chain, transcript)


def extract_key_decisions(transcript: str) -> str:

    chain = build_chain(
        "You are an expert meeting analyst. From the meeting transcript, "
        "extract all key decisions made. Format as a numbered list. "
        "If none found say 'No key decisions found.' but try to infer decisions from context if possible."
    )

    return invoke_with_retry(chain, transcript)


def extract_questions(transcript: str) -> str:

    chain = build_chain(
        "From the meeting transcript, extract all unresolved questions "
        "or topics needing follow-up. Format as a numbered list. "
        "If none found say 'No open questions found.' but try to infer questions from context if possible."
    )

    return invoke_with_retry(chain, transcript)
