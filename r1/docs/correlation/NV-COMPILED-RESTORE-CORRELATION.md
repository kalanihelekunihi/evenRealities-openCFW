# R1 compiled-default NV restore correlation

## Decision

The closure contains two R1 product entries / 498 executable bytes: the restore body at
`0x0007C52C` / 494 bytes and the four-byte storage-event tail veneer at
`0x00042BBE..<0x00042BC2`. Both are classified as `r1_product_specific` with disposition
`clean_room_behavior_only_security_preserving`.

The function is byte-pinned by SHA-256
`433819b86093c162fa3a677ddec6ff52f19d7d378b714bf9e2c682457d382ae0`. Its sole direct entry is
the `B.W` tail branch at `0x00042BBE`, registered as internal storage event `0x2005`; the veneer
bytes `39f0b5bc` have SHA-256
`9135c4f873ba2ac12fb266a466936ed75d7755338ae4c825811f7e846b5e86b6` and are now an exact
manual provenance supplement. The restore caller-set digest is
`f45a3f14c09a7b07753484c80c045687e0b7152826a633439c361a360958eb21`. This is not a BLE command.

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

`r1_nv_compiled_default_restore_plan_build` accepts at most 59 caller-owned 14-byte typed records,
preserves first-match behavior, decodes the low nibble as ring size and high nibble as battery type,
sign-extends the compensation byte, and rejects invalid decoded values. It returns an immutable
write plan only; `r1_nv_compiled_default_restore_event_plan` is the transparent C analogue of the
four-byte event veneer. Neither function reads an address, embeds the recovered table, logs,
touches flash, or invokes a provider.

Nordic SoftDevice address retrieval and the pinned storage provider remain external dependencies;
the only eligible local code is the R1-specific gating, abstract lookup, validation, and commit
orchestration.

## Reproduce

```sh
python3 tools/evidence/summarize_r1_nv_compiled_restore.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```
