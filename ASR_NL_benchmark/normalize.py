""" This module preproces hyp- and reffiles before they enter the NIST benchmarking tool sclite """
import logging
import string
from num2words import num2words

def check_and_covert_interger(word):
    """Checks wether a string contains numbers seperated with a . or , and converts them to their written form
    Args:
        word: an string that is converted to the written form of an interger if possible
    Returns:
        new_word:  returns the written form of an interger if possible and False otherwise

    >>> check_and_covert_interger('2.3')
    'twee punt drie'
    >>> check_and_covert_interger('2,3')
    'twee komma drie'
    """
    if '.' in word:
        try:
            float(word)
            new_word = num2words(word, to='cardinal', lang='nl')
            new_word = new_word.replace('komma', 'punt')
            logging.info(f'converted the number {word} to {new_word}')
            return new_word
        except:
            return False
    elif ',' in word:
        new_word = word.replace(',', '.')
        try:
            float(new_word)
            new_word = num2words(new_word, to='cardinal', lang='nl')
            logging.info(f'converted number {word} to {new_word}')
            return new_word
        except:
            return False

def replace_numbers_and_symbols(text):
    """Replaces the numbers and symbols from a text by their written form
    Args:
        text: a string in which numbers and symbols are to be replaced
    Returns:
        clean_text: the text with symbols replaced by their written form

    >>> replace_numbers_and_symbols('12,3%')
    'twaalf komma drie procent'
    """
    removed_punct = string.punctuation.replace("'", '').replace('-', '')
    text_without_symbols = replace_symbols(text)
    clean_text = replace_numbers(text_without_symbols)
    clean_text = clean_text.translate(str.maketrans('', '', removed_punct))
    return clean_text

def replace_numbers(text):
    """Replaces the numbers form a text by their written form
    Args:
        text: A string in which numbers are to be replaced
    Returns:
        text_without_numbers: The input text with numbers replaced by their written form

    >>> replace_numbers('zin met een getal zoals: 12000')
    'zin met een getal zoals: twaalfduizend'
    """
    number_of_numbers = 0
    text_list = text.split(" ")
    for position, word in enumerate(text_list):
        if word.isdigit():
            number_of_numbers += 1
            text_list[position] = num2words(word, to='cardinal', lang='nl')
        elif check_and_covert_interger(word):
            text_list[position] = check_and_covert_interger(word)
    text_without_numbers = " ".join(text_list)
    logging.info(f'replaced {number_of_numbers} numbers by their written form')
    return text_without_numbers

def replace_symbols(text):
    """Replace symbols by their written form a string
    Args:
        text (str): A text string to replace the symbols from
    Returns:
        clean_text: The text with the symbols replaces with their written form.

    >>> replace_symbols("Een voorbeeld tekst met symbolen zoals %, & en °")
    'Een voorbeeld tekst met symbolen zoals procent, en en graden'
    """
    number_of_symbols = 0
    number_of_symbols += text.count('%') + text.count('&') + text.count('°') + text.count('&')
    text_without_symbols = text.replace('%'," procent").replace('°'," graden") \
                           .replace('&',"en").replace('€',"euro").replace('  ',' ')
    logging.info(f'replaced {number_of_symbols} symbols by their written form')
    return text_without_symbols



if __name__ == "__main__":
    import doctest
    doctest.testmod()
