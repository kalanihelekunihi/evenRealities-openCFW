# G2 Conversate common-data dependency boundary

Six retained-path anchors / 1,718 bytes expand to twelve Ghidra-discovered
functions / 2,208 body bytes for
`app\gui\conversate\conversate_comm_data.c`. The complete physical object is
`[0x005B3EF8,0x005B48F8)`, 2,560 bytes.

The object contains conversation-record initialization, bounded copy/reset,
lookup, mutation, and line-measurement policy. Its 72 external direct calls
terminate at admitted EasyLogger (60), bounded IAR DLIB memory primitives
(11), and the admitted LVGL `lv_text_get_next_line`-compatible implementation
at `0x004897FC` (1). It reuses EasyLogger `a596b264…` and LVGL `344c7c318…`;
there is no serializer, language model, text engine, embedded third-party
definition, or new version/private-commit discriminator.

Ingress closes over 22 BL sites with no stored pointer or indirect call. The
sole raw interior-word collision at `0x00490D18` combines two valid 16-bit
Thumb instructions into a pointer-shaped word and is not callable ingress.
Remaining work is first-party data-policy recreation and UI/device validation;
the object is not production-routed.
