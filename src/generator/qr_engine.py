import qrcode
import qrcode.image.svg
from pathlib import Path
from PIL import Image, ImageColor, ImageDraw
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import SolidFillColorMask
from qrcode.image.styles.moduledrawers.pil import (
    SquareModuleDrawer, GappedSquareModuleDrawer, CircleModuleDrawer,
    RoundedModuleDrawer, VerticalBarsDrawer, HorizontalBarsDrawer,
)
from qrcode.image.styles.moduledrawers.svg import (
    SvgPathSquareDrawer, SvgPathCircleDrawer,
)
from src.generator.config import EYE_RADIUS_MAX

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

EYE_STYLES = {
    "Cuadrado": 0.0,
    "Redondeado": EYE_RADIUS_MAX,
}

EYE_MODULES = 7

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
        eye_style: str = "Cuadrado",
        error_correction: str = "M ~15%",
        fill_color: str = "black",
        back_color: str = "white",
    ):

        if dot_style not in PNG_DOT_STYLES:
            raise ValueError(f"Invalid dot style: '{dot_style}'. Use from: {DOT_STYLES}")
        self.dot_style = dot_style

        if eye_style not in EYE_STYLES:
            raise ValueError(f"Invalid eye style: '{eye_style}'. Use from: {list(EYE_STYLES.keys())}"
            )
        self.eye_style = eye_style
  
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

    @property
    def eye_radius(self) -> float:
        return min(EYE_STYLES[self.eye_style], EYE_RADIUS_MAX)

    def _eye_radii(self):
        r_out = self.eye_radius * EYE_MODULES
        r_hole = max(r_out - 1, 0)
        r_pupil = self.eye_radius * 3
        return r_out, r_hole, r_pupil

    @staticmethod
    def _eye_origins(qr):
        n = qr.modules_count
        return [(0, 0), (n - EYE_MODULES, 0), (0, n - EYE_MODULES)]

    def build_pil_image(self, data: str):
        qr = self._build_qr(data)
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=PNG_DOT_STYLES[self.dot_style](),
            color_mask=SolidFillColorMask(
                back_color=ImageColor.getrgb(self.back_color),
                front_color=ImageColor.getrgb(self.fill_color),
            ),
        )
        self._draw_eyes_png(img.get_image(), qr)
        return img

    def _draw_eyes_png(self, pil_img, qr) -> None:
        if self.eye_radius <= 0:
            return
        box, ss = self.box_size, 4
        side = EYE_MODULES * box
        m = box * ss
        big = side * ss
        front = ImageColor.getrgb(self.fill_color)
        back = ImageColor.getrgb(self.back_color)
        r_out, r_hole, r_pupil = self._eye_radii()

        eye = Image.new("RGB", (big, big), back)
        d = ImageDraw.Draw(eye)
        d.rounded_rectangle((0, 0, big - 1, big - 1), radius=r_out * m, fill=front)
        d.rounded_rectangle((m, m, 6 * m - 1, 6 * m - 1), radius=r_hole * m, fill=back)
        d.rounded_rectangle((2 * m, 2 * m, 5 * m - 1, 5 * m - 1), radius=r_pupil * m, fill=front)
        eye = eye.resize((side, side), Image.LANCZOS).convert(pil_img.mode)

        for col, row in self._eye_origins(qr):
            pil_img.paste(eye, ((self.border + col) * box, (self.border + row) * box))

    def _generate_png(self, data: str, path: Path) -> None:
        self.build_pil_image(data).save(path)

    def _generate_svg(self, data: str, path: Path) -> None:
        if self.dot_style not in SVG_DOT_STYLES:
            raise ValueError(
                f"El estilo '{self.dot_style}' no está disponible en SVG. "
                f"Use: {list(SVG_DOT_STYLES.keys())}"
            )
        qr = self._build_qr(data)
        if self.eye_radius > 0:
            self._clear_eyes(qr)
        img = qr.make_image(
            image_factory=qrcode.image.svg.SvgPathImage,
            module_drawer=SVG_DOT_STYLES[self.dot_style](),
        )
        if self.eye_radius > 0:
            self._append_eyes_svg(img, qr)
        with open(path, "wb") as f:
            img.save(f)

    def _clear_eyes(self, qr) -> None:
        for col, row in self._eye_origins(qr):
            for r in range(row, row + EYE_MODULES):
                for c in range(col, col + EYE_MODULES):
                    qr.modules[r][c] = False

    @staticmethod
    def _rrect_path(x: float, y: float, w: float, r: float) -> str:
        def f(v):
            return f"{v:.4f}".rstrip("0").rstrip(".")
        r = min(r, w / 2)
        if r <= 0:
            return f"M{f(x)},{f(y)}h{f(w)}v{f(w)}h{f(-w)}z"
        return (
            f"M{f(x + r)},{f(y)}H{f(x + w - r)}A{f(r)},{f(r)} 0 0 1 {f(x + w)},{f(y + r)}"
            f"V{f(y + w - r)}A{f(r)},{f(r)} 0 0 1 {f(x + w - r)},{f(y + w)}"
            f"H{f(x + r)}A{f(r)},{f(r)} 0 0 1 {f(x)},{f(y + w - r)}"
            f"V{f(y + r)}A{f(r)},{f(r)} 0 0 1 {f(x + r)},{f(y)}Z"
        )

    def _append_eyes_svg(self, img, qr) -> None:
        u = self.box_size / 10
        r_out, r_hole, r_pupil = self._eye_radii()
        parts = []
        for col, row in self._eye_origins(qr):
            x, y = (self.border + col) * u, (self.border + row) * u
            parts.append(self._rrect_path(x, y, 7 * u, r_out * u))
            parts.append(self._rrect_path(x + u, y + u, 5 * u, r_hole * u))
            parts.append(self._rrect_path(x + 2 * u, y + 2 * u, 3 * u, r_pupil * u))
        attrs = dict(img.path.attrib)
        attrs.update({"id": "qr-eyes", "fill-rule": "evenodd", "d": "".join(parts)})
        xml = qrcode.image.svg.ET
        img._img.append(xml.Element(xml.QName("path"), attrs))