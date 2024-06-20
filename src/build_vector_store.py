import os
import ssl

import nltk
from dotenv import load_dotenv
from langchain.embeddings.openai import OpenAIEmbeddings
from llama_index.core import (Settings, SimpleDirectoryReader, StorageContext,
                              VectorStoreIndex)
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.llms.openai import OpenAI
from llama_index.readers.file import HTMLTagReader, UnstructuredReader
from llama_index.vector_stores.pinecone import PineconeVectorStore
from pinecone import Pinecone


class DocumentIngestion:
    def __init__(self, input_dir, pinecone_api_key, index_name):
        self.input_dir = input_dir
        self.pinecone_api_key = pinecone_api_key
        self.index_name = index_name

    def initialize_nltk(self):
        """Initialize the NLTK library and download the required resource."""
        ssl._create_default_https_context = ssl._create_unverified_context
        nltk.download("averaged_perceptron_tagger")

    def load_documents(self):
        """
        Load documents from the specified directory using SimpleDirectoryReader.

        Returns:
            list: A list of loaded documents.
        """
        dir_reader = SimpleDirectoryReader(
            input_dir=self.input_dir,
            file_extractor={".html": UnstructuredReader()},
        )
        documents = dir_reader.load_data()
        print(f"Number of documents: {len(documents)}")
        return documents

    def setup_node_parser(self):
        """
        Set up the SimpleNodeParser with default settings.

        Returns:
            SimpleNodeParser: Configured node parser.
        """
        return SimpleNodeParser.from_defaults(chunk_size=500, chunk_overlap=20)

    def setup_models(self):
        """
        Initialize the OpenAI language model and embedding model, and set global settings.

        Returns:
            tuple: A tuple containing the LLM and embedding model.
        """
        llm = OpenAI(model="gpt-3.5-turbo", temperature=0)
        embed_model = OpenAIEmbeddings(
            model="text-embedding-ada-002",
            embed_batch_size=100,
        )
        Settings.llm = llm
        Settings.embed_model = embed_model
        return llm, embed_model

    def setup_pinecone(self):
        """
        Initialize Pinecone and create or connect to the specified index.

        Returns:
            PineconeVectorStore: Configured Pinecone vector store.
        """
        pc = Pinecone(api_key=self.pinecone_api_key)
        pinecone_index = pc.Index(name=self.index_name)
        return PineconeVectorStore(pinecone_index=pinecone_index)

    def create_storage_context(self, vector_store):
        """
        Create a StorageContext using the specified vector store.

        Returns:
            StorageContext: Configured storage context.
        """
        return StorageContext.from_defaults(vector_store=vector_store)

    def create_index(self, documents, storage_context):
        """
        Create a VectorStoreIndex from the loaded documents and storage context.

        Args:
            documents (list): List of documents to index.
            storage_context (StorageContext): The storage context to use for the index.

        Returns:
            VectorStoreIndex: Configured vector store index.
        """
        VectorStoreIndex.from_documents(
            documents=documents,
            storage_context=storage_context,
            show_progress=True,
        )
        print("Finished ingesting...")


def main():
    # Load environment variables
    load_dotenv()

    # Initialize DocumentIngestion with necessary parameters
    ingestion = DocumentIngestion(
        input_dir="../data/",
        pinecone_api_key=os.environ["PINECONE_API_KEY"],
        index_name="langchain-doc-query-app",
    )

    # Initialize NLTK
    ingestion.initialize_nltk()

    # Load documents
    documents = ingestion.load_documents()

    # Set up node parser
    node_parser = ingestion.setup_node_parser()

    # Set up models
    llm, embed_model = ingestion.setup_models()

    # Set up Pinecone vector store
    vector_store = ingestion.setup_pinecone()

    # Create storage context
    storage_context = ingestion.create_storage_context(vector_store=vector_store)

    # Create vector store index
    ingestion.create_index(documents=documents, storage_context=storage_context)


if __name__ == "__main__":
    main()
