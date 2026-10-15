/* Include in the final Apollo linker script. This section must remain
 * uninitialized so the 0x48e900 validator can inspect retained contents. */
SECTIONS {
  .noinit.ring_persist (NOLOAD) : {
    KEEP(*(.noinit.ring_persist))
  }
}
INSERT AFTER .bss;
