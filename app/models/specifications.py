import sqlite3

class SQLiteDB2:
    # _instance = None

    # def __new__(cls, db_path):
    #     if cls._instance is None:
    #         cls._instance = super(SQLiteDB2, cls).__new__(cls)
    #         cls._instance.db_path = db_path
    #         cls._instance.connection = None
    #     return cls._instance
    def __init__(self, db_path):
        self.db_path = db_path
        self.connection = None

    def create_all_tables(self):
        self.connect()
        self.create_tech_specs_table()
        self.create_connectivity_specs_table()
        self.create_wireless_specs_table()
        self.create_power_specs_table()
        self.create_physical_specs_table()

    def connect(self):
        if self.connection is None:
            self.connection = sqlite3.connect(self.db_path)

    def create_tech_specs_table(self):
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS tech_specs (
                    product_id INTEGER PRIMARY KEY,
                    cpu TEXT,
                    cpu_core_count INTEGER,
                    cpu_threads_count INTEGER,
                    cpu_nominal_frequency REAL,
                    cpu_temperature_monitor INTEGER,
                    architecture TEXT,
                    chipset TEXT,
                    switch_chip_model TEXT,
                    plc_chipset TEXT,
                    storage_size_mb INTEGER,
                    storage_type TEXT,
                    size_of_ram_mb INTEGER,
                    mtbf INTEGER,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )"""
            )

    def create_connectivity_specs_table(self):
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS connectivity_specs (
                product_id INTEGER PRIMARY KEY,
                number_10_100_1000_ethernet_ports INTEGER,
                number_of_1g_ethernet_ports_with_poe_out INTEGER,
                number_of_1g_2_5g_5g_10g_ethernet_ports INTEGER,
                sfp_ports INTEGER,
                sfp_plus_ports INTEGER,
                port_to_port_isolation TEXT,
                operating_system TEXT,
                FOREIGN KEY (product_id) REFERENCES product(id) ON DELETE CASCADE
                )"""
            )

    def create_wireless_specs_table(self):
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS wireless_specs (
                    product_id INTEGER PRIMARY KEY,
                    wi_fi_generation TEXT,
                    wireless_standards TEXT,
                    wireless_2_4_ghz_generation TEXT,
                    wireless_5_ghz_generation TEXT,
                    wireless_2_4_ghz_chip_model TEXT,
                    wireless_5_ghz_chip_model TEXT,
                    wireless_2_4_ghz_number_of_chains INTEGER,
                    wireless_5_ghz_number_of_chains INTEGER,
                    wireless_2_4_ghz_max_data_rate REAL,
                    wireless_5_ghz_max_data_rate REAL,
                    wifi_speed REAL,
                    dbi REAL,
                    beamwidth REAL,
                    cross_polarization TEXT,
                    polarization TEXT,
                    antenna_header_count INTEGER,
                    allow_2ghz BOOLEAN,
                    allow_5ghz BOOLEAN,
                    matching TEXT,
                    vswr TEXT,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )"""
            )

    def create_power_specs_table(self):
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS power_specs (
                    product_id INTEGER PRIMARY KEY,
                    max_power_consumption REAL,
                    max_power_consumption_without_attachments REAL,
                    power_rating REAL,
                    current REAL,
                    output_power REAL,
                    output_voltage REAL,
                    input_voltage REAL,
                    dc_jack_input_voltage REAL,
                    poe_in REAL,
                    poe_out REAL,
                    poe_out_ports INTEGER,
                    poe_in_input_voltage REAL,
                    max_out_per_port_output_input_18_30_v REAL,
                    max_out_per_port_output_input_30_57_v REAL,
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )"""
            )

    def create_physical_specs_table(self):
        with self.connection:
            self.connection.execute(
                """
                CREATE TABLE IF NOT EXISTS physical_specs (
                    product_id INTEGER PRIMARY KEY,
                    dimensions TEXT,
                    diameter_x_depth TEXT,
                    weight REAL,
                    packaged_weight REAL,
                    material TEXT,
                    color TEXT,
                    outdoor_rating TEXT,
                    ip_protection TEXT,
                    wind_load_125_mph REAL,
                    wind_survivability REAL,
                    can_be_used_indoors INTEGER CHECK(can_be_used_indoors IN (0,1)),
                    can_be_used_outdoors INTEGER CHECK(can_be_used_outdoors IN (0,1)),
                    FOREIGN KEY (product_id) REFERENCES products(id)
                )"""
            )

    def insert_or_update_tech_specs(self, product_id, tech_specs):
        columns = ["cpu", "cpu_core_count", "cpu_threads_count", "cpu_nominal_frequency", "cpu_temperature_monitor", "architecture", "chipset", "switch_chip_model", "plc_chipset", "storage_size_mb", "storage_type", "size_of_ram_mb", "mtbf"]
        # if any column has value continue flow else return
        if not any(tech_specs.get(column) for column in columns):
            return
        with self.connection:
            self.connection.execute(
                """
                INSERT OR REPLACE INTO tech_specs (product_id, cpu, cpu_core_count, cpu_threads_count, cpu_nominal_frequency, cpu_temperature_monitor, architecture, chipset, switch_chip_model, plc_chipset, storage_size_mb, storage_type, size_of_ram_mb, mtbf)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?) """,
                (
                    product_id,
                    tech_specs.get("cpu"),
                    tech_specs.get("cpu_core_count"),
                    tech_specs.get("cpu_threads_count"),
                    tech_specs.get("cpu_nominal_frequency"),
                    tech_specs.get("cpu_temperature_monitor"),
                    tech_specs.get("architecture"),
                    tech_specs.get("chipset"),
                    tech_specs.get("switch_chip_model"),
                    tech_specs.get("plc_chipset"),
                    tech_specs.get("storage_size_mb"),
                    tech_specs.get("storage_type"),
                    tech_specs.get("size_of_ram_mb"),
                    tech_specs.get("mtbf")
                ),
            )

    def insert_or_update_connectivity_specs(self, product_id, connectivity_specs):
        columns = ["number_10_100_1000_ethernet_ports", "number_of_1g_ethernet_ports_with_poe_out", "number_of_1g_2_5g_5g_10g_ethernet_ports", "sfp_ports", "sfp_plus_ports", "port_to_port_isolation", "operating_system"]
        # if any column has value continue flow else return
        if not any(connectivity_specs.get(column) for column in columns):
            return
        with self.connection:
            self.connection.execute(
                """
                INSERT OR REPLACE INTO connectivity_specs (product_id, number_10_100_1000_ethernet_ports, number_of_1g_ethernet_ports_with_poe_out, number_of_1g_2_5g_5g_10g_ethernet_ports, sfp_ports, sfp_plus_ports, port_to_port_isolation, operating_system)
                VALUES (?,?,?,?,?,?,?,?) """,
                (
                    product_id,
                    connectivity_specs.get("number_10_100_1000_ethernet_ports"),
                    connectivity_specs.get("number_of_1g_ethernet_ports_with_poe_out"),
                    connectivity_specs.get("number_of_1g_2_5g_5g_10g_ethernet_ports"),
                    connectivity_specs.get("sfp_ports"),
                    connectivity_specs.get("sfp_plus_ports"),
                    connectivity_specs.get("port_to_port_isolation"),
                    connectivity_specs.get("operating_system")
                ),
            )

    def insert_or_update_wireless_specs(self, product_id, wireless_specs):
        columns = ["wi_fi_generation", "wireless_standards", "wireless_2_4_ghz_generation", "wireless_5_ghz_generation", "wireless_2_4_ghz_chip_model", "wireless_5_ghz_chip_model", "wireless_2_4_ghz_number_of_chains", "wireless_5_ghz_number_of_chains", "wireless_2_4_ghz_max_data_rate", "wireless_5_ghz_max_data_rate", "wifi_speed", "dbi", "beamwidth", "cross_polarization", "polarization", "antenna_header_count", "allow_2ghz", "allow_5ghz", "matching", "vswr"]
        # print(wireless_specs)
        # print((wireless_specs.get(column) for column in columns))
        # print(any(wireless_specs.get(column) for column in columns))
        # if any column has value continue flow else return
        if not any(wireless_specs.get(column) for column in columns):
            return
        with self.connection:
            self.connection.execute(
                """
                INSERT OR REPLACE INTO wireless_specs (product_id, wi_fi_generation, wireless_standards, wireless_2_4_ghz_generation, wireless_5_ghz_generation, wireless_2_4_ghz_chip_model, wireless_5_ghz_chip_model, wireless_2_4_ghz_number_of_chains, wireless_5_ghz_number_of_chains, wireless_2_4_ghz_max_data_rate, wireless_5_ghz_max_data_rate, wifi_speed, dbi, beamwidth, cross_polarization, polarization, antenna_header_count, allow_2ghz, allow_5ghz, matching, vswr)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) """,
                (
                    product_id,
                    wireless_specs.get("wi_fi_generation"),
                    wireless_specs.get("wireless_standards"),
                    wireless_specs.get("wireless_2_4_ghz_generation"),
                    wireless_specs.get("wireless_5_ghz_generation"),
                    wireless_specs.get("wireless_2_4_ghz_chip_model"),
                    wireless_specs.get("wireless_5_ghz_chip_model"),
                    wireless_specs.get("wireless_2_4_ghz_number_of_chains"),
                    wireless_specs.get("wireless_5_ghz_number_of_chains"),
                    wireless_specs.get("wireless_2_4_ghz_max_data_rate"),
                    wireless_specs.get("wireless_5_ghz_max_data_rate"),
                    wireless_specs.get("wifi_speed"),
                    wireless_specs.get("dbi"),
                    wireless_specs.get("beamwidth"),
                    wireless_specs.get("cross_polarization"),
                    wireless_specs.get("polarization"),
                    wireless_specs.get("antenna_header_count"),
                    wireless_specs.get("allow_2ghz"),
                    wireless_specs.get("allow_5ghz"),
                    wireless_specs.get("matching"),
                    wireless_specs.get("vswr")
                ),
            )

    def insert_or_update_power_specs(self, product_id, power_specs):
        columns = ["max_power_consumption", "max_power_consumption_without_attachments", "power_rating", "current", "output_power", "output_voltage", "input_voltage", "dc_jack_input_voltage", "poe_in", "poe_out", "poe_out_ports", "poe_in_input_voltage", "max_out_per_port_output_input_18_30_v", "max_out_per_port_output_input_30_57_v"]
        # if any column has value continue flow else return
        if not any(power_specs.get(column) for column in columns):
            return
        with self.connection:
            self.connection.execute(
                """
                INSERT OR REPLACE INTO power_specs (product_id, max_power_consumption, max_power_consumption_without_attachments, power_rating, current, output_power, output_voltage, input_voltage, dc_jack_input_voltage, poe_in, poe_out, poe_out_ports, poe_in_input_voltage, max_out_per_port_output_input_18_30_v, max_out_per_port_output_input_30_57_v)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?) """,
                (
                    product_id,
                    power_specs.get("max_power_consumption"),
                    power_specs.get("max_power_consumption_without_attachments"),
                    power_specs.get("power_rating"),
                    power_specs.get("current"),
                    power_specs.get("output_power"),
                    power_specs.get("output_voltage"),
                    power_specs.get("input_voltage"),
                    power_specs.get("dc_jack_input_voltage"),
                    power_specs.get("poe_in"),
                    power_specs.get("poe_out"),
                    power_specs.get("poe_out_ports"),
                    power_specs.get("poe_in_input_voltage"),
                    power_specs.get("max_out_per_port_output_input_18_30_v"),
                    power_specs.get("max_out_per_port_output_input_30_57_v")
                ),
            )

    def insert_or_update_physical_specs(self, product_id, physical_specs):
        columns = ["dimensions", "diameter_x_depth", "weight", "packaged_weight", "material", "color", "outdoor_rating", "ip_protection", "wind_load_125_mph", "wind_survivability", "can_be_used_indoors", "can_be_used_outdoors"]
        # if any column has value continue flow else return
        if not any(physical_specs.get(column) for column in columns):
            return
        with self.connection:
            self.connection.execute(
                """
                INSERT OR REPLACE INTO physical_specs (product_id, dimensions, diameter_x_depth, weight, packaged_weight, material, color, outdoor_rating, ip_protection, wind_load_125_mph, wind_survivability, can_be_used_indoors, can_be_used_outdoors)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?) """,
                (
                    product_id,
                    physical_specs.get("dimensions"),
                    physical_specs.get("diameter_x_depth"),
                    physical_specs.get("weight"),
                    physical_specs.get("packaged_weight"),
                    physical_specs.get("material"),
                    physical_specs.get("color"),
                    physical_specs.get("outdoor_rating"),
                    physical_specs.get("ip_protection"),
                    physical_specs.get("wind_load_125_mph"),
                    physical_specs.get("wind_survivability"),
                    physical_specs.get("can_be_used_indoors"),
                    physical_specs.get("can_be_used_outdoors")
                ),
            )

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None