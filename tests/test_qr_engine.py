# qrioso/tests/test_qr_engine.py
# Unit tests
# Run with: uv run pytest

import pytest
from pathlib import Path
from src.generator.qr_engine import QRGenerator


# Fixtures
@pytest.fixture
def generator():
    """Instancia de QRGenerator con valores por defecto."""
    return QRGenerator()


@pytest.fixture
def tmp_output(tmp_path):
    """Carpeta temporal que pytest limpia después de cada test."""
    return tmp_path


# PNG generation
def test_genera_png(generator, tmp_output):
    """Debe crear un archivo .png en la ruta indicada."""
    output = tmp_output / "test.png"
    result = generator.generate("https://example.com", output)

    assert result == output
    assert output.exists()
    assert output.stat().st_size > 0


def test_png_con_url_larga(generator, tmp_output):
    """URLs largas deben generar un QR válido (version auto-escala)."""
    url = "https://www.example.com/very/large/path?param1=value1&param2=value2"
    output = tmp_output / "long_url.png"
    generator.generate(url, output)

    assert output.exists()


def test_png_crea_carpeta_si_no_existe(generator, tmp_output):
    """Debe crear la carpeta de destino si no existe."""
    output = tmp_output / "new_folder" / "subfolder" / "qr.png"
    generator.generate("https://example.com", output)

    assert output.exists()


# SVG generation

def test_genera_svg(generator, tmp_output):
    """Debe crear un archivo .svg con contenido XML válido."""
    output = tmp_output / "test.svg"
    generator.generate("https://example.com", output)

    assert output.exists()
    content = output.read_text(encoding="utf-8")
    assert "<svg" in content


# Builder parameters

def test_error_correction_validos():
    """Todos los niveles de corrección válidos deben instanciar sin error."""
    for level in ["L ~7%", "M ~15%", "Q ~25%", "H ~30%"]:
        gen = QRGenerator(error_correction=level)
        assert gen.error_correction == level


def test_error_correction_invalido():
    """Un nivel de corrección inválido debe lanzar ValueError."""
    with pytest.raises(ValueError, match="Invalid correction level"):
        QRGenerator(error_correction="Z")


def test_colores_personalizados(tmp_output):
    """Colores distintos a negro/blanco deben generar un PNG sin error."""
    gen = QRGenerator(fill_color="#1a237e", back_color="#e3f2fd")
    output = tmp_output / "color.png"
    gen.generate("https://example.com", output)

    assert output.exists()


# Input validations

def test_data_vacia_lanza_error(generator, tmp_output):
    """Contenido vacío debe lanzar ValueError."""
    with pytest.raises(ValueError, match="QR content can't be empty."):
        generator.generate("", tmp_output / "empty.png")


def test_data_solo_espacios_lanza_error(generator, tmp_output):
    """Contenido con solo espacios debe lanzar ValueError."""
    with pytest.raises(ValueError, match="QR content can't be empty."):
        generator.generate("   ", tmp_output / "spaces.png")


def test_formato_no_soportado_lanza_error(generator, tmp_output):
    """Formato desconocido debe lanzar ValueError."""
    with pytest.raises(ValueError, match="not supported"):
        generator.generate("https://example.com", tmp_output / "qr.gif")


# Plain text
def test_texto_plano(generator, tmp_output):
    """El QR debe poder codificar texto plano además de URLs."""
    output = tmp_output / "text.png"
    generator.generate("Hello from QRioso", output)

    assert output.exists()