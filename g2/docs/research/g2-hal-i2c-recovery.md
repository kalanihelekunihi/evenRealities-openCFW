# G2 HAL I2C recovery

The retained `driver\hal\src\hal_i2c.c` anchor expands from one 308-byte body
to nine Ghidra functions / 1,584 body bytes plus a 40-byte pool, for 1,624
physical bytes at `[0x0050412C,0x00504784)`. The object covers initialization,
power/pin transitions, three nonblocking-transfer forms, and the vector-owned
IOM interrupt handler. Thirty-five direct entries, the stored vector pointer,
65 body calls, both adjacent boundaries, and zero indirect or strict-interior
BL targets are pinned by the analyzer.

This closure materially strengthens the Ambiq shortcut. Twenty-one calls map
to the Apollo510 GPIO and complete IOM initialize/enable/interrupt/power/
configure/nonblocking API family in AmbiqSuite 5.1.0 public replay commit
`5efc0228528a8adce5eae0d226fac85d2551eb3b`. Fifteen calls reach exact
source-owned CMSIS-FreeRTOS v10.5.1 mutex/semaphore wrappers; the remainder are
admitted EasyLogger, nanopb's source-owned 48-byte stream initializer, bounded
IAR memory primitives, and a first-party delay wrapper. The stock image still
predates the public Ambiq import, so that commit is the authenticated source
oracle—not proof of the private generating commit. The wrapper is not yet
production-routed and hardware I2C validation remains necessary.
