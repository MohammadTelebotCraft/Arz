def format_number(number):
    """Format a number with commas for thousands and proper decimal places."""
    # Handle scientific notation and convert to a regular number
    if isinstance(number, float):
        # For very large or small numbers that might be in scientific notation
        num_str = f"{number:f}"
        # Remove trailing zeros after decimal point
        if '.' in num_str:
            num_str = num_str.rstrip('0').rstrip('.') if '.' in num_str else num_str
    else:
        num_str = str(number)
    
    # Handle any commas already present
    num_str = num_str.replace(',', '')
    
    # Split into integer and decimal parts
    if '.' in num_str:
        int_part, dec_part = num_str.split('.')
    else:
        int_part, dec_part = num_str, ''
    
    # Format the integer part with commas
    if len(int_part) > 3:
        formatted_int = ''
        while int_part:
            formatted_int = int_part[-3:] + (',' + formatted_int if formatted_int else '')
            int_part = int_part[:-3]
    else:
        formatted_int = int_part
    
    # Combine integer and decimal parts
    if dec_part:
        return f"{formatted_int}.{dec_part}"
    else:
        return formatted_int

def format_change(change):
    """Format the change value with appropriate indicators."""
    # Extract just the number part (removing percentage and parentheses)
    change = change.strip('()')
    if '(' in change:  # If there's still a number in parentheses
        change = change.split('(')[1].split(')')[0]
    
    # Get just the Toman value (last part after space)
    parts = change.split()
    if len(parts) > 1:
        change_value = parts[-1].replace(',', '')
    else:
        change_value = change.replace(',', '')
    
    try:
        # Format the number with commas
        formatted_change = format_number(change_value)
        if change.startswith('-'):
            return f"📉 {formatted_change}-"
        else:
            return f"📈 {formatted_change}+"
    except:
        return change 