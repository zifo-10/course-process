import os
import uuid

import pandas as pd
from openai import OpenAI
from dotenv import load_dotenv

from app.client.vector_db import QdrantDBClient

# Load environment variables
load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Embedding model
EMBEDDING_MODEL = "text-embedding-3-small"

vectordb_client = QdrantDBClient(
        host='http://162.250.127.92/',
        port=6333
    )
#
file_path = '/home/zifo/Documents/zedny/data/skills_en.csv'

# Read the Excel file into a pandas DataFrame
df = pd.read_csv(file_path)

def process_skills():
    print("Columns in the file:", df.columns)
    # Clean the column names by stripping leading/trailing spaces
    df.columns = df.columns.str.strip()
    for index, row in df.iterrows():
        english_text = row['Name']
        print(english_text)
        skill_id = row['SkillId']
        print(skill_id)
        if pd.isna(english_text):
            continue
        embed = client.embeddings.create(
                            input=english_text,
                            model=EMBEDDING_MODEL
                        )
        print('*********',embed.data[0].embedding)
        vectordb_client.insert_point(
            collection_name='skills_en',
            uuid=str(uuid.uuid4()),
            vector=embed.data[0].embedding,
            payload={
                'skill_en': english_text,
                'skill_id': skill_id
            }
        )

def process_objective():
    print("Columns in the file:", df.columns)

    # Clean the column names by stripping leading/trailing spaces
    df.columns = df.columns.str.strip()

    for index, row in df.iterrows():
        english_text = row['English Objectives']
        arabic_text = row['Arabic Objectives']
        if pd.isna(english_text):
            continue
        embed = client.embeddings.create(
                            input=arabic_text,
                            model=EMBEDDING_MODEL
                        )
        print('*********',embed.data[0].embedding)
        vectordb_client.insert_point(
            collection_name='objective',
            uuid=str(uuid.uuid4()),
            vector=embed.data[0].embedding,
            payload={
                'objective_en': english_text,
                'objective_ar': arabic_text
            }
        )

process_skills()
# process_objective()




# -----------------------------------------------------------------
# response = client.embeddings.create(
#                     input=skill,
#                     model=EMBEDDING_MODEL
#                 )


# #
# vectordb_client.create_collection(collection_name='skills_en',
#                                   collection_size=1536)