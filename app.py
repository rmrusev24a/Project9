import streamlit as st
from PIL import Image
import pytesseract

st.title("Скенер за вредни съставки")

uploaded_file = st.file_uploader(
    "Качи снимка",
    type=["jpg", "jpeg", "png"]
)

harmful = [
    "E621",
    "E102",
    "E110",
    "палмово масло",
    "Aspartame"
]

if uploaded_file:

    image = Image.open(uploaded_file)

    st.image(image)

    text = pytesseract.image_to_string(image)

    st.subheader("Разпознат текст:")
    st.write(text)

    st.subheader("Резултат:")

    found = False

    for item in harmful:
        if item.lower() in text.lower():
            st.error(f"Намерено: {item}")
            found = True

    if not found:
        st.success("Няма намерени вредни съставки.")
