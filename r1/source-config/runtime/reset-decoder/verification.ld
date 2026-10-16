SECTIONS {
 .text 0x01000000 : { *(.text*) *(.rodata*) }
 .bounds 0x81bf8 : { *(.r1.reset.decode.bounds) }
 .zero_ring 0x81c00 : { *(.r1.reset.decode.zero_ring) }
 .zero_sdk 0x81c30 : { *(.r1.reset.decode.zero_sdk) }
 .pin_ring 0x81c5c : { *(.r1.reset.decode.pin_ring) }
 .pin_sdk 0x81c88 : { *(.r1.reset.decode.pin_sdk) }
 .dog_ring 0x81cac : { *(.r1.reset.decode.dog_ring) }
 .dog_sdk 0x81cd8 : { *(.r1.reset.decode.dog_sdk) }
 .sreq_ring 0x81cfc : { *(.r1.reset.decode.sreq_ring) }
 .sreq_sdk 0x81d38 : { *(.r1.reset.decode.sreq_sdk) }
 .pc_ring 0x81d6c : { *(.r1.reset.decode.pc_ring) }
 .pc_sdk 0x81da8 : { *(.r1.reset.decode.pc_sdk) }
 .lr_ring 0xbdbbc : { *(.r1.reset.decode.lr_ring) }
 .lr_sdk 0x81de4 : { *(.r1.reset.decode.lr_sdk) }
 .tag_ring 0x81e24 : { *(.r1.reset.decode.tag_ring) }
 .tag_sdk 0x81e60 : { *(.r1.reset.decode.tag_sdk) }
 .caller_ring 0x81e94 : { *(.r1.reset.decode.caller_ring) }
 .caller_sdk 0x81ed0 : { *(.r1.reset.decode.caller_sdk) }
 .unread_ring 0x81f08 : { *(.r1.reset.decode.unread_ring) }
 .unread_sdk 0x81f34 : { *(.r1.reset.decode.unread_sdk) }
 .lock_ring 0x81f5c : { *(.r1.reset.decode.lock_ring) }
 .lock_sdk 0x81f8c : { *(.r1.reset.decode.lock_sdk) }
 .off_ring 0x82040 : { *(.r1.reset.decode.off_ring) }
 .off_sdk 0x82080 : { *(.r1.reset.decode.off_sdk) }
 .lpcomp_ring 0x820b8 : { *(.r1.reset.decode.lpcomp_ring) }
 .lpcomp_sdk 0x820f4 : { *(.r1.reset.decode.lpcomp_sdk) }
 .dif_ring 0xbdb78 : { *(.r1.reset.decode.dif_ring) }
 .dif_sdk 0x82130 : { *(.r1.reset.decode.dif_sdk) }
 .lr_pointer 0x81de0 : { *(.r1.reset.decode.lr_pointer) }
 .dif_pointer 0x8212c : { *(.r1.reset.decode.dif_pointer) }
 /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment) *(.note*) }
}
r1_structured_log_mode_get = 0x20000201;
r1_structured_log_format = 0x20000211;
nrf_log_frontend_std_0 = 0x20000221;
nrf_log_frontend_std_1 = 0x20000231;
r1_reset_trace_program_counter_read = 0x20000241;
r1_reset_trace_return_address_read = 0x20000251;
r1_reset_trace_byte_read = 0x20000261;
