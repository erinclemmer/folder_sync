def remove_substring(string, substring):
    if not substring:
        return string  # Return the original string if substring is empty
    
    return string.replace(substring, "")