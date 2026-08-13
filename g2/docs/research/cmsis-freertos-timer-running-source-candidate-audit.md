# G2 CMSIS-FreeRTOS timer-running source candidate

Status: source-integrated in the Apollo-main production overlay

`osTimerIsRunning` is `[0x00449522,0x0044953E)`, 28 bytes, SHA-256
`3802dd7a15e7c36c1e9490f9f538aef562959fae8e695917bc665a9ef435c482`,
with two external callers. Its only dependencies are source-owned
`IRQ_Context` and the already production-integrated timer-active provider
`open_cfw_rtos_timer_is_active`.

The 813-byte Apache-2.0 candidate has SHA-256
`9e9b8ca7a42f214b381935cf2c32729f7292e3857d166d34f1f6194e40b8845b`.
Apple Clang emits 26 bytes, SHA-256
`9d9b4fb06604b9c023267b986cafc31ff3d7260fd1cd80f6ba78020d4fcd020b`,
with a call to the IRQ helper and a tail jump to the active-state provider.
Host tests cover ISR, null, inactive, and active paths. The complete stock span
now redirects to the source leaf. Apple places it at offset 131,732
(`0x007B45B8`) with linked SHA-256
`e1e29f6fe4b3f60250931d498cd2e6834588c0b285ec1668aed38942f10d9163`;
Linux places it at offset 133,600 with linked SHA-256
`72fbb0d69c325e55f87586ebb3de0a216962862883c675bc4c7a927caae3cfa2`.
