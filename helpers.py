def replace_sides(matrix, value):
    """Replaces the values on the top, right, bottom, and left sides of a matrix."""

    if not matrix:
        return matrix

    rows = len(matrix)
    cols = len(matrix[0])

    # Top and bottom rows
    for i in range(cols):
        matrix[0][i] = value
        matrix[rows - 1][i] = value

    # Left and right columns
    for i in range(1, rows - 1):
        matrix[i][0] = value
        matrix[i][cols - 1] = value

    return matrix

# Limit name to 9 characters to fit on one line. If less than 9 - add spaces
def get_last_name(full_name):
    last_name = full_name.split()[-1]  # Get the last word (last name)
    last_name = last_name[:9]  # Limit to 9 characters
    last_name = last_name.ljust(9)  # Add spaces if less than 9 characters
    return last_name