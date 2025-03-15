from typing import List, Dict, Optional, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import text
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage
import streamlit as st

@tool
def search_products_by_category(category_id: int, top_n: Optional[int] = 4, order_by: Optional[str] = None, order: Optional[str] = 'ASC', max_price:Optional[int] = None, min_price:Optional[int] = None) -> str:
# def search_products_by_category(category_id: int, top_n: int = 4, order_by: Optional[str] = None, order: str = 'ASC', price_range: Optional[Tuple[float, float]] = None) -> List[Dict[str, str]]:
    """

    Busca productos por categoría con opciones de filtrado y ordenamiento, siempre manda categoría.

    Args:
        category_id (int): ID de la categoría para buscar productos. Mandatory.
        top_n (int, opcional): Número máximo de productos a devolver. Por defecto es 4. Optional.
        order_by (str, opcional): [price, name]. Optional.
        order (str, opcional): ['ASC','DESC']. Optional.
        min_price (int, opcional): Optional.
        max_price (int, opcional): Optional.
    """
    conn = st.connection('database', type='sql')
    # with conn.session as s:
    #     result = s.execute(query, params={"n": n})
    #     rows = result.fetchall()

    if top_n is None:
        top_n = 4
    if not order:
        order = 'ASC'
    
    try:
        query = """
            SELECT p.id, p.name, p.description, p.code, p.price, p.image
            FROM products p
            JOIN product_category pc
            ON p.id = pc.product_id
            WHERE pc.category_id = :category_id
        """
        params = {"category_id": category_id}

        if min_price and max_price:
            query += " AND p.price BETWEEN :min_price AND :max_price"
            params["min_price"] = min_price
            params["max_price"] = max_price

        if order_by:
            query += f" ORDER BY {order_by} {order}"

        query += f" LIMIT {top_n}"

        # result = conn.execute(text(query), params)
        # rows = result.fetchall()
        with conn.session as s:
            result = s.execute(query, params)
            rows = result.fetchall()
        products = {}
        for row in rows:
            products[row[0]] = {
                'name': row[1],
                'code': row[3],
                'price': row[4],
                'image': row[5]
            }
        products_str = """
        ID | Nombre | Descripción | Código | Precio
        """
        for row in rows:
            # make a table with the products, id, name, code and price
            products_str += f"{row[0]} | {row[1]} | {row[3]} | {row[4]} \n"

        return {'answer':products_str,'suggestions':products}
    except Exception as e:
        print(e)
        return 'Ha ocurrido un error al buscar los productos por categoría, por favor intenta más tarde.'