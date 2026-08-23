# G2 `util_error_check.c` / Goodix application-error recovery

## Result

The retained first-party path
`D:\01_workspace\s200_ap510b_iar_git\utils\assert\util_error_check.c`
contains a copied and adapted third-party utility. Its sole linked handler and
its out-of-line 43-row error table derive from Goodix GR551x SDK 1.7.0
`components/libraries/app_error/app_error.c`.

This identification is exact at the source-file snapshot level:

- the same 43 error rows occur in the same order with byte-for-byte identical
  messages;
- both use a 512-byte automatic formatter buffer;
- both dispatch API-return errors through `"Error code 0x%04X: %s"` and
  boolean assertions through `"(%s) is not established."`;
- both walk the table with an 8-bit index and the same two-branch control flow.

The result does **not** show that the Apollo firmware links a Goodix BLE stack.
G2 otherwise uses Cordio. It shows that an older Goodix SDK diagnostic helper
was copied into an Even-local utility and retained as project source.

## Authenticated stock boundary

The complete linked object is `[0x00509B48,0x00509C1C)`, 212 bytes, SHA-256
`6fde560091bae10b4785b22bc3bd8d73e1fd98d22fded2ef31c4e7c0ede23317`:

| Region | Bytes | SHA-256 |
|---|---:|---|
| `APP_errorFaultHandler`, `[0x00509B48,0x00509BFA)` | 178 | `3c12f284fbaedb30146e40bad627cebfa6cf2a505d9e5b7fff74b13df2d9e971` |
| alignment/literal pool, `[0x00509BFA,0x00509C1C)` | 34 | `5b823b839a0db910be2f521671dba362b30fb23cd43b1c7334cc40ba58bdecf5` |

The preceding sensor-calibration pool and following independent utility body
are separately pinned, so neither is absorbed into this object. Whole-image
Thumb decoding finds 103 external direct entries to the function, eight body
calls, no stored entry pointer, no strict-interior ingress, and no unresolved
target inside the physical interval.

The source-derived table is out of line at `[0x006C8E60,0x006C8FB8)`: 43 rows,
344 bytes, SHA-256
`c7b7e16e29e0f58dad6a2c290de75e8fbe2df65545267784ad37198f82bf35e1`.
Its codes are `0x00..0x1C`, `0x80`, `0x1D`, and `0x1F..0x2A`. The next bytes
belong to unrelated data, proving that the three later Goodix rows are absent.

## Version and commit recovery

The source comparison produces a narrow and reproducible boundary:

| Snapshot | Source result | Assessment |
|---|---|---|
| GR551x SDK V1.00 | 43 rows, but a 1024-byte buffer and older message wording | authentic Goodix family ancestor, excluded |
| GR551x SDK 1.7.0 | 43 exact strings, 512-byte stack buffer, exact formatter structure | selected exact source snapshot |
| GR551x SDK 2.0.1 | 46 rows, three new repeat-CID/cache errors, static buffer | first located incompatible version |
| official GR551x SDK 2.0.2 | byte-identical to the incompatible 2.0.1 file | official upper-bound confirmation |
| official GR551x SDK 2.1.1 and other current GR5xxx SDKs | retain the 46-row form | excluded |

The selected SDK 1.7.0 file has Git blob
`d5027735dd01b0948a7315d9c595356fcb91f59b`, 7,833 bytes, SHA-256
`2f64e42b0528db162846e91179d4f5be46811b10fae16cfb80c827df7016f40d`.
The earliest located public carrier commit is
[`tiko0755/X216@854c43e0`](https://github.com/tiko0755/X216/commit/854c43e0b96a24051ffce4c06ff629255aa56c59),
dated 2023-05-31. The same blob occurs in two other preserved SDK 1.7.0 trees.

That carrier is not an official Goodix release repository. No official public
Goodix Git commit for the SDK 1.7.0 archive was found, and the G2 copy has local
edits, so neither the archive-producing Goodix commit nor Even's generating
checkout can be recovered honestly. The carrier commit is a selected source
baseline, not the historical producing commit.

The family attribution is independently authenticated by Goodix's official
[`GR551x-MicroPython` V1.00 snapshot](https://github.com/goodix-ble/GR551x-MicroPython/blob/fe8706b37dee646aaa4643edbd75364357ec1dbf/ports/gr55xx/GR551x_SDK_V1_00/components/libraries/app_error/app_error.c).
Goodix's official
[`GR551x.SDK` 2.0.2 commit](https://github.com/goodix-ble/GR551x.SDK/commit/575cedb33858d03f54049ae1d130b6253649a388)
then authenticates the first located incompatible blob in an official release.

## G2 delta and providers

G2 preserves the source semantics but makes a small local integration delta:

- `app_error_fault_handler` becomes retained diagnostic name
  `APP_errorFaultHandler`;
- the 43-row table and automatic buffer remain;
- the upstream out-of-range fallback is removed, leaving an unbounded search
  for unknown API error codes;
- Goodix `app_log_output` / `app_log_flush` are replaced by G2's EasyLogger
  integration while retaining file, function, line, and rendered message;
- IAR `memset` clears the buffer and the known mpaland formatter handles the
  two format calls.

The eight direct provider calls are one IAR `memset`, two formatter calls, and
five logging/configuration calls. These are already identified provider
families; the newly discovered opaque source definition is the Goodix handler
and its table, not those leaf calls.

## Same-commit SDK shortcut sweep

The selected GR551x SDK 1.7.0 carrier was also checked as a complete source
corpus rather than stopping at `app_error.c`. The authenticated checkout has
2,167 C/header paths and 1,681 unique source blobs. Extracting decoded C string
literals of at least 12 characters and requiring at least three distinct
firmware matches leaves only four source blobs:

| Source | Matching literals | Disposition |
|---|---:|---|
| `app_error.c` | 44 | the exact newly admitted Goodix utility |
| `cortex_backtrace.c` | 14 | shared ancestry with the already identified CmBacktrace family; not G2's exact source |
| bundled nanopb 0.4.2 `pb_decode.c` | 22 | known nanopb family, but this version is excluded by stock `pb_read` |
| bundled nanopb 0.4.2 `pb_encode.c` | 11 | non-discriminating diagnostics already covered by nanopb |

The Cortex result does not replace the CmBacktrace provenance. Stock retains
the `third_party/CmBacktrace` tool path, `cm_backtrace_fault`, and a 39-entry
post-1.4.1 / 1.4.2-lineage message table; the Goodix file instead implements
`cortex_backtrace_fault_handler` with a 36-entry older table.

The nanopb result also does not lower the version boundary. Goodix SDK 1.7.0
bundles nanopb 0.4.2, whose `pb_read` directly subtracts `count` after the
callback. Stock contains the post-callback saturating `bytes_left` clamp first
introduced in pristine nanopb 0.4.7. The shared decoder/encoder error strings
therefore identify the already known family but cannot identify the linked
version. The existing pristine candidate interval remains 0.4.7–0.4.9.1 with
0.4.9 selected as OpenCFW's maintained baseline.

This same-commit sweep finds no additional dependency family beyond the copied
Goodix application-error helper. Its reproducible classification is pinned in
`tools/manifests/goodix-gr551x-v170-firmware-string-overlap.tsv`.

## OpenCFW consequence

OpenCFW can reproduce this behavior without importing a Goodix BLE stack. A
clean implementation needs only the recovered error-info ABI, the 43-row
table, the two formatter cases, and the project logging adapter. The exact
BSD-3-Clause source oracle and provenance are recorded under
`third_party/goodix-gr551x-app-error/`.

The handler is production-routed under the reviewed Apple Clang profile. The
254-byte clean-room leaf replaces the 178-byte stock body through one guarded
`B.W` redirect, retains the authenticated 43-row table and stock strings, and
binds its eight calls to the recovered memset, formatter, and EasyLogger
providers. Unknown API-return codes use the table's `Application error.` row
after a bounded 43-entry search; this is the reviewed safety correction to the
stock unbounded walk.

Host tests cover known and unknown API-return codes plus the Boolean assertion
and asynchronous-filter paths. A freestanding Thumb build proves that the
candidate contributes exactly one global text leaf, and the analyzer pins the
candidate, relocated leaf, provider relocations, stock body, redirect, and
aggregate component/package identities. No hardware was accessed or flashed.

## Reproduction

Run:

```sh
make util-error-check-closure
make goodix-v170-source-overlap
```

The analyzer authenticates the official image, physical object, table, exact
SDK 1.7.0 source oracle, version boundary, direct/stored ingress, provider
edges, and qualified commit claim. It performs no signing, flashing, erase, or
hardware operation.

The source-overlap target additionally requires the complete selected SDK tree
at `/var/tmp/opencfw-goodix-v170/GR551x_SDK_V1.7.0`; it authenticates the Git
commit before scanning and fails closed if the full C/header census changes.
