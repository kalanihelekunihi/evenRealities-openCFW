# New finite lead: Cordio signaling-length guard

Strongest bounded target: canonical `l2cRxSignalingPkt`, stock `0x0053076E..0x005308E6`, 376 bytes, SHA-256 `c26ae1510d3d56ca5de518313cd89389c877a3f1047c4512ab0a547e05db9f7d`. Extent hash independently verifies against authenticated Apollo package `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`. Canonical name confidence is Strong, not independent source identity. Full provenance in `TARGET-AND-SOURCE-PROVENANCE.json`.

## Newly useful source evidence

Compared three SDK 5.2 Apache-licensed Cordio files with official public r20.05c `3656312d6b73e2a2c1c8b33ee0385bc199dd97e6`, the already selected Cordio reference. `SOURCE-CHECK.json` records URLs and exact file hashes; individual diffs preserve every textual change.

SDK `l2cRxSignalingPkt` adds `L2C_CHECK_DATA_LENGTH(len, L2C_SIG_HDR_LEN)` before `DmConnIdByHandle`. The supplied macro immediately returns for `len < min_len`; supplied `l2c_defs.h` defines signaling header length as 4. Public r20.05c has no such guard. This gives a source-backed boundary and ordering discriminator without choosing compiler flags or fitting bytes.

The two SDK L2CAP C/H files were acquired into `sdk-licensed-source/`, retaining their explicit Apache-2.0 per-file notices. No proprietary SDK library or binary was copied, executed or publicly registered. This is a licensed source variant from an authenticated SDK package; the exact changed variant was not located at a separately pinned public upstream revision. Exact public searches for its macro name found no results. SDK family and profile README ancestry do not establish the patch's origin or stock inclusion.

Official existing source reference:
https://github.com/packetcraft-inc/cordio/blob/3656312d6b73e2a2c1c8b33ee0385bc199dd97e6/ble-host/sources/stack/l2c/l2c_main.c

No new submodule is needed: the public comparator is already registered at `third-party/upstream/cordio`. Do not initialize or re-pin a duplicate solely for these files.

## Exact next test for the implementation owner

First inspect the complete authenticated 376-byte stock extent, including literals and all exits. Establish parameter registers and call/control bindings rather than assuming them from the canonical name. Determine whether a `len < 4` path returns before any connection lookup, role lookup, callback or trace side effect. Preserve complete bytes and explain any layout/relocation differences; a tiny compare instruction is insufficient.

Then use stubbed source-versus-stock calls with the same argument/control-state contract:

1. Lengths 0, 1, 2 and 3 with a handle that would resolve to a valid connection: SDK variant must perform zero connection/role lookups and zero dispatches.
2. Length 4 with a handle resolving to no connection: exactly one connection lookup, no role lookup or dispatch.
3. Length 4 with a valid master and registered master callback: connection lookup, role lookup, then exactly one callback with unchanged handle, length and packet pointer.
4. Same for valid slave and slave callback.
5. Length 4 with the selected role callback null: no dispatch; preserve the source's trace branch if enabled.
6. Length 65535 with a valid connection: verify unsigned 16-bit length interpretation and ordinary dispatch, not a signed-negative rejection.

This is nine fixture cases when the four short lengths are counted separately. Record call order, callback arguments and mutations, not just return values. No physical BLE delivery, controller state or device action is needed. Do not fabricate packet-length semantics from memory safety expectations: this function receives a trusted caller-supplied pointer; the target here is the explicit length guard and dispatch ordering.

Admission requires both complete stock control/data evidence and the independent fixture review. If stock lacks the guard, retain the older source behavior rather than adding the new patch to match SDK policy. If stock contains the guard, call it a guard-bearing variant until exact producing revision is proven. Stop if the canonical extent is wrong, the target is already owned, or a prior bounded semantic test is found; no new compiler acquisition is justified by this source-only discriminator.

## Deferred adjacent evidence

SDK `attcProcRsp` adds method bounds, minimum-PDU table checks and non-null processor checks; also changes on-deck indexing from `connId` to `connId-1`. Its stock anchor is `0x004B5448..0x004B557A`, 306 bytes, hash verified in the same receipt. SDK `smp_main.c` adds stale-AES queue draining. These are distinct future candidates, not implemented or tested here. Release notes say Cordio security updates, but do not assign these individual changes to a named CVE in this report. No global source-exhaustion claim follows.

No new stock experiment, production edit, index change, commit, push or device write occurred. The closed DSP/LZ4/Nema/STRDIS/FDNB branches were not repeated.
