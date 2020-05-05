def model_name_from_table_name(table_name: str) -> str:
    return "".join([word.title() for word in table_name.split("_")])
