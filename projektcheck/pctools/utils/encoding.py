# -*- coding: utf-8 -*-

from pctools.utils.config_language import mylanguage

def encode(text):
    """encode text to CP1252"""
    if not isinstance(text, unicode):
        try:
            u = text.decode('utf8')
        except UnicodeDecodeError:
            u = text.decode('latin1')
        except UnicodeDecodeError:
            u = text.decode('CP1252')
    else:
        u = text
    text_cp1252 = u.encode('CP1252')
    return text_cp1252

def language(datatype):

    #import ctypes
    #import locale
    #windll = ctypes.windll.kernel32
    #language = str(windll.GetUserDefaultUILanguage())

    if datatype == 'feature class':
        if mylanguage == 'de_DE':
            return u'Feature-Class'
        else:
            return u'feature class'
