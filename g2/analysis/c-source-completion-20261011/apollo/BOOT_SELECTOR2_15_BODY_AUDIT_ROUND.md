# Boot selector 2 and 15 body audit

The rooted header-only proof queue is now **170/654**, down from 172.
The whole 903-label catalogue has **268** header-only leads. These counts
describe evidence attribution, not missing C implementations.

Native PCM22 selector 2 at `0x428240` matches the selected
`event_a_pcm22_transition_sequence_2`: timer gate/service, target state
stores, TON adjustment, fixed profile `+0x50` VDDF trim, capped VDDC ramp,
last-state commit, and timer start. Original literals resolve
`0x428ba8 -> 0x4002004c` and `0x428c84 -> 0x40020044`, matching C.
Native selector 15 at `0x429524` matches
`opencfw_spot_pcm22_transition15`: profile and timer reads, state stores,
and distinct volatile RMW writes to `0x40020048`, `0x40020080`, and
`0x40020044`. Its ambient current-TON high return is retained in C.
Both reviewed bindings are recorded in `manual_body_bindings.json`.

These comparisons did not justify a selected source edit. The last selected
source change remains the selector-17 MMIO reread correction. Its coherent
target receipt is `boot-coplacement-selector17-reread-round/receipt.json`:
373 selected units, 1,010 providers, three ROM imports, 158,628 candidate
bytes and `PASS_BOUNDED_LINK`. Peripheral behavior and whole-image equality
are still unqualified.
