import streamlit as st
import pytesseract
from PIL import Image, ImageEnhance
import re

st.title("📷 Е-та скенер")

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

    img = ImageEnhance.Contrast(img).enhance(3)

    w, h = img.size

    if w < 1500:
        scale = 1500 / w
        img = img.resize((int(w * scale), int(h * scale)))

    return img

if file:

    img = Image.open(file)

    st.image(img, caption="Оригинал")

    processed = preprocess(img)

    st.image(processed, caption="Обработена")

    if st.button("Сканирай"):

        text = pytesseract.image_to_string(processed, lang="eng")

        text = text.lower().replace(" ", "").replace("-", "")

        found = re.findall(r"e\d{3,4}", text)

        found = list(set(found))

        st.subheader("Разпознат текст")

        st.write(text if text else "Нищо не е разпознато")

        st.subheader("Е-та")

        if not found:
            st.success("Няма намерени Е-та")
        else:
            for e in found:
                if e in harmful:
                    st.error(f"{e.upper()} - {harmful[e]}")
                else:
                    st.warning(f"{e.upper()} - неизвестно")
