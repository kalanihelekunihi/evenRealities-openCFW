# Ambiq NemaGFX/NemaVG authenticated interface snapshot

This directory contains a byte-exact, header-only subset of AmbiqSuite 5.1.0's
public `components/graphics/NemaGFX_SDK` package: 32 files and 251,655 bytes.
The reproducible public source is `AmbiqMicro/ambiqhal_ambiq` commit
`b853fded7e545f005727e13bf2ce83018c7e242d`; the complete public SDK subtree
at that commit has Git tree `e690768a6e7b4d6a8d526fc75e8278a2764deff3`.
The imported interface reports NemaGFX 1.4.12 and NemaVG 1.1.8. The unchanged
header license is `headers/LICENSE`.

The payload contains the public API headers, private NemaGFX interface headers,
`gpu_patch.h`, and `nema_sys_defs.h` required to compile the recovered Ambiq
LVGL backend. Its canonical inventory digest is
`186008f77de1bfa3942b4ad0de8f2a8932fcc834558fb1641d87e94f3ccd36a8`;
`g2/tools/manifests/g2-nemagfx-ambiq-provenance.json` records the public source
state and selected artifact identities.

No NemaGFX or NemaVG implementation archive, Ambiq HAL source, or target
binary is imported here. These headers therefore establish interface-level
compile evidence only. They do not establish a linkable firmware provider or
any GPU, cache, power, antialiasing, or display behavior on Apollo510 hardware.

`g2/tools/build_g2_lvgl_ambiq_backend.py` verifies this payload before using
it for the isolated Cortex-M55 compile qualification. The local README is not
part of the authenticated 32-file payload inventory.

