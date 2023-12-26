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


def obtener_fk_tabla(tabla, id, foreign_keys):
    for real_tabla, fk_id, fk_tabla in foreign_keys:
        if tabla == real_tabla and id == fk_id:
            return fk_tabla
    return None


def generate_pydantic_model(table_name, columns, foreign_keys, primary_keys):
    # Template loading
    try:
        with open("init/schema_place_holder.py", "r") as template_file:
            template_code = template_file.read()
    except FileNotFoundError:
        print("No se encontró el archivo schema_place_holder.py")
        exit()

    # Imports
    imports_code = ""
    for column_name, column_type in columns:
        fk_tabla = obtener_fk_tabla(table_name, column_name, foreign_keys)
        if fk_tabla:
            imports_code += f"from src.schemas.{fk_tabla.lower()} import {fk_tabla}\n"

    template_code = template_code.replace("#Imports#", imports_code)

    # Schema name
    template_code = template_code.replace("#SchemaName#", table_name)

    # Schema Columns
    columns_code = ""
    for column_name, column_type in columns:
        fk_tabla = obtener_fk_tabla(table_name, column_name, foreign_keys)
        if fk_tabla:
            columns_code += f"    {column_name}: str\n"
        else:
            columns_code += (
                f"    {column_name}: {convert_sql_type_to_pydantic(column_type)}\n"
            )

    template_code = template_code.replace("# SCHEMACOLUMNS", columns_code)

    # Create Columns
    columns_code = ""
    for column_name, column_type in columns:
        fk_tabla = obtener_fk_tabla(table_name, column_name, foreign_keys)
        if fk_tabla:
            columns_code += f"    {column_name}: {fk_tabla}\n"
        else:
            columns_code += (
                f"    {column_name}: {convert_sql_type_to_pydantic(column_type)}\n"
            )

    template_code = template_code.replace("# CREATECOLUMNS", columns_code)
    return template_code


def generate_crud_file(table_name):
    # Template loading
    try:
        with open("init/crud_place_holder.py", "r") as template_file:
            template_code = template_file.read()
    except FileNotFoundError:
        print("No se encontró el archivo crud_place_holder.py")
        exit()

    # Schema name
    template_code = template_code.replace("#SchemaName#", table_name)
    # Schema tag
    template_code = template_code.replace("#SchemaNameTag#", table_name.title())

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
    table_matches = TABLE_PATTERN.finditer(sql_script)
    for table_match in table_matches:
        table_name = table_match.group(1)
        table_body = table_match.group(2)

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
        primary_keys = set(pk_matches)

        # Generate Pydantic model
        model_code = generate_pydantic_model(
            table_name, columns, foreign_keys, primary_keys
        )
        model_filename = f"{SCHEMA_DIR}/{table_name.lower()}.py"

        print(f"- Modelo: {table_name}")

        with open(model_filename, "w") as model_file:
            model_file.write(model_code)

        # Generate CRUD file
        crud_code = generate_crud_file(table_name)
        crud_filename = f"{ROUTES_DIR}/{table_name.lower()}"
        os.makedirs(crud_filename, exist_ok=True)
        crud_filename = join(crud_filename, "{}.py".format(table_name.lower()))

        with open(crud_filename, "w") as crud_file:
            crud_file.write(crud_code)

        print("_______________________")


if __name__ == "__main__":
    app()
