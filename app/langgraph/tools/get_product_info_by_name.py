import streamlit as st
from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage

@tool
def get_product_info_by_name(name: str) -> str:
    """
    Busca productos por nombre.

    IMPORTANTE: Solo se busca por nombre, descripción y código de producto.

    Args:
        nombre (str): Nombre, descripción o código de producto a buscar.

    Returns:
        str: Producto que coincide con el término de búsqueda.
    """
    conn = st.connection('database', type='sql')
    try:
        query = """
            SELECT p.id, p.name, p.price, p.description, cp.number_10_100_1000_ethernet_ports,cp.number_of_1g_ethernet_ports_with_poe_out,
            cp.number_of_1g_2_5g_5g_10g_ethernet_ports, cp.sfp_ports, cp.sfp_plus_ports, cp.port_to_port_isolation, cp.operating_system,p.image
            FROM products p
            FULL OUTER JOIN connectivity_specs cp ON p.id = cp.product_id
            WHERE p.name LIKE :name LIMIT 1
        """
        params = {"name": f"%{name}%"}

        with conn.session as s:
            result = s.execute(query, params)
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
