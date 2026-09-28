# Adding Authentication to the Streamlit App

This guide covers three ways to put a login in front of the interview-practice app,
from the lightest to the most complete, and recommends one.

| Approach | Best for | Effort | User accounts |
|---|---|---|---|
| [1. Shared password gate](#1-shared-password-gate) | Private demo, a few testers | ~5 min | No (one password) |
| [2. Built-in OIDC login (`st.login`)](#2-built-in-oidc-login-stlogin) — **recommended** | Deployed app, real users | ~20 min | Yes (Google / Microsoft / Auth0 / Okta …) |
| [3. `streamlit-authenticator`](#3-streamlit-authenticator) | Own username/password list, no external provider | ~15 min | Yes (stored in a YAML file) |

**Recommendation:** use **built-in OIDC login** (option 2) with Google. It is part of
Streamlit itself, there are no passwords for you to store or hash, and `st.user.email` gives
you a stable identity to attach each user's practice sessions and interview history to.
Use the password gate (option 1) if you only need to keep a demo private for now.

---

## Before you start

### Keep secrets out of git

All three options read credentials from `.streamlit/secrets.toml`. **Never commit that file.**
The repo has no `.gitignore` yet, so create one in the project root:

```gitignore
# Streamlit secrets
.streamlit/secrets.toml

# Python
__pycache__/
*.pyc
.venv/
venv/
```

### Install Streamlit

```bash
pip install streamlit
```

Put the dependencies in `requirements.txt` as well, because Streamlit Community Cloud reads it
during deployment.

---

## 1. Shared password gate

Everyone uses the same password. This is fine for keeping a work-in-progress app away from
the public, but it can't tell users apart.

**`.streamlit/secrets.toml`**

```toml
password = "choose-a-long-random-password"
```

**`test-app.py`** (or your main app file)

```python
import hmac
import streamlit as st


def check_password() -> bool:
    """Return True once the user has entered the correct password."""
    if st.session_state.get("password_correct"):
        return True

    def password_entered():
        # compare_digest avoids leaking information through timing differences
        if hmac.compare_digest(st.session_state["password"], st.secrets["password"]):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't keep the plaintext around
        else:
            st.session_state["password_correct"] = False

    st.text_input("Password", type="password", on_change=password_entered, key="password")
    if st.session_state.get("password_correct") is False:
        st.error("Incorrect password")
    return False


if not check_password():
    st.stop()  # nothing below this line runs until the password is correct

st.title("Hello World!")
```

---

## 2. Built-in OIDC login (`st.login`)

Streamlit (1.42 and later) has native OpenID Connect login. Users sign in with an existing
account, and Streamlit stores the identity in a signed cookie.

### 2.1 Install the auth extra

```bash
pip install "streamlit[auth]"
```

This installs `Authlib`, which Streamlit needs for OIDC. In `requirements.txt`, write
`streamlit[auth]` rather than plain `streamlit`.

### 2.2 Create a Google OAuth client

1. Open the [Google Cloud Console](https://console.cloud.google.com/) and create or select a project.
2. Go to **APIs & Services → OAuth consent screen**, choose **External**, and fill in the
   required fields. While the app is in *Testing* mode, add your testers' Google accounts
   under **Test users**.
3. Go to **APIs & Services → Credentials → Create credentials → OAuth client ID**.
   - Application type: **Web application**
   - Authorized redirect URIs:
     - `http://localhost:8501/oauth2callback` (local development)
     - `https://<your-app>.streamlit.app/oauth2callback` (once deployed)
4. Copy the **Client ID** and **Client secret**.

### 2.3 Configure `.streamlit/secrets.toml`

```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "a-long-random-string"   # generate one, see below
client_id = "xxxxxxxx.apps.googleusercontent.com"
client_secret = "GOCSPX-xxxxxxxx"
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"
```

To generate a `cookie_secret`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2.4 Use it in the app

```python
import streamlit as st

if not st.user.is_logged_in:
    st.title("Interview Practice")
    st.write("Please sign in to start practising.")
    st.button("Log in with Google", on_click=st.login)
    st.stop()

# --- Everything below this line is only visible to signed-in users ---
with st.sidebar:
    st.write(f"Signed in as **{st.user.name}**")
    st.caption(st.user.email)
    st.button("Log out", on_click=st.logout)

st.title(f"Welcome, {st.user.given_name or st.user.name}!")
```

`st.user` behaves like a dictionary of the identity token's claims. For Google, the useful
claims are `email`, `name`, `given_name`, `picture` and `sub`, which is a stable unique user ID.
Use `sub` or `email` as the key when you save a user's interview history.

> **Version note:** before Streamlit 1.45, the attribute was called `st.experimental_user`.
> If `st.user` raises an `AttributeError`, upgrade Streamlit.

### 2.5 Offering several providers (optional)

To offer more than one provider, give each one its own named section and pass the name to `st.login`:

```toml
[auth]
redirect_uri = "http://localhost:8501/oauth2callback"
cookie_secret = "a-long-random-string"

[auth.google]
client_id = "..."
client_secret = "..."
server_metadata_url = "https://accounts.google.com/.well-known/openid-configuration"

[auth.microsoft]
client_id = "..."
client_secret = "..."
server_metadata_url = "https://login.microsoftonline.com/common/v2.0/.well-known/openid-configuration"
```

```python
st.button("Log in with Google", on_click=st.login, args=["google"])
st.button("Log in with Microsoft", on_click=st.login, args=["microsoft"])
```

### 2.6 Restricting who can get in (optional)

Signing in only proves who a user is. It doesn't limit which users can reach the app. To allow
only certain users, check the email after login:

```python
ALLOWED = set(st.secrets.get("allowed_emails", []))

if ALLOWED and st.user.email not in ALLOWED:
    st.error("Your account doesn't have access to this app.")
    st.button("Log out", on_click=st.logout)
    st.stop()
```

```toml
allowed_emails = ["you@example.com", "mentor@example.com"]
```

---

## 3. `streamlit-authenticator`

This is a community package that keeps usernames and **hashed** passwords in a YAML file.
Choose it when you need separate accounts but don't want an external identity provider.

```bash
pip install streamlit-authenticator
```

> The package's API has changed a lot between versions. The code below targets **0.4.x**,
> so pin that version in `requirements.txt` and check the
> [project README](https://github.com/mkhorasani/Streamlit-Authenticator) if something doesn't match.

**`config.yaml`** (add it to `.gitignore` if it holds real users)

```yaml
credentials:
  usernames:
    jsmith:
      email: jsmith@example.com
      first_name: John
      last_name: Smith
      password: "plain-text-on-first-run"   # hashed automatically, see below
cookie:
  name: interview_app_auth
  key: a-long-random-string
  expiry_days: 30
```

**App code**

```python
import yaml
import streamlit as st
import streamlit_authenticator as stauth
from yaml.loader import SafeLoader

with open("config.yaml") as f:
    config = yaml.load(f, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config["credentials"],
    config["cookie"]["name"],
    config["cookie"]["key"],
    config["cookie"]["expiry_days"],
    auto_hash=True,  # hashes plain-text passwords in memory
)

authenticator.login()

status = st.session_state.get("authentication_status")
if status is False:
    st.error("Username or password is incorrect")
    st.stop()
if status is None:
    st.warning("Please enter your username and password")
    st.stop()

authenticator.logout(location="sidebar")
st.title(f"Welcome, {st.session_state['name']}!")
```

After the first run, replace the plain-text passwords in `config.yaml` with hashes so the file
never contains real passwords:

```python
import streamlit_authenticator as stauth
print(stauth.Hasher.hash("the-password"))
```

---

## Deploying to Streamlit Community Cloud

1. Push the repo to GitHub, making sure `secrets.toml` is **not** included.
2. On [share.streamlit.io](https://share.streamlit.io), create the app and choose the main file.
3. In **App settings → Secrets**, paste the contents of your local `secrets.toml`.
   For OIDC, change `redirect_uri` to `https://<your-app>.streamlit.app/oauth2callback`.
4. For OIDC, check that the same redirect URI is listed in the Google OAuth client.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| `redirect_uri_mismatch` from Google | The `redirect_uri` in secrets doesn't match an **Authorized redirect URI** exactly (check the port, http vs https, and trailing slash). |
| `Authlib` import error when calling `st.login` | You installed `streamlit` instead of `streamlit[auth]`. |
| `AttributeError: st.user` | Your Streamlit version is older than 1.45. Upgrade it, or use `st.experimental_user`. |
| Google "Access blocked: app not verified" | The consent screen is in *Testing* mode and this account isn't listed under **Test users**. |
| Logged out after every redeploy | `cookie_secret` changed between deploys. Keep it fixed in secrets. |
| `KeyError` for `st.secrets[...]` | `.streamlit/secrets.toml` is missing or not in the directory you ran `streamlit run` from. |
