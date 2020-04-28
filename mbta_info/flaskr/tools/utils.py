import os


def create_model_name(data_file_name: str) -> str:
    raw_file_name = os.path.splitext(data_file_name)[0]
    words_no_plural = raw_file_name.rstrip("s").split("_")
    return "".join([word.title() for word in words_no_plural])
