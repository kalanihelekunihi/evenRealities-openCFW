/* Isolated minimum-span placement, not the full Apollo RAM layout. */
SECTIONS
{
  .g2_ble_subsystem_state 0x20071670 (NOLOAD) :
  {
    KEEP(*(.bss.g2.ram.ble_subsystem_state))
  }
}
