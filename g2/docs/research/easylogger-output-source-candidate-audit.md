# EasyLogger `elog_output` source-candidate audit

## Result

`components/shared/easylogger/runtime_easylogger_output_candidate.c` is the
complete **production source replacement** for Apollo main's EasyLogger
`elog_output` at `[0x0043D574, 0x0043D976)`. The candidate is a bounded
MIT-licensed adaptation of authenticated Armink EasyLogger commit
`a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24`; it is not a transcription of
the stock instructions and it is not an unmodified upstream transplant.

The candidate preserves both G2 deltas established by focused disassembly:

1. `IPSR != 0` returns before argument dereference, state access, assertion,
   lock, buffer, formatter, port, or sink activity; and
2. the completed record is submitted through the distinct G2 ABI
   `(buffer, length, level)`, not upstream's `(level, buffer, length)` ABI.

The complete thread-mode formatting path is closed over the six recovered
levels and colors, all eight format bits, the five tag-level slots, the
30-byte tag and 16-byte keyword limits, and the shared 1,024-byte line
buffer. Existing source-owned logger, tag-filter, lock, append, and format
predicate functions are direct link seams. G2 time/task text, assertion wait,
and IAR `snprintf`/`vsnprintf` remain explicitly pinned retained seams.

This tranche deliberately excludes `elog_hexdump`. The historical
`_candidate` filename remains stable for audit links, but the overlay now
registers the formatter, G2 submission wrapper, and stock-compatible record
builder as one strict production chain. The manifest splits all three exact
stock ranges and records their profile-specific appended closures. No hardware
was connected or changed.

## Evidence identity

All runtime ranges below use the installed Apollo-main image after the
official package's 32-byte preamble.

| Artifact | Bytes | SHA-256 |
|---|---:|---|
| Official `ota_s200_firmware_ota.bin` | 3,523,396 | `36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863` |
| Installed payload at `0x00438000` | 3,523,364 | `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701` |
| Authenticated upstream `elog.c` | 28,740 | `d4291ab1314a34cf940c8e0d7246e05570f8d32ae0704b498cf6fbacab76acb1` |
| Authenticated upstream `elog.h` | 10,428 | `2890b272a01820a6336da544c056e7735b88330cd91a5092fb83a5538de11f48` |
| Authenticated upstream `elog_cfg.h` | 3,995 | `bccd34ca41c36ce8201d78fd2b844b071bad25bfbac452d02764617ca4ed3073` |

`third_party/easylogger/verify_snapshot.py` passes offline and rechecks the
selected commit, source-equivalent commit set, MIT notice, and vendored file
hashes. The candidate retains the upstream license notice and identifies the
selected commit and `elog.c` Git blob in its source header.

## Exact stock boundary and topology

| Item | Range | Bytes | SHA-256 / result |
|---|---:|---:|---|
| `elog_output` body | `[0x0043D574,0x0043D976)` | 1,026 | `d7c5fd89997fc677ecce543af7c33cd08614b832a47602f1fd895bb7ab45f90c` |
| following alignment | `[0x0043D976,0x0043D978)` | 2 | `00 00` |
| following CSI data/pad | `[0x0043D978,0x0043D97C)` | 4 | `1B 5B 00 00` |
| exact-entry direct `BL` callers | complete image | 6,239 | first `0x0043C426`, last `0x005F9E7C` |

The ascending caller addresses, encoded as eight-digit uppercase hex and
joined by commas, hash to
`2d4e701757c3ec84ae6c6b53b2638728c3da6d6121eb95579f3b4e13843be2a2`.
A complete installed-image scan finds:

- no direct `B.W` caller to the entry;
- no external wide or narrow branch to an interior instruction; and
- no odd stored Thumb pointer to the entry or any interior byte.

One four-byte fail-closed entry redirect is therefore mechanically sufficient.
Production now writes that redirect at `0x0043D574` and deterministic NOP fill
through `0x0043D976`; the following six official bytes remain intact.

## Recovered ABI and configuration

The public entry remains the 32-bit AAPCS variadic signature:

```c
void open_cfw_easylogger_output(
    uint8_t level,
    const char *tag,
    const char *file,
    const char *function,
    long line,
    const char *format,
    ...
);
```

The candidate header fixes and statically checks the G2 object layout:

| Property | Recovered value |
|---|---:|
| logger object | `0x20070BE8`, padded size `0xF8` |
| shared line buffer | `0x2006BD30`, 1,024 bytes |
| filter level/tag/keyword offsets | `+0x00`, `+0x01`, `+0x20` |
| format-mask table | `+0xD8`, six 32-bit masks |
| output/color flags | `+0xF1`, `+0xF5` |
| tag limit | 30 plus terminator |
| keyword limit | 16 plus terminator |
| tag-level entries | five records of `0x21` bytes |
| line formatter capacity | five bytes, including terminator |
| newline | one byte, `"\n"` |

The six level strings are `A/`, `E/`, `W/`, `I/`, `D/`, and `V/`. The six
color strings are `35;22m`, `31;22m`, `33;22m`, `36;22m`, `32;22m`, and
`34;22m`. The read-only closure also contains only authenticated punctuation,
the assertion identity, and those tables; it has no writable data.

## Observable-order proof

The target body begins with this pinned instruction prefix:

```text
push.w ...
sub    sp, #0x3c
mov    r5, r2
mrs    r2, IPSR
cbz    r2, thread_mode
... return ...
```

The register save and argument-register move are prologue-only operations.
The `MRS IPSR` is the first semantic operation and the inline assembly carries
a `memory` clobber. The host test invokes the candidate with level `0xFF` and
deliberately invalid tag/file/function/format pointers for IPSR values 1, 15,
and 511. Every case records exactly one event, the IPSR read. It records zero
state, assertion, lock, buffer, formatter, port, or sink events.

In thread mode the returning assertion-hook path preserves expression
`level <= ELOG_LVL_VERBOSE`, function `elog_output`, and line 572 before the
first logger-state access. Static target closure also contains the recursive
no-hook diagnostic call and retained fail-stop wait at `0x0044B0AE`.

## Upstream differential and G2 boundary coverage

The independent oracle fixture compiles the complete authenticated vendored
`elog.c` and `elog_utils.c` directly. It substitutes only deterministic host
port text, output locking, asynchronous capture, and `snprintf`/`vsnprintf`;
the filter and formatting algorithm remains the pristine vendored code.

The focused differential compares exact output bytes, final length, level,
and lock balance for:

- all six levels and their six color prefixes;
- format masks zero, each distinct field family, and all bits;
- tags of 0, 15, 16, 30, and 31 bytes, including the exact 15-column pad;
- output-disabled, global-level, exact tag-level, substring miss, and
  substring hit gates;
- all time/process/thread combinations and custom port text;
- null and nonnull file/function fields, zero and nonzero line values, and
  five-byte line-number formatting;
- string and signed-integer variadic messages;
- formatter results 0, 1,023, 1,024, 1,025, and -1;
- color-enabled 1,024-byte final records and color-disabled 1,020-byte final
  records after the upstream four-byte suffix reservation rule;
- keyword hit/miss, including proof that `"\x1b[0m"` and newline do not match
  because filtering occurs before suffix/newline insertion; and
- lock before the first shared-buffer observation/write, unlock on keyword
  miss, sink before final unlock, and no residual lock depth.

The candidate sink captures the G2 argument order and confirms that the
submitted level is the original 8-bit level. The pristine oracle's
level-first callback is normalized only in the host fixture so byte and level
results can be compared without changing either implementation.

## Target text and read-only-data closure

Both profiles compile twice, byte-identically, with the production target
flags including Thumb v7E-M, `-O2`, freestanding mode, ROPI, function/data
sections, no builtins/jump tables/unwind tables, and warnings as errors.

| Profile | Text | Text SHA-256 | Read-only data | Read-only SHA-256 | Combined closure SHA-256 |
|---|---:|---|---:|---|---|
| Apple clang 21.0.0 | 1,614 | `479d6304345334af023d5a1ee464a88b76e05b6d93596c3addc186df516a25dc` | 164 | `22de23c10c0cef980a625e949124f33e9e7b65815986f889c6c2fb3b1e4ed6ca` | `3296e96fdbd2e5b138b9375e67b6d3cbde109d06b62a5e9d0492b317f4deb28b` |
| Homebrew clang 22.1.8 | 1,618 | `315168b42e7f58b9bc9b14a47511866f8fffa930f8eb8499631cab34d9ade958` | 164 | `22de23c10c0cef980a625e949124f33e9e7b65815986f889c6c2fb3b1e4ed6ca` | `21bb86cbf5bb77891a8063eb5111f6c202b55e4bc1416ee57974cf6a351aa918` |

Text alignment is four and read-only-data alignment is one for both. There
are 109 exact text relocations: 45 calls/self-calls and 64 authenticated
MOVW/MOVT ROPI string references. The canonical relocation-record hashes are:

| Profile | All 109 relocations | 45 call relocations |
|---|---|---|
| Apple clang | `fcc72ad8c65860433a6c57097fe08542a9ee5d042f54ff9c372e76f016fbe98a` | `e71c6b182672f1396d6897055afc5ad5107faba5a13ae5b9561f8d702f906d3c` |
| Linux clang | `c2bfd1d4a98235667cc72c12386a3c696bb3f71cf82016e801ccb36bb6e2ea4e` | `b116bc27c2abe769da9bc4e7e448c5c4b2f9a9c22f2f6ed0449fef6757072103` |

The 45 calls have the same semantic multiset on both profiles:

| Symbol | Calls | Ownership |
|---|---:|---|
| `open_cfw_easylogger_helpers_get_logger` | 1 | production source |
| `open_cfw_easylogger_get_filter_tag_level` | 1 | production source |
| `open_cfw_easylogger_output_lock` / `unlock` | 1 / 1 | production source |
| `open_cfw_easylogger_strcpy` | 22 | production source |
| three source format predicates | 8 / 6 / 3 | production source |
| `open_cfw_easylogger_output` | 1 | production self-call on no-hook assertion |
| `open_cfw_g2_easylogger_async_submit` | 1 | production G2 source wrapper |

The undefined-symbol set is exactly the nine external source symbols in that
table. There are no undefined C-library symbols, writable-data sections, local
out-of-line helper functions, or `elog_hexdump` symbol.

The retained fixed-address calls are intentionally indirect and therefore do
not appear as ELF relocations:

| Seam | Address | Reason retained |
|---|---:|---|
| assertion hook pointer | `0x2007456C` | stock application hook ABI |
| assertion wait | `0x0044B0AE` | fail-stop policy |
| time text | `0x0044AAA8` | G2 RTC/task port |
| process text | `0x0044AB14` | G2 task-name port |
| thread text | `0x0044AB1C` | G2 task-name port |
| IAR `snprintf` | `0x0044B728` | five-byte signed-line compatibility |
| IAR `vsnprintf` | `0x0044B76C` | arbitrary 6,239-caller format compatibility |

The table records canonical even code addresses. Every indirect function
pointer sets the Thumb-state low bit before `BLX` (for example the emitted
wait target is `0x0044B0AF`); the focused source gate pins all six conversions.

## Production integration and retained decisions

The production overlay registers three consecutive strict relocated leaves:

- `open_cfw_g2_easylogger_async_record_build_stock`, redirecting all 132 stock
  bytes at `[0x00448D4E,0x00448DD2)`;
- `open_cfw_g2_easylogger_async_submit`, redirecting all 24 stock bytes at
  `[0x0044AA80,0x0044AA98)`; and
- `open_cfw_easylogger_output`, redirecting all 1,026 stock bytes at
  `[0x0043D574,0x0043D976)`.

The canonical manifest splits those exact stock spans as generated entry
replacement regions and separately owns every appended text/read-only-data
span. The output relocation resolves its G2 sink to the adjacent production
submit leaf, which in turn resolves the production builder and retained CMSIS
event-set seam.

The level-aware submission and record-builder sources preserve the audited
private G2 behavior:

- `runtime_easylogger_async_submit.c` preserves `(buffer,length,level)` and
  unconditional event-bit notification;
- `runtime_easylogger_async_record_build_stock.c` preserves stock's observed
  enqueue-failure double-recycle behavior; and
- `runtime_easylogger_async_record_build_single_owner.c` uses the safer
  single-owner failure policy.

The selected production builder deliberately preserves stock's observed
enqueue-failure **double recycle**. The safer single-owner builder remains
nonproduction until concurrency and hardware-oracle evidence authorize that
behavioral change. The stock G2 entry is not reinterpreted as pristine
upstream `elog_async_output`.

Each leaf has strict relocation closure. Clang's exact selected-function
8-byte `.ARM.exidx` CANTUNWIND companion is authenticated (section type,
flags, link, alignment, bytes, and one local-section `R_ARM_PREL31` binding)
and then deliberately discarded as metadata; it is not appended as executable
closure. Personality/data/non-CANTUNWIND and cross-function companions fail
closed.

Replacing the two IAR formatters is a separate tranche. The existing
mpaland-derived source formatter is not yet proven compatible with every
format string reachable from the 6,239 official callers. This candidate keeps
that uncertainty contained behind typed seams rather than expanding its
claim.

## Verification

The focused gate is:

```sh
python3 -m unittest -v tests.test_easylogger_output_candidate
```

Results:

```text
Apple clang 21.0.0:          9/9 OK
Homebrew clang 22.1.8:       9/9 OK
official entry callers:      6,239 exact
external interior transfers: 0
stored Thumb pointers:       0
target closure relocations:  109 exact per profile
production registrations:    3
```

Canonical production artifacts are:

| Profile | Overlay bytes / SHA-256 | Component bytes / SHA-256 | Package bytes / SHA-256 |
|---|---|---|---|
| Apple clang 21.0.0 | 121,298 / `02bfc227db4ad32c51303ea0dc49f908b277b78db1f2e5d7a5108559d863b249` | 3,644,694 / `eecf209bf4df5f61252099b16fb0a17f4493ec5db3c29eb266d07e6cf64d956b` | 4,423,148 / `2b1008c2fc533f1257ee58bd6d0c08b449d2e12bc57d918f101586ba1d3e3d29` |
| exact-root Linux clang 22.1.8 | 123,170 / `36479ef84126bc0075a2bcfa93c86591376eb4f18eb32983f84865f9d51e72e9` | 3,646,566 / `43d02017caa63a2bbe96e7dda056fa61009abcdb2913a12b2298dde131eb0a9c` | 4,425,020 / `12386dc6f165053c3a308b4ec64bf2df90becf2b793a2404830a598b62b7a33d` |

Both profiles were compiled twice with byte-identical results. No device was
connected, flashed, reset, or executed; controlled hardware validation remains
future work.
