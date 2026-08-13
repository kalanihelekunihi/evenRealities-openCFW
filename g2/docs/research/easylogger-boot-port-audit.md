# G2 bootloader EasyLogger configuration and port audit

## Result

The EasyLogger copy in the official G2 `2.2.6.10` S200 bootloader is
source-equivalent to the same authenticated Armink EasyLogger generation as
Apollo main. The defensible upstream source pin remains
[`a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`](https://github.com/armink/EasyLogger/commit/a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24).
The earlier `cd93d9c` commit and the two later documentation-only commits are
binary-indistinguishable because their relevant source blobs are identical.

The bootloader uses the same `0xF8`-byte `EasyLogger` ABI, line-buffer size,
five tag-level records, color table, assertion scheme, thread-mode interrupt
gate, and ordinary `elog_output` formatting flow as Apollo main. It is not,
however, the same port or application policy:

- the boot logger object is at `0x20026700`;
- the shared 1,024-byte line buffer is at `0x200258D0`;
- the boot setup keeps the global filter at verbose rather than reducing it
  to info;
- assert uses format mask `0xFF`, while error through verbose use `0xD7`;
- boot time text is the decimal RTOS tick count, not Apollo main's
  calendar/time tuple;
- the boot sink discards the log level and submits the buffer on downstream
  channel `1`;
- the boot image has no identifiable retained `elog_stop`, deinitialization
  message, upstream async worker, tag-level setter, raw-output body, or
  hexdump body and no associated direct callers or identity strings.

The downstream channel-1 transport uses a 56-byte transfer descriptor,
initiates one lower driver transfer, and polls its completion flag for at
most 1,000 iterations with a ten-unit wait between polls. This is neither
pristine upstream `elog_async.c` nor Apollo main's 255-byte record queue and
event-bit transport.

The core is mechanically well bounded. The boot image has 115 direct `BL`
callers to the exact `elog_output` entry, no `B.W` caller to that entry, no
external wide branch to an interior EasyLogger instruction, and no stored
odd Thumb pointer to a core or port entry/interior. The boot configuration
routine itself is reached through one stored odd Thumb pointer at
`0x00433448`.

The initial audit was read-only. Its helper quartet has since been
production-integrated into both Apollo source overlays; that local build
changed generated firmware artifacts but did not access hardware.

## Evidence corpus

All boot addresses are raw-image addresses based at `0x00410000`. Unlike the
Apollo-main OTA payload, the boot blob has no 32-byte installed-image
preamble.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Official `ota_s200_bootloader.bin` | 148,599 | `f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5` |
| Vendored `third_party/easylogger/src/elog.c` | 28,740 | `d4291ab1314a34cf940c8e0d7246e05570f8d32ae0704b498cf6fbacab76acb1` |
| Vendored `third_party/easylogger/src/elog_utils.c` | 2,975 | `937eaf98151cb5fa25f102621802637d71ccadd56028098e3a45978a0707d9d0` |
| Vendored `third_party/easylogger/inc/elog.h` | 10,428 | `2890b272a01820a6336da544c056e7735b88330cd91a5092fb83a5538de11f48` |
| Vendored `third_party/easylogger/inc/elog_cfg.h` | 3,995 | `bccd34ca41c36ce8201d78fd2b844b071bad25bfbac452d02764617ca4ed3073` |
| Vendored upstream port template | 2,450 | `2cf63c54ca1d4a1a95fd490fdd977a7ac8686bb6639db39eba38ec0e54755f9b` |

The boot image retains:

| Evidence | Address |
|---|---:|
| EasyLogger version `2.2.99` | `0x00434074` |
| `elog.c` build path | `0x00430EC0` |
| `elog_utils.c` build path | `0x00430DA0` |
| level strings `A/` through `V/` | `0x00434178...0x0043418F` |
| six color strings | `0x0043403C...0x0043406B` |
| assertion-hook pointer | `0x200270E4` |

The build paths identify the same downstream
`third_party\EasyLogger-master\easylogger\src` tree as Apollo main. The
argument-aware directory/function/line helpers are present and have the
same complete machine-code hashes as Apollo main. That is the conclusive
`cd93d9c`-or-later source discriminator described in
`easylogger-version-audit.md`.

## Exact object and buffer ABI

The boot `EasyLogger` object occupies `[0x20026700,0x200267F8)`.

| Object field | Offset / size |
|---|---:|
| `filter.level` | `+0x00`, one byte |
| `filter.tag` | `+0x01`, 31 bytes |
| `filter.keyword` | `+0x20`, 17 bytes |
| five tag-level records | `+0x31...+0xD5`, 33 bytes each |
| `sizeof(ElogFilter)` | `0xD6` |
| ABI alignment padding | `+0xD6...+0xD7` |
| six `size_t` format masks | `+0xD8...+0xEF`, four bytes each |
| `init_ok` | `+0xF0` |
| `output_enabled` | `+0xF1` |
| `output_lock_enabled` | `+0xF2` |
| `output_is_locked_before_enable` | `+0xF3` |
| `output_is_locked_before_disable` | `+0xF4` |
| `text_color_enabled` | `+0xF5` |
| field extent / padded object size | `0xF6` / `0xF8` |

Each tag-level record uses the authenticated upstream field order:

| Record field | Record offset |
|---|---:|
| `level` | `+0x00` |
| `tag[31]` | `+0x01...+0x1F` |
| `tag_use_flag` | `+0x20` |

The boot line buffer occupies `[0x200258D0,0x20025CD0)`. The time-string
buffer begins at `0x20026F18` and is passed to `snprintf` with a 28-byte
capacity. The six initialized level-string pointers are read through the
RAM table at `0x2000031C`; the six color-string pointers are read through
the RAM table at `0x20000334`.

These offsets and sizes are identical to Apollo main. Only the absolute RAM
placement differs.

## Recovered configuration and defaults

The linked core proves the following G2 boot configuration.

| Item | Boot value |
|---|---|
| output support | enabled |
| compiled maximum output level | `ELOG_LVL_VERBOSE` (`5`) |
| assertions | enabled |
| line buffer | 1,024 bytes |
| line-number buffer | 5 characters plus terminator storage |
| maximum filter tag | 30 characters plus terminator |
| maximum filter keyword | 16 characters plus terminator |
| tag-level slots | 5 |
| newline | `"\n"` |
| text colors | enabled |
| colors, assert through verbose | `35;22m`, `31;22m`, `33;22m`, `36;22m`, `32;22m`, `34;22m` |
| compiled directory support | enabled |
| compiled function support | enabled |
| compiled line-number support | enabled |

`elog_init` at `0x0041733C`:

1. returns immediately when `init_ok == 1`;
2. initializes the boot port;
3. enables output locking;
4. clears both lock-transition flags;
5. enables text color;
6. sets the global filter to verbose;
7. clears all five tag-level records and makes each silent/inactive;
8. sets `init_ok`.

The boot configuration routine at `[0x0043194C,0x0043198A)` then applies:

| Level | Mask | Enabled fields |
|---|---:|---|
| assert (`0`) | `0xFF` | level, tag, time, process, thread, directory, function, line |
| error through verbose (`1...5`) | `0xD7` | level, tag, time, thread, function, line |

`0xD7` deliberately omits process (`0x08`) and directory/file (`0x20`).
It includes function (`0x40`) and thread (`0x10`), unlike Apollo main's
recovered normal mask `0x87`.

The setup routine does not call `elog_set_filter_lvl` after initialization.
The effective boot filter therefore remains verbose. Both the global tag and
keyword filters remain empty BSS strings. The setup calls `elog_start`,
which enables output and emits the initialization message. Its resulting
ordinary steady state is:

```text
filter.level                         = 5
filter.tag                           = ""
filter.keyword                       = ""
five tag-level use flags             = false
five tag-level levels                = 0 (silent)
init_ok                              = true
output_enabled                       = true
output_lock_enabled                  = true
output_is_locked_before_enable       = false
output_is_locked_before_disable      = false
text_color_enabled                   = true
```

The retained output call explicitly supplies a third `level` argument to a
G2-local sink, but the boot `elog_start` has no upstream
`elog_async_enabled(true)` call and no upstream async implementation is
linked. It is therefore safer to describe this as a downstream three-argument
submission adaptation than to infer an unmodified upstream
`ELOG_ASYNC_OUTPUT_ENABLE` build.

## Core behavior

The boot `elog_output` is the same bounded EasyLogger source flow as Apollo
main:

- it reads `IPSR` immediately after the prologue and silently returns from
  exception/interrupt context;
- in thread mode it asserts `level <= ELOG_LVL_VERBOSE`;
- it applies output-enabled, global-level, tag-level, tag-substring, and
  post-format keyword gates;
- it holds the output lock across shared-buffer formatting, keyword
  filtering, submission, and final unlock;
- it uses the same upstream format bits and six level/color strings;
- it uses a 1,024-byte buffer and reserves room for `"\x1b[0m"` plus newline;
- it calls the same bounded `elog_strcpy` source helper;
- it uses the same argument-aware file/function/line behavior introduced by
  upstream `cd93d9c`.

The boot output body has 58 direct calls. The ordered
`SITE->TARGET` tuple list, encoded as comma-separated uppercase eight-digit
hex pairs, has SHA-256
`d7db5d40f7bfb680e39c61629c52926cf4eb5cf3f6138e27053b641b95b9eede`.

| Target | Calls | Role |
|---:|---:|---|
| `0x0041560C` | 3 | stack-array zero/fill |
| `0x00415FFA` | 2 | substring filters |
| `0x00417570` | 1 | output lock |
| `0x00417592` | 2 | normal and keyword-miss unlock |
| `0x0041760A` | 1 | tag-level query |
| `0x004176CE` | 1 | no-hook assertion diagnostic recursion |
| `0x00417AD4` | 8 | format-mask query |
| `0x00417B48` | 3 | nonzero-line format helper |
| `0x00417B62` | 6 | nonnull-pointer format helper |
| `0x0041A692` | 1 | boot submission sink |
| `0x0041A6AA` | 1 | tick-count time text |
| `0x0041A6F0` | 1 | process text |
| `0x0041A6F8` | 1 | thread text |
| `0x0041AC8A` | 1 | assertion fail-stop wait wrapper |
| `0x0041B120` | 1 | tag length |
| `0x0041B158` | 23 | authenticated bounded append |
| `0x0041B218` | 1 | line-number `snprintf` |
| `0x0041B25C` | 1 | message `vsnprintf` |

## Boot port

### Initialization and lock policy

The port initializer at `0x0041A684` lazily creates a CMSIS-RTOS mutex and
always returns `ELOG_NO_ERR`. Its static mutex attributes are at
`0x00433D28`:

| Attribute | Value |
|---|---:|
| name | `elogMutex` at `0x00433F50` |
| attribute bits | `0` (normal mutex) |
| static control block | `0x20026CB0` |
| control-block size | `0x50` |

The mutex handle is stored at `0x200270E8`. Creation failure leaves the
handle null but does not make `elog_init` fail.

The lower lock routine at `0x0041A65C`:

- skips acquisition when the handle is null;
- otherwise acquires the mutex with timeout `1000`;
- ignores the acquire result.

The lower unlock routine at `0x0041A672` skips release when the handle is
null and otherwise releases the mutex, also ignoring the result.
`elog_output_lock` and `elog_output_unlock` preserve upstream's two
transition flags around these port calls. `elog_output_lock_enabled` can
therefore reconcile a lock state across temporary lock disable/enable just
as in upstream and Apollo main.

Apollo main has the same normal-mutex, timeout-1000, ignored-result policy.
Its absolute object, handle, CMSIS wrapper, and port addresses differ.

### Time, process, and thread strings

`elog_port_get_time` calls the boot tick-count provider, formats the result
as `"%d"` into the 28-byte buffer at `0x20026F18`, and returns that buffer.
Apollo main instead formats seven calendar/time and tick fields.

Both `elog_port_get_p_info` and `elog_port_get_t_info` call one shared boot
helper. When the RTOS state permits, it returns the current task name;
otherwise it returns `"unknown"` at `0x00434084`. Process and thread text
are consequently identical when both format bits are enabled. The normal
boot mask enables thread but disables process.

### Output sink

The boot sink closure is:

```text
elog_output(buffer, length, level)
    -> 0x0041A692
    -> 0x0041B854
       discard level
       downstream_write(channel = 1, buffer, length)
    -> 0x0041F918
```

`0x0041A692` is an eight-byte forwarding wrapper. At `0x0041B854`, the
incoming buffer moves from `r0` to `r1`, length moves from `r1` to `r2`,
and `r0` becomes channel `1`. The incoming level in `r2` is overwritten and
never used.

The channel transport at `[0x0041F918,0x0041F9B6)`:

1. rejects channel indices outside `0...3`;
2. rejects an uninitialized channel;
3. builds a 56-byte stack transfer descriptor containing buffer and length;
4. starts the lower transfer through `0x004233E8`;
5. polls the channel completion byte for up to 1,000 iterations;
6. waits ten units through `0x0041F9E6` between polls;
7. reports success only when the lower start returned zero.

The EasyLogger wrapper does not inspect that result. This transport neither
queues a 255-byte EasyLogger record nor preserves level metadata. Apollo main
does both: it sends `(buffer, length, metadata=0, level)` to its record
builder and raises event bit one.

## Assertions

The default assertion hook is the zero-initialized function pointer at
`0x200270E4`. Every retained EasyLogger assertion follows the same policy:

1. if the hook is nonnull, call
   `hook(expression, function, downstream_line)` and continue if it returns;
2. otherwise recursively call `elog_output` at assert level with
   `"(%s) has assert failed at %s:%ld."`;
3. call the fail-stop wait wrapper at `0x0041AC8A`;
4. loop forever.

The wait wrapper is eight bytes and has SHA-256
`5f9a6b47f08eb58759df839c742eeae1a6c396a5731d2aa80cb635be744cc64f`,
exactly matching Apollo main's wrapper bytes.

| Function | Expression | Downstream line |
|---|---|---:|
| `elog_set_output_enabled` | `(enabled == false) || (enabled == true)` | 278 |
| `elog_set_text_color_enabled` | `(enabled == false) || (enabled == true)` | 290 |
| `elog_set_fmt` | `level <= ELOG_LVL_VERBOSE` | 321 |
| `elog_set_filter_lvl` | `level <= ELOG_LVL_VERBOSE` | 347 |
| `elog_get_filter_tag_lvl` | `tag != ((void *)0)` | 481 |
| `elog_output` | `level <= ELOG_LVL_VERBOSE` | 572 |
| `get_fmt_enabled` | `level <= ELOG_LVL_VERBOSE` | 743 |
| `elog_strcpy` | upstream null-destination/source checks | 44 and 45 |

The boot assertion identities, lines, and continue-after-returning-hook
semantics match Apollo main and the authenticated upstream core. The G2
interrupt-context early return remains a downstream modification: it occurs
before assertion or argument dereference and is absent upstream.

## Complete retained boundaries and hashes

Ends are exclusive. Caller counts include direct whole-image `BL` sites to
the exact entry.

| Function | Range | Bytes | SHA-256 | Direct callers |
|---|---:|---:|---|---:|
| `elog_init` | `[0x0041733C,0x00417392)` | 86 | `3d6da1a7bb77911823a8999d787e232aaf5134a06301a6566a1c6988f91ed13e` | 1 |
| `elog_start` | `[0x00417392,0x004173CA)` | 56 | `68431e6fc495d8a35461500b6fdea63ecd39f98410a5a58a84fd6b988117604f` | 1 |
| `elog_set_output_enabled` | `[0x004173CA,0x00417438)` | 110 | `337a2732ea67532c2f52e83af3905e873d942b8fe36058f2f3c2b34f00a734d8` | 1 |
| `elog_set_text_color_enabled` | `[0x00417438,0x004174A6)` | 110 | `63e8094bcde827d2a3fd91cf64ec9c7b7c198ef11d3a6265719158f5b580e40c` | 1 |
| `elog_set_fmt` | `[0x004174A6,0x00417510)` | 106 | `258488405b3f448615643b67d5d2a27c809ce9bf52d2f1d13368403bbd5ca917` | 6 |
| `elog_set_filter_lvl` | `[0x00417510,0x00417570)` | 96 | `35b3f3bb54bfab028302318966661d8e748ca1c27f46e3a164a105d105d8d205` | 1 |
| `elog_output_lock` | `[0x00417570,0x00417592)` | 34 | `392ca1002e32da529cfb530d17637089baa8e00c9b50bff1e6aca25def797668` | 2 |
| `elog_output_unlock` | `[0x00417592,0x004175B4)` | 34 | `8d48f5842013881552033a3a4870589623c0f4fde269e0f567aec8c80e8e6ef5` | 3 |
| private tag-level reset | `[0x004175B4,0x0041760A)` | 86 | `cc5f546238ab928d2487cf2fb564adbbfc0ba3d8bdda72d224ff74a888b68224` | 1 |
| `elog_get_filter_tag_lvl` | `[0x0041760A,0x004176CE)` | 196 | `fffecb363fe65341db8ea23a28a506f03d5dd06d8b2829cf0f3ea4fd9b62e709` | 1 |
| `elog_output` | `[0x004176CE,0x00417AD0)` | 1,026 | `97645514643e4e4e3e5e04a8d14a08c5c714df3cfd64e764b7b73ab95860e021` | 115 |
| `get_fmt_enabled` | `[0x00417AD4,0x00417B3E)` | 106 | `eb04732c56e958be0b715c98f23dafc9aa9c29a6321a1b58297529e39eb3eb5a` | 10 |
| line-aware format helper | `[0x00417B48,0x00417B62)` | 26 | `95bba933ae9e65022ef0ff0daa76324678aa539c2ba79435b80181ce34a23db7` | 3 |
| pointer-aware format helper | `[0x00417B62,0x00417B7C)` | 26 | `3af2631ad7a44be557a9454da2df68862b6458bf2359f58d41c3d6d2ff86c8a2` | 6 |
| `elog_output_lock_enabled` | `[0x00417B7C,0x00417BB8)` | 60 | `61ab2f07f409287f6b8773559ad3223a72a9550cd9fc25dadfc7cb3a9ddc1c32` | 1 |
| mutex create helper | `[0x0041A648,0x0041A65C)` | 20 | `88fc734f91a9595fff96effb708c9b8e593b6bca403cf1590ec754ecb851c862` | 1 |
| mutex acquire helper | `[0x0041A65C,0x0041A672)` | 22 | `169a7ddcc907f767865c49a201f325c33770f7731e8359424abbe08bc380f34f` | 1 |
| mutex release helper | `[0x0041A672,0x0041A684)` | 18 | `0538c89be6a767f59d04ff9ba0d37c6f8e98a3fffa5d35457104a277590e055a` | 1 |
| `elog_port_init` | `[0x0041A684,0x0041A692)` | 14 | `f0eefbc1594e2e86a7268d2ec186bf619fe4651b65e54a3d86b6b2c0bc3e1a30` | 1 |
| boot submission wrapper | `[0x0041A692,0x0041A69A)` | 8 | `ececfe97080e5d40476e61bb0fa28b31ff6460285d33e9433047d4359d34e408` | 1 |
| `elog_port_output_lock` | `[0x0041A69A,0x0041A6A2)` | 8 | `f4f02ad3353ef68eadb1408b05bd4b2b89440a4f4656dd1075ba92268d770e35` | 2 |
| `elog_port_output_unlock` | `[0x0041A6A2,0x0041A6AA)` | 8 | `a56bdb9407dda49c85a75ce1e3c34b88b0744e3797b68725874d0e3df10eee3e` | 2 |
| `elog_port_get_time` | `[0x0041A6AA,0x0041A6C2)` | 24 | `d4721c085671021321dfc612a27220d9f5e2722f2b1c33c4bb479fbbada6b193` | 1 |
| shared task-name helper | `[0x0041A6C2,0x0041A6DA)` | 24 | `6369de337442570729fecc8933cc1d333aecd1a4356f2eadde26f623342e1472` | 2 |
| `elog_port_get_p_info` | `[0x0041A6F0,0x0041A6F8)` | 8 | `3e76180d81350b11618fc002f8cd142d0ae1c44e2f587c61c2edf0342a72d65f` | 1 |
| `elog_port_get_t_info` | `[0x0041A6F8,0x0041A700)` | 8 | `981e6fe98ffa9b8a2e314502aafc3c1382cec761a7874d200491addc71da6244` | 1 |
| `elog_strcpy` | `[0x0041B158,0x0041B1FA)` | 162 | `9708f61ea38bbac62f5542fdd2701a950ba1bde9fd480c5baf7cb0be6a8461b5` | 23 |
| level-dropping driver wrapper | `[0x0041B854,0x0041B862)` | 14 | `d46fae4c767497230f0f9b6c050033b824887d7e59dd06e893eee604bbb9c59d` | 1 |
| downstream channel transport | `[0x0041F918,0x0041F9B6)` | 158 | `363f18ceab0127d6da1b90de353495e370f50bce9631ee5ffbc83c2d725a2a95` | 1 |
| boot EasyLogger setup | `[0x0043194C,0x0043198A)` | 62 | `3d057acab6aa34a7443a18c5f1a7a63133a12944656603585df0f08982d41316` | stored initializer pointer |

The contiguous core span `[0x0041733C,0x00417BB8)` is 2,172 bytes
including its small punctuation/literal gaps and has SHA-256
`89263d626619d8348f7e9a1f47e5664acb13d812bc039565b380858568f7d7d1`.

## Source-replacement tranche: helper quartet

Four source-equivalent helpers form one closed, atomic replacement tranche:
the authenticated bounded-copy helper, the format-bit predicate, and its
line-aware and pointer-aware argument predicates. Their noncontiguous stock
bodies total 320 bytes and, concatenated in the order below, have SHA-256
`472bbec3de86da7dc9b322d6c1a52a8db714397786b24a556c0171d7a650c250`.

| Function | Stock range | Bytes | SHA-256 | Direct `BL` callers | Packed caller-address SHA-256 |
|---|---:|---:|---|---:|---|
| `get_fmt_enabled` | `[0x00417AD4,0x00417B3E)` | 106 | `eb04732c56e958be0b715c98f23dafc9aa9c29a6321a1b58297529e39eb3eb5a` | 10 | `0ace983e92fb8734b4dc3ea0aaafde1187704f013b42c8234cb878332c8c1d66` |
| line-aware predicate | `[0x00417B48,0x00417B62)` | 26 | `95bba933ae9e65022ef0ff0daa76324678aa539c2ba79435b80181ce34a23db7` | 3 | `77a0d6e0c29d5b8f913ca98fbe13a6743e3d59d566fdf2f5e1341d2c32f38ca9` |
| pointer-aware predicate | `[0x00417B62,0x00417B7C)` | 26 | `3af2631ad7a44be557a9454da2df68862b6458bf2359f58d41c3d6d2ff86c8a2` | 6 | `fa60b266620a201d141332a4a84ff23da9e1b54d38f3c60bc85ddca9d0fcc2b3` |
| `elog_strcpy` | `[0x0041B158,0x0041B1FA)` | 162 | `9708f61ea38bbac62f5542fdd2701a950ba1bde9fd480c5baf7cb0be6a8461b5` | 23 | `35c930490c7eae4ba9b6aa797fdfd34c0594ecbc282ccdee4ebb5f7526ff4804` |

The caller digests above hash the ordered little-endian 32-bit call-site
addresses. Complete boot-image scans establish:

- no `B.W` targets any quartet entry;
- no external wide or narrow branch targets an interior instruction;
- no external narrow branch targets an entry;
- no stored even or odd Thumb pointer names an entry or interior address.

The stock boundary neighbors are pinned independently from the bodies:

| Function | Four bytes immediately before | First eight bytes after |
|---|---|---|
| `get_fmt_enabled` | `1b5b0000` | `0000200000005b00` |
| line-aware predicate | `5b000000` | `80b5002a06d0c0b2` |
| pointer-aware predicate | `c0b202bd` | `80b5134981f8f200` |
| `elog_strcpy` | `70470000` | `0000647374007372` |

The two argument predicates close over the source predicate directly:
stock calls at `0x00417B50` and `0x00417B6A` both target
`get_fmt_enabled` at `0x00417AD4`. The source target must likewise emit
direct relocations to its source-owned predicate, not preserve calls to the
stock body.

The only retained binary seams needed by these four source bodies are the
boot logger object at `0x20026700`, the assertion hook at `0x200270E4`,
the assertion diagnostic entry at `0x004176CE`, and the fail-stop wait
wrapper at `0x0041AC8A`. `get_fmt_enabled` reports downstream line 743;
the two `elog_strcpy` null checks report lines 44 and 45. The source profile
therefore fixes 32-bit `size_t`, all six levels, a 1,024-byte line buffer,
and the corrected 33-byte tag-level record layout (`level +0`, `tag +1`,
`tag_use_flag +0x20`).

The reviewed boot target profile is `arm-none-eabi`, Cortex-M55, Thumb,
`-Oz`, freestanding, FROPI, function/data sections, no builtins, no jump
tables, no unaligned access, and no unwind tables. With the explicit
bootloader profile and one-leaf build guard, it emits:

| Shared source artifact | Bytes | SHA-256 |
|---|---:|---|
| `runtime_easylogger_helpers.c` | 4,975 | `8f2850f789fba3b08bdc3e1fa8f3a4646aaef7e4b16862f3be53478071aa22b5` |
| `runtime_easylogger_helpers.h` | 6,505 | `f3a7e9bce0f136a2ff4a76929c317aef7bbc7c29dfc60d58311d94e58f6e2393` |

| Source leaf | Bytes | SHA-256 | Thumb `CALL` relocations |
|---|---:|---|---|
| `open_cfw_easylogger_get_fmt_enabled` | 38 | `563bc931557c5aae324ecfb98dbc4aa2342c43c90163d462bea5e215c0de6390` | `+0x0E` assertion adapter; `+0x12` logger getter |
| `open_cfw_easylogger_get_fmt_used_and_enabled_u32` | 20 | `3e6f46ecf152d9192ec638cd0eafa92f9c8adcfe7b36e8581add1a865234629a` | `+0x04` source `get_fmt_enabled` |
| `open_cfw_easylogger_get_fmt_used_and_enabled_ptr` | 20 | `3e6f46ecf152d9192ec638cd0eafa92f9c8adcfe7b36e8581add1a865234629a` | `+0x04` source `get_fmt_enabled` |
| `open_cfw_easylogger_strcpy` | 52 | `1fac8de3a83876460e17014da0f845384b253a88d5b79e25f6e5e838e6f46013` | `+0x0C`, `+0x14` assertion adapter |

The canonical target-leaf concatenation in table order is 130 bytes with
SHA-256
`a806e83b595bfa8d37cf27c095b94d6ddfcf359c2c53dad9ab29f3dd2e7c083b`.
It has no writable allocated section and no data or read-only-data
relocation.

### Production integration result

The bootloader now replaces all four authenticated stock spans with
non-linking Thumb redirects and NOP fill. Two alignment bytes at
`[0x004345D6,0x004345D8)` precede the source logger-object provider,
assertion-policy provider, and helper leaves through `0x004346E6`. The
appended increment contains 270 source bytes and two generated alignment
bytes. The official assertion strings, hook global at `0x200270E4`,
`elog_output` at `0x004176CE`, and wait wrapper at `0x0041AC8A` remain
explicit binary seams.

The 622-byte boot overlay hashes to
`fc02cf66854adace4d213e08764e435e27c8c2bc7cc4f7caac6ff286f3adf813`;
the 149,222-byte provider hashes to
`b4a5b0f2028842a2d6fde9424fff05fac2db3bf0e26e7f01d16a990e67ed9052`.
The matching Apollo-main overlay/component pins are 115,910 bytes/
`e59da6e6753c0c8a9fa73bad8cd555313d0e2ae6ed95006c818e6697e4fbe32d`
and 3,639,306 bytes/
`00f5f11dd18c13c56137d0f527da3ecd8ae850a9ae35dc96d671a4b998d79b61`.

The complete 4,417,760-byte package hashes to
`fb662322f26e06aa04eb1d3f55f8c8f18606e510fac9c35885de3e4f92864c4d`.
Its 592,687-byte flash plan hashes to
`c06c84e277bad2160479e0ec1f7a626abb804574f42ecee0709f0978657cd1b3`
and records 822 placed, two unresolved, five container-only, and six
protected regions.

## Caller topology

The boot setup routine's stored Thumb pointer is:

```text
0x00433448 -> 0x0043194D
```

It calls, in order:

```text
0x0043194E -> elog_init
0x00431956 -> elog_set_fmt(assert, 0xFF)
0x0043195E -> elog_set_fmt(error, 0xD7)
0x00431966 -> elog_set_fmt(warn, 0xD7)
0x0043196E -> elog_set_fmt(info, 0xD7)
0x00431976 -> elog_set_fmt(debug, 0xD7)
0x0043197E -> elog_set_fmt(verbose, 0xD7)
0x00431982 -> elog_start
```

The 115 direct `elog_output` caller addresses, encoded as comma-separated
uppercase eight-digit hex values without `0x`, have aggregate SHA-256
`47456628984211dc924d9cd6fa0c011711b7195537c8e3f0729a2894cdbed481`.
This set includes seven assertion diagnostic paths within the retained core,
the initialization message, and normal boot/application diagnostics.

A halfword-aligned scan of the complete boot image found:

- no direct `B.W` call to a retained EasyLogger entry;
- no direct external `BL` or `B.W` target inside, but not at the start of,
  a retained core or port function;
- no stored odd Thumb pointer to any retained core or port entry or interior;
- one stored pointer to the separate boot setup routine, as shown above.

## Differences from Apollo main and pristine upstream

| Area | Bootloader | Apollo main | Pristine upstream |
|---|---|---|---|
| logger object | `0x20026700` | `0x20070BE8` | application-defined |
| line buffer | `0x200258D0` | `0x2006BD30` | application-defined |
| normal mask | `0xD7` | `0x87` | application-defined |
| steady filter | verbose | info after app setup | initialized verbose |
| time text | decimal RTOS tick | calendar/time tuple plus tick | port-defined |
| sink | channel-1 driver transfer | 255-byte queue record plus event bit | async `(level, buffer, size)` or port output |
| level metadata | discarded | preserved | preserved by async API |
| `elog_start` | output enable plus version log | downstream async-state logic plus version log | calls `elog_async_enabled(true)` when configured |
| `elog_stop` | not retained | retained | upstream source present |
| interrupt output | silently suppressed | silently suppressed | no `IPSR` gate |
| mutex | normal static CB, timeout 1000 | same policy, different addresses | port-defined |

The exact line-aware and pointer-aware format helpers are byte-identical
between boot and Apollo main. The larger core functions differ at the byte
level because absolute literals and call displacements differ, while their
ordinary formatting flow remains source-equivalent.

For openCFW, the upstream core can therefore be reused for a future boot
replacement, but the following must remain explicit boot adaptations:

1. the early `IPSR` no-output gate;
2. the recovered object and buffer addresses or source-owned equivalents;
3. the `0xFF`/`0xD7` application format policy;
4. verbose steady filtering;
5. tick-count time formatting;
6. the CMSIS mutex policy;
7. the level-dropping channel-1 submission contract.

Substituting Apollo main's async queue or pristine upstream `elog_async.c`
would change observable boot behavior and should not be treated as an
equivalent library replacement.

## Reproduction and validation

The addresses and hashes in this report were recalculated directly from the
official boot image. Capstone was used in Thumb/M-class mode for function
and call recovery. Whole-image direct-call scans used the project's
`tools/apollo_overlay.py` Thumb branch decoder at every halfword-aligned
offset; stored-pointer scans examined every four-byte little-endian window.

The authenticated vendor snapshot is checked offline with:

```sh
python3 third_party/easylogger/verify_snapshot.py
```

No device, serial link, SWD interface, flash writer, or hardware execution
was used.
