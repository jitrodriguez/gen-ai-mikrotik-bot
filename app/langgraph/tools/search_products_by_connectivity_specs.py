from typing import List, Optional, TypedDict, Literal
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI
from pydantic import Field
import streamlit as st
import configs as cfg


comparison_expressions = Literal["=", "==", "<", "<=", ">", ">=", "!=", "", "IN", "NOT IN", "IS", "IS NOT","like"]
columns = Literal['number_10_100_1000_ethernet_ports','number_of_1g_ethernet_ports_with_poe_out','number_of_1g_2_5g_5g_10g_ethernet_ports','sfp_ports','sfp_plus_ports','port_to_port_isolation','operating_system']
class Condition(TypedDict):
    column: columns
    comparison_expression: Literal[comparison_expressions]= Field(description="Comparator operator (> | like | < | )")
    value: str= Field(description="Value to compare with ( eg. 2 | %RouterOS% ... )")
class Conditions(TypedDict):
    conditions: List[Condition]

connectivity_specs_unique_values_str = """
Column Name | Type | Example
--------------------------
number_10_100_1000_ethernet_ports | INTEGER
number_of_1g_ethernet_ports_with_poe_out | INTEGER
number_of_1g_2_5g_5g_10g_ethernet_ports | INTEGER
sfp_ports  | INTEGER
sfp_plus_ports | INTEGER
port_to_port_isolation | TEXT | >40 dB min
operating_system | TEXT |RouterOS, RouterOS v5 and above, MikroTik SwOS, RouterOS v7, SwOS, RouterOS / SwitchOS, RouterOS v7 / SwitchOS, SwitchOS Lite, RouterOS v7 / SwOS, RouterOS v7 (Special ROSE edition) | TEXT
"""
desc = f"""
    Busca productos por especificaciones de conectividad. por ejemplo, número de puertos ethernet, sistema operativo, etc.
    Las especificaciones de conectividad disponibles son:
    {connectivity_specs_unique_values_str}
    Examples:
        * search_products_by_connectivity_specs("number_10_100_1000_ethernet_ports less than 2","1")
        * search_products_by_connectivity_specs("operating_system RouterOS Rose Edition","3")

    Recuerda: solo puedes mencionar las especificaciones en la tabla de especificaciones de conectividad.
    """
@tool(description=desc)
def search_products_by_connectivity_specs(summarized_question: str, category_id:Optional[int]) -> str:
    llm = ChatOpenAI(
        model='gpt-4o'
    )
    try:
        # TODO: Convertir esto en variable
        query = """
            SELECT p.id, p.name, p.price, p.description, cp.number_10_100_1000_ethernet_ports,cp.number_of_1g_ethernet_ports_with_poe_out,
            cp.number_of_1g_2_5g_5g_10g_ethernet_ports, cp.sfp_ports, cp.sfp_plus_ports, cp.port_to_port_isolation, cp.operating_system,p.image
            FROM products p
            LEFT JOIN connectivity_specs cp ON p.id = cp.product_id
            {category_join}
            WHERE {generated_query}
            {category_condition}
        """

        SYSTEM_MESSAGE = (
            "You have to generate the query to search products by connectivity specs."
            "You have to provide the possible value according unique values."
            "Available connectivity specs are:"
            f"{connectivity_specs_unique_values_str}"
            "The base query is:"
            f"{query}"
            "Good Examples:"
            "summarized question: number_10_100_1000_ethernet_ports less than 2"
            "generated output: {'conditions': [{'column': 'number_10_100_1000_ethernet_ports', 'comparison_expression': '<', 'value': '2'}]}"
            "summarized question: number_10_100_1000_ethernet_ports more than 10"
            "generated output: {'conditions': [{'column': 'number_10_100_1000_ethernet_ports', 'comparison_expression': '>=', 'value': '10'}]}"
            "summarized question: operating_system routeroS Rose Edition"
            "generated query: {'conditions': [{'column': 'operating_system', 'comparison_expression': 'like', 'value': '%RouterOS%'},{ 'column': 'operating_system', 'comparison_expression': 'like', 'value': '%Rose%'}]}"
            "\nIf no column related to the connectivity specs is provided, the query will be generated with the provided values."
        )

        if category_id:
            category_join = "LEFT JOIN product_category pc ON p.id = pc.product_id"
            category_condition = f"AND pc.category_id = {category_id}"
        else:
            category_join = ""
            category_condition = ""

        result = llm.with_structured_output(Conditions,method= 'json_schema').invoke([
            SystemMessage(SYSTEM_MESSAGE),
            HumanMessage(summarized_question)
        ])
        generated_query = ''
        main_operator = ''
        conditions_str = []
        for condition in result['conditions']:
            column = condition['column']
            comparison_expression = condition['comparison_expression']
            value = condition['value']
            is_string = True
            try:
                float(value)
                is_string = False
            except:
                pass
            if is_string:
                value = f"'{value}'"
            main_operator = ' AND ' if comparison_expression != 'like' else ' OR '
            conditions_str.append(f"{column} {comparison_expression} {value} {main_operator}")
        if len(conditions_str) > 0:
            # remove last operator
            conditions_str[-1] = conditions_str[-1][:-len(main_operator)]
            generated_query = ''.join(conditions_str)
        else:
            generated_query = '1=0'

        final_query = query.format(generated_query=generated_query,category_join=category_join,category_condition=category_condition)
        
        if cfg.print_connectivity_specs_query:
            print(final_query)

        conn = st.connection('database', type='sql')
        with conn.session as s:
            result = s.execute(final_query)
            result = result.fetchall()

        head = 'ID | Name | Price | Description | number_10_100_1000_ethernet_ports | number_of_1g_ethernet_ports_with_poe_out | number_of_1g_2_5g_5g_10g_ethernet_ports | sfp_ports | sfp_plus_ports | port_to_port_isolation | operating_system\n'
        final_result = ''
        products = {}
        for row in result:
            row_str = ' | '.join(map(str, row)) + '\n'
            final_result += row_str
            products[row[0]] = {
                'name': row[1],
                'price': row[2],
                'description': row[3],
                'image': row[11]
            }
        if final_result == '':
            final_result = 'No products found.'
        return {'answer':head + final_result,'suggestions':products}
    except Exception as e:
        print(e)
        return {'answer':'Ha ocurrido un error al buscar los productos, por favor intenta más tarde.','suggestions':{}}