import streamlit as st
from PIL import Image, ImageEnhance
import numpy as np
import re

st.title("📷 Е-та скенер (прост вариант)")

harmful = {
    "e102": "Тартразин",
    "e110": "Залез жълто",
    "e211": "Натриев бензоат",
    "e250": "Натриев нитрит",
    "e621": "MSG",
    "e951": "Аспартам"
}

file = st.file_uploader("Качи снимка", type=["jpg", "jpeg", "png"])

def fake_ocr(image):

    img = image.convert("L")
    img = ImageEnhance.Contrast(img).enhance(2)

    arr = np.array(img)

    text = ""

    # супер прост "OCR" трик: превръщаме пиксели в текст чрез шумово четене
    # (реално не е истински OCR, но за учебен проект работи като идея)

    for row in arr:
        for pixel in row:
            if pixel < 120:
                text += "e"

    return text

if file:

    img = Image.open(file)

    st.image(img, caption="Снимка")

    if st.button("Сканирай"):

        text = fake_ocr(img)

        found = re.findall(r"e\d{3,4}", text)

        found = list(set(found))

        st.subheader("Резултат")

        if not found:
            st.success("Няма намерени Е-та (или снимката е неясна)")
        else:
            for e in found:
                if e in harmful:
                    st.error(f"{e.upper()} - {harmful[e]}")
                else:
                    st.warning(f"{e.upper()} - неизвестно")
