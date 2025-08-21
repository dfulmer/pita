import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from pypdf import PdfReader


class PDFInvoiceScanner:
    def __init__(self, log_file: str = "pita.log"):
        self.log_file = log_file
        self.logger = self.setup_logger(log_file)
        self.directory = Path(".")

    def setup_logger(self, log_file: str) -> logging.Logger:
        logger_name = log_file
        logger = logging.getLogger(logger_name)
        logger.setLevel(logging.INFO)

        # Remove all handlers if they exist (important for pytest isolation)
        logger.handlers.clear()

        handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(
            "%(asctime)s - %(message)s", datefmt="%Y-%m-%d %H:%M:%S"
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Create console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        return logger

    def log(self, message):
        self.logger.info(message)

    def get_pdf_files(self):
        return list(self.directory.glob("*.pdf"))

    def extract_text(self, file_path):
        reader = PdfReader(str(file_path))
        return "\n".join(
            page.extract_text(extraction_mode="layout") or "" for page in reader.pages
        )

    def extract_invoices(self, text):
        pattern = re.compile(r"Invoice\s+Invoice #\s+[\w-]+\s+\| .*?FAQs", re.DOTALL)
        return re.findall(pattern, text)

    def extract_invoice_number(self, invoice_text):
        """
        Extracts the invoice number from the given invoice text using a regular expression.

        Args:
          invoice_text (str): The text of the invoice.

        Returns:
          str or None: The extracted invoice number, or None if not found.
        """
        match = re.search(r"Invoice\s+Invoice #\s+([\w-]+)", invoice_text)
        if match:
            return match.group(1)
        else:
            return None

    def extract_invoice_date(self, invoice_text):
        """
        Extracts the invoice date from the given invoice text using a regular expression.

        Args:
          invoice_text (str): The text of the invoice.

        Returns:
          str or None: The extracted invoice date, or None if not found.
        """
        match = re.search(
            r"Invoice\s+Invoice #\s+[\w-]+\s+\|\s*(\w+ \d\d, \d\d\d\d).*", invoice_text
        )
        if match:
            return match.group(1)
        else:
            return None

    def extract_invoice_purchase_order_line_number(self, invoice_text):
        """
        Extracts the invoice purchase order line number from the given invoice text using a regular expression.

        Args:
          invoice_text (str): The text of the invoice.

        Returns:
          str or None: The extracted invoice purchase order line number, or None if not found.
        """
        match = re.search(
            r"Invoice\s+Invoice #\s+[\w-]+\s+\|\s*\w+ \d\d, \d\d\d\d.*PO #\s+([\w-]+)\s.*?",
            invoice_text,
            re.DOTALL,
        )
        if match:
            return match.group(1)
        else:
            return None

    def extract_invoice_total(self, invoice_text):
        """
        Extracts the invoice total from the given invoice text using a regular expression.

        Args:
          invoice_text (str): The text of the invoice.

        Returns:
          str or None: The extracted invoice total, or None if not found.
        """
        match = re.search(
            r"Invoice\s+Invoice #\s+[\w-]+\s+\|\s*\w+ \d\d, \d\d\d\d.*PO #\s+[\w-]+\s.*?Amount due\s*\$\s?(\d+.\d+)",
            invoice_text,
            re.DOTALL,
        )
        if match:
            return match.group(1)
        else:
            return None

    def extract_invoice_shipping_and_handling(self, invoice_text):
        """
        Extracts the invoice shipping and handling from the given invoice text using a regular expression.

        Args:
          invoice_text (str): The text of the invoice.

        Returns:
          str or None: The extracted invoice shipping and handling, or None if not found.
        """
        match = re.search(
            r"Shipping & handling\s+\$\s+([\d.]+)", invoice_text, re.DOTALL
        )
        if match:
            return match.group(1)
        else:
            return None

    def extract_invoice_quantity(self, invoice_text):
        """
        Extracts the invoice quantity from the given invoice text using a regular expression.

        Args:
          invoice_text (str): The text of the invoice.

        Returns:
          str or None: The extracted invoice quantity, or None if not found.
        """
        match = re.search(
            r"Invoice details.*?([\d]+)\s+\$[\d.]+\s+\$[\d.]+\s+[\d.]+%\s+",
            invoice_text,
            re.DOTALL,
        )
        if match:
            return match.group(1)
        else:
            # default to 1
            return "1"

    def extract_invoice_line_price(self, invoice_text):
        """
        Extracts the invoice line price from the given invoice text using a regular expression.

        Args:
          invoice_text (str): The text of the invoice.

        Returns:
          str or None: The extracted invoice line price, or None if not found.
        """
        match = re.search(
            r"Invoice details.*?[\d]+\s+\$[\d.]+\s+\$([\d.]+)\s+[\d.]+%\s+",
            invoice_text,
            re.DOTALL,
        )
        if match:
            return match.group(1)
        else:
            return None

    def extract_yyyymmdd(self, invoice_date):
        try:
            date_object = datetime.strptime(invoice_date, "%B %d, %Y")
            invoicedateyyyymmdd = date_object.strftime("%Y%m%d")
            return invoicedateyyyymmdd
        except Exception:
            return None

    def get_missing_invoice_fields(
        self,
        invoice_number,
        invoice_date,
        invoice_purchase_order_line_number,
        invoice_total,
        invoice_shipping_and_handling,
        invoice_quantity,
        invoice_line_price,
        invoice_date_yyyymmdd,
    ):
        """
        Returns a list of missing invoice fields.
        """
        missing = []
        if invoice_number is None:
            missing.append("invoice_number")
        if invoice_date is None:
            missing.append("invoice_date")
        if invoice_purchase_order_line_number is None:
            missing.append("invoice_purchase_order_line_number")
        if invoice_total is None:
            missing.append("invoice_total")
        if invoice_shipping_and_handling is None:
            missing.append("invoice_shipping_and_handling")
        if invoice_quantity is None:
            missing.append("invoice_quantity")
        if invoice_line_price is None:
            missing.append("invoice_line_price")
        if invoice_date_yyyymmdd is None:
            missing.append("invoice_date_yyyymmdd")
        return missing

    def run(self):
        filename = os.path.basename(__file__)
        self.log(f"Starting {filename}")
        pdfs = self.get_pdf_files()
        if not pdfs:
            self.log("No PDF files found.")
            return

        for pdf in pdfs:
            self.log(f"Processing {pdf.name}")
            invoice_counter = 0
            text = self.extract_text(pdf)
            invoice_list = self.extract_invoices(text)

            if not invoice_list:
                self.log(f"No invoices found in {pdf.name}")
                continue  # Skip to next PDF

            for invoice in invoice_list:
                invoice_counter += 1

                invoice_number = self.extract_invoice_number(invoice)
                invoice_date = self.extract_invoice_date(invoice)
                invoice_purchase_order_line_number = (
                    self.extract_invoice_purchase_order_line_number(invoice)
                )
                invoice_total = self.extract_invoice_total(invoice)
                invoice_shipping_and_handling = (
                    self.extract_invoice_shipping_and_handling(invoice)
                )
                invoice_quantity = self.extract_invoice_quantity(invoice)
                invoice_line_price = self.extract_invoice_line_price(invoice)
                invoice_date_yyyymmdd = self.extract_yyyymmdd(invoice_date)

                missing = self.get_missing_invoice_fields(
                    invoice_number,
                    invoice_date,
                    invoice_purchase_order_line_number,
                    invoice_total,
                    invoice_shipping_and_handling,
                    invoice_quantity,
                    invoice_line_price,
                    invoice_date_yyyymmdd,
                )
                if missing:
                    self.log(
                        f"Missing fields in {pdf.name} invoice number {invoice_counter}: {', '.join(missing)}"
                    )
                    continue  # on to the next invoice

                edifile = f"""UNA:+.? '
UNB+UNOC:3+AMAZ:31B+LIBRDMF:ZZ+240101:0000+110'
UNH++INVOIC:D:96A:UN:EAN008'
BGM+380+{invoice_number}'
DTM+137:{invoice_date_yyyymmdd}:102'
CUX+2:USD:4'
ALC+C++++DL::28:Freight Charges'
MOA+8:{invoice_shipping_and_handling}'
LIN+1'
QTY+47:{invoice_quantity}'
MOA+203:{invoice_line_price}'
PRI+AAB:{invoice_line_price}'
RFF+LI:{invoice_purchase_order_line_number}'
UNS+S'
CNT+2:2'
MOA+79:{invoice_total}'
MOA+9:{invoice_total}'
UNT+23+1'
UNZ+1+1'
"""

                edi_filename = self.directory / f"{invoice_number}.edi"
                try:
                    with open(edi_filename, "w", encoding="utf-8") as edi_file:
                        edi_file.write(edifile)
                    self.log(f"Successfully wrote {edi_filename}")
                except Exception as e:
                    self.log(f"Error writing {edi_filename}: {e}")

            self.log(f"Finished with pdf file: {pdf.name}. Invoices: {invoice_counter}")
