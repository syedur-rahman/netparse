""" 
netparse.table

This module provides the necessary abstraction to take a TABLE pattern
output and generate an accurate datastructure based off it.

For further reading, please check out this article:
https://pyability.com/the-curse-of-the-cli/
"""

class ParseTable:

    def __init__(self, unstructured_data, pattern):
        self.unstructured_data = unstructured_data
        self.pattern = pattern
        self.data_range = self._populate_data_range()
        self.row_data = self._populate_row_data()

    def _populate_data_range(self):
        """ parsetable._populate_data_range

        Initializes the data range attribute which determines the size of each
        column in the TABLE """

        # Define the range of each data attribute
        data_range = {}

        # Populate the first level in the structured datastructure
        for header, header_data in self.pattern.value_set.items():
            header_location = header_data['header_location']

            data_range[header] = {
                'start': header_location,
                'stop': header_location + len(header) - 1,
                }

        return data_range

    def _populate_row_data(self):
        """ parsetable._populate_row_data

        Initializes the row data variable with row header information.
        Also, this finishes up the full data range population as this method
        analyzes all the values in the unstructured dataset """

        # Define row data
        row_data = {}

        # Define the first header at which all rows will begin
        pivot_header = ''
        pivot_location = 100000

        # Start iteration of the unstuctured dataset
        for line_num, line in enumerate(self.unstructured_data):
            # Analyze each word in the unstructured dataset
            for word in line.split():
                # Start iteration of the value set from the TABLE PATTERN
                for header, header_data in self.pattern.value_set.items():
                    # Initialize header location and alignment parameters
                    header_location = header_data['header_location']
                    header_alignment = header_data['header_alignment']

                    # Check alignment as right aligned
                    if header_alignment == 'right_align':
                        # The following sets the value of the word's end location
                        # as the same as the end location for the header as
                        # it is right aligned
                        value_length = line.find(word) + len(word) - 1
                        header_length = header_location + len(header) - 1

                        # If they do match, then the word is indeed under
                        # the correct right aligned column set
                        if value_length == header_length:
                            start = line.find(word)

                            # Adjust the right aligned column's start position
                            # as necessary in case the word's length is longer
                            # than the previous values
                            if start < self.data_range[header]['start']:
                                self.data_range[header]['start'] = start

                    # Check alignment as left aligned
                    elif header_alignment == 'left_align':
                        # The following sets the value of the word's start location
                        # as the same as the start location for the header as
                        # it is left aligned
                        value_length = line.find(word)
                        header_length = header_location

                        # If they do match, then the word is indeed under
                        # the correct left aligned column set
                        if value_length == header_length:
                            stop = value_length + len(word) - 1

                            # Adjust the left aligned column's stop position
                            # as necessary in case the word's length is longer
                            # than the previous values
                            if stop > self.data_range[header]['stop']:
                                self.data_range[header]['stop'] = stop

                    # Sets up the pivot header which is the first header
                    # in the dataset with the lowest character location
                    # as this will determine the row values
                    if header_location < pivot_location:
                        pivot_header = header
                        pivot_location = header_location

                # If the word is equivalent to the pivot location,
                # then it is fair to set that up as the second level
                # for the structured dataset with...
                # COLUMN = HEADERS, ROWS = FIRST COLUMN DATA
                if line.find(word) == pivot_location:
                    # Skip entry if it matches header
                    if word == pivot_header:
                        continue

                    # Otherwise, add the row header data to the dictionary
                    if (line_num+1) not in row_data:
                        row_data[line_num+1] = word

        return row_data

    def generate_structure(self):
        """ parsetable.generate_structure

        Based on the information gleaned from the pattern tuple,
        generate structured data! """

        # Define final datastructure
        structured_data = []

        # Define pattern length
        pattern_length = sum(1 for _ in iter(self.pattern.value_set.items())) - 1

        # Iterate through the unstructured data
        for line_num, line in enumerate(self.unstructured_data):
            # Temporary structure
            json_structure = {}

            # Skip any headers that do not have a row header
            if line_num not in self.row_data:
                continue

            # Define row header
            row_header = self.row_data[line_num]

            # Start iteration of the value set from the TABLE PATTERN
            for i, (c_header, c_header_data) in enumerate(self.pattern.value_set.items()):
                # Initialize the previous and future header datasets
                p_header, p_header_data, f_header, f_header_data = '', '', '', ''

                # Initialize the start and stop parameters
                start, stop = '', ''

                # Fill in previous header data if applicable
                if i != 0:
                    p_header, p_header_data = list(self.pattern.value_set.items())[i-1]

                # Fill in future header data if applicable
                if i != pattern_length:
                    f_header, f_header_data = list(self.pattern.value_set.items())[i+1]

                # Initialize current header data
                c_header_alignment = c_header_data['header_alignment']

                # Initialize the data range values for each header
                start = self.data_range[c_header]
                stop = self.data_range[c_header]

                # Define the correct start and stop conditions
                if c_header_alignment == 'left_align':
                    start = self.data_range[c_header]['start']
                    if f_header:
                        stop = self.data_range[f_header]['start'] - 1
                    else:
                        stop = len(line)

                # Define the correct start and stop conditions
                elif c_header_alignment == 'right_align':
                    stop = self.data_range[c_header]['stop'] + 1
                    if p_header:
                        start = self.data_range[p_header]['stop'] + 1
                    else:
                        start = 0

                json_structure[c_header] = line[start:stop].strip()

            structured_data.append(json_structure)

        return structured_data