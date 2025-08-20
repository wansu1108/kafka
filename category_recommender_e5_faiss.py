
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Category Recommender (E5 + FAISS Exact Search)
----------------------------------------------
- Uses sentence-transformers (intfloat/multilingual-e5-base) for embeddings
- Uses FAISS IndexFlatIP (cosine via L2-normalized vectors) for fast top-k
- Optional: skip reranker or plug your cross-encoder

Requirements:
    pip install sentence-transformers faiss-cpu numpy

Run:
    python category_recommender_e5_faiss.py
"""

from __future__ import annotations
import numpy as np
import re, os
from typing import List, Dict, Any, Tuple

from sentence_transformers import SentenceTransformer
import faiss

# ---------- Sample categories (same as v2, minimal) ----------
CATEGORIES = [
    {"code":"1001","path":"HOME > Tools","desc":"General purpose tools for home use",
     "keywords":["공구","툴","드라이버","렌치","가위","가정용"],
     "synonyms":["도구","수공구"]},
    {"code":"1002","path":"HOME > Tools > living","desc":"Everyday living tools and household aids",
     "keywords":["생활 공구","생활 도구","집","가정"],
     "synonyms":["생활용품","하우스웨어"]},
    {"code":"1003","path":"HOME > Tools > living > general","desc":"General small tools used in daily life",
     "keywords":["다용도","일상","간편","가위","커터"],
     "synonyms":["문구 가위","만능 가위","커터칼"]},
    {"code":"1101","path":"HOME > Kitchen > Cookware","desc":"Pots, pans and cooking vessels",
     "keywords":["프라이팬","팬","냄비","웍","스테인리스","코팅"],
     "synonyms":["후라이팬","프라이 팬"]},
    {"code":"1102","path":"HOME > Kitchen > Cutlery","desc":"Kitchen knives, scissors, and cutting tools",
     "keywords":["주방용 가위","식도","칼","절삭"],
     "synonyms":["키친 가위","부엌 가위"]},
    {"code":"2001","path":"ELECTRONICS > Laptop > Gaming","desc":"High performance gaming laptops",
     "keywords":["게이밍","RTX","고성능","RGB","쿨링","노트북"],
     "synonyms":["게이밍 노트북","그래픽 노트북"]},
    {"code":"2002","path":"ELECTRONICS > Laptop > Ultrabook","desc":"Thin and light ultrabooks",
     "keywords":["슬림","경량","울트라북","휴대성","노트북"],
     "synonyms":["초경량 노트북","라이트 노트북"]},
    {"code":"2101","path":"ELECTRONICS > Audio > Headphones","desc":"Over-ear and in-ear headphones",
     "keywords":["헤드폰","이어폰","노이즈캔슬링","블루투스"],
     "synonyms":["헤드셋","헤드 세트"]},
    {"code":"3001","path":"BEAUTY > Skincare > Cleanser","desc":"Facial cleansers and face wash products",
     "keywords":["클렌저","세안","폼클렌징","저자극"],
     "synonyms":["세안폼","폼클렌저"]},
    {"code":"3002","path":"BEAUTY > Hair > Dryer","desc":"Hair dryers and styling dryers",
     "keywords":["헤어드라이어","드라이기","강풍","온도조절"],
     "synonyms":["헤어 드라이어","헤어 드라이기"]},
    {"code":"4001","path":"SPORTS > Fitness > Treadmill","desc":"Home treadmills and running machines",
     "keywords":["런닝머신","트레드밀","접이식","가정용"],
     "synonyms":["러닝머신","러닝 머신"]},
    {"code":"4002","path":"SPORTS > Outdoor > Camping > Tent","desc":"Camping tents for outdoor use",
     "keywords":["텐트","캠핑","방수","4인용"],
     "synonyms":["원터치 텐트","돔 텐트"]},
    {"code":"5001","path":"FASHION > Men > Shoes > Sneakers","desc":"Men's sneakers and casual shoes",
      "keywords":["스니커즈","운동화","러닝화","경량"],
      "synonyms":["스니커","슈즈"]},
    {"code":"5002","path":"FASHION > Women > Bag > Tote","desc":"Women's tote bags",
      "keywords":["토트백","가죽","수납","데일리백"],
      "synonyms":["토트 백","숄더 토트"]},
    {"code":"6001","path":"AUTOMOTIVE > Parts > Wiper","desc":"Car wiper blades and accessories",
      "keywords":["와이퍼","자동차","빗물제거","블레이드"],
      "synonyms":["차량용 와이퍼"]},
    {"code":"7001","path":"PET > Dog > Food > Dry","desc":"Dry dog food and kibble",
      "keywords":["강아지 사료","드라이","소형견","전연령"],
      "synonyms":["건식 사료"]},
    {"code":"8001","path":"BABY > Diaper > Tape","desc":"Tape diapers for babies",
      "keywords":["기저귀","테이프형","흡수","피부"],
      "synonyms":["테이프 기저귀"]},
    {"code":"9001","path":"GROCERY > Beverage > Coffee","desc":"Coffee beans, ground coffee, and instant",
      "keywords":["커피","원두","드립","인스턴트"],
      "synonyms":["드립백","드립 백","원두커피"]},
    {"code":"10001","path":"OFFICE > Stationery > Scissors","desc":"Office and stationery scissors",
      "keywords":["가위","문구","스테인리스","보관 캡"],
      "synonyms":["사무용 가위","스테인레스 가위"]},
    {"code":"10002","path":"OFFICE > Stationery > Tape Dispenser","desc":"Tape dispensers and cutters",
      "keywords":["테이프","디스펜서","커터기","사무"],
      "synonyms":["테이프 홀더","테이프 커터"]},
]

def label_text(cat):
    kw = ", ".join(cat["keywords"])
    syn = ", ".join(cat.get("synonyms", []))
    return f"category: {cat['path']}. desc: {cat['desc']}. keywords: {kw}. synonyms: {syn}"

def build_query(title: str, spec: str = "") -> str:
    def norm(t):
        t = re.sub(r"[()\\[\\]{}]", " ", t)
        t = re.sub(r"\\s+", " ", t).strip()
        return t
    return f"제목: {norm(title)} [SEP] 규격: {norm(spec)}"

def build_label_index(model: SentenceTransformer):
    texts = [label_text(c) for c in CATEGORIES]
    emb = model.encode(texts, normalize_embeddings=True, show_progress_bar=False).astype('float32')
    index = faiss.IndexFlatIP(emb.shape[1])
    # map ids to codes using IndexIDMap
    index = faiss.IndexIDMap2(index)
    ids = np.array([int(c['code']) for c in CATEGORIES], dtype='int64')
    index.add_with_ids(emb, ids)
    return index

def recommend(model: SentenceTransformer, index, title, spec, k=3):
    q = model.encode([build_query(title, spec)], normalize_embeddings=True, show_progress_bar=False).astype('float32')
    sims, ids = index.search(q, max(k, 10))
    results = []
    for i in range(k):
        code = str(ids[0][i])
        cat = next(c for c in CATEGORIES if c['code'] == code)
        results.append({"path": cat["path"], "code": code, "cosine": float(sims[0][i])})
    return results

def main():
    print(">> Load E5 model... (intfloat/multilingual-e5-base)")
    model = SentenceTransformer("intfloat/multilingual-e5-base")
    print(">> Build FAISS index...")
    index = build_label_index(model)

    QUERIES = [
        ("가위",""),
        ("스테인리스 주방 가위 21cm",""),
        ("게이밍 노트북 rtx4060",""),
        ("프라이팬 28cm",""),
        ("4인용 방수 텐트",""),
        ("자동차 와이퍼 블레이드",""),
        ("커피 드립백",""),
        ("사무용 테이프 커터기",""),
    ]

    print("\n=== E5 + FAISS (Top-3) ===")
    for title, spec in QUERIES:
        recs = recommend(model, index, title, spec, k=3)
        print(f"\n입력: {title} {spec}")
        for i, r in enumerate(recs, 1):
            print(f"{i}. {r['path']} (code={r['code']}, cosine={r['cosine']:.4f})")

if __name__ == "__main__":
    main()
