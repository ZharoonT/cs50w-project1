from flask import redirect, request, session
from functools import wraps

def validadte_sesion_state(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get("user_id_sesion") is None:
            return redirect("/login")
        else:
            return redirect("/")
            
    return decorated_function