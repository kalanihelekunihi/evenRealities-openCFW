# G2 EvenHub loading-page dependency boundary

Status: complete read-only closure of
`app\gui\EvenHub\evenhub_loading_Page.c` in authenticated G2 2.2.6.10.

The physical object `[0x00492CB4,0x004935CC)` contains four functions / 2,042
body bytes / 2,328 physical bytes. Two retained-path anchors expand through a
draw-transform helper and a state getter. Two direct entries and two stored
function pointers close ingress; there is no indirect body call.

Its 137 external calls resolve to 36 admitted LVGL calls, 85 admitted
EasyLogger calls, two bounded IAR runtime calls, and fourteen first-party UI,
event, storage, and widget providers. The adjacent transform helper beginning
at `0x004935CC` belongs to `evenhub_ui.c`, proving the loading-page endpoint.

The object embeds no reusable implementation and adds no version or historical
generating-commit discriminator. Loading animation and transition behavior
remain first-party product policy.

Reproduce with `make evenhub-loading-page-closure`.
