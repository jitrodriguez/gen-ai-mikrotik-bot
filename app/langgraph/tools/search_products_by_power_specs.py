from typing import List, Dict, Optional, Tuple, TypedDict, Literal
from sqlalchemy.orm import Session
from sqlalchemy import text
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage
from langchain_ollama import ChatOllama
from typing import Annotated
from pydantic import Field
import streamlit as st
import configs as cfg

@tool
def search_products_by_power_specs(max_power_consumption: float,min_power_consumption: float, category_id:Optional[int]) -> str:
    """
        Buscar productos por especificaciones de consumo de energía.
        Parámetros:
            - max_power_consumption: Consumo máximo de energía.(float) en watts.
            - min_power_consumption: Consumo mínimo de energía.(float) en watts.
            - category_id: ID de la categoría de productos.
        Retorna:
            - answer: Mensaje con los productos encontrados.
            - suggestions: Productos encontrados
        
    """
    try:
        # TODO: Convertir esto en variable
        query = """
            SELECT p.id, p.name, p.price, p.description, ps.max_power_consumption, p.image
            FROM products p
            FULL OUTER JOIN power_specs ps ON p.id = ps.product_id
            {category_join}
            WHERE ps.max_power_consumption <= {max_power_consumption} AND ps.max_power_consumption >= {min_power_consumption}
            {category_condition}
            LIMIT 4
        """

        if category_id:
            category_join = "FULL OUTER JOIN product_category pc ON p.id = pc.product_id"
            category_condition = f"AND pc.category_id = {category_id}"
        else:
            category_join = ""
            category_condition = ""

        final_query = query.format(category_join=category_join,category_condition=category_condition, max_power_consumption=max_power_consumption, min_power_consumption=min_power_consumption)

        if cfg.print_power_specs_query:
            print(final_query)

        conn = st.connection('database', type='sql')
        with conn.session as s:
            result = s.execute(final_query)
            result = result.fetchall()

        head = 'ID | Name | Price | Description | Max Power Consumption\n'
        final_result = ''
        products = {}
        for row in result:
            row_str = ' | '.join(map(str, row[:-1])) + '\n'
            final_result += row_str
            products[row[0]] = {
                'name': row[1],
                'price': row[2],
                'description': row[3],
                'max_power_consumption': row[4],
                'image': row[5]
            }
        if final_result == '':
            final_result = 'No products found.'
        return {'answer':head + final_result,'suggestions':products}
    except Exception as e:
        print(e)
        return {'answer':'Ha ocurrido un error al buscar los productos, por favor intenta más tarde.','suggestions':{}}