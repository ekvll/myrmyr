def sort_dict_by_value(data: dict) -> dict:
    return dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
