"""This module deals with the input files"""
import logging
import chardet


def change_encoding(file):
    """Detects the encoding of a file and changes it to utf-8
    Args:
        file: the encoded input file
    Returns:
        file: the file with utf-8 encoding
    """
    detected_encoding = chardet.detect(file)['encoding']
    logging.info(f"converted {detected_encoding} to utf-8")
    return file.decode(detected_encoding).encode("utf-8")


def decode_utf8(file):
    """ Checks whether a file is utf-8 encoded end decodes the file
    Args: file: an encoded file
    Returns: file: the decoded file
    """
    try:
        return file.decode('utf-8')
    except UnicodeDecodeError:
        return change_encoding(file).decode('utf-8')


class InputFile:
    """ Class of input files
    Args:
        file_path: the path to the input file
        file_extension: the extension of the input file
    """
    def __init__(self, file_path, file_extension):
        self.path = file_path
        self.name = file_path.split("/")[-1].split(".")[0]
        self.extension = file_extension
        self.normalized_path = f'/input/{self.name}_normalized.{self.extension}'
        self.variation_path = f'/input/{self.name}_normalized_variations.{self.extension}'
        self.read()

    @property
    def text(self):
        """Returns the content of the input file"""
        return self._text

    def read(self):
        """ Reads and decodes the input file"""
        with open(self.path, 'rb') as file:
            input_file = file.read()
            logging.info(f"Opened: {self.path}")
            self._text = decode_utf8(input_file)

    def export(self, export_path):
        """Exports the content of the input file, typically after normalisation
        Args:
            export_path: the path to the export location
        """
        with open(export_path, 'w+', encoding='utf-8') as normalized_file:
            normalized_file.write(self.text)

    def clean_text(self, normalize):
        raise NotImplementedError

    def validate(self, validation_function):
        """Applies the validation function on the data
        Args:
            validation_function: the validation function to apply
            """
        try:
            validation_function(self.path, self.extension)
            return True
        except UnicodeDecodeError:
            self.read()
            self.export(f'{self.name}_utf8.{self.extension}')
            validation_function(f'{self.name}_utf8.{self.extension}', self.extension)
            return True


class CTM(InputFile):
    """Class of CSM input files"""
    def clean_text(self, normalize):
        """ Applies an input function to the text of a CSM
        Args:
            normalize: A function that normalizes text
        """
        clean_text = []
        for line in self.text.splitlines():
            line_list = line.split(" ")
            line_list[4] = normalize(line_list[4])
            new_line = " ".join(line_list)
            clean_text.append(new_line)
        self._text = '\n'.join(clean_text)


class STM(InputFile):
    """Class of STM input files"""
    def clean_text(self, normalize):
        """ Applies an input function to the text of a STM
        Args:
            normalize: A function that normalizes text
        """
        clean_text = []
        for line in self.text.splitlines():
            line_list = line.split(" ")
            if line_list[0].startswith(';;'):
                text = ""
                meta_data = " ".join(line_list)
            elif line_list[5].startswith('<') and line_list[5].endswith('>'):
                text = normalize("  ".join(line_list[6:]))
                meta_data = " ".join(line_list[:6])
            else:
                text = normalize(" ".join(line_list[5:]))
                meta_data = " ".join(line_list[:5])
            new_line = f'{meta_data} {text}'
            clean_text.append(new_line)
        self._text = '\n'.join(clean_text)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
