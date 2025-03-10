# test_lambda.py (Pruebas unitarias con pytest)
import pytest
import requests
from unittest.mock import patch, Mock

from descargador.proyecto import download_page
from scraper.proyecto import extract_info


def test_download_page_success():
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "<html><body>Test HTML</body></html>"
        mock_get.return_value = mock_response
        os.makedirs(f"/tmp/landing-casas-{curr_date}", exist_ok=True)
        file_name = download_page(1, "2025-03-10")
        assert file_name is not None

def test_download_page_failure():
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response
        
        file_name = download_page(1, "2025-03-10")
        assert file_name is None

def test_extract_info():
    sample_html = '<html><body><a class="listing listing-card" data-price="100000" data-location="Centro" data-rooms="2" data-floorarea="60"><p data-test="bathrooms">1 Baño</p></a></body></html>'
    data = extract_info(sample_html, "2025-03-10")
    assert len(data) == 1
    assert data[0] == ["2025-03-10", "Centro", "100000", "2", "1", "60"]
