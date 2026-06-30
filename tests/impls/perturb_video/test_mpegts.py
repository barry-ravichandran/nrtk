"""Tests for reusable MPEG transport-stream parsing utilities."""

import pytest

from nrtk.impls.perturb_video._mpegts import (
    _MPEGTS_PACKET_SIZE,
    _MPEGTS_PAT_PID,
    _MPEGTS_PAYLOAD_UNIT_START,
    _MPEGTS_PID_MASK,
    _MPEGTS_SDT_PID,
    _MPEGTS_SYNC_BYTE,
    _mpegts_table_pids,
    _pmt_pid_from_program_entry,
    _pmt_pids_from_pat_packet,
)

pytestmark = pytest.mark.core


def _make_pat_packet(*, pmt_pid: int = 0x0100) -> bytes:
    packet = bytearray([_MPEGTS_SYNC_BYTE, _MPEGTS_PAYLOAD_UNIT_START, _MPEGTS_PAT_PID, 0x10])
    packet.append(0)
    packet.extend(
        [
            0x00,
            0xB0,
            0x0D,
            0x00,
            0x01,
            0xC1,
            0x00,
            0x00,
            0x00,
            0x01,
            0xE0 | ((pmt_pid >> 8) & _MPEGTS_PID_MASK),
            pmt_pid & 0xFF,
            0x00,
            0x00,
            0x00,
            0x00,
        ],
    )
    packet.extend([0xFF] * (_MPEGTS_PACKET_SIZE - len(packet)))
    return bytes(packet)


def test_mpegts_table_pids_extracts_pmt_from_pat() -> None:
    """Verify table PID discovery includes PMT PIDs from valid PAT packets."""
    pmt_pid = 0x0101

    assert _mpegts_table_pids(stream=_make_pat_packet(pmt_pid=pmt_pid)) == {
        _MPEGTS_PAT_PID,
        _MPEGTS_SDT_PID,
        pmt_pid,
    }


@pytest.mark.parametrize(
    "packet",
    [
        bytes([_MPEGTS_SYNC_BYTE, 0x00, 0x20, 0x10]) + bytes(_MPEGTS_PACKET_SIZE - 4),
        bytes([_MPEGTS_SYNC_BYTE, 0x00, _MPEGTS_PAT_PID, 0x10]) + bytes(_MPEGTS_PACKET_SIZE - 4),
        bytes([_MPEGTS_SYNC_BYTE, _MPEGTS_PAYLOAD_UNIT_START, _MPEGTS_PAT_PID, 0x10, 0x00, 0x01])
        + bytes(_MPEGTS_PACKET_SIZE - 6),
    ],
)
def test_pmt_pids_from_pat_packet_rejects_invalid_packets(packet: bytes) -> None:
    """Verify malformed and non-PAT packets do not report PMT PIDs."""
    assert _pmt_pids_from_pat_packet(packet=packet) == set()


def test_pmt_pid_from_program_entry_ignores_network_pid() -> None:
    """Verify program-zero PAT entries are ignored as network metadata."""
    assert _pmt_pid_from_program_entry(entry=bytes([0, 0, 0xE1, 0])) is None
