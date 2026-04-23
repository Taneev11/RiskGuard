""""
# Testing out Streamlit UI app
"""
import streamlit as st
import polars as pl
import httpx

st.set_page_config(page_title='PSQL Test', layout='wide')
st.title('Psql -> FastAPI -> Streamlit')

#fetch from backend
def fetch_data():
    try:
        with httpx.Client(trust_env=False) as client:
            #Call Fastapi
            response = client.get("http://127.0.0.1:8000/table1")
            response.raise_for_status()

            #load json into polars dataframe
            return pl.DataFrame(response.json())
    except Exception as e:
        st.error(e)
        return pl.DataFrame()

if st.button('Refresh Data'):
    df = fetch_data()
    if not df.is_empty():
        st.subheader('Database Records')
        st.dataframe(df, width=True)
        st.info(f"Total rows retrieved: {df.height}")
    else:
        st.warning('No data found')