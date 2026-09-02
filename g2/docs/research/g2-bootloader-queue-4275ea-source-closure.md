# G2 bootloader Ambiq queue-family source closure

The complete stock Ambiq queue family at `[0x004275EA,0x004276BA)` is routed
to reviewable BSD-3-Clause C. The admitted functions are the 24-byte queue
initializer at `0x004275EA`, the 94-byte item-add service at `0x00427602`, and
the 90-byte item-get service at `0x00427660`. Their compiled bodies occupy
authenticated generated-NOP space inside those same stock spans; generated
entry redirects occupy the leading 6, 6, and 4 bytes respectively. No overlay
growth is required.

## Authentication

- The semantic source is AmbiqSuite Apollo510 `am_hal_queue.c` at commit
  `5efc0228528a8adce5eae0d226fac85d2551eb3b`, SHA-256
  `2ca55e34d5b9d4843e32ce0ab24e312bde580716c708c7f017adcd0a12dbd1e4`,
  upstream Git blob `fa81af8e3f50dc1aff75e8f27df90ad828c803d2`.
- The vendored `am_hal_queue.h` is 10,115 bytes with SHA-256
  `eabc8d95b06f06c24cc160ca85e20bd2fca32d1e7b0d9c8d815b7b3f9dffd2db`.
  It authenticates the exact 24-byte ABI: write index, read index, length,
  capacity, item size, and data pointer at offsets 0, 4, 8, 12, 16, and 20.
- Stock SHA-256 identities are
  `142ce77e922601c4cf495ab896455263777d8088987c0f783477ea4aceff059f`,
  `80fc90006d26902783880b56b7c04c351369282c1624a401c680e6bc66cde1e6`,
  and `6c63753c5d95abac9183eb00ec419aaf3240dceba70170b3a377e7e8ada137b2`.
- Direct callers are `0x00422E04` and `0x00422E20` for initialization,
  `0x00423378` and `0x00423568` for add, and `0x004233BA` and `0x00423656`
  for get. Neither function has an interior entry.
- The initializer is byte-identical to its main-image analogue at
  `0x0053006C`. The add/get analogues at `0x00530084` and `0x005300E2` share
  91 of 94 and 87 of 90 bytes; each has three differing bytes across two
  contiguous-byte runs, exactly the image-specific `BL` encoding to the
  critical-save provider.

## Production behavior

`runtime_queue_4275ea.c` initializes all six fields, serializes add/get with
the authenticated critical-save service at `0x0041B8EC`, restores the exact
saved PRIMASK with the reviewable `msr primask` mnemonic, rejects insufficient
capacity or data atomically, copies optional byte sources/destinations, wraps
indexes modulo byte capacity, and updates byte length only after a successful
operation. Host tests cover field layout, FIFO and wrap behavior, rejection
atomicity, null-buffer semantics, and interrupt-token restoration.

Apple clang emits 18/88/86-byte bodies. Their relocated SHA-256 values are
`7c41f3e3bb6b211f6eb2e8f5d115063d1bd80f4541c0ed2d89e64dc89032d4b9`,
`6d3eae77835f295febb980b300e6f66fcc62653214e517d9977561d390c6bdb8`,
and `c793d2e2dec7fbe5b17fbdb3539d719318faed1b971738295bb4d0d9724014f2`.
Linux clang emits the same sizes with relocated SHA-256 values
`0f1e402222fe9a765b68dd7f50e91dfaba7c0f4c9c2f67fe9bfb26429890d5a3`,
`6964d4faaf1d8c03d31fa51a259b7e56512f44f4d5ec6a72ca8c818e1e8d7840`,
and `721e19cdf487465342ba25c62bd2b99c3b657af073370d17b2d7ebf2851276d8`.
Add and get each contain one reviewed `R_ARM_THM_CALL` relocation at offset 14
to `0x0041B8EC`; initialization has none.

## Hardware evidence

Live interrupt masking/restoration, concurrent producer/consumer behavior,
and downstream consumers on a G2 require authorized hardware and suitable
instrumentation. Their validation is **blocked by unavailable physical
evidence**. No hardware operation was performed by this closure.
