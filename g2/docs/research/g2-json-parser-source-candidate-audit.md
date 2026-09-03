# G2 embedded JSON parser — source candidate audit

Fail-closed provenance analysis of the previously flagged unadmitted JSON
parser body shared by `service_android_notify.c` (13 call sites) and
`service_whitelist.c` (21 call sites) in the stock G2 Apollo510 image
`blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin`
(SHA-256 `36c5b0e4…68a27863`). Reproduce with
`/usr/bin/python3 tools/analyze_g2_json_parser.py` and
`tests/test_analyze_g2_json_parser.py`; pins in
`tools/manifests/g2-json-parser-{function-map,closure}.tsv`.

## Result

**Family: cJSON (DaveGamble/cJSON), version interval v1.7.9 through v1.7.12
(2018-12-16 … 2019-05-17).** The linked parse-side functions are
source-identical across those four releases (verified full-text at tags
v1.7.8, v1.7.9, v1.7.12, v1.7.13, v1.7.15 plus the upstream CHANGELOG), so
the binary cannot discriminate within the interval; no narrower claim is
made. No Even modification of the linked functions was found — the body is
consistent with an unmodified upstream cJSON from the interval, built with
`ENABLE_LOCALES=Off` (constant `get_decimal_point`), with the
print/create/edit/utils side dead-stripped by static linking.

The parse-side closure is now production-routed. The admitted source is
`components/shared/cjson/runtime_cjson_parse.c` (26,626 bytes, SHA-256
`710c9d2357e850730b169fb48b190fbe06e08b8da09f34736b38c3122c6dad63`).
It emits 21 strict relocated leaves and 21 authenticated stock-entry redirects
in both compiler profiles.

## Object enumeration

21 functions / 2,572 body bytes in the physical interval
`[0x004D798C,0x004D83D8)` (2,636 bytes; 64 noncode bytes in 6 interleaved
literal-pool/alignment gaps). Bounded by already-closed neighbors:
`pb_service_notification.c` ends at `0x004D798C` (its closure pins the
preceding pool) and `pb_service_dev_config.c` begins at `0x004D83D8`.
No retained source path; Ghidra missed the entire body. 1,172 reachable
instructions, full recursive-descent coverage, no uncovered bytes.

Whole-image ingress closure: 68 direct BL entry sites (34 internal, 34
external), zero strict-interior BL, zero pseudo-BL into pools, zero B.W
entry/interior targets, zero stored entry pointers, zero raw
instruction-word interior collisions. 47 direct body calls (34 internal,
13 external) plus 6 indirect `blx` sites, all six dispatching through cJSON
`internal_hooks` (allocate/deallocate), none opaque.

Literal pool: `"null"`/`"false"`/`"true"` at
`0x0078D15C/0x0078D164/0x0078D16C`; UTF-8 BOM `EF BB BF 00` at `0x004D7F90`;
pointers to `global_hooks` (`0x2007410C`) and `global_error` (`0x200004BC`);
double constants `0.0`, `2147483647.0` (INT_MAX), `0xC1DFFFFFFFFFFFFF`
(IAR-materialized `(double)INT_MIN`); surrogate mask `0x000FFC00`.

Recovered function roster (upstream symbol, address, bytes):
`case_insensitive_strcmp` 0x004D798C (78), `cJSON_New_Item` 0x004D79DA (32),
`cJSON_Delete` 0x004D79FA (90), `get_decimal_point` 0x004D7A54 (4),
`parse_number` 0x004D7A5C (218), `parse_hex4` 0x004D7B50 (74),
`utf16_literal_to_utf8` 0x004D7B9A (246), `parse_string` 0x004D7C90 (398),
`buffer_skip_whitespace` 0x004D7E1E (58), `skip_utf8_bom` 0x004D7E58 (66),
`cJSON_ParseWithOpts` 0x004D7E9A (226), `cJSON_Parse` 0x004D7F7E (12),
`parse_value` 0x004D7F98 (310), `parse_array` 0x004D80D8 (244),
`parse_object` 0x004D81CC (320), `cJSON_GetArraySize` 0x004D830C (28),
`get_array_item` 0x004D8328 (28), `cJSON_GetArrayItem` 0x004D8344 (16),
`get_object_item` 0x004D8354 (86), `cJSON_GetObjectItem` 0x004D83AA (10),
`cJSON_IsArray` 0x004D83BC (28).

## Family candidates considered

| candidate | verdict | discriminating binary evidence |
| --- | --- | --- |
| cJSON (DaveGamble) | **selected** | exact struct layout `next+0/prev+4/child+8/type+0xC/valuestring+0x10/valueint+0x14/valuedouble+0x18/string+0x20`, `sizeof(cJSON)=0x28`; `parse_buffer{content,length,offset,depth,hooks}` 28 bytes; `internal_hooks` 3-word allocate/deallocate/reallocate; `strncmp` against `null`/`false`/`true` in upstream dispatch order with type codes 4/1/2 and `valueint=1`; escape set and surrogate-pair UTF-16 logic; hooks-based allocation via `blx` |
| jsmn | ruled out | jsmn is token-based: no allocation, no node tree, no literal strings (primitive parse reads only the first character), no hooks; the binary has malloc/free hook dispatch, a linked node tree, and a `null`/`false`/`true` string pool |
| parson (kgabis/parson) | ruled out | parson stores object members in parallel name/value arrays inside `JSON_Object`, not `next/prev/child` linked nodes; no `internal_hooks` struct; no 0x28 node with this field order |
| frozen (cesanta) | ruled out | frozen is scanf/callback-style and builds no DOM tree; the binary is a tree parser with `cJSON_GetObjectItem`-class linked-node walk |
| cJSON ≤ 1.4.x (pre-buffer rewrite) | ruled out | pointer-walking parser without `parse_buffer` offset/length/depth; binary uses the 1.5.0+ buffer-based core with the `CJSON_NESTING_LIMIT` depth counter (0x3E8) at buffer+0x0C |
| cJSON 1.5.0–1.7.8 | ruled out | `get_object_item` carries the 1.7.9 #315 fix (below) |
| cJSON ≥ 1.7.13 | ruled out | `buffer_skip_whitespace` lacks the exhausted-buffer early return (below) |
| cJSON ≥ 1.7.14 | ruled out | `parse_array`/`parse_object` lack the `head->prev = current_item` tail store (below) |
| cJSON ≥ 1.7.19 | ruled out | 1.7.19 allocates the number temp buffer (#939); binary uses the 64-byte stack `number_c_string` |
| Even first-party private implementation | ruled out | function-for-function structural identity with upstream cJSON across 21 functions, including upstream idiosyncrasies (parse_array's missing bounds check on `[` vs parse_object's guarded `{`, the `skipped_bytes` allocation overestimate, `case_insensitive_strcmp`'s NULL-returns-1 contract) |

## Version discrimination within cJSON

Four independent discriminators bound the interval; each is pinned by the
analyzer against exact bytes/instructions.

1. **Lower bound ≥ 1.7.9** — `get_object_item` (0x004D8354) contains both
   the case-sensitive loop guard `current_element->string != NULL` before
   `strcmp` *and* the final
   `if ((current_element == NULL) || (current_element->string == NULL)) return NULL;`
   gate. Tag v1.7.8 has neither (verified full text); the fix is upstream
   issue #315, shipped in v1.7.9 (2018-12-16). Tags v1.7.9/v1.7.12 match
   the binary exactly.
2. **Upper bound < 1.7.13** — `buffer_skip_whitespace` (0x004D7E1E)
   decrements `offset` when `offset == length` even if the buffer was
   already exhausted at entry; v1.7.13 added the
   `if (cannot_access_at_index(buffer, 0)) return buffer;` early return
   (carried with the v1.7.13 `cJSON_ParseWithLength` work, #358), which a
   compiler cannot elide into the observed behavior. v1.7.9–v1.7.12 match
   the binary; v1.7.13/v1.7.15 do not.
3. **Upper bound < 1.7.14** — `parse_array` (0x004D80D8) and `parse_object`
   (0x004D81CC) success paths do `depth--`, set type/child, `offset++`, and
   return, with **no** `head->prev = current_item` store. That store is the
   v1.7.14 tail-node optimization (#503, 2020-09-03), present in the
   verified v1.7.15 text, absent in v1.7.13 and in the binary.
4. **Upper bound < 1.7.19** — `parse_number` (0x004D7A5C) uses the 64-byte
   stack buffer (`sub sp, #0x44`, loop bound 0x3F) with `strtod`;
   v1.7.19 (2025-09-09, post-firmware) switched to an allocated temporary
   buffer (#939).

Consistency evidence (not independently bounding): monolithic
`cJSON_ParseWithOpts` with inline `strlen(value) + sizeof("")` (the v1.7.13
delegation to `cJSON_ParseWithLengthOpts` is also link-compatible, so this
only corroborates); `cJSON_Delete` tests `cJSON_IsReference` (bit 8) and
`cJSON_StringIsConst` (bit 9); `skip_utf8_bom` (upstream since 1.6.0);
INT_MAX/INT_MIN `valueint` saturation (upstream since 1.3.0);
`ENABLE_LOCALES=Off` constant `get_decimal_point`.

Within the interval, upstream released 1.7.10 (pkg-config, cJSON_Utils
merge sort), 1.7.11 (cJSON_Minify overflow), and 1.7.12 (cJSON_Minify loop,
VS link, cJSON_Utils macros) — none touch the linked functions, and the
verified v1.7.9 and v1.7.12 texts of all 21 linked functions are identical.
The binary therefore cannot select a single tag; the honest interval is
**v1.7.9–v1.7.12**.

## Caller inventory

34 external BL entry sites terminate at six public entries; all callers are
the two already-closed sibling objects — no other object in the image uses
the parser:

| entry | symbol | service_android_notify.c | service_whitelist.c | total |
| --- | --- | --- | --- | --- |
| 0x004D7F7E | cJSON_Parse | 1 | 1 | 2 |
| 0x004D79FA | cJSON_Delete | 2 | 8 | 10 |
| 0x004D83AA | cJSON_GetObjectItem | 10 | 9 | 19 |
| 0x004D830C | cJSON_GetArraySize | 0 | 1 | 1 |
| 0x004D8344 | cJSON_GetArrayItem | 0 | 1 | 1 |
| 0x004D83BC | cJSON_IsArray | 0 | 1 | 1 |
| total | | 13 | 21 | 34 |

This supersedes the approximate "19 call sites" figure in
`g2-service-android-notify-dependency-boundary.md` (which predates recovery
of the GetArraySize/GetArrayItem/IsArray entries and counted only the three
originally flagged entries).

## Provider boundary

The 13 external body calls terminate at: the admitted nanopb 0.4.9 shared
48-byte structure initializer `0x0048949C` (1 call — zeroing the 28-byte
parse buffer frame in `cJSON_ParseWithOpts`; commit
`98bf4db69897b53434f3d0ba72e0a3ab1a902824`); bounded IAR DLIB primitives
`memset` 0x0043C0E4 (1), `strlen` 0x0044A43C (1), `strncmp` 0x0044B610 (4),
`strcmp` 0x0046CACC (1); and two **unclosed but semantically bounded** IAR
runtime bodies: the `tolower` trampoline 0x004D58C2 (4 calls, dispatching
via 0x004D43A4 +0x28) and `strtod` 0x00542D48 (1 call). No CMSIS-FreeRTOS
or FreeRTOS kernel API is used. The six `blx` sites are the cJSON
allocator-hook dispatches and are classified, not opaque.

The production adaptation removes every direct provider edge above. Local
freestanding C implements zero-fill, length/comparison, ASCII case folding,
and bounded decimal conversion; the only runtime dispatches are the six
authenticated allocator/deallocator hooks through the existing three-word
SRAM ABI. Target-object inspection reports zero undefined symbols and zero
allocated data sections. Apple clang 21 emits 2,442 function bytes and Linux
clang 22.1.8 emits 2,434; both replace the same 2,572 stock function bytes.

## Production admission

Four independent canonical observations (Apple A/B and Linux A/B) agree on
the complete source closure and profile-specific bytes. The production route
preserves the fixed `global_hooks` and `global_error` SRAM objects, keeps the
v1.7.12 parse data model and 1,000-level nesting limit, and carries no hardware
operation. A host differential corpus covers scalar values, signed and
exponent numbers, UTF-8 BOM input, escapes, UTF-16/surrogate conversion,
arrays, objects, case-insensitive object lookup, deletion, and malformed input.
The ARM audit separately proves exactly 21 function sections, no undefined
symbol, and no non-code allocation section.

The larger Apple core tail is included in the existing service-audio suffix
packing boundary: 11,698 suffix bytes (105 leaves, 11,616 payload bytes, 321
relocations) are moved into authenticated host caves, preserving the LC3 table
start at `0x007EA620`. Ordinary fail-closed Apple and Linux builds reproduce
the canonical 3,956,672-byte components.

## What remains externally gated

- The exact tag within v1.7.9–v1.7.12 and Even's vendoring path (copy-paste
  vs submodule vs SDK carrier) are not observable from the binary; no
  version string or producing commit is recoverable (cJSON versions itself
  only via macros/`cJSON_Version`, which is dead-stripped).
- The stock `tolower` trampoline and `strtod` bodies remain provenance facts,
  but no production cJSON path calls them.
- License: upstream and the bounded production adaptation are MIT. No cJSON
  hardware validation is applicable; the route performs no hardware action.
