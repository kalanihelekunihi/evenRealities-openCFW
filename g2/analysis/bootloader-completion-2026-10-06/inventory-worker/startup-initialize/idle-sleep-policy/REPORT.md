# Native idle sleep-policy dependency recovery

Two leaf functions newly reconstructed in sleep_policy.c; **259 locked-original versus compiled-source comparisons PASS**, all136instruction bytes covered. Bootloader input SHA f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5, load410000. No external calls or stubs. Original instruction ranges4181e4..418228 and418a00..418a44.

`expected_idle_ticks` returns0 if current task priority is nonzero, idle ready-list count is at least2, or top ready priority is nonzero. Otherwise it returns unsigned(next_unblock - tick_count), with stock modular arithmetic. It does not itself clamp wraparound; idle entry separately asserts next_unblock>=tick_count before its suspended recheck.

`confirm_sleep` returns0 if pending-ready list count, yield-pending, or pending-tick count is nonzero. Otherwise it returns2 if suspended-list count == task_count-1; else1. These are FreeRTOS-compatible abort/standard/no-timeout states, but this leaf test establishes numeric decisions only. This means timer suppression eligibility depends on pending scheduler work, not solely the idle interval.

Tests cover all blockers, return states, subtraction wrap and synthetic task-count-underflow. The underflow fixture matches instructions but is not a claim that task_count0 is reachable in a running scheduler. Snapshot tests have no asynchronous state change, timer, WFI or idle-entry integration. Source is an unintegrated addon; shared209-object candidate remains unchanged. Immutable source/object/ELF/receipt identities are in evidence.json.

Next source dependency is tick-step0x418394, then timer access/compare/enable/clear wrappers and full idle entry0x4189ac. Its equality boundary includes pending-tick manipulation/assertion, so it should be recovered rather than replaced with a generic tick increment. Physical timer/IRQ timing remains external to these leaf proofs.
