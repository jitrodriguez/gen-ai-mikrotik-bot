import streamlit as st


class Product:
    def __init__(
        self,
        name=None,
        model=None,
        description=None,
        image=None,
        primary_button_label=None,
        secondary_button_label=None,
        tertiary_button_label=None,
        primary_button_callback=None,
        secondary_button_callback=None,
        tertiary_button_callback=None,
    ):
        self.name = name
        self.model = model
        self.description = description
        self.image = image
        self.primary_button_label = primary_button_label
        self.secondary_button_label = secondary_button_label
        self.tertiary_button_label = tertiary_button_label
        self.primary_button_callback = primary_button_callback
        self.secondary_button_callback = secondary_button_callback
        self.tertiary_button_callback = tertiary_button_callback

    def draw(self, id):
        with st.container(border=True):
            imageCol, nameCol = st.columns([1, 1], vertical_alignment="center")
            with imageCol:
                st.image(self.image, width=50)
            with nameCol:
                st.write(f"**{self.name}**")
            if self.primary_button_label:
                st.button(
                    self.primary_button_label,
                    type="primary",
                    use_container_width=True,
                    on_click=self.primary_button_callback,
                    key=f"{id}-primary-button",
                )
            if self.secondary_button_label:
                st.button(
                    self.secondary_button_label,
                    type="secondary",
                    use_container_width=True,
                    on_click=self.secondary_button_callback,
                    key=f"{id}-secondary-button",
                )
            if self.tertiary_button_label:
                st.button(
                    self.tertiary_button_label,
                    type="tertiary",
                    use_container_width=True,
                    on_click=self.tertiary_button_callback,
                    key=f"{id}-tertiary-button",
                )
