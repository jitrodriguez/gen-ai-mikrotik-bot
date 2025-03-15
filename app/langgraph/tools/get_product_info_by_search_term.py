import streamlit as st
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage




@tool
def get_product_info_by_name_and_code(name_or_code: str,max:int = 5) -> str:
    """
    Busca productos por nombre, descripción o código de producto.

    IMPORTANTE: Solo se busca por nombre, descripción y código de producto.

    Args:
        search_term (str): Nombre, descripción o código de producto a buscar.
        max (int): Máximo de productos a mostrar. default 5

    Returns:
        str: Lista de productos que coinciden con el término de búsqueda.
    """
    conn = st.connection('database', type='sql')
    try:
        query = """
            SELECT p.id, p.name, p.description, p.code, p.price, p.image
            FROM products p
            WHERE p.name LIKE :search_term or p.description LIKE :search_term or p.code LIKE :search_term
            LIMIT :max
        """
        params = {"search_term": f"%{name_or_code}%", "max": max}
        result = conn.execute(text(query), params)
        rows = result.fetchall()
        products_str = """
        ID | Nombre | Descripción | Código | Precio
        """
        products = {}
        for row in rows:
            # make a table with the products, id, name, code and price
            products_str += f"{row[0]} | {row[1]} | {row[3]} | {row[4]} \n"
            products[row[0]] = {
                "name": row[1],
                "description": row[2],
                "code": row[3],
                "price": row[4],
                "image": row[5]
            }

        return {'answer':products_str, 'products':rows}
    finally:
        pass
