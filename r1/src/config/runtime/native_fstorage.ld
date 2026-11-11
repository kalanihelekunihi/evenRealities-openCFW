/* Writable SDK instance records. Final firmware placement must include this
 * section in the initialized RAM copy span; composition only defines bounds. */
SECTIONS
{
 .fs_data 0 : ALIGN(4)
 {
  __start_fs_data = .;
  /* Device flash must participate in global busy scans before FDS. */
  KEEP(*(.r1.flash.fstorage))
  KEEP(*(.fs_data .fs_data.*))
  __stop_fs_data = .;
 }
}
ASSERT((SIZEOF(.fs_data) % 20) == 0, "fstorage registry contains incomplete instances")
