import streamlit as st
import easyocr
from PIL import Image
import numpy as np

st.title("Скенер за вредни съставки")

st.write("Качи снимка на етикет")

uploaded_file = st.file_uploader(
    "Избери снимка",
    type=["jpg", "jpeg", "png"]
)

harmful = [
    "E621",
    "E102",
    "E110",
    "палмово масло",
    "Aspartame"
]

if uploaded_file is not None:

    image = Image.open(uploaded_file)

    st.image(image, caption="Качена снимка")

    img = np.array(image)

    st.write("Разпознаване на текст...")

    reader = easyocr.Reader(
        ['bg', 'en'],
        gpu=False
    )

    result = reader.readtext(
        img,
        detail=0
    )

    text = " ".join(result)

    st.subheader("Разпознат текст:")
    st.write(text)

    st.subheader("Проверка:")

    found = False

    for item in harmful:

        if item.lower() in text.lower():

            st.error(f"Намерено: {item}")

            found = True

    if not found:

        st.success("Няма намерени вредни съставки.")
