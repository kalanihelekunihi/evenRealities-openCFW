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
- Reserve sleep extent metadata before programming the body, write timestamps and CRC afterward,
  and clear a distinct commit bit last. Reboot skips incomplete reservations and quarantines torn
  erase prefixes, so loss of power cannot expose a partial record or collide a later append with
  orphaned programmed bytes. Unlike stock, two transient append failures return an explicit error
  and do not silently erase the entire sleep database.

## Audit findings addressed by design

The `2.2.7.0005` security audit demonstrated a 244-to-36-byte channel-1 overwrite and controlled
callback on retail hardware. `r1` has no corresponding unbounded structured/eAT parser. If an
eAT compatibility parser is later added, it must be a separately fuzzed, length-bounded module with
no object pointers or callback addresses derived from input.

The stock system handlers also contain malformed declared-length paths and several ACK-before-
effect defects. The clean dispatcher rejects the malformed forms and uses honest result timing.
Those deviations are required fixes.

## Source-built owner authorization

The Zephyr target persists a separate, CRC-protected owner identity under
`openr1_auth/owner` in its settings partition. The first pairing that completes
successfully with bonding may create that record. Merely encrypting a link,
restoring a bond, or sending `pairAuth` cannot create or replace it. Subsequent
sessions become product-authorized only when the resolved BLE identity matches
the persisted owner. Owner-store state is implemented in the portable core:
reboot reconstruction authorizes only that exact address/type tuple, every
truncated length and all 96 possible single-bit mutations fail closed, and a
malformed settings reload first evicts any previously active RAM record so
stale authorization cannot survive a failed persistent replay.

Owner revocation is deliberately local-only: the typed platform API deletes the
authorization record, removes the corresponding SMP bond, clears the live
runtime authorization state, and disconnects the owner. It is not reachable
from the normal BLE dispatcher. This transparent trust-on-first-pairing policy
closes the source target's authorization implementation and host-side reboot,
identity-replay, corruption, and revocation-state tests. Physical NVS
interruption/rollback replay, ATT, pairing, and recovery behavior still require
owned-hardware tests.

NV identity and calibration recovery follows a narrow owner-phone rule. The
portable recovery API verifies the exact 116-byte body and CRC, fills only
invalid fields, refuses to co-commit unrelated dirty state, and commits
`nv_r1`, `power`, and `r_size` in one generation-bearing `kv.bin` snapshot.
Success requires provider readback of the complete snapshot and generation.
Exhaustive byte-cut tests prove reboot exposes only the complete old or complete
new state and that an interrupted transaction accepts a clean retry. The
SDK and Zephyr bindings copy an exact authorized command-2 body into bounded
storage queues and reboot only after a changed generation is durable. The
identity-bearing local-report sender remains unreachable; physical
persistence/replay, reboot, and ATT behavior must be established on owned
hardware.

## Boot and signing boundary

The portable sources do not disable, patch, bypass, or emulate the stock
verification path and contain no private signing key, APPROTECT bypass, or DFU
validation toggle. The source-built image instead owns page zero, validates an
ECDSA-P256 signed application on every boot, and retains a source-built BLE
recovery loader below the application partition. The owner key is decrypted
only into a mode-0600 temporary build input using a passphrase retrieved from
macOS Keychain; only its public key enters the image and bundle. Installing the
boot partition remains a separate, explicitly authorized lifecycle.

The source-built bundle's offline deployment contract requires exact backups of
all 1 MiB of internal flash and the complete architected nRF52840 UICR register
extent (`0x10001000..<0x10001308`, matching Nordic's 776-byte
`NRF_UICR_Type`). Installation must leave every architected UICR byte identical
and prove that with a readback. Recovery uses separate, canonical internal-flash and UICR HEX files and is accepted only when both
post-recovery readbacks equal their original backups. These tools do not unlock,
erase, or program a device; authorized debug access and owned-hardware lifecycle
validation remain external requirements.

## Restricted commands

The normal dispatcher refuses `setAlgoKey` and `powerControl`.
`advStart` is admitted only as an exact 12-byte SET from
the encrypted, bonded, independently owner-authorized phone role; its empty
success response enters the EUS queue before a bounded platform worker may
persist or apply either target. `otaStart` is the sole update control:
it accepts only an exact zero-length SET from an encrypted, bonded,
independently owner-authorized session, returns success, then sets the one-shot
recovery request and resets after the reply can drain. Testable/factory
commands and generic health-report enable controls are absent. `nvRecover`
accepts only the recovered command-2, 116-byte body with a matching nonzero
CRC-16/MODBUS from the same owner-authorized phone role. It emits no identity
report and no success response, matching the recovered valid-merge route; a
bounded storage worker atomically commits only fill-only changes and reboots
after a changed generation is durable. Any later specialized implementation
requires a narrow API, explicit authorization, state verification,
interruption recovery, and owned-hardware validation.

`removeRingNotify` is a destructive but explicitly composed owner operation.
Only an exact one-byte SET from the same encrypted, bonded, independently
owner-authorized phone role is admitted. Its empty success response is queued
before a bounded platform work item, matching the recovered order. The worker
then commits two transparent `dev_info` generations in the recovered sequence:
clear byte-24 flag `0x04`; then erase both six-byte peer slots at offsets 8 and
14 and restore `CAMH` at offset 20. Every byte-level interruption reopens to
the old, first-commit intermediate, or final generation, and retry is
idempotent. The stock malformed-length acceptance and ignored storage failures
are not reproduced.

Channel 1 is likewise deny-by-default. The sole composed legacy route is opcode
`0x89`: a bounded 36-byte parser admits it only for an encrypted, bonded,
independently authorized glasses-role link. That route can execute the typed
wear/touch/REG1 lifecycle, apply the recovered immediate-fast/exact-delayed-slow
BLE connection profiles, and return its seven-byte response. Every other
legacy, factory, BC, and eAT destination remains unreachable from the GATT
write callback.
