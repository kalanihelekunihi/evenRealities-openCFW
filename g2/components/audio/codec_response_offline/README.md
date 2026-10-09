# Offline GX8002 response and CRC reconstruction

Reconstructed ARM C for stock response reader0x57C1FC, reader wrapper0x57C442, unpacker0x57BD06, free helper0x57C640 and CRC32 provider0x4D34C4. It is neither production firmware nor byte-identical source. The log-disabled contract is explicit; allocator and scheduler providers remain external. `response.h` describes the recovered packed26-byte message and callable interfaces. Wire integers are little endian.

Evidence and 360 comparisons: [report](../../../analysis/audio-codec-response-crc-2026-10-09/REPORT.md). Caller storage must actually accommodate14 header bytes before advertised-capacity validation. Do not deploy this reconstruction as a hardened parser: malformed uint16 length wrapping and empty CRC-body quirks intentionally preserve stock behavior.
