

def parse_title(attributes: list) -> str:
    """
    Parse the title from an array of attributes
    The title is the attribute with id = 1
    """
    return next((attr['value'] for attr in attributes if attr['id'] == 1), None)