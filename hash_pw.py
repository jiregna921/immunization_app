import streamlit_authenticator as stauth

passwords = ["StrongPass1!", "AnotherPass2!"]  # replace with your real ones
hashes = stauth.Hasher(passwords).generate()
for pw, h in zip(passwords, hashes):
    print(pw, "->", h)
