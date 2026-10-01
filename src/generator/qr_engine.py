import qrcode
import qrcode.image.svg
from pathlib import Path

SUPPORTED_FORMATS = ["png", "svg"]

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
        error_correction: str = "M ~15%",
        fill_color: str = "black",
        back_color: str = "white",
    ):
                
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

    def _generate_png(self, data: str, path: Path) -> None:
        qr = self._build_qr(data)
        img = qr.make_image(
            fill_color=self.fill_color,
            back_color=self.back_color,
        )
        img.save(path)

    def _generate_svg(self, data: str, path: Path) -> None:
        qr = self._build_qr(data)
        img = qr.make_image(image_factory=qrcode.image.svg.SvgPathImage)
        with open(path, "wb") as f:
            img.save(f)