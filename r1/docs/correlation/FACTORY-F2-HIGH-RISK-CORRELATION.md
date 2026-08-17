# Factory command-F2 high-risk correlation

## Outcome

Four high-risk factory command-`0xF2` handlers omitted from the main Ghidra export now have
transparent, inert C plans. The implementation preserves response ordering, delays, selector
precedence, reset metadata, persistent marker intent, and ship-mode sequencing without executing
any destructive action.

| Recovered extent | Bytes | SHA-256 | Behavior |
| --- | ---: | --- | --- |
| `0x00062D6A..<0x00062D84` | 26 | `d1403d57eb8a6b26738f4f0a8eab8b5ef3d8fc479dc619f9e896b9ad9c5b5b26` | send four-byte response, delay 2,000 ms, persist reset reason 3, request NVIC reset |
| `0x00062D84..<0x00062DB0` | 44 | `6927962e2dd3d3764a1ccd72bbd891166fdecccdf1e7349495db9abe8daf7650` | payload byte 4 selects profile 4000; otherwise byte 5 selects profile 2000; otherwise stop stock Goodix profiles; then send four-byte response |
| `0x00062DB0..<0x00062DD4` | 36 | `1932fd3bacf30cb7da4b813606a83bff9c48bd7543908804e6bf874bbb1b3750` | respond, delay 100 ms, persist device marker `0x5A`, invoke destructive ship-mode sequence, delay 100 ms |
| `0x00062DD4..<0x00062DF2` | 30 | `7e5a9beda85c1fb8047ded58f8c46833f254858ad096fc902416d8e30dedc1b9` | respond, delay 100 ms, invoke destructive ship-mode sequence, delay 100 ms |

The PPG selector's first branch has strict precedence when both bytes are one. The two profile
targets are the admitted Goodix adapter profiles 4000 and 2000; the default target stops stock
profiles. Both ship-mode handlers reach the same system-control sequence, while only the first
writes the `nv_r1` marker.

## Clean implementation and safety boundary

`r1_factory_f2_delayed_reset_plan`, `r1_factory_f2_ppg_mode_plan`,
`r1_factory_f2_marked_ship_mode_plan`, and `r1_factory_f2_ship_mode_plan` return caller-owned
descriptions only. The PPG decoder requires the six bytes needed for offsets four and five rather
than reproducing the stock unchecked reads. Tests pin default/4000/2000 selection, dual-one
precedence, response length four, both delay schedules, reset reason 3, marker `0x5A`, and every
destructive-action flag.

No function sends the response, delays a thread, controls Goodix, writes persistent state, pulses
the ship-mode GPIO, writes reset trace state, resets the MCU, or exposes command `0xF2` over BLE.
