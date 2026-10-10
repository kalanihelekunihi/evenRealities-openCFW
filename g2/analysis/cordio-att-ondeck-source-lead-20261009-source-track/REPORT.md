# New finite discriminator: ATT queued-request indexing

Strongest new target is canonical `attcProcRsp`, authenticated stock 0x004B5448..0x004B557A, 306 bytes, SHA-256 `f8256375f5cad966c0c74be78977523bce416b3fdeb41f06c9b98537cd9edd18`. This distinct ATT dispatcher was only listed as a deferred lead in the signaling report; a scoped search found no prior implementation/review packet for it. Do not repeat the closed signaling fixtures.

## Source provenance and discrimination

Official existing Cordio pin: `3656312d6b73e2a2c1c8b33ee0385bc199dd97e6` (r20.05c), https://github.com/packetcraft-inc/cordio/blob/3656312d6b73e2a2c1c8b33ee0385bc199dd97e6/ble-host/sources/stack/att/attc_proc.c

Three public source files and their authenticated SDK 5.2 counterparts were cached locally with complete Apache-2.0 per-file notices. `PROVENANCE.json` records each URL, pin, ZIP member and SHA-256; diffs preserve the exact changes. Public comparator is already the registered Cordio family, so no duplicate checkout/submodule or re-pin is justified. The supplied SDK source is individually Apache-licensed; no proprietary SDK library or executable was acquired or redistributed. Exact modified-source public origin remains unlocated; SDK acquisition hash is `d9751350ef593b306838792a64a5620e4912c84ddf32dc9ff6aacd5cca049cad`.

Old public response handling selects `onDeck[pCcb->connId]`; SDK selects `onDeck[pCcb->connId-1]`. The same change occurs in source API enqueue and cleanup paths in `attc_main.c`. Thus compare it as a coherent queued-request representation difference, not an isolated assumed off-by-one vulnerability. Both source control-block headers are identical and declare `onDeck[DM_CONN_MAX]`; initialization assigns connection IDs as `i + 1`. That is a concrete multi-feature version discriminator independent of nominal SDK labels.

SDK response code also adds method bounds, a minimum-PDU-length table and non-null processor checks. Those are distinct source changes. A match to the selected queue path cannot admit those guards or the entire newer module. Use a valid ordinary response to isolate indexing.

## Exact bounded next test

First decode the complete stock 306-byte body and actual queue/control-field addresses and strides. Bind `pCcb->connId`, slot, main control pointer, flow flag, outstanding request, and setup/free call targets from instructions and authenticated state evidence. Do not impose native-host struct offsets or infer array base from the source name. Validate that the queue-selection branch is present before executing fixtures.

Use a valid connection ID 1 and at least two fully allocated readable queue entries, with distinct event sentinels. Supply a well-formed ordinary write-response fixture (method WRITE, matching outstanding request, valid minimum PDU length) so method/length guards do not distinguish the variants. Confirm header constants from source before encoding. Arrange ordinary bearer slot, flow enabled, no retained outgoing packet after the recorded free, no application callback, and a response processor returning a documented completed-request state. Processing/setup/free are explicit recording mocks, not BLE transmit operations.

Three source-versus-stock fixtures:

1. Queue entry 0 and entry 1 both ready with different request sentinels: record the exact entry pointer/event passed to setup and which entry's event is subsequently cleared. Old public predicts entry 1; SDK predicts entry 0.
2. Entry 0 ready, entry 1 empty: SDK selects/clears entry 0; old public performs no setup.
3. Entry 0 empty, entry 1 ready: SDK performs no setup; old public selects/clears entry 1.

Record provider call order, selected pointer, queue event mutations, other state/buffer guards and Arm ABI preservation. Every entry and packet must be fully readable regardless of logical readiness. Do not use highest connection ID to provoke out-of-range access; that is unnecessary to discriminate indexing. Direct target tests do not establish producer/caller composition, real connection allocation, scheduler, physical transport, or vulnerability.

Admission needs independent complete-body and fixture review. If a variant matches, call it index-by-connId or index-by-connId-minus-one behavior until the queued-request producer and exact private revision are independently bound. If queue offsets cannot be authenticated, stop at source evidence and report those offsets/configuration as missing inputs; do not fit source layouts to results.

## Limits and preservation

No stock execution occurred in this discovery packet. Whole-source/header equality is distinct from compiled equality and stock inclusion. Current missing inputs are stock queue/control-field bindings, actual caller state/producer indexing and producing configuration; a new compiler or broad source download is not necessary for this finite semantic test. Root index, existing pins, sealed inputs/checkpoints, production and devices were untouched. No commit/push. No global source-exhaustion claim follows.
