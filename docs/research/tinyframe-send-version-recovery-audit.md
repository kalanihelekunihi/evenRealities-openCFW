# TinyFrame send-side and upstream-version recovery audit

Status: research-only, read-only recovery. This work adds only a host analyzer,
its focused tests, and this audit. It does not alter a production overlay,
manifest, firmware artifact, release pin, hardware, or flash state.

Scope: close the send-side, peer-ID, buffer/locking, and official-history gaps
left by the earlier receive-side audit. All firmware claims below are checked by
[`tools/analyze_g2_tinyframe_send_version.py`](../../tools/analyze_g2_tinyframe_send_version.py)
against the official G2 `2.2.6.10` Apollo-main image (3,523,396 bytes; SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`).

## Result

The G2 library is a vendor-patched copy of the official MIT-licensed
[MightyPork/TinyFrame](https://github.com/MightyPork/TinyFrame) post-`2.3.0`
lineage. Its send behavior is source-equivalent to official history from
`44ecc0686c6a6b89ec357b6ab187763089e2b2bc` through repository head
`a29167a69f052975b0e0134a73b4d31d03afa8fa`. The machine code cannot select a
single commit inside that interval, and the complete G2 tree is not equal to
any upstream commit, so the exact vendor commit/tree remains deliberately
`null`.

The practical reuse boundary is nevertheless strong: reuse the official
TinyFrame core send source from that interval under MIT, then keep the G2
configuration, object magic checks, logging, callbacks, and transport in a
small reviewed port/vendor-patch layer.

## Independently authenticated identity

The analyzer rechecks the embedded path
`D:\01_workspace\s200_ap510b_iar_git\third_party\TinyFrame\TinyFrame.c` at
run `0x006FE474`, the TinyFrame `TF_InitStatic()` diagnostic at `0x0071A188`,
and the application multipart diagnostic at `0x0071924C`. File offset `0x20`
maps to run `0x00438000`, giving the established load base `0x00437FE0`.

The official upstream objects were resolved from Git object history, not from
release names alone:

| State | Commit | Tree | `TinyFrame.c` blob | `TinyFrame.h` blob |
|---|---|---|---|---|
| latest release `2.3.0` (lightweight tag; excluded) | `74d6451d5076136ed05abb486bacb850ae75d1a9` | `3314102973f01c77583b997f0b5cdfb0acaccb41` | `34899420d6f407c9f4be713647601c2fe51b4741` | `5f6943c92b8eca5c2c81f449a3490633438de277` |
| equivalence floor | `44ecc0686c6a6b89ec357b6ab187763089e2b2bc` | `4cb10d005bc934172a62a5a2301946fc971bb66b` | `771bc1d2c6ffbae6024f542e455a0c10209a5b2f` | `ca66433759f42b09edef526ca9594892283532b0` |
| formatting successor | `eb75483e035916ef9f3e9fce0d2ae389cb09785f` | `0e166ad5f97162b1dbcbcafd2bfef144f68aff13` | `ac64150369dd155f26d1e47c1f5a10f92887298b` | `a142b4bba086f27565bd26282055c357364616b3` |
| equivalence ceiling / repository head | `a29167a69f052975b0e0134a73b4d31d03afa8fa` | `2d9843138511c81f81b42b64524ff4e6b3e2fb86` | `ac64150369dd155f26d1e47c1f5a10f92887298b` | `a142b4bba086f27565bd26282055c357364616b3` |

The upstream `LICENSE` is MIT, 1,072 bytes, Git blob
`22acaabc6b85723107caae262ec537e710c19aac`, SHA-256
`eb7b9df3ca390100d31f9aac23f2d8dfe0183a63987112675fc58af9a42f6874`.
The stable auxiliary blobs are `TF_Config.example.h`
`099d026bfd4c8c7705647958127dee002f1bac88` and
`TF_Integration.example.c` `1e1b3572021629891682e49dcf50c1e4d33bbfb6`.

### Why the interval starts at `44ecc068`

The G2 binary carries a five-argument `TF_SendFrame`/`TF_Query` path:
`TinyFrame*`, message, listener, listener-timeout callback, and timeout ticks.
It stores the timeout callback in each 24-byte ID-listener entry and invokes it
only when non-null. Upstream commit `60e5bcb3` introduced the callback field but
did not yet thread it coherently through the send APIs; `44ecc068` is the first
official state with the recovered send topology.

Tag `2.3.0` predates the listener-timeout callback and is therefore excluded as
the exact source. From `44ecc068` to `eb75483e`, the relevant changes are
formatting plus correction of a header prototype typo; `a29167a` changes demo
content while retaining the same `TinyFrame.c` and `TinyFrame.h` blobs as
`eb75483e`. Those states compile to the same recovered send semantics, so
machine behavior cannot select one textual state.

### Why no complete upstream commit is exact

`TF_InitStatic` at `[0x00491752,0x004917D2)` clears a `0x7160`-byte object and
adds G2-only magic values: `0xA5A5A5A5` at `+0` and `0x5A5A5A5A` at `+0x715C`.
The prefix shifts upstream public/internal fields by four bytes. G2 also
replaces `TF_Error` and `TF_WriteImpl` with application-specific integrations
and supplies a private `TF_Config.h`. These are positive vendor-fork evidence,
not uncertainty to paper over with a release tag.

## Exact recovered send closure

Every complete body below is independently SHA-256-pinned by the analyzer.

| Function | Exact run interval | Bytes | SHA-256 |
|---|---:|---:|---|
| `TF_ClaimTx` soft lock | `[0x004916C8,0x00491722)` | 90 | `b5f0508cbb1efc151513afa92c0c172824f55f82d0ce4ffa25e6303075bc16e2` |
| `TF_ReleaseTx` soft lock | `[0x00491722,0x0049172C)` | 10 | `b177facafe9a96ba339dde25abc5989cc030d7b0f9174f5467bb8466df2eb3c7` |
| `TF_ComposeHead` | `[0x00491F54,0x00492032)` | 222 | `b99f03cff24a278355d37e299be5c7b57ae84ac7d02ac0f625b708e678aaf940` |
| `TF_ComposeBody` | `[0x00492032,0x0049207A)` | 72 | `9c4fb7cece798d4910878de02fc5c2bb5e300eb3c51a793a2e9a176d72a33ebc` |
| `TF_ComposeTail` | `[0x0049207A,0x004920AA)` | 48 | `935d106799c49ded9f420e45c9a7af162d6d9287a56b30b79b3824c82ae5a5cc` |
| `TF_SendFrame_Begin` | `[0x004920AA,0x00492114)` | 106 | `88cc7683407387bd3a05b874cc5854bda1143fe052aeb8813bfd9fa681c7f155` |
| `TF_SendFrame_Chunk` | `[0x00492114,0x00492198)` | 132 | `8a9f0fd729f9c8b16f1fa57661c747ff5d116e10b45eaa10e6d0d243f6eb3792` |
| `TF_SendFrame_End` | `[0x00492198,0x00492200)` | 104 | `3f4560ef0982ed99c25f49100ed1ee3cdef726853c2256ef73879d9d657988db` |
| `TF_SendFrame` | `[0x00492200,0x0049223C)` | 60 | `66163f20aba56809b0eb52f5db199aae616d6f233284ba47c8654c0e9db1addc` |
| `TF_Send` | `[0x0049223C,0x0049224C)` | 16 | `5b1e502cd5ab6ccc920021d8100ba9d015b7d25bbbdb0cf32dac78d381221d39` |
| `TF_Query` | `[0x0049224C,0x0049225A)` | 14 | `e348f1aa2d888197ead654f4cbdc689ea964af5ff8b1d03b647317353ecd3823` |
| `TF_Respond` | `[0x0049225A,0x00492266)` | 12 | `d1ce93ac47083fe0ab1104e930ef6142d439bf44cd6e596ba499ea13da9c59d7` |
| `TF_Query_Multipart` | `[0x00492266,0x00492278)` | 18 | `c53c52b0b4e741bba45b981b405b6040f5e92c965b69c95958c2d26776d56372` |
| `TF_Multipart_Payload` | `[0x00492278,0x00492280)` | 8 | `ce3a5e1407dc2a68941ca1cb5bf191dfa48a9a176d735efb69b747aab42e6bf4` |
| `TF_Multipart_Close` | `[0x00492280,0x00492288)` | 8 | `2e7f95a6afa0b18c10a346869a17a8a73c9f4a38221115f3556303d98e48c201` |

The exact internal topology is:

```text
TF_Send / TF_Query / TF_Respond / TF_Query_Multipart
                         |
                         v
                    TF_SendFrame
                  /      |       \
                 v       v        v
              Begin --> Chunk --> End
                |         |        |
                v         v        v
          ComposeHead ComposeBody ComposeTail
                |         |        |
                +---------+--------+
                          |
                   CRC-16/ARC leaves
```

`Begin` claims the lock, composes the head, stores declared payload length,
optionally adds the response listener, and resets the body checksum. `Chunk`
fills and flushes the fixed transmit buffer. `End` appends a data checksum only
for non-empty payloads, flushes, and releases the lock. A failed listener add
releases the lock before returning false.

The direct branch graph is also checked across the complete image. The only
application calls into retained multipart request transmission are
`0x0045E76A` (`TF_Query_Multipart`), `0x0045E808`
(`TF_Multipart_Payload`), and `0x0045E858` (`TF_Multipart_Close`). Twelve
application response-building sites call `TF_Respond`; their addresses are
reported in analyzer JSON rather than classified as TinyFrame source.

## Wire format and peer-ID policy

The send side confirms the field widths and ordering recovered on receive:

```text
SOF(01) | ID(2 BE) | LEN(2 BE) | TYPE(2 BE) | HEAD_CRC(2 BE)
        | DATA(LEN bytes) | DATA_CRC(2 BE, only when LEN != 0)
```

Both checksums use CRC-16/ARC: normal polynomial `0x8005`, reflected polynomial
`0xA001`, init `0`, xorout `0`. The 512-byte table at
`[0x006C0950,0x006C0B50)` has SHA-256
`961656eaf43bdf70937151a003627324be86c28ca32285f58edd5f5c73c51b79`
and exactly equals a regenerated canonical table.

Important correction to the earlier receive-only description: **the header CRC
includes the SOF byte**. Both `pars_begin_frame` at
`[0x00491BB6,0x00491BE4)` and `TF_ComposeHead` add `0x01` before ID, LEN, and
TYPE. Thus header coverage is `SOF || ID || LEN || TYPE`, not only
`ID || LEN || TYPE`. A zero-length frame ends after `HEAD_CRC`; it does not
carry `DATA_CRC`.

For a new request, the exact expression is:

```c
id = (next_id++ & 0x7fff) | (peer_bit ? 0x8000 : 0);
```

`next_id` is a `uint16_t` at object `+0x0E`; its raw rollover is
`0xFFFF -> 0x0000`, while the request ID visible on one peer repeats every
`0x8000` sends. `peer_bit` is a one-byte value at `+0x0C`. A response sets
`is_response` and preserves the received 16-bit `frame_id` exactly; it does not
toggle or recompute the peer bit.

The analyzer's host-only reference composer pins these examples:

| Case | Exact wire bytes |
|---|---|
| peer 0, request ID 0, type `0x1234`, data `10 20` | `0100000002123477bc1020180c` |
| peer 1, request ID 0, type `0x1234`, data `10 20` | `01800000021234b7a31020180c` |
| response ID `0xBEEF`, type `0x2222`, empty data | `01beef00002222b046` |

These are disassembly-derived reference vectors, not hardware captures.

## Send buffer, limits, and locking

| G2 field/macro | Recovered value |
|---|---|
| `TF_USE_MUTEX` | `0` |
| `TF_SENDBUF_LEN` | `0x400` (1,024) |
| `peer_bit` | `+0x0C`, 1 byte |
| `next_id` | `+0x0E`, 2 bytes |
| `sendbuf` | `+0x6021`, 1,024 bytes |
| `tx_pos` | `+0x6424`, 4 bytes |
| `tx_len` | `+0x6428`, 4 bytes |
| `tx_cksum` | `+0x642C`, 2 bytes |
| `soft_lock` | `+0x642E`, 1 byte |

The lock is upstream's per-instance, non-atomic soft lock: nested transmission
is rejected and logged, but it is not a cross-thread mutex. The buffer is
flushed whenever `tx_pos == 1024`; if fewer than two bytes remain at close, the
body CRC starts in a fresh buffer.

The transmit API encodes a 16-bit length, so its representable length is
`0..65535`. There is no send-side equivalent of the receive cap `0x6000`, and
multipart transmission does not verify that bytes supplied across calls equal
the length declared in the header. Those are upstream behaviors to preserve or
explicitly harden in a later source-integration decision.

## Application transport and callback boundary

`TF_WriteImpl` is not a TinyFrame implementation detail to vendor. The local
wrapper at `[0x004D9522,0x004D9530)` (14 bytes, SHA-256
`12611160fc8e6ee3552e451f338ef1a611ad59ddf77254c51b5a1685d9d7c7f9`)
ignores `TinyFrame*` and forwards `(buffer, length, timeout=100)` to the
first-party entry `0x00541790`. The three TinyFrame flush calls at
`0x0049216C`, `0x004921C0`, and `0x004921F4` are its only direct callers.

Listener callbacks, timeout callbacks, and the higher-level sync-module
message builders are likewise application-owned. This audit authenticates
only their TinyFrame registration/invocation ABI; it does not fold those
callbacks or transport behavior into the upstream source-equivalence claim.

## Reproducibility and remaining gates

Focused verification:

```sh
python3 -m unittest -v tests.test_analyze_g2_tinyframe_send_version
python3 tools/analyze_g2_tinyframe_send_version.py
python3 tools/analyze_g2_tinyframe_send_version.py --json
python3 -m py_compile tools/analyze_g2_tinyframe_send_version.py \
  tests/test_analyze_g2_tinyframe_send_version.py
```

Before production vendoring or a behavioral compatibility claim:

1. Capture real G2 frames and compare them with the host reference vectors.
2. Identify which peer role is selected for every runtime TinyFrame instance.
3. Keep first-party transport `0x00541790` in a separate boundary audit.
4. Review whether the non-atomic soft lock and unchecked multipart declared
   length should be preserved for compatibility or hardened by the custom
   firmware port.

This work does not sign, connect to, erase, program, or flash hardware.
