# openR1 security boundary

## Trust model

`r1` treats BLE bytes, saved flash records, phone-provided profiles, clocks, and every sensor
sample as untrusted input. A connection role is routing metadata, not proof of identity. An
authorized session must be encrypted, bonded, and approved by a product-level policy independent
of `pairAuth`.

## Required invariants

- Carry `(pointer, length)` together across every GATT, queue, dispatcher, storage, and sensor
  boundary. Never copy a characteristic value into a fixed object without checking the destination.
- Reject fragments longer than 244 bytes, logical packets above 4,063 bytes, sequence values above
  16, inconsistent repeated checksums, discontinuities, and incomplete trains.
- Verify both outer and direction-correct inner checksums before dispatch.
- Enforce exact or documented minimum payload length before every field read.
- Validate and persist a mutation before returning success; provide readback where an asynchronous
  hardware effect can fail.
- Keep identifiers and health data out of logs. Bind any retained record to a device identity with
  consent, integrity metadata, bounds, and deletion/revocation support.
- Make flash erase/write, factory/test, restore, provisioning, power-off, raw bus, and update entry
  unreachable from generic BLE dispatch.
- Reset queues, multipart state, credits, permissions, and pending callbacks on disconnect.
- Commit sleep payload bytes before their header so loss of power cannot expose a partially written
  record. Unlike stock, two transient append failures return an explicit error and do not silently
  erase the entire sleep database.

## Audit findings addressed by design

The `2.2.7.0005` security audit demonstrated a 244-to-36-byte channel-1 overwrite and controlled
callback on retail hardware. `r1` has no corresponding unbounded structured/eAT parser. If an
eAT compatibility parser is later added, it must be a separately fuzzed, length-bounded module with
no object pointers or callback addresses derived from input.

The stock system handlers also contain malformed declared-length paths and several ACK-before-
effect defects. The clean dispatcher rejects the malformed forms and uses honest result timing.
Those deviations are required fixes.

## Boot and signing boundary

The portable sources do not disable, patch, bypass, or emulate the stock verification path. They
also do not contain signing keys, UICR/MBR redirect logic, APPROTECT manipulation, MBR copy commands,
or DFU validation toggles. A future deployment build must define its own reviewed secure-boot,
rollback, recovery, key custody, and debug-lock policy. Producing an unsigned development ELF is a
build operation; installing it on hardware is a separate, explicitly authorized lifecycle.

## Withheld commands

The normal dispatcher refuses `otaStart`, `advStart`, `setAlgoKey`, `nvRecover`, `powerControl`, and
`removeRingNotify`. Testable/factory commands and generic health-report enable controls are absent.
Any later specialized implementation requires a narrow API, explicit authorization, state
verification, interruption recovery, and owned-hardware validation.
