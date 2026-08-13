# G2 EvenAI UI object and dependency recovery

Status date: 2026-08-11  
Target: official G2 `s200_v2.2.6.10` Apollo-main image  
Retained path: `app\gui\EvenAI\ui_even_ai.c`

## Result

The complete linked object is `[0x004E54C8,0x004E75B0)`, exactly between the
closed `pb_service_even_ai.c` object and an unrelated helper cluster. Forty-
three callable functions occupy 8,004 function-interval bytes. Fifteen outer
pool regions contribute 420 bytes; one four-byte zero literal at
`[0x004E6FD0,0x004E6FD4)` is embedded in `even_ai_ui_reflash`, leaving 8,000
decoded instruction bytes and 8,424 physical bytes total.

The original retained-path census found only two functions / 346 bytes.
Focused call-target recovery restores 28 functions that the original Ghidra
census missed; the remaining 13 discovered but unanchored functions are now
assigned to the same object. All 43 entries, 512 body calls, 131 direct BL
entry sites, the stored input callback, 21 raw path references, all pools, and
both object boundaries are pinned.

This is first-party EvenAI page, dialog, streaming, and animation policy. It
contains no LVGL, CMSIS-FreeRTOS, EasyLogger, or IAR implementation body.

## Recovered functional groups

The 43-function inventory is recorded individually in
`tools/manifests/g2-ui-even-ai-function-map.tsv`. The principal groups are:

- text-stream lifecycle and automatic refresh: service create/destroy/reset,
  current/pending byte tracking, timeout handling, character-window trimming,
  and streaming/direct-display selection;
- input and timing: the exact `EvenAI_InputEventWarp`, one stored callback,
  fixed six-byte UI event forwarding, and a single tick wrapper;
- layout and scroll: label measurement, cached tail heights, content-height
  checks, scroll animation, and complete linked-list relayout;
- dialog construction: exact retained `even_ai_add_question`,
  `even_ai_gray_question`, `even_ai_add_answer`, and
  `even_ai_create_dialog_node` identities; and
- page lifecycle: exact `even_ai_answer_text_reflash`, `even_ai_ui_reflash`,
  and `even_ai_page_init`, plus the lifecycle-matched deinitializer.

The path string occurs in three literal cells at `0x004E5F9C`, `0x004E6A78`,
and `0x004E7510`. Their 21 raw references arise in 16 functions. The original
two anchored functions remain the conservative retained-path frontier metric;
the larger complete-object count is not substituted into that lower bound.

The one stored entry is the aligned Thumb pointer
`0x004E7598 -> 0x004E5D17`, selecting the input-event callback. A whole-image
BL scan finds no strict-interior target. Several other unaligned byte windows
look like Thumb pointers by chance; they are deliberately not promoted to
callback evidence.

## Dependency boundary and source pins

The 413 external direct calls partition without residue:

| Provider | Calls | Provenance conclusion |
|---|---:|---|
| LVGL | 182 | 44 object/style/label/image/bar/scroll/event/animation targets terminate at the admitted 9.3-compatible source family, selected ceiling `344c7c318047b7348e1be8572a9fd4260c251cfa` |
| EasyLogger | 105 | Three admitted diagnostic targets; 2.2.99-compatible selected core `a596b2642e27af3a2dbdeb0e5f04a6b5b673ef24` |
| IAR DLIB | 22 | `memcpy`, `memset`, and `strlen`; already bounded/source-recreated, with the existing EWARM 9.20+ floor and 9.60.2 leading candidate |
| CMSIS-FreeRTOS | 1 | Exact `osKernelGetTickCount` from v10.5.1 commit `d213f261b5be6bb29a7cce8b84071706b72f4d53` |
| G2 first party | 103 | EvenAI timer, text-stream, animation, page/common-UI, role, protocol, and dialog providers |

The audit composes the already closed 26-function `text_stream_service.c` and
13-function `even_ai_timer.c` objects. This both identifies the local provider
calls and prevents them from being misclassified as another runtime utility.

The LVGL calls exercise already admitted APIs and reveal no new source-version
discriminator. They therefore reinforce the selected source baseline without
proving one historical hybrid-tree commit. The CMSIS wrapper is exact but
likewise adds no checkout discriminator. No third-party functional gap is
opened by this object.

## OpenCFW boundary

The object is not production-routed. Its remaining work is first-party source
reconstruction and target UI validation: dialog allocation limits, page and
animation lifecycle, text-stream callback ordering, scroll geometry, localized
error assets, and role/protocol interactions. Those are application-policy and
hardware/UI-integration tasks, not unresolved dependency origin or version
questions.

## Reproduction

Run:

```sh
make ui-even-ai-closure
```

`tools/analyze_g2_ui_even_ai.py` authenticates the stock image and manifests,
re-decodes all 3,141 instructions, requires the sole inline literal, validates
all pools and boundaries, replays direct and stored ingress, accounts for every
provider call, authenticates the four third-party source baselines, and
composes the timer and text-stream provider audits. It performs no signing,
flashing, erase, or hardware operation.
