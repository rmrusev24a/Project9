import streamlit as st
import easyocr
import numpy as np
from PIL import Image, ImageEnhance
import re

st.title("📷 Проверка за Е-та")

reader = easyocr.Reader(['en'], gpu=False)

harmful = {
    "e102": "Тартразин",
    "e110": "Залез жълто",
    "e124": "Понсо",
    "e211": "Натриев бензоат",
    "e250": "Натриев нитрит",
    "e621": "MSG",
    "e951": "Аспартам"
}

file = st.file_uploader(
    "Качи снимка",
    type=["jpg", "png", "jpeg"]
)

if file:

    image = Image.open(file)

    image = image.convert("L")

    image = ImageEnhance.Contrast(image).enhance(3)

    w, h = image.size

    if w < 1500:

        scale = 1500 / w

        image = image.resize(
            (int(w * scale), int(h * scale))
        )

    st.image(image, caption="Обработена снимка")

    if st.button("Сканирай"):

        result = reader.readtext(
            np.array(image),
            detail=0
        )

        text = " ".join(result)

        text = text.lower()

        text = text.replace(" ", "")

        text = text.replace("-", "")

        found = re.findall(r"e\d{3,4}", text)

        found = list(set(found))

        st.subheader("Намерен текст")

        st.write(text)

        st.subheader("Намерени Е-та")

        if len(found) == 0:

            st.success("Няма намерени Е-та")

        else:

            for e in found:

                if e in harmful:

                    st.error(
                        f"{e.upper()} - {harmful[e]}"
                    )

                else:

                    st.warning(
                        f"{e.upper()} - Няма информация"
                    )
