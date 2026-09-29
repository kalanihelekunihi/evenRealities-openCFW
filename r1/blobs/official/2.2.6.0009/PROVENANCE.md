# Official R1 2.2.6.0009 images

These locally captured reconstruction-oracle images are not part of the
versioned firmware mirrors and remain ignored by Git. Their identities are
recorded here for local verification. See the repository `LICENSE` and `NOTICE`
for licensing terms and boundaries.

| File | Bytes | SHA-256 | Region |
| --- | ---: | --- | --- |
| `application.bin` | 646,408 | `0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a` | `0x27000..0xC4D07` |
| `bootloader.bin` | 24,576 | `566cd2a50cd173680d314643e498202b364e4f8f8b6fd79b12ca71035e34ab8b` | `0xF8000..0xFDFFF` |
| `uicr.bin` | 776 | `1a6dc7725aa1903ed240dd245ecd036a6c72b244e8b26179affdd0fdde74b150` | UICR |
| `approtect-runtime.bin` | 12 | `fafdd44c03daf5f7ecfa57113ebd319de6fb8f84fa0b7b0c5ac60d09f811fb71` | APPROTECT runtime words |

The S140 7.2.0 SoftDevice (`0x00000..0x26FFF`) comes from the nRF5 SDK
17.1.0 archive pinned in [`../../../../third-party/fetched/`](../../../../third-party/fetched).
Its hash is recorded there.

Every R1 tool checks these digests before use. The same identities are pinned in
[`../../../research/decompilation/rebuild/manifest.json`](../../../research/decompilation/rebuild/manifest.json).
The layout is in [`../../../docs/memory-map.md`](../../../docs/memory-map.md).
