# R1 source bootloader linker diagnostic

The recovered GNU layout in `r1/config-recovered/openr1_bootloader.ld` is derived
from the pinned Nordic SDK 17.1.0 secure BLE bootloader layout. Its FLASH origin
0xF8000 and 0x6000 length, RAM origin 0x20005978, settings page 0xFF000, and MBR
parameter page 0xFE000 agree with `r1/docs/memory-map.md`. The SDK's implicit
`GROUP(-lgcc -lc -lnosys)` is removed: runtime providers must be explicit source
objects. The pinned SDK `nrf_common.ld` is still required.

Run from the repository root:

```sh
python3 tools/build/r1_bootloader_link.py \
  --report build/sources-goal-r1-boot-reset-c/report.json \
  --out build/r1-boot-link-new
```

Use a fresh output directory. The helper checks the manifest, composition
status, participating object hashes, and available original source hashes.
It records its exact inputs, linker version, log, map, and result. It does not
recompile sources or establish freshness of included headers or generated
sources. A failed link removes its partial ELF and exits nonzero.

## Historical diagnostic result

The strict link of the 81 bootloader units resolves the 22 linker-provided
memory/registration symbols. It fails on exactly these five code dependencies:

- `nrf_cc310_bl_init`
- `nrf_cc310_bl_hash_sha256_init`
- `nrf_cc310_bl_hash_sha256_update`
- `nrf_cc310_bl_hash_sha256_finalize`
- `nrf_cc310_bl_ecdsa_verify_secp256r1`

No crypto library, stock executable blob, permissive unresolved-symbol option,
or crypto substitute was supplied. The GNU linker additionally reports ARM/Thumb
relocation diagnostics for these unresolved calls. The relocatable source report
still correctly reports 27 bootloader imports; the strict layout does not change
that report or claim firmware completeness.

## Validation and boundaries

`build/goal-r1-boot-layout-c/verify.py` passed checks for fixture vectors at
0xF8000, UICR words at 0x10001014/18, RAM start/stack bound, retained crypto,
DFU, SVC and observer records, fs_data inside the startup copy span, contiguous
FLASH load addresses for initialized data, five strict-link crypto gaps, absent
failed-link ELF, and rejection of a nonempty output directory. The fixture has
nonempty initialized data, as does the actual composition (0x38 bytes plus
0x14 bytes fs_data). An empty `.data` fixture exposed the upstream script's
RAM load-address fallback for `.fs_data`; that variant is not qualified by this
layout and needs explicit load-address treatment if it becomes a real input.

`python3 tools/build/sources.py check --device r1` passes: 777 units, 575 source
files, zero excluded units. The helper passes Python byte compilation. These
checks do not establish physical boot, clock configuration, DFU verification,
full-image linking, settings compatibility, or deployability. In particular,
keep the recorded LFRC versus SDK LFXO hardware warning in
`r1/docs/hardware-observations.md` as an outstanding board gate. No device was
flashed. Byte identity and paid compilers are not requirements for this route.
