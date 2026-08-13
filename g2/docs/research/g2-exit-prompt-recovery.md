# G2 exit-prompt recovery

The retained `app\gui\anim\exit_prompt.c` anchor expands from two Ghidra
bodies / 276 bytes to five functions / 782 body bytes plus a 118-byte pool,
for 900 physical bytes at `[0x0058BDA8,0x0058C12C)`. Three source-order
callbacks missed by the baseline census recover the fade hold/start sequence
and `common_exit_prompt_show`. Seventeen direct entries, three stored callback
pointers, 56 body calls, both adjacent boundaries, and the absence of indirect
or strict-interior targets are pinned by the analyzer.

The 53 direct external calls close over 35 admitted EasyLogger diagnostics,
15 LVGL object/animation/style calls at selected 9.3-compatible commit
`344c7c318047b7348e1be8572a9fd4260c251cfa`, and three first-party
`fade_anim.c` setup calls. There is no CMSIS-FreeRTOS, allocator, nanopb, IAR
runtime, or embedded upstream definition and no new version discriminator.
The remaining implementation is first-party prompt/animation policy, and the
recovered object is not yet production-routed.
