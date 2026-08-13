# CMSIS-FreeRTOS mutex-delete census correction and source candidate

Status: census corrected; source-integrated in the Apollo-main production overlay

The linked-function map previously mislabeled `[0x0044986E,0x0044989A)` as
`osMutexGetOwner`. The 44-byte body cannot implement an owner getter: it clears
bit zero from the input handle, performs IRQ/null status validation, calls
`vQueueDelete`, ignores the callee return, and returns `osOK`, `osErrorISR`, or
`osErrorParameter`. This is exactly CMSIS-FreeRTOS v10.5.1 `osMutexDelete` with
`configQUEUE_REGISTRY_SIZE == 0`.

The corrected stock SHA-256 is
`649cee0eb99f62128cd191253b2d15f446b0867ab11fd406e36eb2d527102a40`;
the entry has eight external callers. `osMutexGetOwner`, not
`osMutexDelete`, is now in the 33-API dead-stripped set. All six fail-closed
linked-census tests pass after the correction.

The 1,462-byte Apache-2.0 candidate has SHA-256
`91d73236a38148437740f7cdb5816acbbe8965991f29a1282271d63193394895`.
Apple Clang emits 38 bytes, SHA-256
`a64571d42510649fc779b82295401a6542614657c1f0cce88d072d01aca0568b`,
with calls only to source-owned `IRQ_Context` and `vQueueDelete`. Host tests
cover ISR rejection, null-after-tag-clear, and recursive-tag stripping before
one deletion.

The complete stock span now redirects to the source leaf after two generated
alignment bytes. Apple places it at offset 131,692 (`0x007B4590`) with linked
SHA-256 `d55a21146fce1f3975eec6ee9c83112cc4350a94197c400a326898a259b6391e`;
Linux places it at offset 133,560 with linked SHA-256
`48dc2ae50f54f7bea4fc713171129027501c737f3d28a51b21607f046665f696`.
