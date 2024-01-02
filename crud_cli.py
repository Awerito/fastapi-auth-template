import re
import os
import typer

from os.path import join


app = typer.Typer()

# Map SQL types to Pydantic types
SQL_TO_PYDANTIC_TYPE = {
    "INT2": "int",
    "INT4": "int",
    "INT8": "int",
    "FLOAT4": "float",
    "FLOAT8": "float",
    "NUMERIC": "float",
    "DECIMAL": "float",
    "CHAR": "str",
    "VARCHAR": "str",
    "TEXT": "str",
    "DATE": "date",
    "TIME": "time",
    "TIMESTAMP": "datetime",
    "BOOLEAN": "bool",
    "UUID": "UUID",
    # "JSON": "Any",
}

# Output directories
SCHEMA_DIR = "src/schemas"
ROUTES_DIR = "src/routes"

# Regex patterns
TABLE_PATTERN = re.compile(r"create table (\w+) \(([\s\S]+?)\);")
COLUMN_PATTERN = re.compile(r"\s+(\w+)\s+(\w+)(?:\s+(not\s+null|\s+null))?,")
FK_PATTERN = re.compile(
    r"alter table (\w+)\s+add constraint FK_\w+_RELATIONS_\w+ foreign key \((\w+)\)\s+references (\w+) \((\w+)\)"
)
PK_PATTERN = re.compile(r"constraint PK_\w+ primary key \((\w+)\)")


def convert_sql_type_to_pydantic(sql_type):
    return SQL_TO_PYDANTIC_TYPE.get(sql_type, sql_type.lower())


def get_fk_table(table, id, foreign_keys):
    for real_table, fk_id, fk_table in foreign_keys:
        if table == real_table and id == fk_id:
            return fk_table
    return None


def generate_pydantic_model(table_name, columns, foreign_keys, primary_key):
    try:
        with open("init/schema_place_holder.py", "r") as template_file:
            template_code = template_file.read()
    except FileNotFoundError:
        print("No se encontró el archivo schema_place_holder.py")
        exit()

    # Imports & Schema Columns & Create Columns
    imports_code = ""
    schema_columns_code = ""
    create_columns_code = ""

    for column_name, column_type in columns:
        fk_table = get_fk_table(table_name, column_name, foreign_keys)

        # Imports & Schema Columns & Create Columns
        if column_name != primary_key:
            create_columns_code += f"    {column_name}: "
            col_name = column_name[:-3] if column_name.endswith("_id") else column_name
            schema_columns_code += f"    {col_name}: "
            if fk_table:
                imports_code += (
                    f"from src.schemas.{fk_table.lower()} import {fk_table}\n"
                )
                schema_columns_code += f"{fk_table}\n"
                create_columns_code += f"str\n"
            else:
                schema_columns_code += f"{convert_sql_type_to_pydantic(column_type)}\n"
                create_columns_code += f"{convert_sql_type_to_pydantic(column_type)}\n"

    # Replace placeholders in the template
    template_code = template_code.replace("#Imports#", imports_code)
    template_code = template_code.replace("#SchemaName#", table_name)
    template_code = template_code.replace("#SchemaColumns#", schema_columns_code)
    template_code = template_code.replace("#CreateColumns#", create_columns_code)
    template_code = template_code.replace("#SchemaNameLower#", table_name.lower())

    return template_code


def generate_crud_file(table_name, foreign_keys):
    # Template loading
    try:
        with open("init/crud_place_holder.py", "r") as template_file:
            template_code = template_file.read()
    except FileNotFoundError:
        print("No se encontró el archivo crud_place_holder.py")
        exit()

    # Imports
    imports_code = f"from src.schemas.{table_name.lower()} import {table_name}, {table_name}Create\n"
    for fk_table in foreign_keys:
        table = fk_table[2]
        imports_code += f"from src.schemas.{table.lower()} import {table}\n"

    # Schema name & tag
    template_code = template_code.replace("#Imports#", imports_code)
    template_code = template_code.replace("#SchemaName#", table_name)
    template_code = template_code.replace("#SchemaNameTag#", table_name)
    template_code = template_code.replace("#SchemaNameLower#", table_name.lower())

    return template_code


@app.command()
def main(sql_file: str):
    try:
        with open(sql_file, "r") as sql_file:
            sql_script = sql_file.read()
    except FileNotFoundError:
        print("{} file not found".format(sql_file))
        return

    os.makedirs(SCHEMA_DIR, exist_ok=True)
    os.makedirs(ROUTES_DIR, exist_ok=True)

    # Find table definitions and foreign keys
    app_imports = ""
    app_routers = ""
    table_matches = TABLE_PATTERN.finditer(sql_script)
    for table_match in table_matches:
        table_name = table_match.group(1)
        table_body = table_match.group(2)

        try:
            crud_filename = f"{ROUTES_DIR}/{table_name.lower()}"
            os.makedirs(crud_filename)
            crud_filename = join(crud_filename, "{}.py".format(table_name.lower()))
        except FileExistsError:
            print("Table {} already exists".format(table_name))
            continue

        print("Processing table: {}".format(table_name))

        # Find columns of the table
        column_matches = COLUMN_PATTERN.finditer(table_body)
        columns = [(match.group(1), match.group(2)) for match in column_matches]

        # Find foreign keys of the table
        fk_matches = FK_PATTERN.finditer(sql_script)
        foreign_keys = [
            (match.group(1), match.group(2), match.group(3))
            for match in fk_matches
            if match.group(1) == table_name
        ]

        # Find primary keys of the table
        pk_matches = PK_PATTERN.findall(table_body)
        primary_keys = list(set(pk_matches))[0]

        # Generate Pydantic model
        model_code = generate_pydantic_model(
            table_name, columns, foreign_keys, primary_keys
        )
        model_filename = f"{SCHEMA_DIR}/{table_name.lower()}.py"

        with open(model_filename, "w") as model_file:
            model_file.write(model_code)

        # Generate CRUD file
        crud_code = generate_crud_file(table_name, foreign_keys)

        with open(crud_filename, "w") as crud_file:
            crud_file.write(crud_code)

        app_imports += f"from src.routes.{table_name.lower()}.{table_name.lower()} import {table_name.lower()}_router\n"
        app_routers += f"app.include_router({table_name.lower()}_router)\n"

    # Modify main file
    app_imports += "# Imports #"
    app_routers += "# Endpoints #"

    with open("src/app.py", "r") as template_file:
        template_code = template_file.read()

    template_code = template_code.replace("# Imports #", app_imports)
    template_code = template_code.replace("# Endpoints #", app_routers)

    with open("src/app.py", "w") as template_file:
        template_file.write(template_code)

    print("_______________________")


if __name__ == "__main__":
    app()
