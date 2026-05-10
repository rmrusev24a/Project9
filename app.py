import streamlit as st
import easyocr
import numpy as np
from PIL import Image, ImageEnhance
import re

st.title("📷 Е-та скенер")

@st.cache_resource
def load_reader():
    return easyocr.Reader(['en'], gpu=False)

reader = load_reader()

harmful = {
    "e102": "Тартразин",
    "e110": "Залез жълто",
    "e211": "Натриев бензоат",
    "e250": "Натриев нитрит",
    "e621": "MSG",
    "e951": "Аспартам"
}

file = st.file_uploader("Качи снимка", type=["jpg", "jpeg", "png"])

def preprocess(img):

    img = img.convert("L")

    img = ImageEnhance.Contrast(img).enhance(2.5)

    w, h = img.size

    if w < 1600:
        scale = 1600 / w
        img = img.resize((int(w * scale), int(h * scale)))

    return img

if file:

    img = Image.open(file)

    st.image(img, caption="Оригинал")

    processed = preprocess(img)

    st.image(processed, caption="Обработена")

    if st.button("Сканирай"):

        result = reader.readtext(np.array(processed), detail=0)

        text = " ".join(result).lower()

        text = text.replace(" ", "").replace("-", "")

        found = re.findall(r"e\d{3,4}", text)

        found = list(set(found))

        st.subheader("Текст")

        st.write(text if text else "Нищо не е разпознато")

        st.subheader("Е-та")

        if not found:
            st.success("Няма Е-та")
        else:
            for e in found:
                if e in harmful:
                    st.error(f"{e.upper()} - {harmful[e]}")
                else:
                    st.warning(f"{e.upper()} - неизвестно")
