# Public task constructors share native C bodies

`xTaskCreate` and `xTaskCreateStatic` now alias the selected native task
constructors. This resolves the two public kernel imports without duplicate
implementations. Dynamic creation uses the exact public `BaseType_t` C return
type; its previous int32_t declaration used a different C integer type with the
same ARM width. A compiler assertion now proves complete dynamic prototype
compatibility. Static creation uses the existing 112-byte word-aligned opaque
public allocation contract; its pointer argument names opaque storage rather
than the recovered field type. Both public symbols have exactly the native
symbol's address and size.

[Machine-readable evidence](task-create-api-c-review.json) binds the current
sources, REA instruction observations, probes, audit, qualification and full
build/hybrid reports by SHA-256. REA confirms dynamic construction at 0x983b8
and static construction at 0x98418. No new instruction region is byte-qualified.

There are 350 paired stock/C constructor cases (700 executions). Actual
constructor and initialization bodies, list-item initialization and stack-frame
construction execute. Cases cover dynamic/static creation, odd/even depths,
priority endpoints, null/empty/31/32/40-byte names, optional dynamic output
handles, entry interrupt masks, failure of either allocation, and invalid
priorities/static buffers. Stack/control/output guard regions, callback order,
returns, ownership flags, final SP, callee-saved registers and interrupt masks
agree. Logical assertion address, width, value and mask agree. Only the task
return LR word is normalized after verifying its source-specific exit-function
address; the remaining initialized stack bytes compare directly.

A further 160 source integration cases execute actual compiled CMSIS
`osThreadNew`, public aliases, constructors, initialization, list-item and stack
routines together. Negative controls reject a wrong static allocation flag,
short control allocation, and omitted cleanup after the second allocation fails.
Memory-fill, allocator/free and scheduler-ready handoffs are modeled. CMSIS
scheduler-state reads are also modeled. Names remain stable during each call.
Malformed depths/pointers, asynchronous mutation, actual allocator integration,
ready-list insertion/startup and physical scheduling remain unverified. Private
frames and caller-clobbered words/flags are outside these comparisons.

All three preexisting native construction function bodies remain byte unchanged;
all other compiled objects are byte unchanged. All 573 R1 units compile without
failures or duplicate strong symbols. Application imports fall from 181 to 179,
resolving only `xTaskCreate` and `xTaskCreateStatic`; bootloader imports remain
34. Five qualification profiles select no exact regions. The unchanged canonical
source plan still produces a stock-identical hybrid: 3,857 source-built bytes,
642,303 binary-pull-through bytes and 248 resource bytes. Complete source linking,
source completeness and hardware operation remain unfinished. No G2 gate advances.
