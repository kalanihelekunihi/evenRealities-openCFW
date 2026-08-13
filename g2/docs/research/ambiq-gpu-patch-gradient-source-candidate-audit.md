# Ambiq GPU-patch gradient source-candidate audit

Status: bounded production-excluded clean-room candidate. This closes the
gradient GPU-patch export directly called by the recovered Ambiq LVGL subtree,
within G2's proven two-stop caller contract.

## Result

The exact public `lv_ambiq_gradient_create` section is 1,416 bytes, has SHA-256
`5870d79c49ee8bd0dfa4b5bf8f6f39b04ed45148c0c00b774467149292d83ae4`,
16 relocations, and DWARF source line 138. The stock IAR body independently
occupies `[0x005FA238,0x005FA7C0)`—also 1,416 bytes—with SHA-256
`82d1ae24eff6da055d251b067ce54e002940cd90a8283af0063381448ea6dc93`.

The exact Ambiq LVGL caller allocates its arrays with
`LV_GRADIENT_MAX_STOPS`; the canonical subtree inherits LVGL's default value
two, and `lv_grad_init_stops` asserts more than one stop. It derives each stop
from an unsigned byte divided by 255, so live values are normalized to
`[0,1]`. That bounds the required path to two normalized stops, including
missing endpoints, equal stops, and descending invalid input.

`tools/emulate_ambiq_gpu_patch_gradient.py` executes the authenticated
Cortex-M55 function section under Unicorn. It patches only the two authenticated
absolute literals, intercepts every relocated Nema call, and models one
unsupported fallback-path coprocessor store by its exact zero-vector memory
effect. Oracle traces establish:

- clip, simple blend, and gradient enable before validation;
- a black-to-white interpolation fallback for descending stops;
- constant implicit segments when the first stop is above zero or the last is
  below one;
- half-pixel adjusted initialization and per-channel slopes for the real
  segment;
- a preserved zero-width/infinite-slope segment for equal stops;
- exact first/last pixel overwrites, including the hard-coded last x coordinate
  63; and
- the original double-disable sequence on the successful path.

Seven focused host/target tests pin those traces, exact public and stock binary
evidence, the two-stop boundary, relocation-free Cortex-M55 output,
independent naming, documentation, and production exclusion.

Run:

```sh
make ambiq-gpu-patch-accessors-candidate
```

The candidate is not a general replacement for calls outside the recovered G2
two-stop contract. Production admission still requires rendered-output or
command-stream comparison on Apollo510 hardware and atomic admission with the
Nema/HAL boundary. It does not claim textual identity with unavailable source.
