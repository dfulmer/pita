from pathlib import Path
import pytest
import shutil
from unittest.mock import patch, mock_open

from app.app import PDFInvoiceScanner


@pytest.fixture
def fake_pdf():
    return "tests/fixtures/fakepdf.pdf"


@pytest.fixture
def fake_blank_pdf_source():
    return Path(__file__).parent / "fixtures/fakeblankpdf.pdf"


@pytest.fixture
def fake_invoice_text():
    fixture_path = Path(__file__).parent / "fixtures" / "fakeinvoicetext.txt"
    with open(fixture_path, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def fake_pdf_without_total():
    return Path(__file__).parent / "fixtures/fakepdfwithouttotal.pdf"


@pytest.fixture
def fake_pdf_source():
    return Path(__file__).parent / "fixtures/fakepdf.pdf"


def test_log_file_is_created(tmp_path):
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.log("Test message")
    assert log_file.exists()
    assert "Test message" in log_file.read_text()


def test_setup_logger_method_prints(tmp_path, capsys):
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.log("Test message")
    captured = capsys.readouterr()
    assert "Test message" in captured.out


def test_no_pdfs_found(tmp_path):
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.directory = tmp_path  # override current directory
    list_of_pdfs = scanner.get_pdf_files()
    assert list_of_pdfs == []


def test_no_pdfs_found_logging(tmp_path):
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.directory = tmp_path  # override current directory
    scanner.run()
    assert "No PDF files found" in log_file.read_text()


def test_no_pdfs_found_prints(tmp_path, capsys):
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.directory = tmp_path  # override current directory
    scanner.run()
    captured = capsys.readouterr()
    assert "No PDF files found" in captured.out


def test_extract_text(fake_pdf, tmp_path):
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.directory = tmp_path  # override current directory
    text = scanner.extract_text(fake_pdf)
    assert "Invoice # 1KRT-XP11-PKD7" in text


def test_extract_invoices(fake_pdf, tmp_path):
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.directory = tmp_path  # override current directory
    text = scanner.extract_text(fake_pdf)
    invoice_list = scanner.extract_invoices(text)
    assert len(invoice_list) == 2


def test_for_no_invoice_text(fake_blank_pdf_source, tmp_path):
    destination_path = tmp_path / "fakeblankpdf.pdf"
    shutil.copyfile(fake_blank_pdf_source, destination_path)
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.directory = tmp_path  # override current directory
    scanner.run()
    assert "No invoices found in" in log_file.read_text()


def test_extract_invoice_number(fake_invoice_text, tmp_path):
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.directory = tmp_path  # override current directory
    invoice_number = scanner.extract_invoice_number(fake_invoice_text)
    assert invoice_number == "1LC7-4XGY-N1MK"


def test_extract_invoice_number_no_match(fake_invoice_text, tmp_path):
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.directory = tmp_path  # override current directory
    fake_invoice_text = "blah blah blah"
    invoice_number = scanner.extract_invoice_number(fake_invoice_text)
    assert invoice_number is None


def test_extract_invoice_date(fake_invoice_text, tmp_path):
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.directory = tmp_path  # override current directory
    invoice_date = scanner.extract_invoice_date(fake_invoice_text)
    assert invoice_date == "July 01, 2025"


def test_extract_invoice_date_no_match(fake_invoice_text, tmp_path):
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.directory = tmp_path  # override current directory
    fake_invoice_text = "blah blah blah"
    invoice_date = scanner.extract_invoice_date(fake_invoice_text)
    assert invoice_date is None


def test_extract_invoice_purchase_order_line_number(fake_invoice_text, tmp_path):
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.directory = tmp_path  # override current directory
    invoice_purchase_order_line_number = (
        scanner.extract_invoice_purchase_order_line_number(fake_invoice_text)
    )
    assert invoice_purchase_order_line_number == "POL-218829"


def test_extract_invoice_purchase_order_line_number_no_match(
    fake_invoice_text, tmp_path
):
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.directory = tmp_path  # override current directory
    fake_invoice_text = "blah blah blah"
    invoice_purchase_order_line_number = (
        scanner.extract_invoice_purchase_order_line_number(fake_invoice_text)
    )
    assert invoice_purchase_order_line_number is None


def test_extract_invoice_total(fake_invoice_text, tmp_path):
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.directory = tmp_path  # override current directory
    invoice_total = scanner.extract_invoice_total(fake_invoice_text)
    assert invoice_total == "32.11"


def test_extract_invoice_total_no_match(fake_invoice_text, tmp_path):
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.directory = tmp_path  # override current directory
    fake_invoice_text = "blah blah blah"
    invoice_total = scanner.extract_invoice_total(fake_invoice_text)
    assert invoice_total is None


def test_extract_invoice_shipping_and_handling(fake_invoice_text, tmp_path):
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.directory = tmp_path  # override current directory
    invoice_shipping_and_handling = scanner.extract_invoice_shipping_and_handling(
        fake_invoice_text
    )
    assert invoice_shipping_and_handling == "0.00"


def test_extract_invoice_shipping_and_handling_no_match(fake_invoice_text, tmp_path):
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.directory = tmp_path  # override current directory
    fake_invoice_text = "blah blah blah"
    invoice_shipping_and_handling = scanner.extract_invoice_shipping_and_handling(
        fake_invoice_text
    )
    assert invoice_shipping_and_handling is None


def test_extract_invoice_quantity(fake_invoice_text, tmp_path):
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.directory = tmp_path  # override current directory
    invoice_quantity = scanner.extract_invoice_quantity(fake_invoice_text)
    assert invoice_quantity == "1"


def test_extract_invoice_quantity_no_match(fake_invoice_text, tmp_path):
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.directory = tmp_path  # override current directory
    fake_invoice_text = "blah blah blah"
    invoice_quantity = scanner.extract_invoice_quantity(fake_invoice_text)
    assert invoice_quantity == "1"


def test_extract_invoice_line_price(fake_invoice_text, tmp_path):
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.directory = tmp_path  # override current directory
    invoice_line_price = scanner.extract_invoice_line_price(fake_invoice_text)
    assert invoice_line_price == "32.11"


def test_extract_invoice_line_price_no_match(fake_invoice_text, tmp_path):
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.directory = tmp_path  # override current directory
    fake_invoice_text = "blah blah blah"
    invoice_line_price = scanner.extract_invoice_line_price(fake_invoice_text)
    assert invoice_line_price is None


def test_invoice_with_missing_data(fake_pdf_without_total, tmp_path, capsys):
    destination_path = tmp_path / "fakepdfwithouttotal.pdf"
    shutil.copyfile(fake_pdf_without_total, destination_path)
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.directory = tmp_path  # override current directory
    scanner.run()
    captured = capsys.readouterr()
    assert "Missing fields in" in log_file.read_text()
    assert "Missing fields in" in captured.out


def test_extract_yyyymmdd(tmp_path):
    datestring = "July 01, 2025"
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.directory = tmp_path  # override current directory
    formatteddate = scanner.extract_yyyymmdd(datestring)
    assert formatteddate == "20250701"


def test_extract_yyyymmdd_without_a_date(tmp_path):
    datestring = "Jul 01, 2025"
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.directory = tmp_path  # override current directory
    formatteddate = scanner.extract_yyyymmdd(datestring)
    assert formatteddate is None


def test_the_whole_thing(tmp_path, fake_pdf_source, capsys):
    destination_path = tmp_path / "fakepdf.pdf"
    shutil.copyfile(fake_pdf_source, destination_path)
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.directory = tmp_path  # override current directory
    scanner.run()
    file_to_write = tmp_path / "1KRT-XP11-PKD7.edi"
    assert log_file.exists()
    assert file_to_write.exists()
    assert "Successfully wrote" in log_file.read_text()


def test_get_missing_invoice_fields_all_present():
    scanner = PDFInvoiceScanner()
    missing = scanner.get_missing_invoice_fields(
        invoice_number="INV123",
        invoice_date="January 01, 2024",
        invoice_purchase_order_line_number="PO456",
        invoice_total="100.00",
        invoice_shipping_and_handling="10.00",
        invoice_quantity="2",
        invoice_line_price="50.00",
        invoice_date_yyyymmdd="20240101",
    )
    assert missing == []


def test_get_missing_invoice_fields_some_missing():
    scanner = PDFInvoiceScanner()
    missing = scanner.get_missing_invoice_fields(
        invoice_number=None,
        invoice_date="January 01, 2024",
        invoice_purchase_order_line_number=None,
        invoice_total="100.00",
        invoice_shipping_and_handling=None,
        invoice_quantity="2",
        invoice_line_price=None,
        invoice_date_yyyymmdd=None,
    )
    assert set(missing) == {
        "invoice_number",
        "invoice_purchase_order_line_number",
        "invoice_shipping_and_handling",
        "invoice_line_price",
        "invoice_date_yyyymmdd",
    }


def test_get_missing_invoice_fields_some_other_missing():
    scanner = PDFInvoiceScanner()
    missing = scanner.get_missing_invoice_fields(
        invoice_number="1",
        invoice_date=None,
        invoice_purchase_order_line_number="1",
        invoice_total=None,
        invoice_shipping_and_handling="1.99",
        invoice_quantity=None,
        invoice_line_price="5.99",
        invoice_date_yyyymmdd="20250807",
    )
    assert set(missing) == {"invoice_date", "invoice_total", "invoice_quantity"}


def selective_open(file, mode="r", *args, **kwargs):
    # Support both str and Path objects
    filename = str(file)
    if filename.endswith(".edi") and "w" in mode:
        raise OSError("Disk full")
    return open_orig(file, mode, *args, **kwargs)


open_orig = open  # Save reference to the real open


def test_edi_write_failure_precise(tmp_path, fake_pdf_source):
    """Test error handling when writing .edi files fails."""
    destination_path = tmp_path / "fakepdf.pdf"
    shutil.copyfile(fake_pdf_source, destination_path)
    log_file = tmp_path / "test_log.log"
    scanner = PDFInvoiceScanner(log_file=str(log_file))
    scanner.directory = tmp_path

    with patch("builtins.open", side_effect=selective_open):
        scanner.run()

    log_contents = log_file.read_text()
    assert "Error writing" in log_contents
    assert "Disk full" in log_contents
