# AmbiqSuite ANCC profile source recovery

Status: source lineage and complete linked-object boundary authenticated for G2
2.2.6.10. Analysis only; no signing, flashing, erase, or hardware operation was
performed.

## Result

The retained product path
`platform\ble\profiles\ancc\profile_ancc.c` is not wholly proprietary Even
code. Its foundation is AmbiqSuite's Apple Notification Center Service client:
`ambiq_ble/profiles/ancc/ancc_main.c` plus `ancc_api.h`.

The match is structurally decisive. Stock retains all of the implementation's
unusual coupled choices:

- a 64-element, 12-byte notification list, updated by UID and popped in reverse;
- a 19-byte notification-attribute command requesting all eight attributes;
- six-byte action and up-to-64-byte app-attribute command encoders;
- a 512-byte fragmented attribute buffer with three parser states;
- the one-byte attribute ID / little-endian two-byte length framing;
- completion after exactly eight attributes;
- five-handle, 128-bit ANCS service discovery through `AppDiscFindService`.

These features occur together in AmbiqSuite's 17-definition ANCC unit and map
directly onto G2's machine-code state layout, immediates, provider calls, and
control flow. Packetcraft's similarly named standard ANP client is excluded: it
uses the Bluetooth Alert Notification Service, 16-bit UUIDs, seven handles, and
only three public operations.

## Version and commit interval

The public SparkFun mirror of AmbiqSuite provides a reproducible release
history:

| AmbiqSuite release | Public import commit | `ancc_main.c` Git blob |
|---|---|---|
| 2.2.0 | `ca79fc6e140d25b0c596a5c87c3d311cd2710ad9` | `bfb4f06…` |
| 2.3.2 | `8f2a86b4b4a200291ea607fd94e585d6e4f15447` | `43b4e4c…` |
| 2.4.2 | `c4b62222921b1b87ddd21108cdaeaa4c4cf9f76d` | `075d853…` |
| 2.5.1 | `de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f` | `4023359bf02612b07ed95f51561e7b8e7936810c` |

The complete files differ only in copyright/release-header text. Everything
from source line 49 onward is byte-identical, SHA-256
`ffe2356399545ad7d0f617f14a2f2621df788e978f8da5d069e97340002701f4`.
Public AmbiqSuite 4.3.0 and 4.5.0 package copies independently retain that same
implementation body, but their community mirrors are corroboration rather than
historical G2 provenance.

OpenCFW selects AmbiqSuite 2.5.1 commit
`de5c6ba3044f4ef0f0c907c3f83fbbaa5795262f`. This is the newest release in the
authenticated public Git interval, and its official archive is already pinned
in this repository at SHA-256
`87b03680c0ac5a5291938e7c522f86146a954d935588f1deb046f35012fe4133`.
The admitted source blobs are:

| File | Bytes | Git blob | SHA-256 |
|---|---:|---|---|
| `ancc_main.c` | 25,099 | `4023359bf02612b07ed95f51561e7b8e7936810c` | `1435b838f7a7b18cec6f0b24f49266d4254c2d10f3ed6dd08eb029193069002d` |
| `ancc_api.h` | 11,988 | `5594c66a09026d49592ae1a0983c75ffc0c1ec53` | `c1af7746ddb649c2906b4ee69d06bf2d234baabad8197d3d7dba3754826cfce6` |

The exact private G2 generating commit remains `null`. No binary discriminator
can choose among source-identical releases, and G2 clearly carries local edits.

## Stock object boundary

The authenticated physical object is `[0x004BEA04,0x004BF990)`: 3,980 bytes,
SHA-256
`5a89c723bca33d424ca99ebfdfd2ac69b567f7a09f23b0be5c98549e70758d67`.
It contains 21 function bodies / 3,712 bytes with concatenated SHA-256
`fc95fcf77551c5c0153b44108bfc34d7d29e740f10d7e4a2a9c8390683f8ff06`
and 268 bytes of pools/alignment. The complete ingress audit authenticates:

- 26 direct `BL` entry sites;
- 155 direct calls made by the 21 bodies;
- two stored Thumb callbacks (`0x004BF8C0 -> 0x004BED0F` and
  `0x004BF8DC -> 0x004BEA7B`);
- zero strict-interior direct-branch targets.

Twelve stock functions are directly Ambiq-derived: connection open/close,
`anccNoConnActive`, list push/pop, all three command encoders,
`AnccNtfValueUpdate`, the fragmented attribute handler, initialization/callback
binding, and service discovery. Nine functions are G2 additions or extracted
adapters: message-based scheduling, sync/completion/removal callbacks, policy
gating, notification projection, centralized parser reset, event dispatch, and
an active-record getter.

## G2 deltas and shortcut value

G2 replaces Ambiq's action/discovery timers with its WSF message service, adds
EasyLogger expansions, dual-glasses synchronization, application whitelist
policy, and product notification callbacks. These are first-party deltas, not
evidence for a different ANCC library.

The admitted `ancc_api.h` shortcuts several otherwise opaque recovery tasks. It
fixes the exact UUID byte order; five handle indexes; 64-slot list and 512-byte
buffer sizes; command/category/attribute enum values; callback signatures; and
the base layouts of `ancc_notif_t`, `active_notif_t`, and `anccCb_t`. OpenCFW
only needs to reconstruct the documented G2 extensions around those known
interfaces rather than rediscover the complete ANCS protocol and parser.

## Source admission and reproduction

The BSD-3-Clause-style Ambiq notices remain embedded in both admitted files at
`third_party/ambiqsuite-ancc-profile`. They are provenance/implementation
oracles and are not currently routed into the production overlay.

Run:

```sh
make ambiqsuite-ancc-profile-closure
```

The target authenticates both upstream blobs, every stock body and pool, the
path/name/UUID constants, provider calls, direct ingress, stored callbacks,
ownership split, and the production-exclusion boundary.
