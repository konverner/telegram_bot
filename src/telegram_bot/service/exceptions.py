class FileTooLargeException(Exception):
	def __init__(self, max_file_size_mb: int = 10):
		message = f"The file is too large, the maximum size is {max_file_size_mb} MB"
		super().__init__(message)


class UnsupportedFileTypeException(Exception):
	def __init__(self, file_type:str, supported_types: list = ["txt", "pdf", "docx"]):
		message = f"File type {file_type} is not supported. Supported types: {', '.join(supported_types)}"
		super().__init__(message)


class TextFileDecodingException(Exception):
	def __init__(self, message="Decoding error while reading the text file"):
		super().__init__(message)


class WordFileReadingException(Exception):
	def __init__(self, message="Error reading the Word document"):
		super().__init__(message)


class UnexpectedFileReadingException(Exception):
	def __init__(self, message="Unexpected error while reading the text file"):
		super().__init__(message)


class PDFFileReadingException(Exception):
	def __init__(self, message="Error reading the PDF file"):
		super().__init__(message)
