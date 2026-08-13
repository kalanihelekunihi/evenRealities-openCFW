# Cordio ATT core source audit

Status date: 2026-08-09  
Target: G2 `s200_v2.2.6.10` Apollo main

## Outcome

The stock `att_main.c` object is bounded at `[0x004B4DE0,0x004B5230)`,
1,104 bytes, SHA-256
`0540437900968a8a29771142d36c14d9f4a5eafb21d606e779c58611367970ec`.
Twenty-one of the 23 source definitions link and contribute 1,030 code bytes;
their source-order concatenation hashes to
`c1530e0a1d6ed2ab1e0e0ac5bd9b63592cb0a97e2fc83b5ce78e4081ca4b6e0c`.
The remaining 74 bytes are five alignment/category/literal spans. The next TU
begins at `0x004B5230`.

| function | stock span | bytes | SHA-256 |
|---|---:|---:|---|
| `attL2cDataCback` | `[0x4B4DE0,0x4B4E08)` | 40 | `3c50f4bd...7bc3e` |
| `attL2cCtrlCback` | `[0x4B4E08,0x4B4E50)` | 72 | `6b428384...b2973` |
| `attDmConnCback` | `[0x4B4E50,0x4B4EE6)` | 150 | `2da7bc7e...c46b6` |
| four empty callbacks | `[0x4B4EE6,0x4B4EEE)` | 8 | each `c7dfbb7d...28df8` |
| `attCcbByConnId` | `[0x4B4EEE,0x4B500E)` | 288 | `b30b7670...aa187` |
| `attUuidCmp16to128` | `[0x4B5014,0x4B5036)` | 34 | `10bde0c9...22897` |
| `attSetMtu` | `[0x4B503C,0x4B5074)` | 56 | `22a9af06...8194c` |
| `attExecCallback` | `[0x4B5074,0x4B50AE)` | 58 | `d5e7273c...a1234` |
| `attMsgAlloc` | `[0x4B50AE,0x4B50BA)` | 12 | `ec586584...13bcf` |
| `attL2cDataReq` | `[0x4B50BA,0x4B50EA)` | 48 | `e23b6dde...e19b` |
| `attMsgParam` | `[0x4B50F0,0x4B50FE)` | 14 | `885ee48a...3cba` |
| `attDecodeMsgParam` | `[0x4B50FE,0x4B511E)` | 32 | `f02b7da4...fe825` |
| `AttHandlerInit` | `[0x4B511E,0x4B5146)` | 40 | `3fd39a6e...8f342` |
| `AttHandler` | `[0x4B5146,0x4B519E)` | 88 | `525512ef...e3b35` |
| `AttRegister` | `[0x4B519E,0x4B51C8)` | 42 | `ed79bfc1...dac5f` |
| `AttConnRegister` | `[0x4B51C8,0x4B51CE)` | 6 | `fb95ef4a...965c2` |
| `AttGetMtu` | `[0x4B5204,0x4B5210)` | 12 | `7662e7e4...96309` |
| `AttMsgFree` | `[0x4B5210,0x4B522E)` | 30 | `89f7706f...bde99` |

`attCcbByHandle` and public zero-copy allocator `AttMsgAlloc` are source-only.
Neither has a body in its source-order position, a direct caller, or a stored
entry pointer. Internal `attMsgAlloc` remains heavily linked; the distinction
is intentional.

## Default routing and EATT boundary

`attCb=0x200610AC`. Its three 20-byte connection control blocks occupy the
first `0x3C` bytes and each contains three bearer slots. `AttHandlerInit`
stores the handler ID at `+0x60`, installs the legacy interface at `+0x3C`
and `+0x40`, and installs the EATT default interface at `+0x44` and `+0x48`.
It then registers the stock L2CAP callbacks and DM connection callback.

The exact constant interfaces are:

- `attFcnDefault [0x007851E0,0x007851F0)` =
  `{attEmptyDataCback, attEmptyHandler, attEmptyHandler, attEmptyConnCback}`;
- `eattFcnDefault [0x007851F0,0x00785200)` =
  `{attEmptyL2cCocCback, attEmptyL2cCocCback, attEmptyHandler,
  attEmptyConnCback}`.

`AttHandler` is stored as an odd Thumb pointer at `0x004B8788`. It routes
message event ranges at `0x20`, `0x40`, `0x60`, and `0x80` through the
legacy client, legacy server, enhanced client, enhanced server, and optional
top-level EATT handler fields. This is the r20 three-bearer/EATT architecture,
not the r19 single-bearer layout.

This TU proves that EATT starts disabled through real no-op defaults. It does
not by itself prove that no later initializer overwrites `attCb+0x44..+0x54`;
that separate whole-image store/caller census is the remaining requirement
for excluding `atts_eatt.c`.

The initialized 16-byte Bluetooth base UUID lives at `0x2000044C`. The
literal pool also pins `pAttCfg=0x200004B4` and the retained source path
`D:\01_workspace\s200_ap510b_iar_git\third_party\cordio\ble-host\sources\stack\att\att_main.c`
at `0x006DC754`.

## Ingress closure

Sixty-five direct BL sites reach linked entries. The three L2CAP/DM callbacks,
four empty callbacks, and `AttHandler` additionally enter through 14 exact
stored Thumb pointers in the registration literal pool, WSF handler table,
legacy/enhanced default interfaces, and consumer interfaces. Thirty-two
decoded direct calls leave the object. One raw BL-looking halfword at
`0x004B5108` is the second half of the valid wide arithmetic instruction used
to divide the encoded message parameter by three.

The exhaustive byte-window scan finds 17 values numerically inside the large
diagnostic-expanded `attCcbByConnId` body. Fifteen are rolling windows through
unrelated ASCII strings ending in `" OK\0"`; the other two are unaligned packed
data. None is an accepted function pointer. No decoded direct branch enters a
strict interior.

## Source lineage

AmbiqSuite 2.4.2/2.5.1 is the Packetcraft r19 source: Git blob
`a18b4fd69d7fbd0d039777a4e3d2edb6041a11d6`, 15,873 bytes, SHA-256
`08aa7bf9bf36504510f71ca28f95748fffcc444424c46eb2aed796c818da62e0`.
Its single bearer, absent EATT defaults, and old handler routing are excluded
by stock.

Packetcraft r20.05c is blob
`e21a30766686e1657906412187b223d2c7a92f9d`, 19,467 bytes, SHA-256
`2706979a8ec7c310bcc41ce057e16aaa0ae7381086e0c0cb82fb60a423d74058`.
The later official AmbiqSuite R4.4.1 import is blob
`decbdafce60ebc2fe2b9e986ffd97207fceebcb2`, 19,463 bytes, SHA-256
`38c4287295d85efd7c153495a51248397496e71f60b26cf5f1364e9317797359`.
The two implementations are byte-identical from the first include onward;
their only file delta is four trailing spaces in the Apache header. R4 is an
exact later corroborating oracle, not a resolved historical producing commit.

## Reproduction

```sh
python3 tools/analyze_g2_cordio_att_main.py --json
python3 -m unittest tests.test_analyze_g2_cordio_att_main
```

The next step is the whole-image enhanced-ATT initializer census. If no
override of the defaults survives, `atts_eatt.c` and `atts_dyn.c` can be
audited as optional exclusions rather than treated as unknown linked code.
