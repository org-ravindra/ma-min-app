import os
from pathlib import Path
from dotenv import load_dotenv

from src.ma_app.retriever import Retriever, COLLECTION_NAME

load_dotenv()

DATA_DIR = Path(os.getenv("DATA_DIR", "./data"))
CORPUS_DIR = DATA_DIR / "corpus"

SAMPLE_DOCS = [
    (
        "spark-overview",
        "Apache Spark is a multi-language engine for executing data engineering, data science, and machine learning on single-node machines or clusters.",
    ),
    (
        "spark-structured-streaming",
        "Structured Streaming is a scalable and fault-tolerant stream processing engine built on the Spark SQL engine.",
    ),
    (
        "spark-datasets",
        "A Dataset is a distributed collection of data. Dataset API provides the benefits of RDDs (strong typing, ability to use powerful lambda functions) with the benefits of Spark SQL's optimized execution engine.",
    ),
]


def main():
    CORPUS_DIR.mkdir(parents=True, exist_ok=True)

    # If user has placed .txt files in data/corpus, use them; else write samples
    txt_files = list(CORPUS_DIR.glob("*.txt"))
    if not txt_files:
        for doc_id, text in SAMPLE_DOCS:
            (CORPUS_DIR / f"{doc_id}.txt").write_text(text, encoding="utf-8")
        txt_files = list(CORPUS_DIR.glob("*.txt"))

    docs = []
    ids = []
    metadatas = []

    for f in txt_files:
        text = f.read_text(encoding="utf-8").strip()
        if not text:
            continue
        docs.append(text)
        ids.append(f.stem)
        metadatas.append({"source": str(f.name)})

    # Upsert into Chroma
    r = Retriever()  # ensures collection with embedding fn
    r.col.upsert(documents=docs, ids=ids, metadatas=metadatas)

    print(f"Ingested {len(docs)} docs into collection '{COLLECTION_NAME}'.")


if __name__ == "__main__":
    main()

