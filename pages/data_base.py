import streamlit as st
import random

# Inicializar estados de sesión
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'buttons_disabled' not in st.session_state:
    st.session_state.buttons_disabled = False
if 'nested_button_disabled' not in st.session_state:
    st.session_state.nested_button_disabled = False

# CSS personalizado
st.markdown("""
<style>
.disabled-btn {
    pointer-events: none;
    opacity: 0.5;
}
</style>
""", unsafe_allow_html=True)

# Dividir en columnas
col1, col2 = st.columns(2)

with col1:
    st.header("Controles")
    
    # Botón 1
    btn1 = st.button("Botón 1", disabled=st.session_state.buttons_disabled)
    if btn1:
        # Mensaje especial con nested button
        st.session_state.messages.append({
            'type': 'special_message', 
            'content': "Presionaste Botón 1",
            'nested_btn_state': False
        })
    
    # Botón 2  
    btn2 = st.button("Botón 2", disabled=st.session_state.buttons_disabled)
    if btn2:
        st.session_state.messages.append(f"Presionaste Botón 2")

print('re run =======')
with col2:
    st.header("Chat")
    
    # Mostrar mensajes del chat
    for i, message in enumerate(st.session_state.messages):
        if isinstance(message, dict) and message['type'] == 'special_message':
             # Mensaje especial con botón anidado
            st.write(message['content'])
            
            # Botón 3 con estado deshabilitado dentro de un div
            st.markdown(f"""
            <div>
                Este es un div
                {st.button("Botón 3", key=f"nested_btn_{i}", disabled=message.get('nested_btn_state', False))}
            </div>
            """, unsafe_allow_html=True)
            
            # if nested_btn3:
            #     # Deshabilitar el botón específico
            #     message['nested_btn_state'] = True
        else:
            st.write(message)
    
    # Input de chat
    if prompt := st.chat_input("Escribe tu mensaje"):
        st.session_state.messages.append(f"Tú: {prompt}")
        
        # Respuesta simulada del asistente
        assistant_response = f"Asistente: Respuesta generada para: {prompt}"
        st.session_state.messages.append(assistant_response)
        
        # Probabilidad de mostrar div de confirmación
        if random.random() < 0.5:
            # Div de confirmación
            confirm = st.checkbox("¿Aceptar respuesta?")
            if confirm:
                st.session_state.buttons_disabled = True
                st.success("Botones desactivados")