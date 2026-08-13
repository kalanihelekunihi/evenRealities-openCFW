# G2 charger-common recovery

Status: complete linked-object census and host/Thumb-qualified clean-room
candidate; not production-routed. Run addresses use
`run = file_offset + 0x00437FE0`.

## Result

The retained first-party path
`platform\service\charger\charger_common.c` owns 14 linked bodies in
`[0x004ACE10,0x004AD908)`. They total 2,764 logical code bytes, SHA-256
`cc3b89cc5efc5d671fdda351e6fb3a194f6bf1277a798e2f399ecaf3603cbd88`.
Three alignment/literal regions contribute another 220 bytes. The complete
physical object is `[0x004ACE10,0x004AD9B8)`, 2,984 bytes, SHA-256
`66629608034c65df865a5376ea4e6caf566216810d698d842f77ea487031004c`.

Twenty-five direct calls land on object entries, including ten exterior
callers. The bodies contain 157 direct calls in total. No stored entry pointer,
direct or `B.W` strict-interior branch survives. Six unaligned raw values that
look like interior addresses are instruction or packed-data byte windows, not
ingress.

## State and synchronization ABI

The 24-byte runtime at `0x20073B30` stores peer SOC at `+0x08`, peer charging
at `+0x0C`, aggregate SOC at `+0x10`, and aggregate charging at `+0x14`. The
eight-byte local cache is at `0x20074104`; the synchronization mutex is at
`0x20074370`. Raw charger state remains at `0x20073B18`, with charge state at
`+0x15` and the signed current used to determine whether charging is active.

Initialization creates the mutex, clears runtime and local state, writes `-1`
SOC sentinels, and starts the synchronization timer. Initial synchronization
retries at polls 2, 4, 6, and 8 and times out at poll 16. Deinitialization
deletes the mutex, clears its slot, and stops the timer.

## Battery policy

Local SOC applies the stock near-full compensation:

- 93 becomes 94 only in charge state 1;
- 94 becomes 95 or 96, and 95 becomes 97 or 98, according to charge state;
- 96 becomes 99; and values above 96 become 100.

SOC values below 101 are valid. Aggregate SOC is the lower of the local and
peer values. When the peer reports charging, aggregate charging is local
charging or local SOC 100. Otherwise it requires local charging and peer SOC
100. A charging-state change is immediate below raw SOC 98 but requires four
observations near full.

## Peer wire contract

The charger synchronization service is `0x0105`. Its message is exactly 12
bytes: message ID, payload length, source role, destination role, and an
eight-byte `{soc, is_charging, padding}` record. IDs 3, 2, and 4 mean notify,
response, and request. Receiving a notify updates peer state, sends a response,
and recomputes both aggregates; receiving a response recomputes without a
reply.

## Reconstruction boundary

`components/apollo_main/core_overlay/charger_common.c` is an independently
authored candidate (13,467 bytes, SHA-256
`1c3b2d7fa0da4e3e4aed565c1e8585638c5dcb0e3ba7a36e0f9335956d7c12ab`).
Host tests cover SOC compensation, signed-current interpretation,
initialization/deinitialization, exact wire layout, peer aggregation and reply,
and near-full debounce. A freestanding Thumb build with warnings as errors
exports exactly 11 intended global text symbols. The analyzer pins all 14
stock bodies, the owned non-code regions, retained names/path, call closure,
globals, wire ABI, and qualified raw overlaps.

No historical source for this first-party file has been authenticated. The
candidate is absent from `overlay.json`; concrete RTOS mutex/timer, role,
transport, publisher, diagnostic, placement, redirect, and package-validation
work remains. It therefore claims zero package ownership bytes.
