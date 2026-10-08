# Semaphore creation and failure ownership

Source: `g2/components/bootloader/initializer_callbacks/semaphore_create.c`. Locked bootloader load0x410000, SHA256 f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5. The ownership ledger records416762..416816 (180B), counting constructors419e62..419e94 (50B)/419e94..419ec0 (44B) and destroy41a470..41a492 (34B):308B total. The compiled wrapper inlines child C bodies; their separate sections are discarded by GC. Ownership is distinct from tested path coverage266B.

## Call chain and layout

`platform_finish` calls create(maximum1,initial0,attributeNULL) and stores the returned handle at0x20027104. Guard41602a is checked first. Nonzero guard, zero maximum or unsigned initial>maximum returnsNULL. Attribute+8 is control storage and+12 its byte size: nonzero storage with size≥80 chooses static; both zero chooses dynamic; any other pair rejects. Name+0 and bits+4 are ignored by this wrapper.

Maximum1 uses queue type3; maximum>1 uses type2. All queues have item_size0. Static factory419c9c uses caller storage; dynamic419d08 asks RTOS heap419730 for80B. Queue count is+0x38, maximum+0x3c, item size+0x40, allocation flag byte+0x46 and type byte+0x4c. Counting constructors write initial count after successful creation, with no queue-put. Binary creation with initial1 calls queue-put419ec0(queue,NULL,0,0); result1 accepts. Any other result invokes destroy41a470 and returnsNULL.

## Proven ownership table

| Path | Storage owner | Failure/cleanup effect |
| --- | --- | --- |
| Static creation | Caller; queue flag+0x46=1 | Allocation never taken from heap; put failure returnsNULL without freeing caller storage |
| Dynamic creation | RTOS heap; flag+0x46=0 | Queue needs80B; synthetic native allocator consumes96B including its header/alignment |
| Allocation failure | No returned object | Wrapper returnsNULL; no queue-put/free |
| Binary initial-token failure | Dynamic queue | Stock destroy reads+0x46 and invokes native RTOS free419830; it does not perform waiter cancellation |
| Successful binary/counting creation | Queue remains allocated | No release is invented; later consumer deletion is outside this wrapper |

1344 controlled-factory comparisons PASS, including invalid counts/storage, allocation outcomes and put failure. Twelve additional composed cases run native queue factories, heap allocation/free/coalescing and destroy while controlling scheduler suspend/resume, guard and queue-put outcome. Whole81920B arena and heap globals match. Failed dynamic binary initialization restores free bytes81904, increments allocation/free counters1/1, and retains low-water81808. Successful allocation leaves81808 free bytes/counters1/0. Static paths leave cold heap globals unchanged.

The direct harness explicitly clears XPSR/IT state between independent calls. Without that reset, a reused Unicorn CPU could carry conditional-execution state into another fixture; the diagnostic failure was a harness issue, not evidence for a firmware change. Neither test exercises actual scheduler delivery, hardware IRQ, waiter cancellation or independent constructor-invalid/null-destroy fatal paths. Shared seven-case integration separately executes native allocator/guard on startup; its initializer semaphore handle is0x20000568 on both sides.

## Next concrete edge

IOM descriptor publisher42c45a selects record `(head+1)%capacity` from32-byte entries at context+0x854, then issues ordered MMIO writes; this is not a software descriptor copy/release operation. It and service42c6f8 remain next asynchronous boundaries. No IOM release policy can be inferred from semaphore creation or the queue-destroy flag alone.
