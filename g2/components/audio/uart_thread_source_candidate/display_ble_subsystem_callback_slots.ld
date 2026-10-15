/* Isolated Apollo callback-cell placement fragment. */
SECTIONS
{
  .g2_ble_primary_callback_slot 0x200740fc (NOLOAD) :
  {
    KEEP(*(.bss.g2.ram.ble_subsystem_primary_callback_slot))
  }
  .g2_ble_callback_slot 0x20074100 (NOLOAD) :
  {
    KEEP(*(.bss.g2.ram.ble_subsystem_callback_slot))
  }
}
