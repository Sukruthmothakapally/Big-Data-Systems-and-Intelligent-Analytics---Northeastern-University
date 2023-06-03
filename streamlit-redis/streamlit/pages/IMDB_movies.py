import os
import redis
import pandas as pd
import streamlit as st
from redis.commands.search.query import Query

#to convert json to dataframe
def docs_to_dict(docs):
    reslist = []
    for doc in docs:
        # meta = {"id": getattr(doc, "id"), "score": getattr(doc, "score")}
        fields = {}
        for field in dir(doc):
            if (field.startswith('__') or field == 'id' or field == 'score' or field == 'payload'):
                continue
            fields.update({field: getattr(doc, field)})
        # ddict = {"meta": meta, "fields": fields};
        # reslist.append(ddict)
        reslist.append(fields)
    return reslist

st.title('IMDB Movies')

redis_conn = redis.Redis(host=os.getenv("DB_HOST", "localhost"),
                         port=os.getenv("DB_PORT", 6379),
                         username=os.getenv("DB_USERNAME", ""),
                         password=os.getenv("DB_PASSWORD", ""),
                         decode_responses=True
                         )

st.subheader("DB Hash Count")
col1, col2, col3 = st.columns(3)
col1.metric("Movies", len(redis_conn.keys("movie:*")))
col2.metric("Theator", len(redis_conn.keys("theator:*")))
col3.metric("Users", len(redis_conn.keys("user:*")))

st.divider()


with st.form("form_1", clear_on_submit=True):
    st.subheader(
        "Find all the movies that contain the word 'heat' or related to 'heat'")

    queryString = st.text_input("Movie title", value="Heat",
                                placeholder="Enter movie title", key="user-input-search-title", type='default')
    limit = st.slider("Result Limit", min_value=1, max_value=10, value=3, step=1,
                      format="%d", key="result-limit-slider", disabled=False, label_visibility="visible")
    raw_data_checkbox = st.checkbox('Show raw data')

    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    if submitted:
        redis_index = r"idx:movie"
        q = Query(queryString).with_scores().paging(0, limit)

        searchResult = redis_conn.ft(index_name=redis_index).search(q)
        # print(searchResult.docs)
        dictResult = {
            "meta": {
                "totalResults": getattr(searchResult, "total"),
                "offset": 0,
                "limit": limit,
                "queryString": queryString},
            "docs": docs_to_dict(searchResult.docs)
        }
        if raw_data_checkbox:
            st.json(dictResult['docs'])

        df = pd.DataFrame(dictResult['docs'])
        # print(df.columns.tolist())
        st.dataframe(df[['ibmdb_id', 'title', 'release_year',
                     'genre', 'rating', 'plot', 'poster', 'votes']])


st.divider()