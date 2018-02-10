""" 
netparse.pattern

This module provides the necessary abstraction to determine the pattern in the
provided unstructured data by the user.

For further reading, please check out this article:
https://pyability.com/the-curse-of-the-cli/
"""

from collections import namedtuple, OrderedDict
import re


def remove_unnecessary_characters(line):
    """ Remove Unnecessary Characters """

    special_characters = [' ', '-', '/']

class Pattern:

    def __init__(self, unstructured_data):
        # Convert the data into a list
        self.unstructured_data = self._convert_to_list(unstructured_data)

    def _add_padding_to_lines(self, unstructured_data):
        """ pattern._add_padding_to_lines

        Adds padding to smaller length lines to make all lines in the
        unstructured data list completely equal for comparison reasons """

        # Define empty character
        empty_char = ' '

        # Define max length
        max_length = 0

        # Find out which line has the highest length
        for line in unstructured_data:
            length = len(line)

            # Update with the highest value
            if length > max_length:
                max_length = length

        # Iterate through the list to pad each line
        for i, line in enumerate(unstructured_data):
            if len(line) < max_length:
                line = line + (max_length - len(line)) * empty_char

            unstructured_data[i] = line

        return unstructured_data


    def _convert_to_list(self, unstructured_data):
        """ pattern._convert_to_list

        Converts the unstructured data into a list. This functionality
        is ignored if the user already submitted the data as a list """

        # Define new unstructured data
        new_unstructured_data = []

        # Verify the type of the unstructured dataset
        if type(unstructured_data) is str:
            unstructured_data = unstructured_data.splitlines()

        # Remove unnecessary lines in unstructured dataset
        for line in unstructured_data:
            if re.sub('\W+','', line).isalnum():
                new_unstructured_data.append(line)

        return self._add_padding_to_lines(new_unstructured_data)

    def determine_pattern(self, variance):
        """ pattern.determine_pattern

        Based on the unstructured data provided by the user, this method
        will determine the type of pattern to use.

        Types of patterns:

        TABLE PATTERN (1)      
        This is set on any unstructured dataset that 'looks' like a table.

        VALUE-KEY PATTERN (2) - FUTURE TODO
        This is set on any unstructured dataset that 'looks' like there is a
        value for some type of data within the line, such as '23 unicast packets'.

        TOP-DOWN PATTERN (3) - FUTURE TODO
        This is set on any unstructured dataset that 'looks' like there is a
        parent and child relationship, such as a router's running configuration.

        Basic Usage:

        >>> import netparse
        >>> unstructured_data = '
            Port    Name          Status    Vlan     Duplex   Speed   Type\n
            Eth1/1  test-host1    connected routed   full     10G     10Gbase-SR\n
            Eth1/2  test-host2    connected 123      full     10G     10Gbase-SR\n
            '
        >>> p = netparse.Parse(unstructured_data)
        >>> p = determine_pattern()
        Pattern(
            type='TABLE',
            value_set={
                'Port': {0, 'left_align'},
                'Name': {8, 'left_align'},
                'Status': {22, 'left_align'},
                'Vlan': {32, 'left_align'},
                'Duplex': {41, 'left_align'},
                'Speed': {50, 'left_align'},
                'Type': {58, 'left_align'}
                },
            reliability=100
            )
        """
        # Define empty character
        empty_char = ' '

        # Define the Pattern tuple
        Pattern = namedtuple('Pattern', 'type value_set reliability')

        # Define the header line which should be the first line in raw data
        header_line = self.unstructured_data[0]

        # Define headers for TABLE pattern using a generator
        headers = OrderedDict((header.strip(), 0) for header in header_line.split(variance*empty_char))
        headers.pop('', None)

        # Define the patterm match based on alignment in TABLE
        pattern_match = {}

        # Iterate through the headers to determine TABLE pattern validity
        for header in headers.keys():
            # Find the exact character location for each header
            header_location = header_line.find(header)

            # Update the headers with the correct header location and
            # assume data is left aligned by default, but this may change
            # upon actual analysis of the header dataset in TABLE
            headers[header] = {
                'header_location': header_location,
                'header_alignment': 'left_align',
                }

            # Fully initialize the pattern match datastructure
            pattern_match[header] = {}
            pattern_match[header]['left_align'] = 0
            pattern_match[header]['right_align'] = 0
            pattern_match[header]['no_align'] = 0

        # Iterate through the unstructured data to determine PATTERN
        for line in self.unstructured_data:
            # Iterate through the recently generated header information
            for header, header_values in headers.items():
                # Initialize the header values
                header_location = header_values['header_location']
                header_alignment = header_values['header_alignment']

                # If the observed line does not contain an empty character
                # in the header location, then assume line fits left align
                if line[header_location] != empty_char:
                    if header_location == 0:
                        pattern_match[header]['left_align'] += 1
                    elif line[header_location - 1] == empty_char:
                        pattern_match[header]['left_align'] += 1

                # If the observed line does not contain an empty character
                # in the header location, then assume lline fits right align
                if line[header_location + len(header) - 1] != empty_char:
                    if header_location + len(header) == len(line):
                        pattern_match[header]['right_align'] += 1
                    elif line[header_location + len(header)] == empty_char:
                        pattern_match[header]['right_align'] += 1

                # If the observed line does contain an empty character
                # in the header location, then assume possibly not TABLE pattern
                else:
                    pattern_match[header]['no_align'] += 1

        # Initialize some basic variables for TABLE check
        aligned = 0
        not_aligned = 0

        # Iterate through the alignment results to see if TABLE PATTERN
        for header, align_type in pattern_match.items():
            left_align = align_type['left_align']
            right_align = align_type['right_align']
            no_align = align_type['no_align']

            aligned += left_align
            aligned += right_align
            not_aligned += no_align

            # Also rewrite alignment if necessary
            if right_align > left_align:
                headers[header]['header_alignment'] = 'right_align'

        # If the unstructured data is more aligned than not
        # then we can safely assume this is a TABLE PATTERN
        if aligned > not_aligned:
            return Pattern(type='TABLE', value_set=headers, reliability=aligned)
        else:
            return Pattern(type='NO_MATCH', value_set=None, reliability=None)