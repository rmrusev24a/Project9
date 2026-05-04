import streamlit as st
import easyocr
import numpy as np
from PIL import Image

# OCR (само български)
@st.cache_resource
def load_reader():
    return easyocr.Reader(['bg'])

reader = load_reader()

# Основни категории на Е-тата
def get_category(e_num):
    e = int(e_num)

    if 100 <= e <= 199:
        return "Оцветител"
    elif 200 <= e <= 299:
        return "Консервант"
    elif 300 <= e <= 399:
        return "Антиоксидант"
    elif 400 <= e <= 499:
        return "Сгъстител / стабилизатор"
    elif 500 <= e <= 599:
        return "Регулатор на киселинност"
    elif 600 <= e <= 699:
        return "Подобрител на вкус"
    elif 900 <= e <= 999:
        return "Подсладител / глазиращ агент"
    elif 1000 <= e <= 1520:
        return "Други добавки"
    else:
        return "Неизвестно"

# По-важни Е-та с описание
important_db = {
    "e621": "Мононатриев глутамат – усилва вкуса",
    "e950": "Ацесулфам К – изкуствен подсладител",
    "e951": "Аспартам – спорен подсладител",
    "e330": "Лимонена киселина – често използвана",
    "e202": "Калиев сорбат – консервант",
    "e211": "Натриев бензоат – може да дразни",
}

# Търсене на Е-та в текст
import re

def find_e_numbers(text):
    pattern = r"e\d{3,4}"
    return re.findall(pattern, text.lower())

# UI
st.title("📷 Проверка за Е-та в храна")

choice = st.radio("Избери:", ["Качи снимка", "Камера"])

img = None

if choice == "Качи снимка":
    file = st.file_uploader("Качи снимка", type=["jpg", "png"])
    if file:
        img = Image.open(file)
else:
    cam = st.camera_input("Снимай")
    if cam:
        img = Image.open(cam)

if img:
    st.image(img, caption="Снимка")

    if st.button("Провери"):
        text = " ".join([r[1] for r in reader.readtext(np.array(img))]).lower()

        st.subheader("📄 Текст:")
        st.write(text)

        e_numbers = find_e_numbers(text)

        st.subheader("⚠️ Намерени Е-та:")

        if e_numbers:
            for e in set(e_numbers):
                num = e.replace("e", "")
                category = get_category(num)

                if e in important_db:
                    st.error(f"{e.upper()} → {important_db[e]} ({category})")
                else:
                    st.warning(f"{e.upper()} → {category}")
        else:
            st.success("Няма намерени Е-та 👍")
