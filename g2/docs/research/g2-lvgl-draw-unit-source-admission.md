# G2 LVGL draw-unit source admission

## Scope

This note bounds an isolated provider for `lv_draw_create_unit` required by the
retained Ambiq draw backend.  It does not register the provider in the Apollo
production overlay and does not qualify hardware behavior.

## Authenticated behavior

LVGL commit `344c7c318047b7348e1be8572a9fd4260c251cfa`, tree
`2c76db856ec570f3ee12565181e5cf52bdd33d78`, defines the function in
`src/draw/lv_draw.c`.  The exact valid-input sequence is:

1. allocate a zeroed caller-selected extent with `lv_malloc_zeroed`;
2. prepend the unit to `LV_GLOBAL_DEFAULT()->draw_info.unit_head`;
3. increment `unit_cnt`; and
4. copy the resulting one-based value to the unit's signed `idx` field.

The isolated provider preserves that sequence.  It additionally returns null
without allocation or state mutation for an extent smaller than
`sizeof(lv_draw_unit_t)`, for allocator failure, or when the next ID is not
representable by `int32_t`.  These checks prevent the upstream unchecked write,
null dereference, and implementation-defined unsigned-to-signed conversion on
hostile inputs without changing valid LVGL behavior.

## Link boundary

The Cortex-M55 source object exports only `lv_draw_create_unit`.  Its only
imports are the already reviewed local providers `lv_malloc_zeroed` and
`lv_global`.  The deterministic aggregate link with those providers has no
undefined symbol.  The retained consumer is `lv_draw_ambiq.o`; its exact call
relocation is pinned by the analyzer.

## Admission boundary

This is source admission, not production routing.  The provider mutates LVGL's
global draw-unit list without internal locking, exactly as upstream does.
Correct `lv_init` ordering, exclusive list/count ownership, draw-thread
serialization, teardown ordering, object collision, RAM placement, and the
allocation lifetime are not established by source or link evidence.  Hardware
qualification therefore remains false.
