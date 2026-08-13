# G2 tracepoint-settings linked-object recovery

Status: authenticated analysis closure; not production-routed. The complete
G2 `2.2.6.10` object retained as
`app\gui\tracepoint\tracepoint_setting.c` is bounded, recursively mapped, and
reconciled against every direct provider edge. No device or flash state was
changed.

## Result

The physical object is `[0x005EDADC,0x005EF0B0)`: 5,588 bytes, SHA-256
`2ca261b24af1f8cc441f159e55a0f74b403e1668dcd3432199f37f5b5d74f0ca`.
Twenty-one functions account for 5,100 bytes, with concatenated SHA-256
`5eb33cca3f8d78f650e6ee0ced70c57a07ddc47688e469c9fe8620694b838bc5`.
Eight pool/alignment intervals account for the remaining 488 bytes and hash to
`973cbc7de4006c3d51107eeb7b84622f649f18e02e2f0085ec51148368f4f3d0`.

Nine functions carry the retained path. Twelve adjacent functions are rooted
by direct calls, stored pointers, source order, strings, and behavior. Four of
them were missing from the baseline Ghidra function census:

- `tracepoint_delete_all_files` at `[0x005EE650,0x005EE78A)`;
- `tracepoint_handle_delete_all` at `[0x005EE7B4,0x005EE87E)`;
- `tracepoint_handle_ble_data` at `[0x005EE8BC,0x005EEB44)`;
- `tracepoint_setting_common_data_handler` at
  `[0x005EEEC4,0x005EEFAA)`.

Whole-image ingress is closed at 42 direct entries, all internal to the
object, 294 in-image body calls (42 internal and 252 external), and one stored
callback pointer from `0x006A46D4` to Thumb entry `0x005EEEC5`. There are no
strict-interior BL decodes and no direct target in the interval without a
mapped entry.

The preceding terminal-session function `[0x005ED492,0x005ED4F8)` and its
1,508-byte terminal pool are independently pinned outside the object. The
following `[0x005EF0B0,0x005EF100)` interval consists of independent FreeType
callbacks. The authoritative per-function boundaries and hashes are in
`tools/manifests/g2-tracepoint-setting-function-map.tsv`.

## Recovered behavior

This is first-party tracepoint file-list and command policy. It owns:

- the `/log/tp` directory and `tp_%u.bin` backing-file convention;
- left/right role prefixes and the `%c:%c%u` display-name convention;
- directory scanning, sequence parsing, file-size discovery, and sorted
  inventory construction;
- protobuf heartbeat, file-list, delete-file, and delete-all commands;
- request/result construction and routing to the peer/master and phone; and
- the registered common-data handler used to dispatch incoming BLE messages.

The schema descriptors and command policy are G2-specific. No public upstream
project supplies this translation unit, and the private producing source
commit remains unobservable.

## Third-party provider resolution

No third-party definition is embedded in the object. All 252 external calls
terminate at known seams:

| Provider seam | Calls | Origin/version | Commit boundary | Result |
|---|---:|---|---|---|
| diagnostics | 205 | armink EasyLogger 2.2.99 source-equivalent core plus G2 adapters | `cd93d9c768415f4b7279f2d3ef2366ce15ea087c..a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24` | admitted core; no tracepoint policy |
| memory/string/numeric primitives | 19 | proprietary IAR DLIB | EWARM 9.20+ floor; 9.60.2 leading candidate | exact release and archive options remain unobservable; no new discriminator |
| protobuf runtime | 7 | nanopb compatible with 0.4.7 through 0.4.9.1 | selected 0.4.9 snapshot `98bf4db69897b53434f3d0ba72e0a3ab1a902824` | generic runtime admitted; exact stock point release unproven |
| file runtime | 14 | G2 wrappers over littlefs v2.10.1 source-equivalent baseline | `0494ce7169f06a734a7bd7585f49a9fa91fa7318` | wrappers are already source-owned; exact historical littlefs checkout unproven |
| role/BLE/message policy | 7 | first-party G2 | private source unavailable | bounded provider seam |

The object therefore introduces no remaining opaque third-party utility. Its
nanopb call set cannot distinguish the compatible 0.4.7--0.4.9.1 releases,
and its DLIB calls repeat already catalogued primitives rather than revealing
the exact IAR archive. The executable accounting is in
`tools/manifests/g2-tracepoint-setting-provider-map.tsv`.

## Limits and reproduction

The exact Even source revision and private producing commit are unavailable.
Production admission would require a clean-room schema/policy implementation,
exact callback/message ABI integration, and target BLE/filesystem validation.
The present work deliberately remains analysis-only.

Run:

```sh
make tracepoint-settings-closure
```

This authenticates the image and manifests, reproduces the function/provider
graph, runs focused tests, and reconciles the aggregate retained-path frontier.
