import base64
import os

import docx

from cStringIO import StringIO
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
import os
import sys
import getopt

try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML
import zipfile

WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
PARA = WORD_NAMESPACE + 'p'
TEXT = WORD_NAMESPACE + 't'


def text_catdoc(filename):
    (fi, fo, fe) = os.popen3('catdoc -w "%s"' % filename)
    fi.close()
    retval = fo.read()
    erroroutput = fe.read()
    fo.close()
    fe.close()
    if not erroroutput:
        return retval
    else:
        return ""


def get_docx_text(path):
    """
    Take the path of a docx file as argument, return the text in unicode.
    """
    document = zipfile.ZipFile(path)
    xml_content = document.read('word/document.xml')
    document.close()
    tree = XML(xml_content)

    paragraphs = []
    for paragraph in tree.getiterator(PARA):
        texts = [node.text
                 for node in paragraph.getiterator(TEXT)
                 if node.text]
        if texts:
            paragraphs.append(''.join(texts))

    return '\n\n'.join(paragraphs)


def getText(filename):
    doc = docx.Document(filename)
    fullText = []
    print(doc)
    for para in doc.paragraphs:
        fullText.append(para.text)
    return '\n'.join(fullText)


def convert_pdf_to_text(fname, pages=None):
    if not pages:
        pagenums = set()
    else:
        pagenums = set(pages)

    output = StringIO()
    manager = PDFResourceManager()
    converter = TextConverter(manager, output, laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)

    infile = file(fname, 'rb')
    for page in PDFPage.get_pages(infile, pagenums):
        interpreter.process_page(page)
    infile.close()
    converter.close()
    text = output.getvalue()
    output.close
    return text


def document_to_text(base64data, document_type, name):

    fres = open("/var/tmp/" + name, "w")
    fres.write(base64.b64decode(base64data))
    fres.close()
    text = ""
    if document_type == ".pdf":
        text = convert_pdf_to_text(name)
    if document_type == ".docx":
        text = get_docx_text(name)
    os.remove("/var/tmp/" + name)

    return text
