import streamlit as st



def get_categories() -> str:
    """
    Obtiene todas las categorías de la base de datos.

    Returns:
        str: Tabla con los detalles de las categorías.
    """
    conn = st.connection('database', type='sql')
    query = "SELECT * FROM categories"
    result = conn.execute(query)
    rows = result.fetchall()
    categories_str = ""
    for row in rows:
        categories_str += f"{row[0]} - {row[1]}\n"
    return categories_str


def get_products_info( product_id_1:str='',product_id_2:str='',product_id_3:str='',product_id_4:str=''):
    """
    Get products fields from the database
    """
    conn = st.connection('database', type='sql')
    p_columns = ["p.id","p.name","p.description","p.price"]
    c_columns = ["c.number_10_100_1000_ethernet_ports","c.number_of_1g_ethernet_ports_with_poe_out","c.number_of_1g_2_5g_5g_10g_ethernet_ports","c.sfp_ports","c.sfp_plus_ports","c.port_to_port_isolation","c.operating_system"]
    phs_columns = ["phs.dimensions","phs.diameter_x_depth","phs.weight","phs.packaged_weight","phs.material","phs.color","phs.outdoor_rating","phs.ip_protection","phs.wind_load_125_mph","phs.wind_survivability","phs.can_be_used_indoors","phs.can_be_used_outdoors"]
    ps_columns = ["ps.max_power_consumption","ps.max_power_consumption_without_attachments","ps.power_rating","ps.current","ps.output_power","ps.output_voltage","ps.input_voltage","ps.dc_jack_input_voltage","ps.poe_in","ps.poe_out","ps.poe_out_ports","ps.poe_in_input_voltage","ps.max_out_per_port_output_input_18_30_v","ps.max_out_per_port_output_input_30_57_v"]
    ts_columns = ["ts.cpu","ts.cpu_core_count","ts.cpu_threads_count","ts.cpu_nominal_frequency","ts.cpu_temperature_monitor","ts.architecture","ts.chipset","ts.switch_chip_model","ts.plc_chipset","ts.storage_size_mb","ts.storage_type","ts.size_of_ram_mb","ts.mtbf"]
    ws_columns = ["ws.wi_fi_generation","ws.wireless_standards","ws.wireless_2_4_ghz_generation","ws.wireless_5_ghz_generation","ws.wireless_2_4_ghz_chip_model","ws.wireless_5_ghz_chip_model","ws.wireless_2_4_ghz_number_of_chains","ws.wireless_5_ghz_number_of_chains","ws.wireless_2_4_ghz_max_data_rate","ws.wireless_5_ghz_max_data_rate","ws.wifi_speed","ws.dbi","ws.beamwidth","ws.cross_polarization","ws.polarization","ws.antenna_header_count","ws.allow_2ghz","ws.allow_5ghz","ws.matching","ws.vswr"]
    # select product with id join tables with product_id and product that has only id
    general_query = f"""
    SELECT { ",".join(p_columns)}, {",".join(c_columns)}, {",".join(phs_columns)}, {",".join(ps_columns)}, {",".join(ts_columns)}, {",".join(ws_columns)}
    from products p
    FULL OUTER JOIN connectivity_specs c ON p.id = c.product_id
    FULL OUTER JOIN physical_specs phs ON p.id = phs.product_id
    FULL OUTER JOIN power_specs ps ON p.id = ps.product_id
    FULL OUTER JOIN tech_specs ts ON p.id = ts.product_id
    FULL OUTER JOIN wireless_specs ws ON p.id = ws.product_id
    """
    #  validate that at least 2 products are provided
    if(product_id_1 == "" and product_id_2 == "" and product_id_3 == "" and product_id_4 == ""):
        return {"wrong_product":True, "result":"Please provide at least 2 products to compare"}
    if(product_id_1 != ""):
        general_query += f" WHERE p.id = {product_id_1}"
    if(product_id_2 != ""):
        general_query += f" OR p.id = {product_id_2}"
    if(product_id_3 != ""):
        general_query += f" OR p.id = {product_id_3}"
    if(product_id_4 != ""):
        general_query += f" OR p.id = {product_id_4}"

    with conn.session as s:
            result = s.execute(general_query)
            products = result.fetchall()
    converted_products = []
    full_columns = p_columns + c_columns + phs_columns + ps_columns + ts_columns + ws_columns
    for product in products:
        product_dict = {}
        for i in range(len(full_columns)):
            value = product[i]
            if value is None or value == "":
                continue
            key = full_columns[i]
            converted_key = key.split(".")[1]
            product_dict[converted_key] = product[i]
        converted_products.append(product_dict)
    return converted_products



