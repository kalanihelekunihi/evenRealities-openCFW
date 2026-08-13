# G2 dashboard data-process recovery

The seven retained-path anchors / 2,492 bytes expand to fourteen functions /
5,706 body bytes for `dashboard_data_process.c`. The complete physical object
is `[0x004FE0AA,0x004FF8E4)`, 6,202 bytes. Four restored routines complete
dashboard protobuf record processing, role-aware dispatch, allocation/copy,
shared-state synchronization, and state updates.

One large recovered routine has a nine-instruction switch-dispatch island at
`[0x004FEC02,0x004FEC14)` that the recursive decoder does not reach; the audit
pins that linear code separately instead of misclassifying it as data. The
closed surface contains 2,143 instructions, 262 direct calls, 23 whole-image
BL entries, no stored entry pointers, no indirect calls, and no
strict-interior ingress.

All 255 external calls terminate at EasyLogger (170), bounded IAR DLIB (32),
admitted nanopb runtime (19), source-owned CMSIS-FreeRTOS (4) and FreeRTOS (1),
or first-party dashboard providers (29). This reuses EasyLogger `a596b264…`, nanopb
`98bf4db6…`, CMSIS-FreeRTOS `d213f261…`, and FreeRTOS-Kernel `def7d2df…`; it
embeds no third-party implementation and adds no version or generating-commit
discriminator. Remaining work is first-party schemas and dashboard behavior;
the object is not production-routed.
