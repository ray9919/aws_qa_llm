import base64

import json


import streamlit as st
import requests as req
from typing import List, Tuple, Dict


import datetime
import uuid

import extra_streamlit_components as stx
from streamlit import runtime
from streamlit.runtime.scriptrunner import get_script_run_ctx


# Page title
st.set_page_config(page_title='AWS Q&A', layout='wide')

def get_user_id() -> str:
    cookies = stx.CookieManager()
    if cookies.get("aws_qa_user_id") is None:
        sess_id = str(uuid.uuid4())
        cookies.set("aws_qa_user_id", sess_id, expires_at=datetime.datetime(year=2025, month=12, day=1))

    aws_qa_user_id = cookies.get("aws_qa_user_id")
    print(f'aws_qa_user_id = {aws_qa_user_id}')
    return aws_qa_user_id


def get_all_cookies():
    cm = stx.CookieManager()
    for c in cm.get_all():
        print(f'cookie = {c} ,value = {cm.get(c)}')


"""Get remote ip."""


def get_remote_ip() -> str:
    try:
        ctx = get_script_run_ctx()
        if ctx is None:
            return None

        session_info = runtime.get_instance().get_client(ctx.session_id)
        if session_info is None:
            return None
    except Exception as e:
        return None

    return session_info.request.remote_ip



# def _get_session():
#     from streamlit.runtime import get_instance
#     from streamlit.runtime.scriptrunner import get_script_run_ctx
#     runtime = get_instance()
#     session_id_str = get_script_run_ctx().session_id
#     session_info = runtime._session_mgr.get_session_info(session_id_str)
#     if session_info is None:
#         raise RuntimeError("Couldn't get your Streamlit Session object.")
#     return session_info.session.id


# 生成唯一的会话 ID
session_id = get_user_id()
outputs = {}

# global constants
STREAMLIT_SESSION_VARS: List[Tuple] = [("generated", []), ("past", []), ("input", ""), ("stored_session", [])]
HTTP_OK: int = 200

# two options for the chatbot, 1) get answer directly from the LLM
# 2) use RAG (find documents similar to the user query and then provide
# those as context to the LLM).
MODE_RAG: str = 'RAG'
MODE_TEXT2TEXT: str = 'Text Generation'
MODE_VALUES: List[str] = [MODE_RAG, MODE_TEXT2TEXT]

api_rag_ep: str = 'https://9ey0k10ca3.execute-api.us-east-1.amazonaws.com/dev/aws_qa_llm_chat_entry'

print(f"api_rag_ep={api_rag_ep}")

####################
# Streamlit code
####################


# keep track of conversations by using streamlit_session
_ = [st.session_state.setdefault(k, v) for k, v in STREAMLIT_SESSION_VARS]


# Define function to get user input
def get_user_input() -> str:
    """
    Returns the text entered by the user
    """
    # print(st.session_state)
    input_text = st.text_input("You: ",
                               st.session_state["input"],
                               key="input",
                               placeholder="Please input your question",
                               label_visibility='hidden')

    return input_text


st.title("AWS Q&A")
st.subheader(
    f" Powered by AWS Bedrock")

with st.sidebar:
    st.subheader('control panel')
    btns = st.container()

    if btns.button("clear context"):
        for key in st.session_state.keys():
            del st.session_state[key]
        # TODO should call api to remove history in dynamodb
        st.experimental_rerun()

# get user input
user_input: str = get_user_input()
mode = MODE_RAG
# based on the selected mode type call the appropriate API endpoint
if user_input:
    # headers for request and response encoding, same for both endpoints
    headers: Dict = {"accept": "text/plain", "Content-Type": "text/plain"}
    output: str = None
    print(f'user_input = {user_input}')
    payload = {
        'user_input': user_input,
        'session_id': session_id
    }
    json_string = json.dumps(payload)
    base64data = base64.b64encode(json_string.encode('utf-8')).decode('utf-8')
    print(f'base64data = {base64data}')
    resp = req.post(api_rag_ep, headers=headers, json=base64data)
    if resp.status_code != HTTP_OK:
        output = resp.text
    else:
        resp = resp.json()
        # print(resp)
        # sources = [d['metadata']['source'] for d in resp['docs']]
        output = resp['answer']

    print(f'resp={resp}')
    st.session_state.past.append(user_input)
    st.session_state.generated.append(output)

# download the chat history
download_str: List = []
with st.expander("History", expanded=True):
    for i in range(len(st.session_state['generated']) - 1, -1, -1):
        st.info(st.session_state["past"][i], icon="❓")
        st.success(st.session_state["generated"][i], icon="👩‍💻")
        download_str.append(st.session_state["past"][i])
        download_str.append(st.session_state["generated"][i])

    download_str = '\n'.join(download_str)
    if download_str:
        st.download_button('Download', download_str)
