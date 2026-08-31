# G2 FreeType CFF production-source admission

Status date: 2026-08-30  
Target: official G2 `s200_v2.2.6.10` Apollo-main image  
Mode: software-only; no signing, flashing, erase, or hardware operation

## Result

After the complete base upgrade and the previously admitted default modules,
CFF was the largest remaining authenticated FreeType frontier.  The tempting
`raster1` renderer is absent from the exact ten-entry G2 default module table;
CFF is present there, but its previous source admission was only a retained
subset rather than a complete callable and physical map.

This tranche adds a warning-clean production C adapter for the public CFF
property service.  It pins the recovered build to the Adobe engine, rejects the
excluded legacy engine, validates stem-darkening Booleans, and validates all
eight darkening coordinates before calling FreeType.

The admission analyzer reconciles:

| Partition | Functions | Official retained bytes |
|---|---:|---:|
| CFF engine bodies | 38 | 11,326 |
| Exact FreeType base support | 9 | 736 |
| **Source-authenticated total** | **47** | **12,062** |

The new complete map closes `[0x005ABEF8,0x005B0114)`:

| Complete CFF envelope partition | Functions/intervals | Bytes |
|---|---:|---:|
| Callable bodies | 101 | 16,718 |
| Literal-pointer/data pools | 12 | 204 |
| Alignment padding | 1 | 2 |
| **Physical total** | **114** | **16,924** |

Thus the earlier 38-body CFF candidate gains 63 functions and 5,392 callable
bytes.  No callable or physical byte remains unresolved or unclassified.  The
identity evidence combines the exact official-image body hash, the pinned
FreeType 2.9.1 definition and source order, and an independent class, service,
parser table, call, string, or Thumb-semantic corroborator.  This is source
identity evidence, not a claim that a new compiler reproduces the stock bytes.

The admission separately authenticates the complete selected CFF source inventory: 17
`.c`/`.h` files and 269,028 source bytes at FreeType tag `VER-2-9-1`, peeled
commit `86bc8a95056c97a810986434a3f268cbe67f2902`, under the FreeType Project
License.  It provides compilable maintained implementation source without
pretending that the new Clang object has IAR compiler-byte identity.

## Deterministic qualification

`analyze_g2_freetype_cff_function_map.py` fails closed on the official image,
Ghidra relation, exact upstream source, single-object include order, prior two
retained waves, class/service tables, all 101 body boundaries and hashes, and
all 13 residue intervals.  `analyze_g2_freetype_cff_source_admission.py` then
requires that checked-in complete-map manifest in addition to the version,
license, 17-file inventory, recovered feature state, component manifest, and
public runtime surface.

Host qualification executes the adapter against the actual selected FreeType
2.9.1 module set.  It verifies the Adobe-only engine, strict Boolean handling,
default and custom darkening parameters, rejection without mutation for three
invalid parameter classes, null-output clearing, allocator teardown, and exact
module registration.  A separate Cortex-M55 Thumb hard-float build compiles both
the adapter and the full unmodified `src/cff/cff.c` translation unit with short
enums and `-Wall -Wextra -Werror`.  Hostile tests mutate the official image,
Ghidra input, retained evidence, and physical-residue digest and require every
case to fail closed.

The companion production-route census now authenticates the completed
component route instead of requiring permanent absence.  The official stock
default-module table at `0x0073EEF8` contains `cff_driver_class`
(`0x006DCB74`) at index 2, and its retained call chain remains
`FT_Init_FreeType` (`0x0052431C`) to `FT_Add_Default_Modules` (`0x005242FC`)
and `FT_Add_Module` (`0x0052729C`).  The source-owned LVGL font manager already
reaches that subsystem through eight guarded redirects to the retained
FreeType create/delete adapter.

The admitted whole-translation-unit `-Oz` link retains all 101 mapped CFF
source functions, six policy-adapter exports, the driver class, zero undefined
symbols, and zero final relocations.  Its exact four-section scatter is:

| Section | Apple bytes | Linux bytes | Address |
|---|---:|---:|---|
| CFF rodata | 4,918 | 4,918 | `0x005ABEF8` |
| stock-envelope text | 11,382 | 11,322 | `0x005AD230` |
| application-tail text | 4,100 | 4,100 | `0x007FCEC0` |
| application-tail exidx | 16 | 16 | `0x007FDEC4` |

The component builder first authenticates the complete stock CFF interval and
the four-byte module slot.  It writes all four admitted sections and only then
changes the class word at `0x0073EF00` from little-endian `74cb6d00`
(`0x006DCB74`) to `14c05a00` (`0x005AC014`).  The canonical core builder invokes
this stage after core, liblc3, and product-test, using the same-build pre-CFF
component.  The exact resulting components are 3,956,468 bytes in both
profiles: Apple SHA-256
`aa3dbf59ad8912a92fcd9ea6e1ce33834da51989f5fb19257e7064871fb6a3b2`
and Linux SHA-256
`3255f998ea3c115803bf957e63b50e0b4a969cf478e64939610592c6fd4758f7`.

`analyze_g2_freetype_cff_production_route.py` pins the stock call graph, the
complete map, LVGL consumer audit, scatter builder/config, canonical core
builder/config, exact scatter manifest, and current package manifest.  It
independently checks the guarded stock bytes, required four-section closure,
seven exports, zero relocations/undefined symbols, dual-profile component
hashes, and core post-link invocation.  Hostile tests mutate both component
builders and both configs and require an exact pin-drift rejection.

Canonical publication now promotes the same exact closure at the package
boundary.  The manifest pins the Apple and Linux 3,956,468-byte components,
six Apple CFF ownership rows plus five Linux profile-replacement rows, and
packages of 4,749,540 / 4,749,524 bytes with SHA-256
`482756200d1b3c70685d7c1c29c422a5725436801e3600d7cf55fa3e16809128` /
`d9386d30c0c6b1bd706b36c9ee095ad6e2e9ee9b5dacf9c58a52357c7620a362`.
Thus `canonical_package_manifest_route_enabled` and
`software_production_route_permitted` are true.  The six policy exports are
present, but there is still no authenticated first-party caller that changes
the Adobe-default CFF policy.  External font payload and physical behavior
also remain unqualified.

Reproduce with:

```sh
cd g2
make freetype-cff-source-closure
```

## Evidence bounds and remaining gates

This closes the software-side CFF callable/physical map, maintained
runtime-policy source seam, exact final relocation, scatter placement, and
guarded canonical component route.  It does not claim canonical package
publication beyond the exact pinned dual-profile receipts, IAR byte identity,
external G2 CFF font identity, face-path
configuration, task stack, WCET, display quality, or physical-device behavior.

The policy-callsite audit authenticated `cff_driver_class` (`0x006DCB74`), its
Adobe-only constructor (`0x005B004A`), and the indirect `ps_property_set` /
`ps_property_get` service entries (`0x00527F0A` / `0x00527FF2`).  It recovered
no authenticated first-party caller that changes CFF policy.  The adapter is
placed and retained as an exported surface; absence of a caller prevents any
claim that target policy mutation has executed.

Hardware validation is blocked because no authorized physical G2 hardware and
no authenticated external CFF font payload were supplied to this software-only
tranche.  Those unavailable inputs are required before rendering behavior can
be evaluated.  Any future canonical package regeneration remains a separate
root-owned, receipt-checked operation; this census authenticates the current
published software route but does not turn it into physical-device evidence.
