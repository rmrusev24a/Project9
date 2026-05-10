import streamlit as st
from PIL import Image
import numpy as np
import easyocr

st.set_page_config(page_title="Food Scanner")

st.title("Скенер за вредни съставки")

st.write("Качи снимка на етикет.")

uploaded_file = st.file_uploader(
    "Избери снимка",
    type=["png", "jpg", "jpeg"]
)

# Вредни съставки
harmful = [
    "e621",
    "e102",
    "e110",
    "палмово масло",
    "aspartame"
]

if uploaded_file is not None:

    image = Image.open(uploaded_file)

    st.image(image, caption="Качена снимка")

    img = np.array(image)

    st.write("Сканиране...")

    # OCR
    reader = easyocr.Reader(['bg', 'en'], gpu=False)

    result = reader.readtext(img, detail=0)

    text = " ".join(result)

    st.subheader("Разпознат текст:")
    st.write(text)

    st.subheader("Проверка:")

    found = False

    for item in harmful:
        if item in text.lower():
            st.error(f"Намерено: {item}")
            found = True

    if not found:
        st.success("Няма намерени вредни съставки.")
