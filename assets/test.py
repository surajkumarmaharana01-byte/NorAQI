import streamlit as st
import os

path = r"D:\NorAQI\assets\AQI_Image.jpg"

st.write(os.path.exists(path))
st.image(path)