from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

import os 

def get_llm():        
    return ChatGroq(model="qwen/qwen3.8-27b",temperature=0.2)

def split_transcript(transcript:str)-> list:
    splitter=RecursiveCharacterTextSplitter(
        chunk_size=3000,
        chunk_overlap=200
    )
    return splitter.split_text(transcript)

def summarize(transcript:str)-> str:
    llm=get_llm()
    map_prompt=ChatPromptTemplate.from_messages(
        [
            ('system','Summarize the following transcript into a concise summary in 3-4 sentences.'),
            ('human','{text}')
        ]
    )

    map_chain=map_prompt | llm | StrOutputParser()

    chunks=split_transcript(transcript)
    summaries=[]
    for chunk in chunks:
        summary=map_chain.invoke({'text':chunk})
        summaries.append(summary)

    combined="\n\n".join(summaries)

    combined_prompt=ChatPromptTemplate.from_messages(
        [
            ('system','You are an expert meeting summarizer. Combine the partial summaries into one final professional meeting summary in bullet points.'),
            ('human','{text}')
        ]
    )

    combined_chain=(RunnablePassthrough() | RunnableLambda(lambda x:{"text":x}) | combined_prompt | llm | StrOutputParser())
    final_summary=combined_chain.invoke({'text':combined})

    return final_summary

def generate_title(transcript:str)-> str:
    llm=get_llm()
    title_prompt=ChatPromptTemplate.from_messages(
        [
            ('system','You are an expert meeting summarizer. Generate a concise and descriptive title for the following transcript. Max 8 words.'),
            ('human','{text}')
        ]
    )

    title_chain=(RunnablePassthrough() | RunnableLambda(lambda x:{"text":x}) | title_prompt | llm | StrOutputParser())
    title=title_chain.invoke({'text':transcript[:2000]})

    return title

