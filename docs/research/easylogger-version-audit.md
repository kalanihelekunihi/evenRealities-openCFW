# EasyLogger core revision audit

## Result

The Apollo-main EasyLogger core is source-equivalent to the official
`armink/EasyLogger` core at
[`cd93d9c768415f4b7279f2d3ef2366ce15ea087c`](https://github.com/armink/EasyLogger/commit/cd93d9c768415f4b7279f2d3ef2366ce15ea087c)
or either of the two later official master commits through the currently
vendored
[`a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`](https://github.com/armink/EasyLogger/commit/a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24).
The minimal inclusive source-equivalent set is:

1. `cd93d9c768415f4b7279f2d3ef2366ce15ea087c`, 2024-03-25
2. `34cc1717825c799979a1b4b3739be1e5668a7322`, 2024-11-30
3. `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`, 2024-12-26

The last two commits changed documentation only. At all three commits the
four relevant upstream blobs are identical:

| Upstream path | Git blob |
|---|---|
| `easylogger/src/elog.c` | `b3a00e3927edf97013ddfffeb157be5c1462a6b4` |
| `easylogger/src/elog_utils.c` | `165d855d2c8e8470b3543380ca6064c0799a8a44` |
| `easylogger/inc/elog.h` | `adde47c2df84ea40e4a876f02557c7a4801e8c03` |
| `easylogger/inc/elog_cfg.h` | `0b4481ed49de06e310e72f4ba53bd5871d0e1722` |

Consequently, the official G2 binary cannot select one exact commit from
this set. There is no binary discriminator: the later changes did not
contribute code or data. The existing `a596b264` vendor pin is therefore a
correct reproducible snapshot for the core, while `cd93d9c` is the earliest
official baseline proven by the firmware.

This is a source-equivalence result, not proof that Even built an unmodified
checkout of one of those commits. The retained path
`easylogger/src/elog_async_api.c` is downstream. It has never existed in the
official repository history inspected here and must not be attributed to
upstream EasyLogger.

## Evidence corpus and method

The primary upstream source was the official
[`armink/EasyLogger`](https://github.com/armink/EasyLogger) Git repository.
The authenticated `origin/master` observed during this audit was
`a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`. History was bounded from
`a607e1715b83d42b2d431e4e415263b7044e0ecb`, which first changed
`ELOG_SW_VERSION` to `2.2.99`, through that head.

The binary corpus was the official G2 Apollo payload:

- wrapper: `ota_s200_firmware_ota.bin`, SHA-256
  `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`
- installed image: 3,523,364 bytes at `0x00438000`, SHA-256
  `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`

The comparison used source diffs and Git blob identity rather than trying
to byte-match IAR output with another compiler. Thumb bodies were normalized
structurally: calls were identified by behavior and argument flow, literal
addresses were resolved to strings or globals, and commit discrimination
used control flow, object offsets, source-line constants, and semantic
constants. Exact stock body hashes below remain useful for detecting a
different official image.

## Commit sieve

| Earliest upstream change | Binary discriminator | G2 result |
|---|---|---|
| `bb20ae32`, 2021-04-01 | Adds `elog_stop` and its deinitialization message | Present at `0x0043D1FC` |
| `c8ee6358`, 2021-07-28 | Changes location formatting to file, then line, then function | G2 uses that order |
| `3d95192f`, 2022-06-26 | Makes the hexdump input pointer `const void *` | ABI-neutral on ARM; not independently distinguishable |
| `0869689c`, 2022-07-11 | Routes tag-level updates through conditional output locking | Not needed for the final lower bound |
| `1600a2b2`, 2022-08-30 | Enables text color during initialization | G2 calls the color setter with `true` |
| `647478e8`, 2022-12-15 | Adds the boolean assertion to `elog_set_text_color_enabled` | Assertion body and expression are present |
| `ad264f0d`, 2023-06-28 | Renames the raw API to `elog_raw_output` | No stronger retained-name discriminator was needed |
| `cd93d9c7`, 2024-03-25 | Adds argument-aware directory/function/line helpers | Both helpers and their complete call pattern are present |

The `cd93d9c` discriminator is conclusive for the official source baseline.
At `0x0043D7C6...0x0043D8DB`, `elog_output` tests the file pointer with
format bit `0x20`, the function pointer with `0x40`, and the line value with
`0x80`. The two 26-byte helpers at `0x0043D9F0` and `0x0043DA0A` each return
true only when the supplied argument is nonzero and `get_fmt_enabled`
accepts the format bit. This is the behavior introduced by `cd93d9c`; no
earlier official core in the bounded history contains those helpers.

Call sites also pass nonzero file, function, and line arguments, consistent
with `ELOG_FMT_USING_DIR`, `ELOG_FMT_USING_FUNC`, and
`ELOG_FMT_USING_LINE` all being enabled in the G2 build.

## Stock Thumb boundaries

The following boundaries are complete-function ranges in the installed
image. The displayed ends are inclusive; each hash covers
`[start, end + 1)`.

| Function | Range | Bytes | SHA-256 |
|---|---:|---:|---|
| `elog_init` | `0x0043D144...0x0043D199` | 86 | `9f7e3c6a7931ccdf103e2065ebbeccb311f2c90e770867fbefd0affe7c5171c9` |
| `elog_start` | `0x0043D19A...0x0043D1FB` | 98 | `6aa415170b0772dab28e5f76f4de5da01826d5cb7db75caddf9b04d75faaeaee` |
| `elog_stop` | `0x0043D1FC...0x0043D25F` | 100 | `fc0b96bb6e754f729d432a5304f381867c0ea5d3fca150c81d9b0e332943295c` |
| `elog_set_fmt` | `0x0043D33C...0x0043D3A5` | 106 | `819c008ba3c645a4d711ccec7eaca6cd6b573db2f27b188ae279c23f7464ea89` |
| `elog_set_filter_lvl` | `0x0043D3A6...0x0043D405` | 96 | `dc6524c43cb10777aa81332adc7b0e02b9f152afa4250077799308a1b951d06a` |
| `elog_output` | `0x0043D574...0x0043D975` | 1,026 | `d7c5fd89997fc677ecce543af7c33cd08614b832a47602f1fd895bb7ab45f90c` |
| `get_fmt_enabled` | `0x0043D97C...0x0043D9E5` | 106 | `d0a18c1e6bc1a42e8a91b37c891aaf3425b98f6bc56741211512d871056b136d` |
| argument-aware `u32` helper | `0x0043D9F0...0x0043DA09` | 26 | `95bba933ae9e65022ef0ff0daa76324678aa539c2ba79435b80181ce34a23db7` |
| argument-aware pointer helper | `0x0043DA0A...0x0043DA23` | 26 | `3af2631ad7a44be557a9454da2df68862b6458bf2359f58d41c3d6d2ff86c8a2` |
| `elog_hexdump` | `0x0043DACC...0x0043DC87` | 444 | `782cb65686dde396075abdd4f7c6a168bbf64962498d97446ab35e0e1670536c` |
| `elog_strcpy` | `0x0044B668...0x0044B709` | 162 | `aac245096c55f678eec81bf04dfe27ef63fffbe1c225e8ab73fe99f6c97f1997` |

Only `elog_strcpy` from `elog_utils.c` is retained as a named assertion-
bearing utility in this image. Its assertion line constants are 44 and 45,
exactly matching the official source. `elog_utils.c` did not change anywhere
in the bounded `2.2.99` history, so it cannot narrow the three-commit result.

## Strings, lines, and object ABI

The installed image retains:

- version `2.2.99` at `0x0078D4F4`
- `elog.c` build path at `0x006E3098`
- `elog_utils.c` build path at `0x006DD234`
- `elog_start`, `elog_stop`, `elog_output`, `elog_set_fmt`,
  `elog_set_filter_lvl`, and `elog_strcpy` assertion/function strings
- both upstream start/stop message strings

The early core assertions and log calls carry downstream source-line values
247, 268, 278, 290, 321, and 347. These are consistently one line after the
corresponding current upstream lines through `elog_set_filter_lvl`.
`elog_output` and its helpers have different later drift, consistent with
minor downstream source-layout edits. Line numbers therefore corroborate
the source generation but do not justify an exact commit claim.

The global logger object starts at `0x20070BE8` and matches the 32-bit
upstream layout under the recovered G2 configuration:

- `ElogFilter` fields occupy `0xD6` bytes, followed by two alignment bytes.
- Six 32-bit format masks occupy `0xD8...0xEF`.
- `init_ok`, output-enabled, lock-enabled, two lock-transition flags, and
  text-color-enabled occupy `0xF0...0xF5`.
- The field extent is `0xF6` bytes and the 32-bit ABI `sizeof(EasyLogger)`
  is `0xF8` after tail padding.

`elog_init` checks `init_ok` at `+0xF0`, calls the G2 port initializer,
enables output locking, clears both transition flags, enables text color,
sets the filter to verbose, initializes five tag-level slots, and finally
sets `init_ok`. This matches the selected upstream core plus the recovered
G2 configuration and port.

## What would be required for an exact commit

No additional disassembly of these core functions can distinguish
`cd93d9c`, `34cc171`, and `a596b264`; their compiled inputs are identical.
An exact historical checkout requires evidence outside this stripped
firmware, such as Even's dependency lockfile, Git submodule revision, source
archive, build log, or an unstripped object carrying a source checksum or
build identifier. A firmware timestamp or release date would only bound the
choice and would not prove a commit.

For source replacement, vendor the existing pristine `a596b264` snapshot,
apply the recovered G2 configuration separately, and keep
`elog_async_api.c` behavior in explicitly downstream Apollo glue.
