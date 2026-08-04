import pytest

from decoder_model import decode_block_payload
from fileformat import J650FormatError


def test_decode_block_payload_rejects_truncated_payload():
    with pytest.raises(J650FormatError):
        decode_block_payload(bytes([0x01, 0x05, 0x02]))
