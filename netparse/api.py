""" 
netparse.api

This module provides the necessary API endpoints to generate a
structured dataset based on unstructured information.

For further reading, please check out this article:
https://pyability.com/the-curse-of-the-cli/
"""

from .pattern import Pattern
from .table import ParseTable

def get(unstructured_data):
    """ netparse.get

    The only required function in the API for the NetParse library.
    The function takes the unstructured data and returns structured data. """

    # Define the final structured result
    structured_data = ''

    # Set up the parse cllass
    pattern_init = Pattern(unstructured_data)

    # Check three levels of variance
    pattern_types = []
    for variance in range(3):
        pattern_types.append(pattern_init.determine_pattern(variance=variance+1))

    # Determine the best variance that generated the most accurate pattern
    best_pattern_reliability = 0
    best_pattern = ''

    # Iterate through the available pattern types
    for pattern_type in pattern_types:
        reliability = pattern_type.reliability

        # If the variance reliability is higher than the current, set as best
        if reliability > best_pattern_reliability:
            best_pattern_reliability = reliability
            best_pattern = pattern_type

    # Run the appropriate structure generator based off the pattern type
    if best_pattern.type == 'TABLE':
        table_parse = ParseTable(pattern_init.unstructured_data, best_pattern)
        structured_data = table_parse.generate_structure()

    return structured_data