import streamlit as st
import easyocr
from PIL import Image
import numpy as np

st.title("Проверка на вредни съставки")

st.write("Качи снимка на етикет на храна.")

uploaded_file = st.file_uploader(
    "Избери снимка",
    type=["jpg", "png", "jpeg"]
)

# Списък с вредни съставки
harmful_ingredients = [
    "E621",
    "E102",
    "E110",
    "палмово масло",
    "Palm Oil",
    "Aspartame"
]

if uploaded_file is not None:
    image = Image.open(uploaded_file)

    st.image(image, caption="Качена снимка", use_container_width=True)

    # Превръщаме снимката в масив
    img_array = np.array(image)

    st.write("Разпознаване на текст...")

    # EasyOCR
    reader = easyocr.Reader(['bg', 'en'])

    results = reader.readtext(img_array, detail=0)

    detected_text = " ".join(results)

    st.subheader("Разпознат текст:")
    st.write(detected_text)

    st.subheader("Намерени вредни съставки:")

    found = False

    for ingredient in harmful_ingredients:
        if ingredient.lower() in detected_text.lower():
            st.warning(f"Намерена съставка: {ingredient}")
            found = True

    if not found:
        st.success("Не са намерени вредни съставки.")
