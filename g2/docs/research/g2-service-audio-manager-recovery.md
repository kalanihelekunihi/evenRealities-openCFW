# G2 audio-manager recovery

## Result

The retained `platform\audio\service_audio_manager.c` object is closed as
seven functions at `[0x0054F364, 0x0054FA24)`. It occupies 1,728 physical
bytes with SHA-256
`c1044f123eecf9afce8e604681f57055c72ac644379d00cf0d5f239ed9ea6a8f`:
1,554 executable bytes plus 174 bytes of alignment and shared literals.

The authenticated Ghidra corpus discovered five functions, four of which carry
the retained-path anchor. The complete 410-byte `AUDM_HandlePeerSyncMsg` and
132-byte `AUDM_Init` bodies were missed. Their exact diagnostic names, sixteen
object-local path references, contiguous prologue/epilogue boundaries, shared
literal pool, complete decoding, internal call graph, and whole-image ingress
restore both without guessing. The common-data callback is independently rooted
by its stored odd Thumb pointer at `0x006A4604`.

No CMSIS-FreeRTOS, codec-vendor DSP, or other third-party implementation is
embedded. Eighty calls reach the admitted EasyLogger/private compact seams and
one reaches bounded IAR `memset`. The remaining twenty external calls reach
first-party role/system policy, audio hardware/power services, and common-data
peer transport. The object supplies no new dependency version discriminator or
recoverable private generating commit.

## Reproduction

Run:

```sh
make service-audio-manager-closure
```

The analyzer authenticates the official image, all seven bodies, physical
boundaries and shared pool, every instruction and call, whole-image BL ingress,
the stored callback entry, path references and exact diagnostic names,
logging/compiler provenance, and production-routing status.

| Evidence | Result |
|---|---:|
| Linked / Ghidra-discovered / restored functions | 7 / 5 / 2 |
| Path-anchored functions | 4 |
| Raw path references / referencing functions | 16 / 6 |
| Body / alignment-pool / physical bytes | 1,554 / 174 / 1,728 |
| Reachable instructions | 595 |
| Direct calls | 112 |
| Internal / external direct calls | 11 / 101 |
| Indirect calls | 0 |
| Whole-image direct `BL` entries | 38 |
| Stored exact entries / strict-interior entries | 1 / 0 |

The executable-body SHA-256 is
`765778845b689e2b9efe344a4124ad234937dc9153fc1c42bab082fd19a84a34`.
The instruction topology digest is
`7d834996a706d2a5363e6e84b6caba23af75be44ab7b610bcae8787576a2ef02`,
and the direct-call digest is
`1b63b834d7f5d096ea3bc99480e000cc06fa57aedf36e59f46fb3b3724ee04af`.

## Recovered ownership and peer protocol

An eight-byte table tracks application ownership; valid public IDs are one
through seven. Acquire and release only manipulate hardware for product role
two. The first successful acquire resets shared audio state and enables PDM and
codec paths. The final release disables both paths. Duplicate operations and
out-of-range IDs are diagnosed but do not change ownership.

Peer synchronization is a one-byte protocol carried on common-data frame
`0x010C`. Four message IDs drive a role-sensitive close, low-power,
reopen, and initialization handshake. The stored common-data callback rejects
null or empty payloads and dispatches only the first byte. Initialization clears
all eight ownership slots and performs a role-specific audio/system setup before
sending the initial peer status.

The dependency split is exact:

- EasyLogger and the already bounded G2 compact hook: 80 calls, selected
  EasyLogger commit `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`;
- IAR DLIB: one bounded eight-byte `memset`, with the established EWARM 9.20+
  floor and 9.60.2 leading candidate but no binary-observable exact archive;
- G2 product-role/system policy: eight calls;
- G2 audio hardware and power policy: eleven calls; and
- G2 common-data transport: one call.

## OpenCFW implication

This is first-party ownership and peer orchestration, not another RTOS or DSP
source tree. A clean-room implementation should preserve the role-two ownership
gate, first-acquire/last-release hardware transitions, duplicate-operation
idempotence, and the four-message `0x010C` handshake. Host tests can cover table
state and peer-message sequencing; codec/PDM power behavior and dual-device
handshake timing remain hardware-validation work.

No device, signing, flashing, erase, or runtime operation was performed.
