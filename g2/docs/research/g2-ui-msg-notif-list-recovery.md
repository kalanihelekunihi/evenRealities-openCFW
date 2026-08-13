# G2 notification-list UI recovery

The 18 retained-path anchors / 5,392 bytes for
`app\gui\MessageNotify\ui_msg_notif_list.c` expand to fifty functions /
10,808 body bytes. The complete physical object is
`[0x0054FF36,0x00552CDC)`, 11,686 bytes including 878 bounded literal, string,
table, and alignment bytes. Thirteen restored functions include the large
post-shard UI constructor, notification-string helpers, and small stored
callbacks that the baseline Ghidra sweep missed.

The fail-closed audit pins 4,221 reachable instructions, 661 direct calls, 93
whole-image BL entries, four stored Thumb pointers, no indirect calls, and no
strict-interior ingress. All 599 external calls terminate at selected or
bounded providers: EasyLogger (205), LVGL (304), CMSIS-FreeRTOS (6), IAR DLIB
(11), production-routed TLSF heap wrappers (8), and 65 first-party UI,
notification-service, time-format, resource, role, and string-helper edges.

The object therefore reuses LVGL 9.3-compatible commit `344c7c318…`,
CMSIS-FreeRTOS v10.5.1 commit `d213f261…` over FreeRTOS-Kernel `def7d2df…`,
EasyLogger `a596b264…`, and TLSF `deff9ab5…`. It embeds no third-party
definition and exposes no new version or exact historical-commit
discriminator. Clean-room notification-list policy and UI recreation remain
first-party work; the object is not yet production-routed.
