/* Isolated native placement for two existing source-owned BLE arrays. */
SECTIONS
{
  .g2_ble_subsystem_link_state 0x200719c8 (NOLOAD) :
  {
    KEEP(*(.bss.g2.ram.ble_subsystem_link_state))
  }
  .g2_ble_subsystem_rows 0x200733fc (NOLOAD) :
  {
    KEEP(*(.bss.g2.ram.ble_subsystem_rows))
  }
}
