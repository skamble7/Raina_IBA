import zlib
import base64

# PlantUML base64 alphabet
PLANTUML_ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_"

def encode_plantuml(plantuml_text: str) -> str:
    """Encode PlantUML text to PlantUML server-compatible base64."""
    data = plantuml_text.encode("utf-8")
    compressed = zlib.compress(data)[2:-4]  # strip zlib header and checksum
    return _encode_base64(compressed)

def _encode_base64(data: bytes) -> str:
    """Custom base64 encoder using PlantUML's alphabet."""
    res = ""
    buffer = 0
    buffer_len = 0

    for byte in data:
        buffer = (buffer << 8) | byte
        buffer_len += 8
        while buffer_len >= 6:
            buffer_len -= 6
            res += PLANTUML_ALPHABET[(buffer >> buffer_len) & 0x3F]

    if buffer_len > 0:
        res += PLANTUML_ALPHABET[(buffer << (6 - buffer_len)) & 0x3F]

    return res
