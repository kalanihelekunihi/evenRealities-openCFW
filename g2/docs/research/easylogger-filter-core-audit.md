# EasyLogger tag-level filter-core audit

## Result

The complete installed-image range
`[0x0043D45A, 0x0043D574)` contains exactly two EasyLogger functions:

1. the private five-slot `elog_set_filter_tag_lvl_default`;
2. the public `elog_get_filter_tag_lvl`.

Both functions are source-equivalent to the authenticated EasyLogger
`elog.c` snapshot at commit
`a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24` under the already recovered G2
configuration. No boundary expansion is required. The preceding
`elog_output_unlock` ends at `0x0043D45A`, and the next function,
`elog_output`, begins at `0x0043D574`.

The recommended atomic increment is one new MIT-licensed source translation
unit containing both functions plus local, source-owned 31-byte clear and
30-byte equality helpers. Redirect both stock entries together. Call the
already integrated source `open_cfw_easylogger_output_lock` and
`open_cfw_easylogger_output_unlock` symbols directly. This removes the two
stock C-library calls from the boundary and does **not** pull the variadic
`elog_output` core into the ordinary valid-input path.

The two replaced stock bodies total 282 bytes. This audit did not modify
firmware, manifests, overlay sources, or hardware.

## Evidence corpus

All installed-image addresses below use an exclusive end.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Official `ota_s200_firmware_ota.bin` wrapper | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Installed payload after the 32-byte preamble, based at `0x00438000` | 3,523,364 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| Vendored `third_party/easylogger/src/elog.c` | 28,740 | `d4291ab1314a34cf940c8e0d7246e05570f8d32ae0704b498cf6fbacab76acb1` |
| Vendored `third_party/easylogger/inc/elog.h` | 10,428 | `2890b272a01820a6336da544c056e7735b88330cd91a5092fb83a5538de11f48` |
| Vendored `third_party/easylogger/inc/elog_cfg.h` | 3,995 | `bccd34ca41c36ce8201d78fd2b844b071bad25bfbac452d02764617ca4ed3073` |

`third_party/easylogger/verify_snapshot.py` passes offline. The selected
snapshot is byte-identical to the official upstream source and is the latest
member of the three-commit source-equivalent set established by
`easylogger-version-audit.md`.

## Exact stock functions

| Function identity | Stock range | Bytes | Stock SHA-256 | Sole direct caller |
|---|---:|---:|---|---:|
| private `elog_set_filter_tag_lvl_default` | `[0x0043D45A, 0x0043D4B0)` | 86 | `7f77794d5e81ef5fe375f98e37f63520f20f4538f7187ca90036769087582c36` | `0x0043D18A`, inside `elog_init` |
| `elog_get_filter_tag_lvl` | `[0x0043D4B0, 0x0043D574)` | 196 | `53770f37005d894be731529ef8bdcaa2588f2f7917239b3feb18bb59cf5a9c17` | `0x0043D600`, inside `elog_output` |
| Combined redirect interval | `[0x0043D45A, 0x0043D574)` | 282 | `f3a68b77d6d89e7431c926aafef7466b190aeacd545b3cfe522206d13283b043` | two entry calls above |

The neighboring caller bodies are independently pinned:

| Caller | Range | Bytes | SHA-256 |
|---|---:|---:|---|
| `elog_init` | `[0x0043D144, 0x0043D19A)` | 86 | `9f7e3c6a7931ccdf103e2065ebbeccb311f2c90e770867fbefd0affe7c5171c9` |
| `elog_output` | `[0x0043D574, 0x0043D976)` | 1,026 | `d7c5fd89997fc677ecce543af7c33cd08614b832a47602f1fd895bb7ab45f90c` |

The G2 linker removed the unreferenced public
`elog_set_filter_tag_lvl` body. Its absence does not create a hole in this
range: the private default initializer ends immediately where the retained
getter begins.

## Recovered behavior

### Private default initializer

The body iterates over exactly five records. For every record it:

- clears all 31 bytes of `tag`;
- writes level zero, `ELOG_FILTER_LVL_SILENT`;
- writes `tag_use_flag = false`.

It does not check `init_ok` and does not acquire the output lock. This is the
upstream contract: `elog_init` calls it at `0x0043D18A` before setting
`init_ok` at logger offset `+0xF0`.

The stock implementation calls the ARM memory-fill helper at
`0x0043C0E4`. Its arguments prove a 31-byte zero fill. The recommended
source implementation should use a local byte loop instead, so the new
boundary has no opaque memory-fill dependency.

### Tag-level getter

The getter preserves the following upstream ordering:

1. assert that `tag` is non-null;
2. initialize the return level to five, `ELOG_FILTER_LVL_ALL`;
3. if `init_ok` is false, return five without locking;
4. lock output;
5. scan five records in ascending index order;
6. consider only records whose use flag is exactly one;
7. compare at most 30 tag bytes;
8. return the first matching record's level, or five if none match;
9. unlock output exactly once.

The assertion carries downstream source line 481, expression
`tag != ((void *)0)`, and function name `elog_get_filter_tag_lvl`. If the
assert hook returns, execution continues, exactly as in upstream. A null tag
with `init_ok == false` is therefore safe after a returning hook; a null tag
with `init_ok == true` retains upstream undefined behavior when comparison
begins.

The stock body calls `strncmp` at `0x0044B610` with a count of 30. Only
equality is observed. A source-owned helper can reproduce that predicate by
comparing unsigned bytes in order, returning equal on a shared terminator or
after 30 equal bytes. In particular, byte 30 of each 31-byte tag array is not
part of this comparison.

## G2 configuration and object ABI

The logger object remains the existing object at `0x20070BE8`; no new state
or heap allocation is needed.

| Item | Recovered G2 value |
|---|---:|
| `ELOG_FILTER_TAG_MAX_LEN` | 30 |
| Stored tag bytes per tag-level record | 31 |
| `ELOG_FILTER_TAG_LVL_MAX_NUM` | 5 |
| `ELOG_FILTER_LVL_SILENT` | 0 |
| `ELOG_FILTER_LVL_ALL` | 5 |
| Tag-level record size | `0x21` |
| `ElogFilter` size | `0xD6` |
| `EasyLogger.init_ok` | `+0xF0` |
| Padded `EasyLogger` object size | `0xF8` |

The five tag-level records begin at logger offset `+0x31`. Record `i` uses:

| Field | Logger-relative offset |
|---|---:|
| record base / level | `0x31 + 0x21 * i` |
| `tag[31]` | `0x32 + 0x21 * i` |
| `tag_use_flag` | `0x51 + 0x21 * i` |

Thus the complete record array occupies `+0x31...+0xD5`, inclusive. The
recommended candidate must carry compile-time assertions for these offsets,
record/filter/object sizes, and the five-slot count.

## Calls and retained seams

The stock functions contain these non-local calls:

| Call site | Target | Meaning | Replacement policy |
|---:|---:|---|---|
| `0x0043D47C` | `0x0043C0E4` | ARM 31-byte zero fill | replace with local source helper |
| `0x0043D4E8` | `0x0043D574` | assertion output through `elog_output` | retain only for invalid input with no hook |
| `0x0043D4EC` | `0x0044B0AE` | assertion fail-stop wait wrapper | retain only for invalid input with no hook |
| `0x0043D500` | hook loaded from `0x2007456C` | application assertion callback | retain global hook seam |
| `0x0043D518` | `0x0043D416` | `elog_output_lock` | call integrated source symbol directly |
| `0x0043D552` | `0x0044B610` | 30-byte `strncmp` | replace with local source equality helper |
| `0x0043D568` | `0x0043D438` | `elog_output_unlock` | call integrated source symbol directly |

Relevant stock seam pins are:

| Seam | Range | Bytes | SHA-256 |
|---|---:|---:|---|
| ARM memory fill, not retained by candidate | `[0x0043C0E4,0x0043C14A)` | 102 | `34da1a99d5cb56ca41cfaff98190ced2a7767f53cd95c53c504009566e9ca10a` |
| `strncmp`, not retained by candidate | `[0x0044B610,0x0044B63A)` | 42 | `54f728bd5a2e5182930c90a30b127c9f6690dbdfbc727e781bf4ee3a7cbab045` |
| Assertion `elog_output` | `[0x0043D574,0x0043D976)` | 1,026 | `d7c5fd89997fc677ecce543af7c33cd08614b832a47602f1fd895bb7ab45f90c` |
| Assertion wait wrapper | `[0x0044B0AE,0x0044B0B6)` | 8 | `5f9a6b47f08eb58759df839c742eeae1a6c396a5731d2aa80cb635be744cc64f` |

The retained assertion file string is at `0x006E3098`. The assertion hook
global is the 32-bit function pointer at `0x2007456C`. The valid getter path
does not call either opaque assertion function.

## Whole-image closure

An exhaustive halfword scan of the entire installed payload decoded both
Thumb `BL` and `B.W` encodings. An exhaustive byte-offset scan also checked
all possible stored odd Thumb pointers.

| Entry | Direct `BL` callers | `B.W` callers | External branches to interiors | Stored entry pointers | Stored interior pointers |
|---:|---|---|---|---|---|
| `0x0043D45A` | `0x0043D18A` | none | none | none | none |
| `0x0043D4B0` | `0x0043D600` | none | none | none | none |

All conditional and unconditional interior branches originate inside their
own function. Entry redirects are therefore closed: neither function needs
an interior trampoline, caller-site rewrite, or pointer-table relocation.

## Recommended atomic redirect set

Use a new source file named
`components/apollo_main/core_overlay/runtime_easylogger_filter_core.c` with
these exported symbols:

```text
open_cfw_easylogger_filter_tag_level_default
open_cfw_easylogger_get_filter_tag_level
```

The exact fail-closed patch records are:

```json
[
  {
    "name": "replace_easylogger_filter_tag_level_default",
    "runtime_address": 4445274,
    "expected_size": 86,
    "expected_sha256": "7f77794d5e81ef5fe375f98e37f63520f20f4538f7187ca90036769087582c36",
    "branch": "b_w",
    "target_function": "open_cfw_easylogger_filter_tag_level_default"
  },
  {
    "name": "replace_easylogger_get_filter_tag_level",
    "runtime_address": 4445360,
    "expected_size": 196,
    "expected_sha256": "53770f37005d894be731529ef8bdcaa2588f2f7917239b3feb18bb59cf5a9c17",
    "branch": "b_w",
    "target_function": "open_cfw_easylogger_get_filter_tag_level"
  }
]
```

The source provenance record should be:

```json
{
  "path": "components/apollo_main/core_overlay/runtime_easylogger_filter_core.c",
  "sha256": "<SHA-256 of the reviewed implementation>",
  "license": "MIT",
  "origin": "bounded Apollo-main adaptation of the authenticated EasyLogger 2.2.99-labeled tag-level default/query boundary",
  "upstream": "https://github.com/armink/EasyLogger/blob/a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24/easylogger/src/elog.c",
  "upstream_commit": "a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24",
  "evidence": "docs/research/easylogger-filter-core-audit.md"
}
```

The SHA field is intentionally not invented before the implementation
exists. After implementation it must be replaced with the exact file hash
and pinned by tests. No explicit `overlay.json` relocation records are
needed: calls to the two existing EasyLogger lock symbols should be normal
source-to-source ELF relocations resolved by the overlay linker.

The two redirects should land in one build and one manifest-region split.
Although their preserved ABI permits independent replacement, installing
them together keeps initialization and query semantics under one source
implementation and one host oracle.

## Required implementation tests

The integration should not be accepted until all of the following are
automated:

1. Recompute the wrapper/payload hashes and both exact stock body hashes.
2. Pin the two function boundaries, sizes, patch records, B.W encodings, and
   full NOP fill after each four-byte redirect.
3. Repeat the complete BL/B.W and stored-pointer closure scan above.
4. Compile the candidate freestanding for `thumbv7em-none-eabi` with the
   overlay flags, pin its source hash, extracted function offsets/sizes/body
   hashes, and resolved source-to-source relocation count.
5. Extend the pristine vendored-source host oracle by wrapping the static
   upstream default initializer and the public getter; do not copy their
   algorithms into the oracle.
6. Prefill the complete logger object with sentinels, invoke the default
   initializer, and prove all five levels, 155 tag bytes, and five use flags
   match upstream while every byte outside `+0x31...+0xD5` is unchanged.
7. For the getter, compare candidate and oracle results plus lock/unlock
   counts for: uninitialized state, no used records, first and last record
   matches, multiple matching records, unused matching records, and no
   match.
8. Exercise bounded comparison at byte positions 0, 29, and 30; a
   difference at 29 must reject while a difference only at 30 must still
   match.
9. With a returning assertion hook and `init_ok == false`, pass a null tag
   and verify the expression, function, G2 line 481, one hook call, return
   level five, and no lock call. Verify the no-hook output/wait addresses
   statically rather than entering the fail-stop loop.
10. Assert lock occurs before the first record read and unlock occurs after
    the final comparison on every initialized path.
11. Verify the candidate introduces no memory-fill or `strncmp` stock
    address, no unresolved external symbol after overlay linking, and only
    the reviewed logger/assertion fixed-address seams.
12. Rebuild the full component and package in isolated output directories,
    verify manifest ownership splits at `0x0043D45A`, `0x0043D4B0`, and
    `0x0043D574`, run the full test suite, and prove reproducible hashes.

## Boundary left for the next increment

This audit intentionally stops before `elog_output` at `0x0043D574`. That
function is variadic, owns the shared 1,024-byte line buffer, calls the G2
downstream asynchronous transport, and depends on formatting, time/task
port functions, string helpers, tag filtering, color tables, and assertion
behavior. The two tag-level functions above are closed without it; expanding
into `elog_output` would turn a 282-byte source-equivalent increment into a
materially different transport and formatting audit.
