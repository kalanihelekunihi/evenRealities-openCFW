/* Bounded Apollo Main RAM placement fragment, not a complete image layout. */
SECTIONS {
  . = 0x00600000;
  .text : { *(.text*) }
  .rodata : { *(.rodata*) }
  . = 0x200014e8;
  .data.opencfw.terminal.voice_frames : {
    KEEP(*(.data.opencfw.terminal.voice_frames))
  }
}
ASSERT(SIZEOF(.data.opencfw.terminal.voice_frames) == 0x4c,
       "voice frame pointer table must be 19 words");
