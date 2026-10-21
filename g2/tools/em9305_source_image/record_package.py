#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Deterministic parser/builder for the G2 EM9305 record-table package."""

from __future__ import annotations

from dataclasses import dataclass
import struct
from typing import Iterable


MAGIC = bytes.fromhex("00020404")
HEADER = struct.Struct("<4sIII")
DESCRIPTOR = struct.Struct("<III")
UINT16_MAX = (1 << 16) - 1
UINT32_MAX = (1 << 32) - 1


class RecordPackageError(ValueError):
    pass


@dataclass(frozen=True)
class Record:
    address: int
    payload: bytes


@dataclass(frozen=True)
class ParsedPackage:
    records: tuple[Record, ...]
    erase_sectors: tuple[int, ...]
    metadata_size: int
    payload_size: int


def _align4(value: int) -> int:
    return (value + 3) & ~3


def _validate_records(records: tuple[Record, ...]) -> None:
    if not records:
        raise RecordPackageError("at least one EM9305 record is required")
    if len(records) > UINT32_MAX:
        raise RecordPackageError("record count exceeds the package field")
    intervals = []
    for index, record in enumerate(records):
        if not isinstance(record.payload, bytes) or not record.payload:
            raise RecordPackageError(f"record {index} payload is empty or mutable")
        if (type(record.address) is not int or
                not 0 <= record.address <= UINT32_MAX):
            raise RecordPackageError(f"record {index} address is out of range")
        end = record.address + len(record.payload)
        if end > UINT32_MAX + 1:
            raise RecordPackageError(f"record {index} target interval wraps")
        intervals.append((record.address, end, index))
    intervals.sort()
    for previous, current in zip(intervals, intervals[1:]):
        if previous[1] > current[0]:
            raise RecordPackageError(
                f"target records {previous[2]} and {current[2]} overlap")


def build_package(
    records: Iterable[Record],
    erase_sectors: Iterable[int],
) -> bytes:
    record_tuple = tuple(records)
    sector_tuple = tuple(erase_sectors)
    _validate_records(record_tuple)
    if len(sector_tuple) > UINT32_MAX:
        raise RecordPackageError("erase-sector count exceeds the package field")
    for index, sector in enumerate(sector_tuple):
        if type(sector) is not int or not 0 <= sector <= UINT16_MAX:
            raise RecordPackageError(f"erase sector {index} is out of range")

    payload_size = sum(len(record.payload) for record in record_tuple)
    if payload_size > UINT32_MAX:
        raise RecordPackageError("record payload exceeds the package field")
    metadata_size = _align4(
        HEADER.size + len(record_tuple) * DESCRIPTOR.size +
        len(sector_tuple) * 2
    )
    if metadata_size > UINT32_MAX:
        raise RecordPackageError("package metadata exceeds the offset field")
    cursor = metadata_size
    descriptors = bytearray()
    for index, record in enumerate(record_tuple):
        if cursor > UINT32_MAX:
            raise RecordPackageError(f"record {index} file offset is out of range")
        descriptors.extend(DESCRIPTOR.pack(cursor, len(record.payload), record.address))
        cursor += len(record.payload)

    metadata = bytearray(HEADER.pack(
        MAGIC, payload_size, len(record_tuple), len(sector_tuple),
    ))
    metadata.extend(descriptors)
    if sector_tuple:
        metadata.extend(struct.pack(f"<{len(sector_tuple)}H", *sector_tuple))
    metadata.extend(b"\0" * (metadata_size - len(metadata)))
    return bytes(metadata) + b"".join(record.payload for record in record_tuple)


def parse_package(package: bytes) -> ParsedPackage:
    if not isinstance(package, bytes) or len(package) < HEADER.size:
        raise RecordPackageError("EM9305 package is truncated or mutable")
    magic, payload_size, record_count, erase_count = HEADER.unpack_from(package)
    if magic != MAGIC:
        raise RecordPackageError("EM9305 package magic changed")
    metadata_size = _align4(
        HEADER.size + record_count * DESCRIPTOR.size + erase_count * 2
    )
    if metadata_size > UINT32_MAX:
        raise RecordPackageError("EM9305 metadata exceeds the offset field")
    if metadata_size > len(package):
        raise RecordPackageError("EM9305 metadata extends past the package")
    if payload_size != len(package) - metadata_size:
        raise RecordPackageError("EM9305 payload-length field disagrees with the file")

    records = []
    cursor = metadata_size
    descriptor_offset = HEADER.size
    for index in range(record_count):
        offset, size, address = DESCRIPTOR.unpack_from(package, descriptor_offset)
        descriptor_offset += DESCRIPTOR.size
        if size == 0:
            raise RecordPackageError(f"record {index} is empty")
        if offset != cursor or offset + size > len(package):
            raise RecordPackageError(f"record {index} is not a canonical contiguous slice")
        records.append(Record(address, package[offset:offset + size]))
        cursor += size
    if cursor != len(package):
        raise RecordPackageError("record descriptors do not consume the payload")

    sector_offset = HEADER.size + record_count * DESCRIPTOR.size
    sectors = struct.unpack_from(f"<{erase_count}H", package, sector_offset)
    padding_start = sector_offset + erase_count * 2
    if any(package[padding_start:metadata_size]):
        raise RecordPackageError("EM9305 metadata alignment padding is nonzero")
    _validate_records(tuple(records))
    return ParsedPackage(tuple(records), tuple(sectors), metadata_size, payload_size)
