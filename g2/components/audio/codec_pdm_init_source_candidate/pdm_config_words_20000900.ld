SECTIONS
{
  .data.opencfw.pdm.alternate_config 0x20000900 : { KEEP(*(.data.opencfw.pdm.alternate_config)) }
  .data.opencfw.pdm.alternate_descriptor 0x2000091c : { KEEP(*(.data.opencfw.pdm.alternate_descriptor)) }
  .data.opencfw.pdm.production_config 0x20000928 : { KEEP(*(.data.opencfw.pdm.production_config)) }
  .data.opencfw.pdm.production_descriptor 0x20000944 : { KEEP(*(.data.opencfw.pdm.production_descriptor)) }
}
ASSERT(SIZEOF(.data.opencfw.pdm.alternate_config) == 28, "alternate config size")
ASSERT(SIZEOF(.data.opencfw.pdm.alternate_descriptor) == 12, "alternate descriptor size")
ASSERT(SIZEOF(.data.opencfw.pdm.production_config) == 28, "production config size")
ASSERT(SIZEOF(.data.opencfw.pdm.production_descriptor) == 12, "production descriptor size")
