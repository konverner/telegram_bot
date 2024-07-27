from io import BytesIO
from typing import Set

from PyPDF2 import PdfReader
import docx
from fastapi import UploadFile

from telegram_bot.service.exceptions import TextFileDecodingException, UnexpectedFileReadingException, \
    WordFileReadingException, FileTooLargeException, PDFFileReadingException, UnsupportedFileTypeException


class FileParser:
    """Class to parse and extract content from uploaded files."""

    def __init__(self, max_file_size_mb: int, allowed_file_types: Set[str]):
        self.max_file_size_mb = max_file_size_mb
        self.handlers = {
            "txt": self.extract_txt_content,
            "doc": self.extract_word_content,
            "docx": self.extract_word_content,
            "pdf": self.extract_pdf_content
        }

    def extract_txt_content(self, file: UploadFile) -> str:
        """Extract content from a text file.

        Returns:
            The content of the text file.

        Raises:
            TextFileDecodingException: Error decoding the text file.
            UnexpectedFileReadingException: Unexpected error while reading the text file.
        """
        try:
            content = file.file.read()
            return content.decode("utf-8")
        except UnicodeDecodeError as e:
            raise TextFileDecodingException() from e
        except Exception as e:
            raise UnexpectedFileReadingException() from e

    def extract_word_content(self, file: UploadFile) -> str:
        """Extract content from a Word document.

        Returns:
            The content of the Word document.

        Raises:
            WordFileReadingException: Error reading the Word document.
        """
        try:
            content = ""
            doc = docx.Document(file.file)
            for paragraph in doc.paragraphs:
                content += paragraph.text + "\n"
            return content.strip("\n")
        except Exception as e:
            raise WordFileReadingException() from e

    def extract_pdf_content(self, file: UploadFile) -> str:
        """Extract content from a PDF file.

        Returns:
            The content of the PDF file.

        Raises:
            PDFFileReadingException: Error reading the PDF file.
        """
        try:
            pdf = PdfReader(BytesIO(file.file.read()))
            content = ""
            for page in pdf.pages:
                content += page.extract_text()
            return content
        except Exception as e:
            raise PDFFileReadingException() from e

    def extract_content(self, file: UploadFile) -> str:
        """Extract content from an uploaded file based on its type.

        Returns:
            The content of the file.

        Raises:
            FileTooLargeException: The file is too large.
            UnsupportedFileTypeException: The file type is not supported.
            TextFileDecodingException: Error decoding the text file.
            WordFileReadingException: Error reading the Word document.
            UnexpectedFileReadingException: Unexpected error while reading the file.
        """
        if file.size > self.max_file_size_mb * 1024 * 1024:
            raise FileTooLargeException()

        try:
            file_extension = file.filename.rsplit(".", 1)[1].lower()
        except IndexError:
            raise UnsupportedFileTypeException("The file has no extension")

        handler = self.handlers.get(file_extension)
        if handler:
            try:
                return handler(file)
            except UnsupportedFileTypeException as e:
                raise e
            except TextFileDecodingException as e:
                raise e
            except WordFileReadingException as e:
                raise e
            except Exception as e:
                raise UnexpectedFileReadingException(f"Unexpected error: {str(e)}") from e
        else:
            raise UnsupportedFileTypeException(file_extension)
