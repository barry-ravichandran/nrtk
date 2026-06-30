"""Utilities for parsing the MPEG transport-stream structures used by video perturbers."""

from __future__ import annotations

from collections.abc import Generator

# These values follow the MPEG-TS packet header and Program Association Table
# layouts defined by ISO/IEC 13818-1, except the SDT PID assigned by DVB SI.
# MPEG-TS packets have a fixed 188-byte size and 0x47 sync byte; the remaining
# masks, offsets, and sizes select standardized header and PAT fields.
# See ITU-T H.222.0 sections 2.4.3.2 and 2.4.4.4:
# https://www.itu.int/rec/T-REC-H.222.0-202308-S/en
_MPEGTS_PACKET_SIZE = 188  # fixed byte length of one mpeg ts packet
_MPEGTS_SYNC_BYTE = 0x47  # value marking the start of every mpeg ts packet
_MPEGTS_PID_MASK = 0x1F  # selects the upper five bits of the 13 bit packet identifier
_MPEGTS_PAYLOAD_UNIT_START = 0x40  # byte one flag marking the start of a payload unit
_MPEGTS_ADAPTATION_FIELD_CONTROL_MASK = 0x03  # selects the two bit adaptation field control value
_MPEGTS_ADAPTATION_FIELD_CONTROL_SHIFT = 4  # moves adaptation field control bits to the low positions
_MPEGTS_PAYLOAD_ONLY = 1  # adaptation field control value for packets containing only payload
_MPEGTS_ADAPTATION_AND_PAYLOAD = 3  # value for packets containing an adaptation field and payload
_MPEGTS_PAT_PID = 0  # reserved packet identifier for the program association table
_MPEGTS_SDT_PID = 17  # dvb si packet identifier assigned to the service description table
_MPEGTS_PAT_TABLE_ID = 0x00  # table identifier assigned to program association sections
_MPEGTS_SECTION_LENGTH_MASK = 0x0F  # selects the upper four bits of the 12 bit section length
_MPEGTS_PAT_MIN_SECTION_BYTES = 12  # smallest valid pat section including header and crc
_MPEGTS_PAT_PROGRAM_LOOP_START = 8  # byte offset where pat program entries begin
_MPEGTS_PAT_CRC_BYTES = 4  # byte length of the crc field ending a pat section
_MPEGTS_PAT_PROGRAM_ENTRY_BYTES = 4  # byte length of each pat program to pmt mapping


def _mpegts_table_pids(*, stream: bytes) -> set[int]:
    """Return MPEG-TS table PIDs, including PMT PIDs discovered from PAT packets."""
    table_pids = {_MPEGTS_PAT_PID, _MPEGTS_SDT_PID}
    for packet in _complete_mpegts_packets(stream=stream):
        table_pids.update(_pmt_pids_from_pat_packet(packet=packet))
    return table_pids


def _complete_mpegts_packets(*, stream: bytes) -> Generator[bytes, None, None]:
    """Yield complete MPEG-TS packets with valid synchronization bytes."""
    for packet_start in range(0, len(stream) - _MPEGTS_PACKET_SIZE + 1, _MPEGTS_PACKET_SIZE):
        packet = stream[packet_start : packet_start + _MPEGTS_PACKET_SIZE]
        if len(packet) == _MPEGTS_PACKET_SIZE and packet[0] == _MPEGTS_SYNC_BYTE:
            yield packet


def _pmt_pids_from_pat_packet(*, packet: bytes) -> set[int]:
    """Extract Program Map Table PIDs from one Program Association Table packet."""
    section = _pat_section_from_packet(packet=packet)
    if section == b"":
        return set()

    section_length = ((section[1] & _MPEGTS_SECTION_LENGTH_MASK) << 8) | section[2]
    section_end = min(3 + section_length, len(section))
    program_info_end = section_end - _MPEGTS_PAT_CRC_BYTES
    pmt_pids = set()
    for entry_start in range(
        _MPEGTS_PAT_PROGRAM_LOOP_START,
        program_info_end,
        _MPEGTS_PAT_PROGRAM_ENTRY_BYTES,
    ):
        pmt_pid = _pmt_pid_from_program_entry(
            entry=section[entry_start : entry_start + _MPEGTS_PAT_PROGRAM_ENTRY_BYTES],
        )
        if pmt_pid is not None:
            pmt_pids.add(pmt_pid)
    return pmt_pids


def _pat_section_from_packet(*, packet: bytes) -> bytes:
    """Return a PAT section from a valid PAT packet, or an empty byte string."""
    if _mpegts_pid(packet=packet) != _MPEGTS_PAT_PID:
        return b""
    if not _mpegts_payload_unit_start(packet):
        return b""

    payload = _mpegts_payload(packet=packet)
    if len(payload) < _MPEGTS_PAT_MIN_SECTION_BYTES:
        return b""

    pointer = payload[0]
    section = payload[1 + pointer :]
    if len(section) < _MPEGTS_PAT_MIN_SECTION_BYTES or section[0] != _MPEGTS_PAT_TABLE_ID:
        return b""
    return section


def _mpegts_payload(*, packet: bytes) -> bytes:
    """Return an MPEG-TS packet payload after any adaptation field."""
    adaptation_field_control = (
        packet[3] >> _MPEGTS_ADAPTATION_FIELD_CONTROL_SHIFT
    ) & _MPEGTS_ADAPTATION_FIELD_CONTROL_MASK
    if adaptation_field_control == _MPEGTS_PAYLOAD_ONLY:
        return packet[4:]
    if adaptation_field_control == _MPEGTS_ADAPTATION_AND_PAYLOAD:
        return packet[5 + packet[4] :]
    return b""


def _pmt_pid_from_program_entry(*, entry: bytes) -> int | None:
    """Return the PMT PID from a PAT program entry, excluding network entries."""
    if len(entry) != _MPEGTS_PAT_PROGRAM_ENTRY_BYTES:
        return None

    program_number = (entry[0] << 8) | entry[1]
    if program_number == 0:
        return None

    return ((entry[2] & _MPEGTS_PID_MASK) << 8) | entry[3]


def _mpegts_pid(*, packet: bytes) -> int:
    """Return the 13-bit PID from an MPEG-TS packet header."""
    return ((packet[1] & _MPEGTS_PID_MASK) << 8) | packet[2]


def _mpegts_payload_unit_start(packet: bytes) -> bool:
    """Return whether a complete MPEG-TS packet starts a payload unit."""
    return (
        len(packet) == _MPEGTS_PACKET_SIZE
        and packet[0] == _MPEGTS_SYNC_BYTE
        and bool(packet[1] & _MPEGTS_PAYLOAD_UNIT_START)
    )
