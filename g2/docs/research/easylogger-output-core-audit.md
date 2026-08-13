# EasyLogger `elog_output` core audit

## Result

The Apollo-main function at
`[0x0043D574, 0x0043D976)` is the complete variadic EasyLogger
`elog_output` body. It is 1,026 bytes and has SHA-256
`d7c5fd89997fc677ecce543af7c33cd08614b832a47602f1fd895bb7ab45f90c`.
The exclusive end is exact: the final `pop.w ... pc` ends at
`0x0043D976`, followed by two zero alignment bytes and the four-byte
`CSI_START` string/padding at `0x0043D978`.

The ordinary thread-mode formatting and filtering behavior is
source-equivalent to the authenticated Armink EasyLogger `elog.c` snapshot
at commit
[`a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`](https://github.com/armink/EasyLogger/commit/a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24).
Two deliberate G2 semantic changes must be preserved:

1. G2 reads `IPSR` immediately after the prologue and returns without
   dereferencing arguments, asserting, locking, or emitting when it is
   nonzero. Upstream EasyLogger has no interrupt-context suppression in
   `elog_output`.
2. G2 sends the finished record to a downstream
   `(const char *buffer, size_t length, uint8_t level)` wrapper at
   `0x0044AA80`. Pristine upstream instead calls
   `elog_async_output(uint8_t level, const char *buffer, size_t length)`.

An entry redirect is mechanically closed. A whole-image scan finds 6,239
direct `BL` sites to the exact entry, no direct `B.W` callers, no narrow
branch callers, no external branches to an interior address, and no stored
odd Thumb pointer to the entry or an interior address. All existing callers
therefore continue to work through one four-byte entry redirect.

An **unmodified upstream transplant is not safe** because it would lose the
G2 interrupt gate and call the downstream sink with the wrong register
order. A bounded G2 adaptation of the authenticated upstream function is a
reasonable next source increment once the conditions in this report are
tested. Initially retaining the downstream async wrapper and the IAR
`vsnprintf` implementation as pinned seams is safer than expanding this
already broad boundary into transport and arbitrary-format compatibility at
the same time.

This audit did not modify firmware, manifests, overlay sources, tests, or
hardware.

## Evidence corpus

All firmware ranges use installed-image addresses and exclusive ends.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Official `ota_s200_firmware_ota.bin` wrapper | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Installed payload after the 32-byte preamble, based at `0x00438000` | 3,523,364 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| Vendored `third_party/easylogger/src/elog.c` | 28,740 | `d4291ab1314a34cf940c8e0d7246e05570f8d32ae0704b498cf6fbacab76acb1` |
| Vendored `third_party/easylogger/src/elog_utils.c` | 2,975 | `937eaf98151cb5fa25f102621802637d71ccadd56028098e3a45978a0707d9d0` |
| Vendored `third_party/easylogger/inc/elog.h` | 10,428 | `2890b272a01820a6336da544c056e7735b88330cd91a5092fb83a5538de11f48` |
| Vendored `third_party/easylogger/inc/elog_cfg.h` | 3,995 | `bccd34ca41c36ce8201d78fd2b844b071bad25bfbac452d02764617ca4ed3073` |

`third_party/easylogger/verify_snapshot.py` passes offline. The selected
snapshot is byte-identical to official upstream source and is the latest
member of the three-commit source-equivalent set established in
`easylogger-version-audit.md`.

## Exact boundary

| Item | Range | Bytes | SHA-256 |
|---|---:|---:|---|
| Preceding `elog_get_filter_tag_lvl` | `[0x0043D4B0,0x0043D574)` | 196 | `53770f37005d894be731529ef8bdcaa2588f2f7917239b3feb18bb59cf5a9c17` |
| `elog_output` | `[0x0043D574,0x0043D976)` | 1,026 | `d7c5fd89997fc677ecce543af7c33cd08614b832a47602f1fd895bb7ab45f90c` |
| Following alignment | `[0x0043D976,0x0043D978)` | 2 | `96a296d224f285c67bee93c30f8a309157f0daa35dc5b87e410b78630a09cfc7` |
| Following `"\x1b["` plus terminator/pad | `[0x0043D978,0x0043D97C)` | 4 | `2bf3e50cffdd270f80c0d2c95da60024539eb34a8ed2d367a00c2db17f037e13` |
| `get_fmt_enabled` | `[0x0043D97C,0x0043D9E6)` | 106 | `d0a18c1e6bc1a42e8a91b37c891aaf3425b98f6bc56741211512d871056b136d` |

The output body also addresses punctuation in the data gaps surrounding the
three private format helpers. Those strings are not executable interiors:

| Address | String |
|---:|---|
| `0x0043D978` | `"\x1b["` |
| `0x0043D9E8` | `" "` |
| `0x0043D9EC` | `"["` |
| `0x0043DA60` | `"] "` |
| `0x0043DA64` | `"("` |
| `0x0043DA68` | `":"` |
| `0x0043DA6C` | `"%ld"` |
| `0x0043DA74` | `")"` |
| `0x0043DA80` | `"\n"` |

A source candidate should emit its own read-only strings. The old pool can
remain mapped compatibility data until its other consumers are audited.

## Recovered G2 configuration

The output body and its application call sites prove:

| Configuration item | G2 value / result |
|---|---|
| `ELOG_OUTPUT_ENABLE` | enabled |
| `ELOG_OUTPUT_LVL` | `ELOG_LVL_VERBOSE` |
| `ELOG_ASSERT_ENABLE` | enabled |
| `ELOG_LINE_BUF_SIZE` | 1,024 |
| `ELOG_LINE_NUM_MAX_LEN` | 5 |
| `ELOG_FILTER_TAG_MAX_LEN` | 30 |
| `ELOG_FILTER_KW_MAX_LEN` | 16 |
| `ELOG_FILTER_TAG_LVL_MAX_NUM` | 5 |
| `ELOG_NEWLINE_SIGN` | `"\n"` |
| `ELOG_COLOR_ENABLE` | enabled |
| Assert/error/warn/info/debug/verbose colors | `35;22m`, `31;22m`, `33;22m`, `36;22m`, `32;22m`, `34;22m` |
| `ELOG_FMT_USING_DIR` | enabled at application call sites |
| `ELOG_FMT_USING_FUNC` | enabled at application call sites |
| `ELOG_FMT_USING_LINE` | enabled at application call sites |
| `ELOG_ASYNC_OUTPUT_ENABLE` equivalent | enabled, but through downstream G2 glue |

The output core proves that the async branch won preprocessing. It cannot
prove whether `ELOG_BUF_OUTPUT_ENABLE` was also defined because upstream's
`#if defined(ELOG_ASYNC_OUTPUT_ENABLE)` shadows the buffered branch. Likewise,
the core does not prove upstream async ring-buffer sizes or pthread settings:
G2 does not use the upstream async implementation at this boundary.

The level strings are `A/`, `E/`, `W/`, `I/`, `D/`, and `V/`. The stock
function reads them through the six-pointer initialized-RAM table at
`0x20000974`; it reads the six color strings through the table at
`0x2000098C`. A source candidate can use authenticated constant tables in
overlay read-only data instead.

## State and ABI

The function retains the normal 32-bit AAPCS variadic signature:

```c
void elog_output(
    uint8_t level,
    const char *tag,
    const char *file,
    const char *func,
    long line,
    const char *format,
    ...
);
```

Disassembly loads `line` from the incoming stack at the adjusted
`sp + 0x48`, `format` at `sp + 0x4C`, and initializes the variadic cursor at
`sp + 0x50`. A normally compiled Thumb source function with this prototype
preserves all 6,239 caller ABIs; no caller rewrite is required.

The fixed state used directly by the function is:

| State | Address / logger offset | Use |
|---|---:|---|
| Shared 1,024-byte line buffer | `0x2006BD30` | complete formatted output |
| `EasyLogger` object | `0x20070BE8` | filters, masks, and output flags |
| `filter.level` | `+0x00` | global level gate |
| `filter.tag[31]` | `+0x01` | substring tag gate |
| `filter.keyword[17]` | `+0x20` | post-format keyword gate |
| `enabled_fmt_set[6]` | `+0xD8` | per-level format bits |
| `output_enabled` | `+0xF1` | immediate output gate |
| `text_color_enabled` | `+0xF5` | color prefix/suffix gate |
| Assertion-hook pointer | `0x2007456C` | invalid-level hook |

The logger remains `0xF8` bytes after 32-bit padding, as already pinned by
the integrated control and tag-filter sources.

## Recovered behavior

### G2 interrupt gate and assertion

The first semantic operation is:

```text
MRS  r1, IPSR
CMP  r1, #0
BNE  return
```

Thus every exception/interrupt context is a silent no-op. In particular, G2
does not even read `tag`, `file`, `func`, `format`, the logger object, or the
shared buffer in that path.

In thread mode it asserts `level <= ELOG_LVL_VERBOSE`. The stock assertion
identity is:

| Field | Value |
|---|---|
| Expression | `level <= ELOG_LVL_VERBOSE` at `0x0076B634` |
| Function | `elog_output` at `0x0078A988` |
| Source path | `elog.c` path at `0x006E3098` |
| Downstream source line | 572 (`0x23C`) |
| Hook global | `0x2007456C` |
| No-hook diagnostic format | `(%s) has assert failed at %s:%ld.` at `0x007542A8` |
| Fail-stop wait wrapper | `0x0044B0AE` |

With no hook, it recursively calls `elog_output` at `0x0043D5C6` using
assert level and then loops through the wait wrapper. With a returning hook,
execution continues, preserving upstream behavior even though an invalid
level can later index past the six-entry tables.

### Gates and locking

In order, the thread-mode valid path:

1. rejects output when `output_enabled == 0`;
2. rejects when `level > filter.level`;
3. calls `elog_get_filter_tag_lvl(tag)` and rejects when its result is below
   `level`;
4. requires `strstr(tag, filter.tag)` to succeed;
5. computes `strlen(tag)`;
6. clears the six-byte line-number array and 16-byte tag-padding array;
7. locks output.

The lock covers all shared-buffer formatting, keyword filtering, downstream
submission, and final unlock. The keyword-miss path unlocks before return.
All earlier gates return without locking.

### Formatting

The remaining control flow matches upstream `elog.c`:

- optional `"\x1b["` plus the selected color;
- optional two-byte level marker;
- optional tag, padded with spaces to 15 characters when its length is at
  most 15, followed by one space;
- optional time/process/thread fields in brackets with conditional spaces;
- optional file, line, and function fields in parentheses;
- arbitrary message formatting through `vsnprintf`;
- truncation/reservation so a color suffix and one-byte newline fit within
  1,024 bytes;
- optional keyword search over a temporarily terminated buffer;
- optional `"\x1b[0m"`;
- final newline;
- asynchronous submission and unlock.

The format bits are the upstream values:

| Bit | Meaning |
|---:|---|
| `0x01` | level |
| `0x02` | tag |
| `0x04` | time |
| `0x08` | process |
| `0x10` | thread |
| `0x20` | directory/file |
| `0x40` | function |
| `0x80` | line |

The line conversion calls the IAR `snprintf` entry with size five and
`"%ld"`. The message conversion calls the IAR `vsnprintf` entry with
`buffer + log_len` and `1024 - log_len`. A nonnegative result whose unsigned
sum with the prefix is at most 1,024 is accepted; otherwise the length
becomes 1,024. If the suffix plus newline would overflow, the length is
reduced to 1,019.

If `filter.keyword[0] != 0`, the body writes a terminator at the computed
length and searches the formatted prefix/message before adding the color
suffix and newline. A miss unlocks and discards the record.

### Downstream async delta

At `0x0043D960...0x0043D968`, G2 calls:

```c
g2_elog_async_output(log_buf, log_len, level);
```

The wrapper at `[0x0044AA80,0x0044AA98)` converts `level` to eight bits,
passes `(buffer, length, 0, level)` to the downstream record builder at
`0x00448D4E`, and then sets event bit one through the handle loaded from
`0x20074570`.

The record builder clamps lengths of 256 or more to 255, copies the payload
at record offset `+0x0D`, terminates it, stores the 16-bit length at `+0x08`,
stores the default metadata value at `+0x0A`, and stores the level byte at
`+0x0C` before queue submission. This is G2 application policy from the
retained `elog_async_api.c` path, not authenticated upstream
`elog_async.c`.

| Downstream seam | Range | Bytes | SHA-256 |
|---|---:|---:|---|
| G2 async output wrapper | `[0x0044AA80,0x0044AA98)` | 24 | `787d13cfe59fad83061379298387393fa94266c9b31420e7f67e8e07d63f7356` |
| G2 async record builder | `[0x00448D4E,0x00448DD2)` | 132 | `9d95b63bc62e11910e39344ddea65213798d75caa4b91d5ce9cf033d09509e17` |

The output replacement should initially preserve the wrapper with an
explicit typed function pointer or a separately named G2 port function.
Calling the pristine upstream async signature at this address would corrupt
the arguments.

## Direct dependency closure

The stock body contains 58 direct `BL` instructions. Their ordered
`SITE->TARGET` tuple list, encoded as comma-separated uppercase eight-digit
hex values without `0x`, has SHA-256
`04428eb63e39d72ea3602be29f1c2de7b23f024ac48fa3d9017fba4c9a4ea003`.

| Target | Calls | Role | Replacement policy |
|---:|---:|---|---|
| `0x0043C0E4` | 3 | zero/fill stack arrays and tag padding | use source byte loops |
| `0x0043D416` | 1 | output lock | link integrated source symbol directly |
| `0x0043D438` | 2 | normal and keyword-miss unlock | link integrated source symbol directly |
| `0x0043D4B0` | 1 | tag-level filter query | link integrated source symbol directly |
| `0x0043D574` | 1 | no-hook assertion diagnostic recursion | source self-call |
| `0x0043D97C` | 8 | format-bit query | local source helper |
| `0x0043D9F0` | 3 | nonzero line plus format query | local source helper |
| `0x0043DA0A` | 6 | nonnull pointer plus format query | local source helper |
| `0x0044A43C` | 1 | tag length | use integrated source length or local helper |
| `0x0044AA80` | 1 | downstream async submission | retain pinned G2 seam initially |
| `0x0044AAA8` | 1 | time text | retain pinned G2 port seam initially |
| `0x0044AB14` | 1 | process text | retain pinned G2 port seam initially |
| `0x0044AB1C` | 1 | thread text | retain pinned G2 port seam initially |
| `0x0044B0AE` | 1 | assertion fail-stop wait | retain only on invalid/no-hook path |
| `0x0044B63A` | 2 | substring filters | local source helper |
| `0x0044B668` | 23 | bounded EasyLogger append | authenticated local source helper |
| `0x0044B728` | 1 | line-number `snprintf` | local five-byte signed-decimal helper or retain after oracle |
| `0x0044B76C` | 1 | arbitrary message `vsnprintf` | retain pinned IAR seam initially |

Exact stock pins for the external seams are:

| Seam | Range | Bytes | SHA-256 |
|---|---:|---:|---|
| memory fill | `[0x0043C0E4,0x0043C14A)` | 102 | `34da1a99d5cb56ca41cfaff98190ced2a7767f53cd95c53c504009566e9ca10a` |
| output lock | `[0x0043D416,0x0043D438)` | 34 | `4d87d1bcc02e66513c6774076ff4ba4c1024c5592013439d7e8dfdf53bb483b0` |
| output unlock | `[0x0043D438,0x0043D45A)` | 34 | `86bff518c98f24bd440f5ebe4150c5d66c0e0090e844c3af3c446ab53e4799ea` |
| tag-level getter | `[0x0043D4B0,0x0043D574)` | 196 | `53770f37005d894be731529ef8bdcaa2588f2f7917239b3feb18bb59cf5a9c17` |
| format query | `[0x0043D97C,0x0043D9E6)` | 106 | `d0a18c1e6bc1a42e8a91b37c891aaf3425b98f6bc56741211512d871056b136d` |
| line-aware format query | `[0x0043D9F0,0x0043DA0A)` | 26 | `95bba933ae9e65022ef0ff0daa76324678aa539c2ba79435b80181ce34a23db7` |
| pointer-aware format query | `[0x0043DA0A,0x0043DA24)` | 26 | `3af2631ad7a44be557a9454da2df68862b6458bf2359f58d41c3d6d2ff86c8a2` |
| string length | `[0x0044A43C,0x0044A472)` | 54 | `1e68ab720083f9d7a67b3df35eb64d8dab5b90457f3c193427624a68bb630451` |
| time text | `[0x0044AAA8,0x0044AAE0)` | 56 | `5c53db03b25eb1ef19bce3f63825dbc176889eccdb37b5a8ec3c0db0785fdf74` |
| process wrapper | `[0x0044AB14,0x0044AB1C)` | 8 | `a9f2a0a2bb12b213c65871b1654bf23fa528fd3fe73c59dbce8396c2c92f9379` |
| thread wrapper | `[0x0044AB1C,0x0044AB24)` | 8 | `3f4f980e3ab1c9afbabe7ab5ddedde924ad8f5962346c746a81922a70249d621` |
| assertion wait | `[0x0044B0AE,0x0044B0B6)` | 8 | `5f9a6b47f08eb58759df839c742eeae1a6c396a5731d2aa80cb635be744cc64f` |
| substring search | `[0x0044B63A,0x0044B666)` | 44 | `3807c4da8b7f2aa7353295d2d625cc6c982739c1fddfc99f99e68711d2166cc5` |
| EasyLogger bounded append | `[0x0044B668,0x0044B70A)` | 162 | `aac245096c55f678eec81bf04dfe27ef63fffbe1c225e8ab73fe99f6c97f1997` |
| IAR `snprintf` | `[0x0044B728,0x0044B766)` | 62 | `0b3f0ee4463f8a2560eb9a1ac68060b39fb797c0c44f5a85daa923fe5bcf14fd` |
| IAR `vsnprintf` | `[0x0044B76C,0x0044B7A2)` | 54 | `6370164665446b0f6232e3883ca06fe954ee4aa335dc433328232bbf5e90ee12` |

The time port formats
`"%d/%d/%d %02d:%02d:%02d %d"` into the 28-byte buffer at `0x20073A74`.
Both process and thread wrappers call the same G2 helper, which returns the
current FreeRTOS task name or `"unknown"`.

The project already source-owns the public runtime formatter based on
mpaland/printf, but the stock logger calls a separate IAR `vsnprintf` entry.
Because the 6,239 callers supply arbitrary formats, substituting the
mpaland implementation is a separate compatibility decision. The first
`elog_output` increment should retain the pinned IAR formatter unless an
oracle proves the complete logging format corpus equivalent.

## Whole-image caller and interior topology

The scan examines every halfword of the installed payload for Thumb-2 `BL`
and `B.W`, every halfword for narrow unconditional/conditional branches and
`CBZ`/`CBNZ`, and every byte offset for a 32-bit odd Thumb pointer.

| Topology item | Result |
|---|---|
| Direct `BL` sites to `0x0043D574` | 6,239 |
| First / last direct site | `0x0043C426` / `0x005F9E7C` |
| Direct `B.W` sites to entry | none |
| Narrow branch sites to entry | none |
| External wide branches into `(0x0043D574,0x0043D976)` | none |
| External narrow branches into the interior | none |
| Stored odd pointer to entry or interior | none |

The exact direct-call list is pinned without copying 6,239 addresses into
this report. Encoding each ascending site as uppercase eight-digit hex
without `0x`, joined by commas, yields SHA-256
`2d4e701757c3ec84ae6c6b53b2638728c3da6d6121eb95579f3b4e13843be2a2`.
Counts by caller address's 64-KiB page are:

```text
43:23 44:206 45:309 46:434 47:384 48:38 49:386 4A:340
4B:342 4C:96 4D:339 4E:308 4F:268 50:184 51:115 52:116
53:298 54:342 55:236 56:152 57:431 58:226 59:160 5A:13
5B:226 5C:50 5D:8 5E:183 5F:26
```

The raw topology is unusually broad but redirect-safe: all direct sites
land on the one public entry. There is no evidence of an alternate ABI,
mid-function entry, callback table, or veneer that must be changed with it.

## Recommended source boundary

Use one MIT-licensed G2 adaptation of the authenticated upstream body:

```text
open_cfw_easylogger_output
```

The fail-closed stock patch record is:

```json
{
  "name": "replace_easylogger_output",
  "runtime_address": 4445556,
  "expected_size": 1026,
  "expected_sha256": "d7c5fd89997fc677ecce543af7c33cd08614b832a47602f1fd895bb7ab45f90c",
  "branch": "b_w",
  "target_function": "open_cfw_easylogger_output"
}
```

The source should:

1. reuse the existing logger object and shared `0x2006BD30` line buffer so
   every stock consumer observes the same state;
2. reproduce the `IPSR != 0` silent return before any other access;
3. preserve the four-register/stack AAPCS variadic entry exactly;
4. link the integrated source tag-level getter and lock functions directly;
5. use local authenticated format predicates, append logic, string search,
   string length, fill loops, punctuation, level strings, and color strings;
6. preserve G2 assertion expression/function/line 572 and its hook/fail-stop
   behavior;
7. retain a typed three-argument G2 async seam with argument order
   `(buffer, length, level)`;
8. retain the IAR `vsnprintf` seam for the first increment;
9. either prove a local five-byte signed-decimal conversion byte-equivalent
   to IAR `snprintf` or retain the pinned line formatter too.

The three private format helpers at `0x0043D97C`, `0x0043D9F0`, and
`0x0043DA0A` need not be patched in the same increment. The output candidate
can implement them locally while leaving their stock entries for any other
callers. A later caller audit can source-own those public stock ranges
independently.

## Required acceptance tests

The redirect should not ship until automated tests cover:

1. wrapper/payload/body hashes, exact boundary, two-byte pad, and following
   `CSI_START` data;
2. the 6,239-site caller hash plus the negative wide/narrow/interior/stored-
   pointer topology;
3. target compilation with the overlay flags and an exact AAPCS variadic
   signature;
4. thread-mode comparison to a pristine vendored EasyLogger oracle for all
   six levels, output enable, global/tag/tag-level filters, colors, and
   format masks;
5. a target-side or substituted `IPSR` test proving every nonzero exception
   number returns before argument, state, buffer, assertion, lock, formatter,
   and sink access;
6. empty, 15-byte, 16-byte, 30-byte, and longer tags, including exact
   15-column padding;
7. time/process/thread combinations and null/non-null file/function plus
   zero/nonzero line combinations;
8. line values around the five-byte `snprintf` truncation boundary;
9. ordinary, zero-length, exact-capacity, oversized, and negative
   `vsnprintf` results, with final lengths 1,024 and 1,019 where required;
10. keyword empty/match/miss behavior, including unlock-on-miss and the fact
    that matching occurs before color suffix/newline insertion;
11. lock-before-first-buffer-write, one normal unlock, no early-gate lock,
    and no sink call while rejected;
12. exact G2 sink argument order, eight-bit level, event-bit notification,
    and downstream 255-byte record clamp;
13. returning assertion hook and static no-hook recursion/wait verification
    without entering the fail-stop loop;
14. candidate-vs-oracle message bytes for every distinct format string used
    by the current 6,239 caller corpus before considering replacement of the
    IAR formatter seam;
15. full component/package rebuild, complete test suite, offline flash
    inspectors, and three-way reproducible artifact hashes.

## Safety verdict and next dependency

The stock entry is topologically safe to redirect and the upstream source
identity is strong enough to avoid decompiling its formatting algorithm from
scratch. The next implementation should nevertheless be described as a
**G2 adaptation**, not an unmodified EasyLogger import.

The remaining opaque dependencies after that bounded replacement would be
the arbitrary-format IAR formatter and the G2 time/task/async port. Of those,
the async wrapper is the highest-value next focused disassembly because it
owns the event notification and 255-byte downstream record policy. It should
be recovered as a separate `g2_elog_async_glue.c` boundary after
`elog_output` is stable, rather than silently substituted with upstream
`elog_async.c`, whose ring-buffer and notification contracts do not match
the installed G2 path.
