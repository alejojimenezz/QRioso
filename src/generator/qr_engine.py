import qrcode
import qrcode.image.svg
from pathlib import Path
from PIL import ImageColor
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers.pil import (
    SquareModuleDrawer, GappedSquareModuleDrawer, CircleModuleDrawer,
    RoundedModuleDrawer, VerticalBarsDrawer, HorizontalBarsDrawer,
)
from qrcode.image.styles.moduledrawers.svg import (
    SvgPathSquareDrawer, SvgPathCircleDrawer,
)

SUPPORTED_FORMATS = ["png", "svg"]

PNG_DOT_STYLES = {
    "Cuadrado": SquareModuleDrawer,
    "Cuadrado con espacio": GappedSquareModuleDrawer,
    "Círculo": CircleModuleDrawer,
    "Redondeado": RoundedModuleDrawer,
    "Barras verticales": VerticalBarsDrawer,
    "Barras horizontales": HorizontalBarsDrawer,
}

SVG_DOT_STYLES = {
    "Cuadrado": SvgPathSquareDrawer,
    "Círculo": SvgPathCircleDrawer,
}

DOT_STYLES = list(PNG_DOT_STYLES.keys())

ERROR_CORRECTION_LEVELS = {
    "L ~7%": qrcode.constants.ERROR_CORRECT_L,
    "M ~15%": qrcode.constants.ERROR_CORRECT_M,
    "Q ~25%": qrcode.constants.ERROR_CORRECT_Q,
    "H ~30%": qrcode.constants.ERROR_CORRECT_H,
}

class QRGenerator:
    
    # Basic:
    #     gen = QRGenerator()
    #     gen.generate("https://example.com", "output/mi_qr.png")

    # Advanced:
    #     gen = QRGenerator(box_size=12, border=2, error_correction="H")
    #     gen.generate("https://example.com", "output/mi_qr.svg")

    def __init__(
        self,
        box_size: int = 10,
        border: int = 2,
        dot_style: str = "Cuadrado",
        error_correction: str = "M ~15%",
        fill_color: str = "black",
        back_color: str = "white",
    ):

        if dot_style not in PNG_DOT_STYLES:
            raise ValueError(f"Invalid dot style: '{dot_style}'. Use from: {DOT_STYLES}")
        self.dot_style = dot_style
                
        if error_correction not in ERROR_CORRECTION_LEVELS:
            raise ValueError(
                f"Invalid correction level: '{error_correction}'. "
                f"Use from: {list(ERROR_CORRECTION_LEVELS.keys())}"
            )

        self.box_size = box_size
        self.border = border
        self.error_correction = error_correction
        self.fill_color = fill_color
        self.back_color = back_color

    def generate(self, data: str, output_path: str) -> Path:
        
        if not data or not data.strip():
            raise ValueError("QR content can't be empty.")

        path = Path(output_path)
        fmt = path.suffix.lstrip(".").lower()

        if fmt not in SUPPORTED_FORMATS:
            raise ValueError(
                f"Format '{fmt}' not supported. Use: {SUPPORTED_FORMATS}"
            )

        path.parent.mkdir(parents=True, exist_ok=True)

        if fmt == "png":
            self._generate_png(data, path)
        elif fmt == "svg":
            self._generate_svg(data, path)

        return path

    # Private methods

    def _build_qr(self, data: str) -> qrcode.QRCode:
        qr = qrcode.QRCode(
            version=None,
            error_correction=ERROR_CORRECTION_LEVELS[self.error_correction],
            box_size=self.box_size,
            border=self.border,
        )
        qr.add_data(data)
        qr.make(fit=True)
        return qr

    def build_pil_image(self, data: str):
        qr = self._build_qr(data)
        return qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=PNG_DOT_STYLES[self.dot_style](),
            color_mask=SolidFillColorMask(
                back_color=ImageColor.getrgb(self.back_color),
                front_color=ImageColor.getrgb(self.fill_color),
            ),
        )

    def _generate_png(self, data: str, path: Path) -> None:
        self.build_pil_image(data).save(path)

    def _generate_svg(self, data: str, path: Path) -> None:
        if self.dot_style not in SVG_DOT_STYLES:
            raise ValueError(
                f"El estilo '{self.dot_style}' no está disponible en SVG. "
                f"Use: {list(SVG_DOT_STYLES.keys())}"
            )
        qr = self._build_qr(data)
        img = qr.make_image(
            image_factory=qrcode.image.svg.SvgPathImage,
            module_drawer=SVG_DOT_STYLES[self.dot_style](),
        )
        with open(path, "wb") as f:
            img.save(f)