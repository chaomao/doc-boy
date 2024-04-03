import chromadb
from chromadb.config import Settings
from datetime import datetime
from langchain.embeddings.openai import OpenAIEmbeddings
import re
import os
import json
import psycopg2
import psycopg2.extras as extras

t1 = datetime.now()

ONLY_COPY_SOURE_TYPES = ['doc']

BATCH_SIZE = 1000
DB_NAME = os.getenv("DB_NAME", "gitlabhq_development_embedding")
TABLE_NAME = os.getenv("TABLE_NAME", "tanuki_bot_mvc")
PG_HOST = os.getenv("PG_HOST", "localhost")
PG_USER = os.getenv("PG_USER", "postgres")
PG_PASS = os.getenv("PG_PASS", "password")
PG_PORT = os.getenv("PG_PORT", "5432")

embedding = OpenAIEmbeddings()
persist_directory = '../db_new_categorized'
collection_name = 'langchain'
client = chromadb.Client(Settings(
    chroma_db_impl="duckdb+parquet",
    persist_directory=persist_directory
))
collection = client.get_collection(name=collection_name, embedding_function=embedding)
result = collection.get(include=["documents", "embeddings", "metadatas"])

def generate_url(metadata):
    source = metadata['source']
    match metadata['source_type']:
        case 'doc':
            path = re.sub('doc/', '', source, count = 1)
            page = re.sub('.md', '', path, count = 1)
            return "https://docs.gitlab.com/ee/%s" % (page)
        case 'handbook':
            path = re.sub('handbook/', '', source, count = 1)
            page = re.sub('.(md|erb)', '', path, count = 1)
            return "https://about.gitlab.com/%s" % (page)
        case _: # blog
            page = re.sub('.(md|erb)', '', path, count = 1)
            "https://about.gitlab.com/%s" % (page)


typles = []
for idx, chroma_id in enumerate(result['ids']):
    metadata = result['metadatas'][idx]

    if metadata['source_type'] in ONLY_COPY_SOURE_TYPES:
        document = result['documents'][idx]
        url = generate_url(metadata)
        embeddings = result['embeddings'][idx]
        timestamp = datetime.now()
        typles.append((chroma_id, json.dumps(metadata), document, url, embeddings, timestamp, timestamp))

conn = psycopg2.connect(database=DB_NAME, host=PG_HOST, user=PG_USER, password=PG_PASS, port=PG_PORT)
cursor = conn.cursor()

query = "INSERT INTO %s (%s) VALUES %%s" % (TABLE_NAME, "chroma_id, metadata, content, url, embedding, created_at, updated_at")

def batch(iterable, n=1):
    l = len(iterable)
    for ndx in range(0, l, n):
        yield iterable[ndx:min(ndx + n, l)]

total = len(typles)
print("Total number of records: %i" % total)
i = 0
for t in batch(typles, BATCH_SIZE):
    extras.execute_values(cursor, query, t)
    conn.commit()
    i += len(t)
    percentage = round((float(i + 1) / total) * 100, 2)
    print("Processed: %i (%.2f%%)" % (i, percentage))

cursor.close()

t2 = datetime.now()
print("Elapsed: %is (%im)" % ((t2 - t1).seconds, (t2 - t1).seconds / 60))
