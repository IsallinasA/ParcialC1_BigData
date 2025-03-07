import unittest
import pandas as pd
from unittest.mock import patch, MagicMock
import lambda_scraper  # Importa la Lambda del scraper
import lambda_parser  # Importa la Lambda del parser

class TestLambdaFunctions(unittest.TestCase):

    ## 1️⃣ Prueba: Validar que el CSV se genera correctamente ##
    def test_csv_generation(self):
        data = [
            {"nombre": "Apartamento 1", "precio": 1000, "ubicación": "Bogotá"},
            {"nombre": "Apartamento 2", "precio": 1200, "ubicación": "Medellín"}
        ]
        csv_content = lambda_parser.generate_csv(data)
        df = pd.read_csv(csv_content)

        self.assertEqual(len(df), 2)
        self.assertEqual(df.iloc[0]["nombre"], "Apartamento 1")
        self.assertEqual(df.iloc[1]["precio"], 1200)

    ## 2️⃣ Prueba: Validar que la Lambda puede leer HTML del S3 ##
    @patch("lambda_scraper.boto3.client")
    def test_s3_html_fetch(self, mock_s3_client):
        mock_s3 = MagicMock()
        mock_s3.get_object.return_value = {"Body": MagicMock(read=lambda: b"<html><body><h1>Test</h1></body></html>")}
        mock_s3_client.return_value = mock_s3

        html_content = lambda_scraper.get_html_from_s3("landing-casas-xxx", "test.html")
        self.assertIn("<h1>Test</h1>", html_content)

    ## 3️⃣ Prueba: Validar que la Lambda filtra la información correctamente ##
    def test_parse_apartments(self):
        html = """
        <html>
            <body>
                <div class='apartment'>
                    <h2>Apartamento 1</h2>
                    <span class='price'>1000</span>
                </div>
                <div class='apartment'>
                    <h2>Apartamento 2</h2>
                    <span class='price'>1200</span>
                </div>
            </body>
        </html>
        """
        result = lambda_parser.parse_html(html)
        expected_result = [
            {"nombre": "Apartamento 1", "precio": 1000},
            {"nombre": "Apartamento 2", "precio": 1200}
        ]
        self.assertEqual(result, expected_result)

if __name__ == "__main__":
    unittest.main()
