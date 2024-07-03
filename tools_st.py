import streamlit as st

class StreamlitApp:
    def __init__(self):
        pass

    def header_principal(self, title):

        self.title = title

        c1, c2, c3 = st.columns((2, 3, 2))

        with c1:
            st.image("/home/renan/dev/frotas_st/adm/img/adm.jpg")

        with c2:
            st.header(f"{self.title}")

        with c3:
            st.image("/home/renan/dev/frotas_st/adm/img/ituran_fleet.png")

        st.header('', divider='rainbow')