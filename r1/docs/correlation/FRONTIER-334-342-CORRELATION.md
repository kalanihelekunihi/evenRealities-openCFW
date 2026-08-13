# 334...342-byte frontier correlation

The next five largest unresolved application functions are now source-routed from exact body
hashes and complete direct/tail-caller scans:

| Recovered function | Bytes | SHA-256 | Disposition |
| --- | ---: | --- | --- |
| `0x00033AF8..<0x00033C4E` | 342 | `0d66762846139eee2e58bad4c4cec3c95ce4d5aee990ac7a12342c3c901bb263` | R1 factory-test thread envelope |
| `0x0004D024..<0x0004D176` | 338 | `292da396faeaf54280bcc662ab6de7265b32096dcaddfa10e7e12f83fe939ec2` | R1 peripheral-link/advertising watchdog |
| `0x000653E6..<0x00065536` | 336 | `c8ac5c9174bab8d9d5b7dd9089b08e6ae8625342011ea998a559d0a6f777ba6e` | GoMore licensed-provider boundary |
| `0x00090ACC..<0x00090C1A` | 334 | `070fb3bf75ac9151085d8cbecd6d2baa778096ca615b7a207292d7757d227bd5` | GoMore licensed-provider boundary |
| `0x00074190..<0x000742DE` | 334 | `4cc0c4d0e74a60a2a41d29ede8715f8aa4bcdabdc1dc63c2add307622f165068` | Goodix GH_SPO2/dlCom provider boundary |

`0x00033AF8` is called only at `0x0005D662` by the BAE8 BC receiver. It is the
factory-test sibling of `0x00033DBC`: both allocate `(payload + 15) & ~3` bytes, clear the
allocation, write message type/context/length as three little-endian UInt32 values, copy the
payload after the 12-byte header, queue the allocation, wake the consumer, and free it on queue
failure. `r1_factory_thread_message_encode` shares only the deterministic envelope helper.
Allocation, FreeRTOS queue/wake operations, logging, and ownership transfer remain external.

`0x0004D024` has one direct caller at `0x00092010`. It increments an eight-bit periodic counter,
reports the peripheral link count every 60 invocations, normalizes `0xFF` back to zero, rejects the
impossible state in which both glasses handles are valid while no more than one peripheral is
connected, conditionally cancels a pending restart and calls Nordic `ble_advertising_start` in
mode 3, then schedules the next check after `0x2800` ticks. The clean-room
`r1_peripheral_watchdog_plan_step` returns typed decisions only. Nordic connection-state and
advertising functions, the assertion/fatal path, delayed-event execution, and logging remain
their respective provider seams.

`0x000653E6` is called only at `0x000653AC` inside the already byte-pinned GoMore sleep-model
range. It constructs and releases multiple private tensor branches through the recovered GoMore
floating-point graph runtime. `0x00090ACC` is called at `0x0005F8C8` and `0x0005FB44` from the
already gated GoMore energy output producer and updates private activity-mode estimator state.
Neither function, its constants, its tensor descriptors, nor its formulas are reconstructed.
Both are licensed-provider-only boundaries.

`0x00074190` is called only at `0x00076832` in the Goodix dlCom signal path and invokes the
already gated Goodix helper at `0x000929D6`. It selects bounded local peaks, applies a private
threshold factor, maintains a ranked peak-index set, and returns selected values. The thresholds,
selection implementation, and dlCom state remain in the matching licensed Goodix provider.

Reproduce with:

```sh
python3 tools/evidence/summarize_r1_frontier_334_342.py
python3 tools/build_r1_source_ownership.py --check
python3 tools/verify_openr1.py
```

The two product APIs are retained by the Nordic SDK link at `0x00037F66` and `0x00037F92`.
The current unsigned application is 95,040 bytes (`text=94,804`, `data=236`, `bss=132,544`),
with HEX SHA-256 `48e1b3fadfdb956fbdf5f637d48c9a5808db5394848fb4538450c0ff98be80cf`
and BIN SHA-256 `421a42cf37dad04dadcff5d3b1742efcba4ba50fd1d2e52f26bcf00e5df24d35`.
No code signing or deployment bypass is part of this closure.
