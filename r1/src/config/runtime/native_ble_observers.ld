/* Relocatable source composition. The legacy SDK iterator uses four
 * independent handler/context ranges. Keep boundaries section-relative so
 * a later firmware link can place each range without absolute stock RAM or
 * flash addresses. Entries have one existing C owner; no records are added. */
SECTIONS
{
 .sdh_ble_observers0 0 : ALIGN(4)
 {
  __start_sdh_ble_observers0 = .;
  KEEP(*(.sdh_ble_observers0 .sdh_ble_observers0.*))
  __stop_sdh_ble_observers0 = .;
 }
 .sdh_ble_observers1 0 : ALIGN(4)
 {
  __start_sdh_ble_observers1 = .;
  KEEP(*(.sdh_ble_observers1 .sdh_ble_observers1.*))
  __stop_sdh_ble_observers1 = .;
 }
 .sdh_ble_observers2 0 : ALIGN(4)
 {
  __start_sdh_ble_observers2 = .;
  KEEP(*(.sdh_ble_observers2 .sdh_ble_observers2.*))
  __stop_sdh_ble_observers2 = .;
 }
 .sdh_ble_observers3 0 : ALIGN(4)
 {
  __start_sdh_ble_observers3 = .;
  KEEP(*(.sdh_ble_observers3 .sdh_ble_observers3.*))
  __stop_sdh_ble_observers3 = .;
 }
}
ASSERT((SIZEOF(.sdh_ble_observers0) % 8) == 0, "BLE priority 0 must contain observer pairs")
ASSERT((SIZEOF(.sdh_ble_observers1) % 8) == 0, "BLE priority 1 must contain observer pairs")
ASSERT((SIZEOF(.sdh_ble_observers2) % 8) == 0, "BLE priority 2 must contain observer pairs")
ASSERT((SIZEOF(.sdh_ble_observers3) % 8) == 0, "BLE priority 3 must contain observer pairs")
