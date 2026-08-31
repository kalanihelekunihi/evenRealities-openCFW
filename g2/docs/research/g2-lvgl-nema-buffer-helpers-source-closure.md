# G2 LVGL Nema buffer-helper source closure

Status date: 2026-08-30  
Scope: `nema_buffer_invalidate` and `nema_buffer_is_within_pool` only  
Mode: authenticated stock-byte analysis, clean-room C, host hostile-input tests,
and Cortex-M55 object/relocation qualification; no overlay registration or
hardware operation

## Closure result

Both previously missing Nema HAL symbols now have component-local MIT source:

- `third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_nema_buffer_helpers.c`
- `third_party/lvgl-ambiq-backend/g2-runtime/lvgl_ambiq_nema_buffer_helpers.h`

The source exports the exact public ABIs:

```c
void nema_buffer_invalidate(nema_buffer_t *buffer);
bool nema_buffer_is_within_pool(int pool, uint32_t start, uint32_t length);
```

The imported Think Silicon header pins the 32-bit `nema_buffer_t` layout to 16
bytes: `size` at 0, `fd` at 4, `base_virt` at 8, and `base_phys` at 12. The
provider has one target dependency,
`am_hal_cachectrl_dcache_invalidate(am_hal_cachectrl_range_t *, bool)`, through
one `R_ARM_THM_CALL` relocation. It introduces no allocator, LVGL, libc, global
cache, or FreeRTOS dependency.

## Authenticated stock semantics

The official 3,523,396-byte G2 image contains:

| Function | Span | Bytes | SHA-256 |
|---|---|---:|---|
| `nema_buffer_invalidate` | `[0x0051411A,0x00514148)` | 46 | `7899709976ddd9c5dff28a3f0d312b79d6bea138a2fdcf85af83b2d1c737e260` |
| `nema_buffer_is_within_pool` | `[0x00514148,0x0051416C)` | 36 | `aa2873c2e579c1e1ff6d0914451629553552d54175ca2f0ee8b64853901eda07` |

The adjacent authenticated `select_heap` body and literal pool prove the exact
mapping:

- pools 0 and 1 select the render descriptor at `0x20000354`;
- pool 2 selects the assets descriptor at `0x20000370`;
- pool 3 selects the CPU/clipped-path descriptor at `0x20000338`; and
- every other pool value follows stock and selects render.

The descriptor fields used by these helpers are size at offset `0x10`, arena
start at `0x14`, and the cacheable byte at `0x18`.

Stock invalidate reads `fd`, selects the descriptor, and returns without a
cache call when the cacheable byte is zero. Otherwise it constructs the exact
two-word Ambiq cache range from `base_phys` and `size`, passes `false` as the
clean selector, and calls the authenticated Apollo510 data-cache invalidate
entry. Stock pool checking accepts `start >= arena_start` and
`start + length <= arena_start + arena_size`. The public AmbiqSuite 5.1.0
Zephyr port corroborates the API and normal range/cache intent, but differs in
heap implementation and rejects invalid pool IDs; it is not claimed as the G2
generating source.

## Deliberate hostile-input hardening

For valid G2 descriptors and ranges, the C result is identical to stock. The
provider deliberately does not preserve unchecked 32-bit addition on hostile
inputs. It uses subtraction-based containment and rejects a wrapped heap end,
a wrapped requested end, a negative buffer size, null buffer, and any
out-of-pool cache range. Invalidate rechecks containment internally rather than
depending only on the caller's potentially compiled-out LVGL assertion.

Zero-length ranges at a valid address, including exactly at the arena end,
remain accepted as in stock. Invalid pool IDs retain stock's render-pool
mapping. Non-cacheable valid buffers perform no cache HAL call. Cacheable valid
buffers pass the physical address and exact size and always request invalidate
without clean.

## Deterministic verification

`tools/audit_g2_lvgl_nema_link.py` pins the complete stock function bytes,
descriptor literals, source/header identities, Arm object identity, exports,
undefined symbols, and relocation. The warning-free Cortex-M55 object is 1,436
bytes with SHA-256
`ff6dd3f339eebd009310abc3d7fe610b97e1501c1d0a1dcebc53ce22ac60fca9`.

`tests.test_runtime_lvgl_ambiq_nema_buffer_helpers` exercises all pool routes,
boundary-inclusive zero lengths, below/above-pool addresses, requested-range
wrap, descriptor-end wrap, empty pools, null and negative-size buffers,
non-cacheable suppression, and the exact physical range/`clean=false` cache
call. The atomic link now has zero missing Nema HAL symbols. The component-local
Apollo HAL provider also closes this helper's cache dependency, leaving 73
symbols at that stage. The separate FreeRTOS queue provider closes the final
three queue/semaphore names, leaving 70 symbols in the maximal ledger: LVGL
core, target runtime, and the bounded GPU-patch helper.

Reproduce from `g2`:

```sh
python3 tools/audit_g2_lvgl_nema_link.py
python3 -m unittest -v tests.test_runtime_lvgl_ambiq_nema_buffer_helpers
python3 -m unittest -v tests.test_audit_g2_lvgl_nema_link
```

## Remaining boundary

The source is not registered or linked in the core overlay. Atomic production
admission still requires deliberate routing of the source-qualified Apollo510
cache provider and the rest of the platform/FreeRTOS closure. No authorized
target identity, cache
trace, GPU command-list observation, or display evidence was supplied, so
cache coherency and live hardware behavior remain explicitly unqualified.
