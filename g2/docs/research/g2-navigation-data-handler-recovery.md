# G2 navigation data-handler recovery

Status: authenticated complete linked-object closure for official G2
`2.2.6.10`. This is analysis only; no hardware or flash operation was
performed.

## Result

The seven retained-path anchors / 2,290 Ghidra body bytes for
`app\gui\navigation\navigation_data_handler.c` expand to 22 linked functions,
8,076 reachable code bytes, and the complete 8,556-byte physical object
`[0x00586448,0x005885B4)`. Twenty-one functions were discovered by the
authenticated Ghidra corpus. The large dispatcher at `0x005872F4` was missed
because it crosses a corpus shard boundary and is restored by control-flow
recovery.

The object contains 480 non-code bytes. Two literal pools totaling 64 bytes
are embedded inside the dispatcher at `[0x00588012,0x0058803C)` and
`[0x005881AE,0x005881C4)`; the remaining seven regions separate functions or
hold resource tables and literals. The audit treats those pools as data even
though linear Thumb decoding produces plausible instructions.

## Recovered behavior

Seventeen compact helpers construct navigation protobuf union variants. Four
allocate private 0x2024-byte records and most of the remainder use the shared
record/encode buffers. The restored dispatcher handles the navigation data
record, role/display gates, state serialization, and service notifications.
The tail maps numeric navigation codes 0 through 35 to resource names, scans
an authenticated 89-entry named-resource table, and applies the resolved
resource through the first-party UI seam.

The complete graph has 2,926 reachable instructions and 435 direct calls: 12
remain inside the object and all 423 external calls terminate at bounded
providers. The provider split is EasyLogger 165, IAR DLIB 94, nanopb 37,
CMSIS-FreeRTOS mutex wrappers 9, source-owned allocation wrappers 49, and
first-party navigation/role/transport/resource policy 69. No third-party
implementation is embedded in this object and it adds no new dependency or
version discriminator. The generic dependency commits remain nanopb
`98bf4db6…`, CMSIS-FreeRTOS `d213f261…`, FreeRTOS-Kernel `def7d2df…`, and
EasyLogger `a596b264…`.

## Ingress and false positives

Whole-image scanning finds 45 direct `BL` entry sites and no stored function
entry pointer. Two apparent interior/non-code calls are overlapping raw-byte
artifacts, not executable calls:

- bytes at `0x0050566C` are the second halfword of the `SXTAB` at
  `0x0050566A`, not a call to dispatcher interior `0x005877CA`;
- bytes at `0x0057FB58` are the second halfword of the `MUL` at `0x0057FB56`,
  not a call to literal-pool address `0x005872BC`.

Two unaligned four-byte windows elsewhere in the image similarly resemble
odd Thumb pointers into the object; neither is aligned storage. These four
pseudo references are pinned so they cannot become accepted ingress silently.

## Reproduction

```sh
make navigation-data-handler-closure
```

The fail-closed evidence is in
`tools/manifests/g2-navigation-data-handler-function-map.tsv`,
`tools/manifests/g2-navigation-data-handler-provider-map.tsv`, and
`tools/manifests/g2-navigation-data-handler-closure.tsv`. Production routing
remains false: complete object analysis establishes the contract but does not
by itself justify a clean-room implementation of product navigation policy.
