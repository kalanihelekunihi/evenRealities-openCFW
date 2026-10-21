/* Isolated placement proof. Integrate after the full Apollo RAM map is checked. */
SECTIONS {
  .bss.opencfw.file.lfs_context 0x20071ac8 (NOLOAD) : {
    KEEP(*(.bss.opencfw.file.lfs_context))
  }
}
INSERT AFTER .bss;
ASSERT(SIZEOF(.bss.opencfw.file.lfs_context) == 0x80,
       "LittleFS context size")
ASSERT(ADDR(.bss.opencfw.file.lfs_context) + SIZEOF(.bss.opencfw.file.lfs_context)
       <= 0x20071cc8, "LittleFS context before EFS transfer state")
