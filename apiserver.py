from langchain.llms import OpenAI
from langchain.chains.qa_with_sources import load_qa_with_sources_chain
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import Chroma
from langchain.document_loaders import TextLoader
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chains import VectorDBQAWithSourcesChain

from flask import Flask, request
import json 

persist_directory = './db_new_categorized'
embedding = OpenAIEmbeddings()

# Now we can load the persisted database from disk, and use it as normal. 
vectordb = Chroma(persist_directory=persist_directory, embedding_function=embedding)
chain = load_qa_with_sources_chain(OpenAI(temperature=0), chain_type="map_reduce")

print(vectordb)

# Setup flask server
app = Flask(__name__) 
  
@app.route('/ask', methods = ['GET']) 
def ask_result(): 
    args = request.args
    print(args.get("q"))
    print(args.get("source"))

    sub_filter = None
    if (args.get("source")):
        sub_filter = {"source_type":args.get("source")}

    print(sub_filter)


    # Return data in json format 
    query = args.get('q')

    # docs = vectordb.similarity_search_with_score(query)
    if query is not None:
        docs_from_search_result = vectordb.similarity_search_with_score(query=query, k=7, filter=sub_filter)
        if len(docs_from_search_result)>0:
            docs_from_search = []
            for doc_result in docs_from_search_result:
                docs_from_search.append(doc_result[0])

            print('Similarity Search Done')

            result = chain({"input_documents": docs_from_search, "question": query}, return_only_outputs=True)

            result_split = result["output_text"].split("SOURCES:")

            msg = result_split[0].strip()
            sources = result_split[1].strip()

            print('MSG');
            print(msg)

            result_sources = sources.split(",")

            result_metadata = []
            for sourcefile in result_sources:
                sourcefile = sourcefile.strip()
                for doc in docs_from_search:
                    if doc.metadata["source"] == sourcefile:
                        result_metadata.append(doc.metadata)
                        break

            print(result_metadata)

            
            result_obj = {"msg": msg, "sources": result_metadata}
            print('Sending Result')
            print(result_obj)
            return json.dumps(result_obj)
        else:
            return json.dumps({})
    else:
        return json.dumps({})
if __name__ == "__main__": 
    app.run(port=5000, debug=True)
