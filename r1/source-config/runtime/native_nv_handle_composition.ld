SECTIONS {
 .r1.nv.handles : {
  r1_nv_handles_begin = .;
  *(.r1.battery.kv.devinfo.handle)
  *(.r1.nv.ble_mult.handle)
  *(.r1.nv.health.handle)
  *(.r1.nv.hsync.handle)
  *(.r1.battery.kv.power.handle)
  *(.r1.serial.kv.handle)
  *(.r1.nv.r_size.handle)
  r1_nv_handles_end = .;
 }
}
INSERT AFTER .data;
ASSERT(SIZEOF(.r1.nv.handles)==28,"native7-handle table")
ASSERT(r1_health_record_kv_handle-r1_nv_handles_begin==12,"hsync table offset")
ASSERT(r1_device_info_record_kv_handle==r1_nv_handles_begin,"dev_info table start")
