ENTRY(reset)
SECTIONS {
  . = 0x00000000;
  .vectors : { *(.vectors) }
  .text : { *(.text*) }
}
