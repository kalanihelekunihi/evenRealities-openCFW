SECTIONS { .b0 0x8b8e8 : { *(.text.r1_event_service_0008b8e8) } .b1 0x8d6ac : { *(.text.r1_hr_latest_sample) } .b2 0x8d858 : { *(.text.r1_hrv_latest_sample) } .b3 0x8e524 : { *(.text.r1_spo2_latest_sample) } .b4 0x5ace8 : { *(.text.r1_hr_latest_packed) } .b5 0x5af20 : { *(.text.r1_hrv_latest_packed) } .b6 0x5baf4 : { *(.text.r1_spo2_latest_packed) } .b7 0x83930 : { *(.text.r1_health_get_hr_encode) } .b8 0x83972 : { *(.text.r1_health_get_hrv_encode) } .b9 0x83c20 : { *(.text.r1_health_get_spo2_encode) } .b10 0x82ef4 : { *(.text.r1_protocol_health_sample_send) } .templates 0x99bc8 : { *(.r1.health.get.templates) } .cache0 0x2001654c : { *(.r1.health.cache.hr) } .cache1 0x200165a0 : { *(.r1.health.cache.spo2) } .cache5 0x200169c0 : { *(.r1.health.cache.hrv) } /DISCARD/ : { *(.ARM.exidx*) } }
r1_structured_log_mode_get = 0x914ed;
r1_structured_log_format = 0x91639;
nrf_log_frontend_std_2 = 0x799d7;
r1_time_backend_timestamp = 0x8ada5;
r1_time_utc_offset_get = 0x8adb5;
r1_health_notification_stage_0008c150 = 0x8c151;
r1_health_notification_stage_0008cd60 = 0x8cd61;
r1_health_notification_stage_0008c750 = 0x8c751;
r1_health_notification_stage_0008baec = 0x8baed;
r1_health_notification_stage_0008b818 = 0x8b819;
r1_event_publish = 0x8d8fd;
r1_phone_connection_handle_get = 0x4cba5;
r1_protocol_send_flag_set_a = 0x8280d;
r1_protocol_send_response = 0x828b5;
__start_log_const_data = 0xc441c; r1_health_notification_last_timestamp = 0x200067a4;
