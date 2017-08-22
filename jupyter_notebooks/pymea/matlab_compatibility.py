from datetime import datetime

def datetime_str_to_datetime(datetime_str):
    """
    This converts the strings generated when matlab datetimes are written to a table to python datetime objects
    """
    return datetime.strptime(datetime_str, '%d-%b-%Y %H:%M:%S')

def well_row_letter_to_number(letter):
    """
    Converts the letter corresponding to the Axis well row to the corresponding integer row number.
    Starts with A = 1
    """
    return ord(letter) - 64

def get_row_number(unit_name):
    """
    Returns the row_number corresponding to the row_number of the 
        unit specified by unit_name. Useful for filtering rows by condition.
    """
    row_num = well_row_letter_to_number(unit_name[0])
    return row_num

def get_col_number(unit_name):
    """
    Returns the col_number tuple corresponding to the column of the 
        unit specified by unit_name. Useful for filtering rows/columns by condition.
    """
    col_num = int(unit_name[1])
    return col_num

def get_row_col_number_tuple(unit_name):
    """
    Returns the (row_number, col_number) tuple corresponding to the row_number and column of the 
        unit specified by unit_name. Useful for filtering rows/columns by condition.
    """
    row_num = get_row_number(unit_name)
    col_num = get_col_number(unit_name)
    return (row_num, col_num)


