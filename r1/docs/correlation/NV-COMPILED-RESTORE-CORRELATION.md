# R1 compiled-default NV restore correlation

## Decision

The formerly unclassified function at `0x0007C52C` / 494 executable bytes is R1 product behavior,
not Nordic SDK or third-party code. It is classified as `r1_product_specific` with disposition
`clean_room_behavior_only_security_preserving` and named `r1_nv_compiled_default_restore`.

The function is byte-pinned by SHA-256
`433819b86093c162fa3a677ddec6ff52f19d7d378b714bf9e2c682457d382ae0`. Its sole direct entry is
the `B.W` tail branch at `0x00042BBE`, registered as internal storage event `0x2005`; the exact
caller-set digest is `f45a3f14c09a7b07753484c80c045687e0b7152826a633439c361a360958eb21`.
This is not a BLE command.

## Recovered behavior

The routine first checks the persisted battery-type field. A value other than `0x00` or `0xFF`
means configuration already exists and returns -1. Otherwise it obtains the six-byte device
address through SoftDevice SVC `0x6D`, formats it as 12 hexadecimal bytes, and scans 59 fixed
14-byte records. Each record contains a 12-byte match key followed by a packed ring-size/battery-
type byte and signed ADC-compensation byte.

On a match it reads the current ring-size and power records, replaces those three fields, writes
them through the existing KV primitives at `0x00073968`, and commits through `0x00073688`. It then
returns 0. MAC-read failure or absence from the table returns -2. The read-before-write calls at
`0x00073930`, 12-byte comparison at `0x0002781A`, and persistence edges are all pinned by the
summarizer.

The identity-bearing table occupies `0x0009A0F8..<0x0009A432` (826 bytes), with SHA-256
`4f0fe353d4a0b2d5ecdfc49a1a6d8c73f790d693c12ca3462ecbacb0bee5cf5c`. Its raw 59 identity rows are intentionally neither rendered
in the report nor copied into OpenR1 source.

## Clean-room and security boundary

OpenR1 may reproduce the control behavior only against an explicit caller-supplied restore policy
owned by the deployer. It must not redistribute the recovered identity table, log a live device
address, or enable persistent mutation until authorized provisioning, rollback, and physical-device
validation exist. The current live restore path remains disabled, consistent with the firmware
security audit's treatment of identity and calibration restore surfaces.

Nordic SoftDevice address retrieval and the pinned storage provider remain external dependencies;
the only eligible local code is the R1-specific gating, abstract lookup, validation, and commit
orchestration.

## Reproduce

```sh
python3 tools/summarize_r1_nv_compiled_restore.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
