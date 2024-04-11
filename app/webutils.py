import datetime
import uuid

import extra_streamlit_components as stx
from streamlit import runtime
from streamlit.runtime.scriptrunner import get_script_run_ctx


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
