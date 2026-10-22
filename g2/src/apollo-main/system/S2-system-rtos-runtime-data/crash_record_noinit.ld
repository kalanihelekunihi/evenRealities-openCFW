/* Include in the final Apollo linker script. The crash record must stay
 * uninitialised across a warm reset (stock RAM 0x20075048, past the startup
 * zero-init range [0x20004558, 0x20075048)). */
SECTIONS {
  .noinit.crash_record (NOLOAD) : {
    KEEP(*(.noinit.crash_record))
  }
}
INSERT AFTER .bss;
