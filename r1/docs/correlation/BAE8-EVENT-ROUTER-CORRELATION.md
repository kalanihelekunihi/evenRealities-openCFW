# BAE8 custom-service event-router correlation

## Decision

The 418-byte callback at `0x0005D5E0..<0x0005D782` is R1 product-specific routing around the
custom BAE8 GATT service, not Nordic service implementation. It is classified
`r1_product_specific` / `clean_room_behavior_only`. Nordic SDK service registration and link
context management remain upstream; adjacent BC receivers and the unidentified event helper keep
their independent ownership gates.

The local equivalent is split deliberately: `r1_runtime_plan_bae8_event` is a pure routing plan,
while `r1_runtime_receive_eus` owns the bounded channel-2 data path. The planner does not call BLE,
role, logging, BC, or unresolved providers.

## Exact identity and registration

| Recovered range | Bytes | SHA-256 |
| --- | ---: | --- |
| `0x0005D5E0..<0x0005D782` | 418 | `a767809ef6dd28fd1e49ca67838942c7eae79ea180b781f0e8dcc7d078d3c7d3` |

There are no direct branch callers. Registration is instead proven by the exact Thumb pointer
`0x0005D5E1` stored at `0x0004E6E4`. The R1 provider-configuration function at `0x0004E66C`
passes that pointer to the BAE8 service configuration at `0x000529BC`, which installs it at
service callback offset `0x2C`.

## Event policy

| Service event | Product route |
| ---: | --- |
| `2` | BC receive path |
| `3` | EUS receive reassembler at `0x00032198` |
| `6`, `7` | link-context group A lookup and glasses-role assignment |
| `8`, `9` | link-context group B lookup |
| all others | ignored |

The clean planner reproduces this selection and the two link-context/role flags. The Nordic
`ble_link_ctx_manager` lookup, the role-state commit, BC receiver bodies `0x00033AF8` and
`0x00033DBC`, event helper `0x00065D64`, factory-marker accessor `0x0007BA24`, and all logging
remain outside this closure. No adjacent function changes ownership by association.

## Verification

```sh
python3 tools/evidence/summarize_r1_bae8_event_router.py
```

The static summarizer validates the recovered application hash, complete callback body, absence of
direct callers, exact callback pointer, registration chain, event routes, clean-room split, and
dependency exclusions. Host tests exhaust the six recognized event values and unknown-event
behavior.
