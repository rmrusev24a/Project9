import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import streamlit as st
import easyocr
import numpy as np
from PIL import Image, ImageEnhance
import re

harmful_db = {
    "e102": ("Тартразин – може да причинява алергии", 2),
    "e110": ("Залез жълто – вреден оцветител", 2),
    "e124": ("Понсо – алергии и хиперактивност", 2),
    "e211": ("Натриев бензоат – спорен консервант", 2),
    "e250": ("Натриев нитрит – опасен при честа употреба", 3),
    "e621": ("Мононатриев глутамат – може да причинява главоболие", 2),
    "e951": ("Аспартам – спорен подсладител", 2),
}

def get_category(num):

    e = int(num)

    if 100 <= e <= 199:
        return "Оцветител"

    elif 200 <= e <= 299:
        return "Консервант"

    elif 300 <= e <= 399:
        return "Антиоксидант"

    elif 400 <= e <= 499:
        return "Стабилизатор"

    elif 500 <= e <= 599:
        return "Регулатор"

    elif 600 <= e <= 699:
        return "Подобрител"

    elif 900 <= e <= 999:
        return "Подсладител"

    return "Неизвестно"

def preprocess_image(img):

    img = img.convert("RGB")

    w, h = img.size

    if w < 1800:
        scale = 1800 / w
        img = img.resize((int(w * scale), int(h * scale)))

    gray = img.convert("L")

    gray = ImageEnhance.Contrast(gray).enhance(3)

    arr = np.array(gray)

    arr = np.where(arr > 140, 255, 0).astype(np.uint8)

    img = Image.fromarray(arr)

    return img

@st.cache_resource
def load_reader():

    return easyocr.Reader(
        ['en'],
        gpu=False,
        verbose=False
    )

reader = load_reader()

def find_e_numbers(text):

    text = text.replace("Е", "E")
    text = text.replace("е", "e")
    text = text.replace("|", "E")
    text = text.replace("€", "E")

    pattern = r"e[\s\-]?\d{3,4}"

    found = re.findall(pattern, text.lower())

    result = []

    for item in found:

        item = item.replace(" ", "")
        item = item.replace("-", "")

        if item not in result:
            result.append(item)

    return result

st.set_page_config(page_title="E Scanner")

st.title("📷 Проверка за Е-та")

file = st.file_uploader(
    "Качи снимка",
    type=["jpg", "jpeg", "png"]
)

if file:

    img = Image.open(file)

    processed = preprocess_image(img)

    col1, col2 = st.columns(2)

    with col1:
        st.image(img, caption="Оригинал")

    with col2:
        st.image(processed, caption="Обработена")

    if st.button("🔍 Сканирай"):

        with st.spinner("Сканиране..."):

            result = reader.readtext(
                np.array(processed),
                detail=0,
                paragraph=True
            )

            full_text = " ".join(result)

        st.subheader("📄 Разчетен текст")

        st.write(full_text)

        e_numbers = find_e_numbers(full_text)

        st.subheader("⚠️ Намерени Е-та")

        if len(e_numbers) == 0:

            st.success("Няма намерени Е-та")

        else:

            for e in e_numbers:

                num = e.replace("e", "")

                if not num.isdigit():
                    continue

                category = get_category(num)

                if e in harmful_db:

                    desc, level = harmful_db[e]

                    if level == 3:
                        st.error(f"{e.upper()} - {desc}")

                    elif level == 2:
                        st.warning(f"{e.upper()} - {desc}")

                    else:
                        st.info(f"{e.upper()} - {desc}")

                else:
                    st.info(f"{e.upper()} - {category}")
