#!/usr/bin/env python3
"""Account for every ownership entry without upgrading symbol hints to closure."""
import collections
import csv
import hashlib
import json
from pathlib import Path
import struct

ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'r1/research/source-build'
REPORTS=['native-gxt310-bus/report.json','native-gxt310-id/report.json','native-yhm-chip-id/report.json','native-device-checks/report.json','native-dfu-vector-set/report.json','native-dfu-svci-init/report.json','native-cmbacktrace-init/report.json','native-device-reset-startup/report.json','native-peripheral-module/report.json','native-application-entry/report.json','native-scatter-dispatch/report.json','native-scatter-data/report.json','native-scanf-core/report.json','native-sscanf-frontend/report.json','native-ctype/report.json','native-scanf-conversion/report.json','native-libc-sequences/report.json','native-libc-primitives/report.json','native-pow-core/report.json','native-pow-dispatch/report.json','native-sqrt-core-abi/report.json','native-powf-core/report.json','native-powf-dispatch/report.json','native-log/report.json','native-exp/report.json','native-expm1/report.json','native-tanh/report.json','native-atan/report.json','native-tanf/report.json','native-sinf/report.json','native-cosf/report.json','native-trig-reduce/report.json','native-atan2f/report.json','native-atanf/report.json','native-float-logs/report.json','native-expf-tanhf/report.json','native-math-special/report.json','native-math-round/report.json','native-double-directed/report.json','native-double-flags/report.json','native-math-selection/report.json','native-math-sqrt/report.json','native-float-sqrt/report.json','native-float-rounding/report.json','native-polynomial/report.json','native-float-bits/report.json','native-formatter-stream/report.json','native-rtt-write/report.json','native-formatter-wrappers/report.json','native-formatter-core/report.json','native-formatter-product/report.json','native-formatter-add/report.json','native-formatter-unsigned/report.json','native-formatter-decimal/report.json','native-formatter-output/report.json','native-protocol-device-info/report.json','native-protocol-device-status/report.json','native-protocol-event-handlers/report.json','native-protocol-modules/report.json','native-protocol-ingress/report.json','native-protocol-receive/report.json','native-protocol-port/report.json','native-protocol-fragment/report.json','native-protocol-fragment-state/report.json','native-protocol-send-registration/report.json','native-protocol-send-hook/report.json','native-protocol-connection-gates/report.json','native-protocol-encoder/report.json','native-protocol-response/report.json','native-phone-operation/report.json','native-protocol-response-header/report.json','native-battery-protocol/report.json','native-battery-frame/report.json','native-battery-voltage/report.json','native-kv-device-fields/report.json','native-battery-low/report.json','native-battery-diagnostic/report.json','native-battery-initial-curve/report.json','native-battery-recovery/report.json','native-battery-cadence/report.json','native-battery-configuration/report.json','native-battery-discharge/report.json','native-battery-filter/report.json','native-yhm-system-track/report.json','native-yhm-status/report.json','native-yhm-state/report.json','native-stacmd-state/report.json','native-stacmd-receive/report.json','native-stacmd-transmit/report.json','native-stacmd-frames/report.json','native-stacmd-write-retry/report.json','native-stacmd-delay/report.json','native-stacmd-recovery/report.json','native-stacmd-operations/report.json','native-yhm-initialize/report.json','native-yhm-transport/report.json','native-yhm-frontend/report.json','native-charger-state/report.json','native-battery-control/report.json','native-battery-statistics/report.json','native-battery-runtime/report.json','native-status-record/report.json','native-thread-init-logs/report.json','native-delayed-cancel/report.json','rtos-timer-new/report.json','rtos-timer-id/report.json','native-delayed-worker/report.json','native-delayed-initialize/report.json','native-delayed-state/report.json','native-delayed-reschedule/report.json','rtos-timer-controls/report.json','rtos-timer-active/report.json','native-delayed-push/report.json','native-delayed-schedule/report.json','rtos-notification-wrappers/report.json','rtos-notification-tasks/report.json','rtos-event-groups/report.json','rtos-timer-pend/report.json','rtos-unordered-event/report.json','rtos-synchronization/report.json','rtos-mutex-kernel/report.json','rtos-mutex-tasks/report.json','rtos-message-queue/report.json','rtos-queue-receive-isr/report.json','rtos-timer-runtime/report.json','rtos-timer-queue/report.json','rtos-timer-task-wait/report.json','rtos-timer-api/report.json','rtos-timer-isr-queue/report.json','rtos-task-count/report.json','native-stack-overflow/report.json','rtos-context-port/report.json','rtos-port-start/report.json','rtos-scheduler-start/report.json','rtos-sleep-kernel/report.json','rtos-tickless-port/report.json','rtos-idle/report.json','rtos-task-termination/report.json','rtos-thread-new/report.json','native-task-construction/report.json','rtos-task-wait/report.json','rtos-queue-operations/report.json','rtos-scheduler-tick/report.json','rtos-scheduler-resume/report.json','native-heap/report.json','rtos-queue-create/report.json','rtos-semaphore-new/report.json','native-output-gpio-registration/report.json','native-stacmd-registration/report.json','native-hw-twi-registration/report.json','native-initcalls/report.json','native-rtc-discovery/report.json','native-rtc-error/report.json','sdk-nrfx-rtc/report.json','native-rtc-lifecycle/report.json','native-rtc-device/report.json','runtime-memmove/report.json','native-clock-calendar/report.json','native-clock-port/report.json','native-clock-bootstrap/report.json','native-rtt-delay/report.json','native-log-calendar/report.json','sdk-log-modules/report.json','sdk-fprintf/report.json','sdk-log-formatter/report.json','sdk-log-serial/report.json','sdk-segger-rtt/report.json','sdk-rtt-backend/report.json','sdk-memobj/report.json','sdk-logger-frontend/report.json','sdk-dfu-state/report.json','sdk-power-management/report.json','sdk-nrfx-clock/report.json','sdk-clock/report.json','sdk-soc/report.json','sdk-sdh/report.json','sdk-atfifo/report.json','sdk-fstorage-sd/report.json','sdk-fstorage/report.json','native-internal-flash-operations/report.json','native-internal-flash/report.json','native-fal-device/report.json','sdk-fal-partition/report.json','sdk-fal-device/report.json','runtime-strncmp/report.json','sdk-fal-core/report.json','native-kv-scans/report.json','sdk-fal-readiness/report.json','native-kv-initialize/report.json','native-kv-store-put/report.json','native-kv-store-get/report.json','native-kv-port/report.json','native-kv-class/report.json','native-advertising-configuration/report.json','sdk-advertising-init/report.json','sdk-advertising/report.json','native-gatt/report.json','sdk-gatt/report.json','sdk-qwr/report.json','sdk-ble-dispatch/report.json','sdk-connection-events/report.json','sdk-connection-index/report.json','sdk-link-context/report.json','native-bae8-send/report.json','native-ble-send/report.json','native-output/report.json','watchdog-logging/report.json','sdk-critical/report.json','integer-runtime/report.json','report.json','bootloader/report.json','public-providers/report.json','rtos/report.json','crypto/report.json','application-sdk/report.json','goodix/report.json','sensors/report.json','i2c5/report.json','software-twi/gpio-report.json','gpio/report.json','adc/report.json','runtime/report.json','board-seams/report.json','structured-log/report.json','rtos-critical/report.json','structured-encode/report.json','structured-time/report.json','rtos-ticks/report.json','structured-float/report.json','structured-cache/report.json','structured-cache-copy/report.json','native-events/report.json','connection-handle/report.json','native-tx/report.json','native-task-lifecycle/report.json','native-tasks/report.json','native-sync/report.json','native-watchdog/report.json','native-event-dispatch/report.json','watchdog-startup/report.json']
VERIFIED={
 '0x00050efc':('r1_gxt310_bus_release','native-gxt310-bus/verification.json'),
 '0x00050f08':('r1_i2c2_handle_cache','native-gxt310-bus/verification.json'),
 '0x00050f28':('r1_gxt310_bus_acquire','native-gxt310-bus/verification.json'),
 '0x00050f34':('r1_gxt310_transfer_read_native','native-gxt310-bus/verification.json'),
 '0x00050f5c':('r1_gxt310_transfer_write_native','native-gxt310-bus/verification.json'),
 '0x0006f640':('r1_gxt310_register_read_native','native-gxt310-bus/verification.json'),
 '0x0006f644':('r1_gxt310_register_write_native','native-gxt310-bus/verification.json'),
 '0x0006f53c':('r1_gxt310_chip_id_native','native-gxt310-id/verification.json'),
 '0x0006f812':('r1_gxt310_chip_id_channel0','native-gxt310-id/verification.json'),
 '0x0006f82c':('r1_gxt310_chip_id_channel2','native-gxt310-id/verification.json'),
 '0x0003530c':('r1_yhm_chip_id_native','native-yhm-chip-id/verification.json'),
 '0x0003510c':('r1_yhm_configure_native','native-device-checks/verification.json'),
 '0x00050ecc':('r1_gxt310_self_check','native-device-checks/verification.json'),
 '0x00078590':('nrf_dfu_svci_vector_table_set','native-dfu-vector-set/verification.json'),
 '0x00052018':('ble_dfu_buttonless_async_svci_init','native-dfu-svci-init/verification.json'),
 '0x000588a4':('cm_backtrace_init','native-cmbacktrace-init/verification.json'),
 '0x0005c4c8':('r1_device_module_init','native-device-reset-startup/verification.json'),
 '0x0004e9ec':('r1_rtc_open_enable','native-device-reset-startup/verification.json'),
 '0x0004e9e8':('r1_device_init_thunk_4e9e8','native-device-reset-startup/verification.json'),
 '0x00077e98':('r1_reset_reason_nordic_adapter','native-device-reset-startup/verification.json'),
 '0x0004e1e4':('r1_native_boot_initcall_dispatch','native-boot-ctors/verification.json'),
 '0x00050384':('r1_peripheral_module_init','native-peripheral-module/verification.json'),
 '0x00075f64':('r1_native_application_entry','native-application-entry/verification.json'),
 '0x000283a0':('r1_native_scatterload','native-scatter-dispatch/verification.json'),
 '0x00027208':('r1_native_runtime_entry','native-scatter-dispatch/verification.json'),
 '0x000286f4':('r1_native_scatter_decompress','native-scatter-data/verification.json'),
 '0x00027898':('r1_native_sscanf','native-scanf-core/verification.json'),
 '0x0002801c':('r1_native_scanf_descriptor_init','native-scanf-core/entry-verification.json'),
 '0x000283c4':('r1_native_scanf_core','native-scanf-core/verification.json'),
 '0x000275ec':('r1_native_ctype_pointer','native-ctype/verification.json'),
 '0x000275f4':('r1_native_isspace','native-ctype/verification.json'),
 '0x000278d0':('r1_native_scanf_integer','native-scanf-conversion/verification.json'),
 '0x00027a1c':('r1_native_scanf_string','native-scanf-conversion/verification.json'),
 '0x00028038':('r1_native_scanf_input_getc','native-scanf-conversion/verification.json'),
 '0x00028056':('r1_native_scanf_input_ungetc','native-scanf-conversion/verification.json'),

 '0x00027606':('r1_native_qsort','native-libc-sequences/verification.json'),
 '0x000277c0':('r1_native_strcat','native-libc-sequences/verification.json'),
 '0x000277d8':('r1_native_strncpy','native-libc-sequences/verification.json'),
 '0x0002781a':('r1_native_memcmp','native-libc-sequences/verification.json'),
 '0x00027854':('r1_native_strtok','native-libc-sequences/verification.json'),

 '0x000276a4':('r1_native_rand','native-libc-primitives/verification.json'),
 '0x000276b8':('r1_native_srand','native-libc-primitives/verification.json'),
 '0x00027ff4':('r1_native_scanf_digit','native-libc-primitives/verification.json'),
 '0x00028010':('r1_native_scanf_format_getc','native-libc-primitives/verification.json'),

 '0x000399d0':('r1_native_pow','native-pow-dispatch/source-verification.json'),
 '0x00090e8c':('r1_native_sqrt_core_abi_bits','native-sqrt-core-abi/verification.json'),
 '0x0003a620':('r1_native_powf','native-powf-dispatch/source-verification.json'),
 '0x00039320':('r1_native_log','native-log/verification.json'),
 '0x00038bb0':('r1_native_exp','native-exp/verification.json'),
 '0x0003b5c0':('r1_native_expm1','native-expm1/verification.json'),
 '0x0003b1c8':('r1_native_tanh','native-tanh/source-verification.json'),
 '0x000381f0':('r1_native_atan','native-atan/verification.json'),
 '0x0003b048':('r1_native_tanf','native-tanf/verification.json'),
 '0x0003ae04':('r1_native_sinf','native-sinf/verification.json'),
 '0x00038a5c':('r1_native_cosf','native-cosf/verification.json'),
 '0x0003bb04':('r1_native_trig_reduce32','native-trig-reduce/verification.json'),
 '0x000384c8':('r1_native_atan2f','native-atan2f/verification.json'),
 '0x00038774':('r1_native_atanf','native-atanf/verification.json'),
 **{a:(n,'native-float-logs/verification.json') for a,n in [('0x000396e4','r1_native_log10f'),('0x00039864','r1_native_logf')]},
 **{a:(n,'native-expf-tanhf/verification.json') for a,n in [('0x00038f08','r1_native_expf'),('0x0003b328','r1_native_tanhf')]},
 **{a:(n,'native-math-special/verification.json') for a,n in [('0x0003b508', 'r1_math_divzero64'), ('0x0003b538', 'r1_math_self_add64'), ('0x0003b54c', 'r1_math_add64'), ('0x0003b560', 'r1_math_invalid64'), ('0x0003b580', 'r1_math_high_square64'), ('0x0003b5a0', 'r1_math_low_square64'), ('0x0003bab4', 'r1_math_divzero32'), ('0x0003bac8', 'r1_math_self_add32'), ('0x0003bace', 'r1_math_add32'), ('0x0003bad4', 'r1_math_invalid32'), ('0x0003bae4', 'r1_math_high_square32'), ('0x0003baf4', 'r1_math_low_square32')]},
 **{a:(n,'native-math-round/verification.json') for a,n in [('0x0003ac88','r1_native_round'),('0x0003ad68','r1_native_roundf')]},
 **{a:(n,'native-double-directed/verification.json') for a,n in [('0x000388d8','r1_native_ceil'),('0x00039108','r1_native_floor')]},
 **{a:(n,'native-double-flags/verification.json') for a,n in [('0x00027f0c','r1_binary64_compare_reverse_flags'),('0x00027f3c','r1_binary64_compare_flags')]},
 **{a:(n,'native-math-selection/verification.json') for a,n in [('0x00028364','r1_binary32_compare_flags'),('0x000389f0','r1_native_ceilf'),('0x00039220','r1_native_floorf'),('0x00039290','r1_native_fmaxf'),('0x000392d8','r1_native_fminf'),('0x000390f0','r1_native_fabs'),('0x000620f4','r1_native_fabs_core_bits'),('0x00098eca','r1_native_compare_absf')]},
 **{a:(n,r) for a,n,r in [('0x0002820a','r1_binary64_square_root_bits','native-float-sqrt/verification.json'),('0x0003af94','r1_native_sqrt','native-math-sqrt/verification.json'),('0x0003b00e','r1_native_sqrtf','native-math-sqrt/verification.json'),('0x0003bc9c','r1_native_errno_set','native-math-sqrt/verification.json')]},
 **{a:(n,'native-float-rounding/verification.json') for a,n in [('0x00027e0c','r1_signed64_to_binary32_bits'),('0x0002808a','r1_binary32_pack_words'),('0x000280e6','r1_binary32_round_integral_bits'),('0x000282ac','r1_binary64_round_integral_bits')]},
 '0x0003b40c':('r1_native_polynomial','native-polynomial/verification.json'),
 '0x00038110':('r1_binary64_classify_bits','native-float-bits/verification.json'),
 '0x00038140':('r1_binary32_classify_bits','native-float-bits/verification.json'),
 '0x00027e38':('r1_signed32_to_binary64_bits','native-float-bits/verification.json'),
 '0x00027e5a':('r1_unsigned32_to_binary64_bits','native-float-bits/verification.json'),
 '0x00027e74':('r1_binary64_to_signed32_bits','native-float-bits/verification.json'),
 '0x00027eb2':('r1_binary64_to_unsigned32_bits','native-float-bits/verification.json'),
 '0x00027ee4':('r1_binary32_to_binary64_bits','native-float-bits/verification.json'),
 '0x00027c3e':('r1_binary64_subtract_bits','native-float-bits/verification.json'),
 '0x00027c44':('r1_binary64_reverse_subtract_bits','native-float-bits/verification.json'),
 '0x000281dc':('r1_binary64_scale_power2_bits','native-float-bits/verification.json'),
 '0x0002839a':('r1_native_floating_environment_control','native-float-bits/verification.json'),
 '0x00038060':('r1_native_printf','native-formatter-stream/verification.json'),
 '0x000380b4':('r1_native_sprintf','native-formatter-stream/verification.json'),
 '0x00044a6c':('r1_format_unbounded_putc','native-formatter-stream/verification.json'),
 '0x0006570a':('r1_format_stdout_putc','native-formatter-stream/verification.json'),
 '0x000319e0':('r1_stdout_write','native-rtt-write/verification.json'),
 '0x00038080':('r1_native_snprintf','native-formatter-wrappers/verification.json'),
 '0x000380dc':('r1_native_vsnprintf','native-formatter-wrappers/verification.json'),
 '0x00043080':('r1_format_core','native-formatter-core/verification.json'),
 '0x00027c4a':('r1_format_double_multiply_bits','native-formatter-product/verification.json'),
 '0x00027d2e':('r1_format_double_divide_bits','native-formatter-product/verification.json'),
 '0x00027afc':('r1_format_double_add_bits','native-formatter-add/verification.json'),
 '0x00027fd0':('r1_format_signed_shift_bits','native-formatter-add/verification.json'),
 '0x00028122':('r1_format_double_round_bits','native-formatter-add/verification.json'),
 '0x00028140':('r1_format_double_normalize_bits','native-formatter-add/verification.json'),
 '0x00028334':('r1_format_double_to_unsigned_bits','native-formatter-unsigned/verification.json'),
 '0x0003f530':('r1_format_decimal_digits','native-formatter-decimal/verification.json'),
 '0x00043734':('r1_format_left_padding','native-formatter-output/verification.json'),
 '0x00043758':('r1_format_width_padding','native-formatter-output/verification.json'),
 '0x00043bbc':('r1_format_bounded_putc','native-formatter-output/verification.json'),
 '0x00083d5c':('r1_device_info_handler','native-protocol-device-info/verification.json'),
 '0x00083872':('r1_system_response_wrapper','native-protocol-device-info/verification.json'),
 '0x00083de4':('r1_device_status_handler','native-protocol-device-status/verification.json'),
 '0x00091244':('r1_charge_state_is_full','native-protocol-device-status/verification.json'),
 '0x00091256':('r1_charge_state_is_active','native-protocol-device-status/verification.json'),
 '0x00082c10':('r1_activity_refresh_handler','native-protocol-event-handlers/verification.json'),
 '0x00082be8':('r1_health_registration_dispatcher','native-protocol-modules/verification.json'),
 '0x00083ca8':('r1_eus_system_dispatch_plan_build','native-protocol-modules/verification.json'),
 '0x00084c98':('r1_ble_event_dispatch','native-protocol-modules/verification.json'),
 '0x00083298':('r1_health_registration_binary_search','native-protocol-modules/verification.json'),
 '0x0008316c':('r1_eus_ingress_plan_decode','native-protocol-ingress/verification.json'),
 '0x000826b4':('r1_proto_ble_recv_validate','native-protocol-receive/verification.json'),
 '0x000830a8':('r1_proto_port_init','native-protocol-port/verification.json'),
 '0x000832d4':('r1_proto_register_ble_recv_callback','native-protocol-port/verification.json'),
 '0x00032408':('r1_fragment_message','native-protocol-fragment/verification.json'),
 '0x00083448':('r1_protocol_send_callback_set','native-protocol-send-registration/verification.json'),
 '0x000827f8':('r1_protocol_send_hook_call','native-protocol-send-hook/verification.json'),
 '0x0004cbb0':('r1_authenticated_phone_connection_gate','native-protocol-connection-gates/verification.json'),
 '0x0004cb40':('r1_peer_channel_b_valid','native-protocol-connection-gates/verification.json'),
 '0x00082f9c':('r1_model_encode','native-protocol-encoder/verification.json'),
 '0x000828b4':('r1_protocol_send_response','native-protocol-response/verification.json'),
 **{a:(n,'native-phone-operation/verification.json') for a,n in [('0x00083896','r1_phone_cmd_send_op1'),('0x00084c0c','r1_protocol_response_send_0x100')]},
 '0x0008345c':('r1_proto_report_battery_status','native-battery-protocol/verification.json'),
 '0x0003e274':('dispatch','native-battery-runtime/frame-tx-integration-verification.json'),
 '0x000913fc':('r1_glasses_tag_frame_send','native-battery-frame/verification.json'),
 '0x00091290':('r1_battery_voltage_get','native-battery-voltage/verification.json'),
 '0x00031fcc':('r1_battery_runtime_service','native-battery-runtime/voltage-integration-verification.json'),
 '0x00073710':('r1_kv_dev_info_fields_set','native-kv-device-fields/verification.json'),
 '0x0003d88c':('r1_battery_low_escalation','native-battery-low/verification.json'),
 '0x0003d9b8':('r1_battery_diagnostic_cadence_step','native-battery-diagnostic/verification.json'),
 '0x0004ff3c':('r1_battery_charging_initial_curve','native-battery-initial-curve/verification.json'),
 '0x0003db70':('r1_battery_stuck_charge_recovery','native-battery-recovery/verification.json'),
 '0x0004fe70':('r1_battery_charging_cadence','native-battery-cadence/verification.json'),
 **{a:(n,'native-battery-configuration/verification.json') for a,n in [('0x0007bb44','r1_batcfg_byte0_get'),('0x0007bb5c','r1_batcfg_flag1_get'),('0x0007bb7c','r1_batcfg_word1_signed_get')]},
 '0x00050004':('r1_battery_discharge_curve','native-battery-discharge/verification.json'),
 '0x00091184':('r1_battery_five_sample_filter_and_conversion','native-battery-filter/verification.json'),
 **{a:(n,'native-stacmd-receive/verification.json') for a,n in [('0x00087b30','r1_stacmd_read_bit_native'),('0x000969ec','r1_stacmd_read_bit_adapter_native')]},
 **{a:(n,'native-stacmd-transmit/verification.json') for a,n in [('0x0005cbe4','r1_stacmd_drive_bit_native'),('0x0005cc68','r1_stacmd_write_bits_native'),('0x0005cccc','r1_stacmd_idle_native'),('0x000968a8','r1_stacmd_parity_native')]},
 **{a:(n,'native-stacmd-frames/verification.json') for a,n in [('0x00028bb0','r1_stacmd_read_frame_native'),('0x00028c6c','r1_stacmd_write_frame_native')]},
 '0x00035698':('r1_stacmd_write_retry_native','native-stacmd-write-retry/verification.json'),
 '0x0005c0fa':('r1_stacmd_recovery_delay_native','native-stacmd-delay/verification.json'),
 '0x0005cc8c':('r1_stacmd_bus_recovery_native','native-stacmd-recovery/verification.json'),
 **{a:(n,'native-stacmd-operations/verification.json') for a,n in [('0x00056568','r1_stacmd_close'),('0x0005657c','r1_stacmd_open'),('0x00056590','r1_stacmd_read'),('0x0005660c','r1_stacmd_write')]},
 '0x00050578':('r1_yhm_device_handles_initialize','native-yhm-initialize/verification.json'),
 **{a:(n,'native-yhm-transport/verification.json') for a,n in [('0x00035760','r1_yhm_register_write_native'),('0x000507cc','r1_yhm_register_read_record'),('0x00050608','r1_yhm_transport_acquire'),('0x000507a0','r1_yhm_transport_release')]},
 **{a:(n,'native-yhm-frontend/verification.json') for a,n in [('0x0003541c','r1_yhm_ready_native'),('0x0003540c','r1_yhm_register_read_native'),('0x00035412','r1_yhm_register_read_byte_native')]},
 **{a:(n,'native-yhm-system-track/verification.json') for a,n in [('0x000355bc','r1_yhm_system_track_native'),('0x0005079c','r1_native_charger_initialize')]},
 '0x0003529a':('r1_yhm_status_native','native-yhm-status/verification.json'),
 **{a:(n,'native-charger-state/verification.json') for a,n in [('0x00035272','r1_yhm_charge_state_native'),('0x00050618','r1_native_charger_state_get')]},
 **{a:(n,'native-battery-control/verification.json') for a,n in [('0x0004fe5c','r1_battery_charging_progress_reset'),('0x00077240','r1_battery_task_flags_set'),('0x00050778','r1_shared_power_client_acquire'),('0x00050758','r1_shared_power_client_release'),('0x000355a8','r1_yhm_shared_power_active')]},
 **{a:(n,'native-battery-statistics/verification.json') for a,n in [('0x0003dd0c','r1_battery_charged_state_refresh'),('0x0003dda0','r1_battery_voltage_average'),('0x0003d834','r1_battery_level_average')]},
 '0x00031fd0':('r1_battery_runtime_update_service','native-battery-runtime/verification.json'),
 **{a:(n,'native-status-record/verification.json') for a,n in [('0x0005e118','r1_status_record_ring_publish'),('0x00091264','r1_device_state_byte_2d_get'),('0x0004cb08','r1_peer_channel_count'),('0x00091270','r1_charge_state_byte_get')]},
 **{a:(n,'native-thread-init-logs/verification.json') for a,n in [('0x00045c84','r1_native_service_hardware_initialize'),('0x00045d00','r1_native_storage_hardware_initialize')]},
 '0x00065d64':('r1_native_delayed_cancel','native-delayed-cancel/verification.json'),
 **{a:(n,'rtos-timer-new/verification.json') for a,n in [('0x0007d90c','osTimerNew'),('0x0008569c','pvTimerGetTimerID')]},
 '0x00065f84':('r1_native_delayed_reschedule','native-delayed-reschedule/verification.json'),
 **{a:(n,'rtos-timer-controls/verification.json') for a,n in [('0x0007d9b0','osTimerStart'),('0x0007d9ea','osTimerStop'),('0x00098d68','xTimerIsTimerActive')]},
 '0x000659e8':('r1_native_delayed_push','native-delayed-push/verification.json'),
 '0x00065b4c':('r1_native_delayed_schedule','native-delayed-schedule/verification.json'),
 **{a:(n,'rtos-notification-wrappers/verification.json') for a,n in [('0x0007d154','osDelay'),('0x0007d1a0','osEventFlagsSet'),('0x0007d6f4','osThreadFlagsSet'),('0x0007d780','osThreadFlagsWait')]},
 **{a:(n,'rtos-notification-tasks/verification.json') for a,n in [('0x00095fd4','vTaskDelay'),('0x00098484','xTaskGenericNotify'),('0x000985ac','xTaskGenericNotifyFromISR'),('0x00098700','xTaskGenericNotifyWait')]},
 **{a:(n,'rtos-event-groups/verification.json') for a,n in [('0x000977de','xEventGroupGetBitsFromISR'),('0x000977f4','xEventGroupSetBits'),('0x0009787c','xEventGroupSetBitsFromISR')]},
 '0x000963e8':('vTaskRemoveFromUnorderedEventList','rtos-unordered-event/verification.json'),
 **{a:(n,'rtos-synchronization/verification.json') for a,n in [('0x0007d488','osMutexAcquire'),('0x0007d4d6','osMutexNew'),('0x0007d536','osMutexRelease'),('0x0007d57c','osSemaphoreAcquire'),('0x0007d5e8','osSemaphoreGetCount'),('0x0007d698','osSemaphoreRelease')]},
 **{a:(n,'rtos-mutex-kernel/verification.json') for a,n in [('0x0008507c','prvInitialiseMutex'),('0x00097ade','xQueueCreateMutex'),('0x00097af4','xQueueCreateMutexStatic'),('0x00097e6c','xQueueGiveFromISR'),('0x00097f14','xQueueGiveMutexRecursive'),('0x00098120','xQueueSemaphoreTake'),('0x00098284','xQueueTakeMutexRecursive')]},
 **{a:(n,'rtos-mutex-tasks/verification.json') for a,n in [('0x00085684','pvTaskIncrementMutexHeldCount'),('0x0009626c','vTaskPriorityDisinheritAfterTimeout'),('0x000989ac','xTaskPriorityInherit')]},
 **{a:(n,'rtos-message-queue/verification.json') for a,n in [('0x0007d310','osMessageQueueGet'),('0x0007d388','osMessageQueueGetCapacity'),('0x0007d390','osMessageQueueGetCount'),('0x0007d3b4','osMessageQueueNew'),('0x0007d40c','osMessageQueuePut')]},
 **{a:(n,'rtos-queue-receive-isr/verification.json') for a,n in [('0x0009807c','xQueueReceiveFromISR'),('0x00084ea4','prvCopyDataFromQueue')]},
 **{a:(n,'rtos-timer-runtime/verification.json') for a,n in [('0x000851f4','r1_timer_runtime_InsertTimerInActiveList'),('0x000852a0','r1_timer_runtime_ProcessExpiredTimer'),('0x000852e0','r1_timer_runtime_ProcessReceivedCommands'),('0x000853d4','r1_timer_runtime_ProcessTimerOrBlockTask'),('0x00085440','r1_timer_runtime_ReloadTimer'),('0x00085484','r1_timer_runtime_SampleTimeNow')]},
 **{a:(n,'rtos-timer-api/verification.json') for a,n in [('0x0008515a','r1_timer_initialise_new'),('0x00098c48','xTimerCreate'),('0x00098c7c','xTimerCreateStatic'),('0x00098d04','xTimerGenericCommand')]},
 **{a:(n,'rtos-timer-queue/verification.json') for a,n in [('0x00097f50','xQueueReceive'),('0x00095f8e','vQueueWaitForMessageRestricted')]},
 '0x000961b8':('vTaskPlaceOnEventListRestricted','rtos-timer-task-wait/verification.json'),
 '0x00097da4':('xQueueGenericSendFromISR','rtos-timer-isr-queue/verification.json'),
 '0x0009566c':('uxTaskGetNumberOfTasks','rtos-timer-isr-queue/verification.json'),
 '0x00095bfc':('vApplicationStackOverflowHook','native-stack-overflow/verification.json'),
 **{a:(n,'rtos-context-port/verification.json') for a,n in [('0x00027218','SVC_Handler'),('0x00027238','vPortStartFirstTask'),('0x0002725c','PendSV_Handler'),('0x000965ac','vTaskSwitchContext')]},
 '0x000979dc':('xPortStartScheduler','rtos-port-start/verification.json'),
 '0x00095da4':('vPortSetupTimerInterrupt','rtos-port-start/verification.json'),
 **{a:(n,'rtos-scheduler-start/verification.json') for a,n in [('0x000964c8','vTaskStartScheduler'),('0x00098ca8','xTimerCreateTimerTask'),('0x00084e58','r1_native_timer_infrastructure')]},
 '0x0005cf78':('eTaskConfirmSleepModeStatus','rtos-sleep-kernel/verification.json'),
 '0x0009653c':('vTaskStepTick','rtos-sleep-kernel/verification.json'),
 '0x00095de4':('vPortSuppressTicksAndSleep','rtos-tickless-port/verification.json'),
 **{a:(n,'rtos-task-termination/verification.json') for a,n in [('0x00084f68','r1_native_expected_idle_time'),('0x00096020','vTaskDelete'),('0x0005cfac','eTaskGetState'),('0x00084f36','r1_native_task_reclaim'),('0x0007d8d6','osThreadTerminate'),('0x00095cdc','vListInsertEnd')]},
 '0x0007d818':('osThreadNew','rtos-thread-new/verification.json'),
 **{a:(n,'native-task-construction/verification.json') for a,n in [('0x000850b6','r1_native_task_initialize'),('0x000983b8','r1_native_task_create'),('0x00098418','r1_native_task_create_static'),('0x00084d68','prvAddNewTaskToReadyList'),('0x000856c0','pxPortInitialiseStack'),('0x000854e0','prvTaskExitError'),('0x00095ca6','vListInitialiseItem')]},
 **{a:(n,'rtos-task-wait/verification.json') for a,n in [('0x00096160','vTaskInternalSetTimeOutState'),('0x00096170','vTaskMissedYield'),('0x00096188','vTaskPlaceOnEventList'),('0x00098340','xTaskCheckForTimeOut'),('0x00098910','xTaskPriorityDisinherit'),('0x00084cf0','prvAddCurrentTaskToDelayedList'),('0x0009560e','uxListRemove'),('0x00095cac','vListInsert')]},
 **{a:(n,'rtos-queue-operations/verification.json') for a,n in [('0x00097c50','xQueueGenericSend'),('0x00095f70','vQueueDelete'),('0x00084eca','prvCopyDataToQueue'),('0x00085534','prvUnlockQueue')]},
 **{a:(n,'rtos-scheduler-tick/verification.json') for a,n in [('0x000987e0','xTaskIncrementTick'),('0x00098a4c','xTaskRemoveFromEventList')]},
 **{a:(n,'rtos-scheduler-resume/verification.json') for a,n in [('0x0009659c','vTaskSuspendAll'),('0x00098b24','xTaskResumeAll'),('0x00085468','prvResetNextTaskUnblockTime')]},
 **{a:(n,'native-heap/verification.json') for a,n in [('0x00084f98','r1_heap_initialize'),('0x000851a4','r1_heap_insert'),('0x000855a0','pvPortMalloc'),('0x00095d48','vPortFree'),('0x00095bec','r1_malloc_failed_hook')]},
 **{a:(n,'rtos-queue-create/verification.json') for a,n in [('0x00097b0e','xQueueGenericCreate'),('0x00097b62','xQueueGenericCreateStatic'),('0x00097a88','xQueueCreateCountingSemaphore'),('0x00097ab0','xQueueCreateCountingSemaphoreStatic'),('0x00097ba4','xQueueGenericReset'),('0x00095c90','vListInitialise')]},
 '0x0007d60c':('osSemaphoreNew','rtos-semaphore-new/verification.json'),
 **{a:(n,'native-stacmd-registration/verification.json') for a,n in [('0x000565f4','r1_yhm2710_stacmd_binding_configuration'),('0x000791e4','r1_twi_gpio_low'),('0x000794ac','r1_twi_gpio_high'),('0x0007910c','r1_twi_gpio_output'),('0x000790aa','r1_twi_gpio_input'),('0x00079408','r1_twi_gpio_read'),('0x0007902c','r1_twi_gpio_release'),('0x0007a6fc','r1_stacmd_delay_us')]},
 **{a:(n,'native-hw-twi-registration/verification.json') for a,n in [('0x00054f90','r1_twi_primary_device_binding_configuration'),('0x00054fc4','r1_twi_secondary_device_binding_configuration')]},
 '0x0005cb6c':('r1_module_init_table_run','native-initcalls/verification.json'),
 '0x00050dc0':('r1_native_rtc_cached_device','board/rtc-startup-verification.json'),
 '0x0007294c':('r1_sdk_rtc_irq_dispatch','sdk-nrfx-rtc/irq-verification.json'),
 **{a:(n,'sdk-nrfx-rtc/verification.json') for a,n in [('0x0007ad6c','nrfx_rtc_init'),('0x0007ad20','nrfx_rtc_enable'),('0x0007ae4c','nrfx_rtc_tick_enable')]},
 **{a:(n,'native-rtc-lifecycle/verification.json') for a,n in [('0x000276c8','r1_native_rtc_gmtime'),('0x000562e0','r1_native_rtc_epoch_to_calendar'),('0x00056274','r1_native_rtc_tick'),('0x0005649c','r1_native_rtc_epoch_initialize'),('0x00056318','r1_native_rtc_open')]},
 **{a:(n,'native-rtc-device/verification.json') for a,n in [('0x0005639c','r1_native_rtc_snapshot'),('0x000563f8','r1_native_rtc_calendar_write'),('0x00056444','r1_native_rtc_callback_bind'),('0x0002775c','r1_native_memory_move')]},
 **{a:(n,'native-clock-calendar/verification.json') for a,n in [('0x00050d64','r1_clock_backend_slot20'),('0x00050d8a','r1_clock_backend_slot24'),('0x0005a8ac','time_calendar_broken_down_to_unix'),('0x0008ae58','time_calendar_to_utc'),('0x0008af40','time_calendar_utc_to_calendar')]},
 **{a:(n,'native-clock-port/verification.json') for a,n in [('0x00050df0','r1_clock_rtc_write'),('0x00050de0','r1_clock_rtc_bind'),('0x00050db6','r1_clock_backend_update'),('0x00050daa','r1_clock_backend_bind_tick'),('0x00051494','r1_clock_backend_slot12')]},
 '0x000780d2':('nrf_balloc_alloc','sdk-memobj/verification.json'),
 '0x00078116':('nrf_balloc_free','sdk-memobj/verification.json'),
 '0x00078146':('nrf_balloc_init','sdk-memobj/verification.json'),
 '0x00079bfe':('nrf_memobj_alloc','sdk-memobj/verification.json'),
 '0x00079c5e':('nrf_memobj_free','sdk-memobj/verification.json'),
 '0x00079c90':('nrf_memobj_get','sdk-memobj/verification.json'),
 '0x00079c98':('nrf_memobj_pool_init','sdk-memobj/verification.json'),
 '0x00079c9c':('nrf_memobj_put','sdk-memobj/verification.json'),
 '0x00079cba':('nrf_memobj_read','sdk-memobj/verification.json'),
 '0x00079cca':('nrf_memobj_write','sdk-memobj/verification.json'),
 '0x00079af4':('nrf_log_init','sdk-logger-frontend/initialization-verification.json'),
 '0x00079520':('nrf_log_backend_add','sdk-logger-frontend/initialization-verification.json'),
 '0x00079dcc':('nrf_ringbuf_init','sdk-logger-frontend/initialization-verification.json'),
 '0x00079576':('nrf_log_backend_rtt_init','sdk-rtt-backend/verification.json'),
 '0x0007968c':('nrf_log_default_backends_init','sdk-rtt-backend/verification.json'),
 '0x00036d68':('SEGGER_RTT_Init','sdk-segger-rtt/verification.json'),
 '0x00031948':('SEGGER_RTT_Init','sdk-segger-rtt/verification.json'),
 '0x00031a18':('SEGGER_RTT_WriteNoLock','sdk-segger-rtt/verification.json'),
 '0x00079598':('nrf_log_backend_serial_put','sdk-log-serial/verification.json'),
 '0x00079b48':('nrf_log_std_entry_process','sdk-log-formatter/verification.json'),
 '0x00079a44':('nrf_log_hexdump_entry_process','sdk-log-formatter/verification.json'),
 '0x000813e0':('postfix_process','sdk-log-formatter/verification.json'),
 '0x0008185c':('r1_log_prefix_process','sdk-log-formatter/verification.json'),
 '0x00078a40':('nrf_fprintf','sdk-fprintf/verification.json'),
 '0x00078a72':('nrf_fprintf_fmt','sdk-fprintf/verification.json'),
 '0x00078a5a':('nrf_fprintf_buffer_flush','sdk-fprintf/verification.json'),
 '0x00056744':('buffer_add','sdk-fprintf/verification.json'),
 '0x00072310':('int_print','sdk-fprintf/verification.json'),
 '0x00093ef8':('unsigned_print','sdk-fprintf/verification.json'),
 '0x0007965c':('nrf_log_color_id_get','sdk-log-modules/verification.json'),
 '0x0008ac28':('r1_log_local_datetime_fill','native-log-calendar/verification.json'),
 '0x00099340':('r1_rtt_delay_cycles','native-rtt-delay/verification.json'),
 '0x00099cb0':('r1_rtt_delay_cycles','native-rtt-delay/verification.json'),
 '0x00099cc0':('r1_rtt_delay_cycles','native-rtt-delay/verification.json'),
 '0x00099cd0':('r1_rtt_delay_cycles','native-rtt-delay/verification.json'),
 '0x00099ce0':('r1_rtt_delay_cycles','native-rtt-delay/verification.json'),
 '0x00099cf0':('r1_rtt_delay_cycles','native-rtt-delay/verification.json'),
 '0x00099d00':('r1_rtt_delay_cycles','native-rtt-delay/verification.json'),
 '0x00099d10':('r1_rtt_delay_cycles','native-rtt-delay/verification.json'),
 '0x0009a5f0':('r1_rtt_delay_cycles','native-rtt-delay/verification.json'),
 '0x0009a610':('r1_rtt_delay_cycles','native-rtt-delay/verification.json'),
 '0x0009a640':('r1_rtt_delay_cycles','native-rtt-delay/verification.json'),
 '0x0009a650':('r1_rtt_delay_cycles','native-rtt-delay/verification.json'),
 '0x0009a660':('r1_rtt_delay_cycles','native-rtt-delay/verification.json'),
 '0x0009a670':('r1_rtt_delay_cycles','native-rtt-delay/verification.json'),
 '0x0009a6a0':('r1_rtt_delay_cycles','native-rtt-delay/verification.json'),
 '0x0009a710':('r1_rtt_delay_cycles','native-rtt-delay/verification.json'),
 '0x0009bb10':('r1_rtt_delay_cycles','native-rtt-delay/verification.json'),
 '0x0009c790':('r1_rtt_delay_cycles','native-rtt-delay/verification.json'),
 '0x0009c7a0':('r1_rtt_delay_cycles','native-rtt-delay/verification.json'),
 '0x0009c9e0':('r1_rtt_delay_cycles','native-rtt-delay/verification.json'),
 '0x0009d3d0':('r1_rtt_delay_cycles','native-rtt-delay/verification.json'),
 '0x00079918':('nrf_log_frontend_hexdump','sdk-logger-frontend/frontend-verification.json'),
 '0x00079a0c':('nrf_log_frontend_std_5','sdk-logger-frontend/frontend-verification.json'),
 '0x00079a28':('nrf_log_frontend_std_6','sdk-logger-frontend/frontend-verification.json'),
 '0x0005a990':('r1_clock_backend_snapshot','native-clock-bootstrap/verification.json'),
 '0x000796a8':('nrf_log_frontend_dequeue','sdk-logger-frontend/frontend-verification.json'),
 '0x000799c0':('nrf_log_frontend_std_0','sdk-logger-frontend/frontend-verification.json'),
 '0x000799c8':('nrf_log_frontend_std_1','sdk-logger-frontend/frontend-verification.json'),
 '0x000799d6':('nrf_log_frontend_std_2','sdk-logger-frontend/frontend-verification.json'),
 '0x000799e6':('nrf_log_frontend_std_3','sdk-logger-frontend/frontend-verification.json'),
 '0x000799f8':('nrf_log_frontend_std_4','sdk-logger-frontend/frontend-verification.json'),
 '0x000566ac':('buf_prealloc','sdk-logger-frontend/frontend-verification.json'),
 '0x00056774':('buffer_is_empty','sdk-logger-frontend/frontend-verification.json'),
 '0x00072848':('invalid_packets_omit','sdk-logger-frontend/frontend-verification.json'),
 '0x00075ce4':('log_skip','sdk-logger-frontend/frontend-verification.json'),
 '0x00090fec':('std_n','sdk-logger-frontend/frontend-verification.json'),
 '0x0005ccfc':('dropped_sat16_get','sdk-logger-frontend/frontend-verification.json'),
 '0x00079b1c':('nrf_log_panic','sdk-logger-frontend/panic-verification.json'),
 **{entry:(name,'sdk-power-management/verification.json') for entry,name in (('0x00079d50','nrf_pwr_mgmt_shutdown'),('0x0008f234','r1_sdk_power_shutdown_process'),('0x000780b0','nrf_atomic_u32_fetch_store'))},
 '0x00030ac8':('POWER_CLOCK_IRQHandler','sdk-nrfx-clock/irq-verification.json'),
 **{entry:(name,'sdk-nrfx-clock/verification.json') for entry,name in (('0x0007a640','nrfx_clock_enable'),('0x0007a66c','nrfx_clock_init'),('0x0007a68c','nrfx_clock_lfclk_start'))},
 **{entry:(name,'sdk-clock/critical-integration-verification.json') for entry,name in (('0x000584d4','r1_sdk_clock_irq_handler'),('0x00072bca','r1_sdk_clock_item_enqueue'),('0x000788c8','nrf_drv_clock_init'),('0x00078990','nrf_drv_clock_lfclk_request'))},
 '0x0007a500':('r1_sdk_soc_events_poll','sdk-soc/verification.json'),
 **{entry:(name,'sdk-sdh/irq-integration-verification.json') for entry,name in (('0x0007a3ec','nrf_sdh_disable_request'),('0x0007a440','nrf_sdh_enable_request'),('0x0007a4b4','nrf_sdh_evts_poll'),('0x0007a4d8','nrf_sdh_is_enabled'),('0x0007a4e4','nrf_sdh_request_continue'))},
 **{entry:(name,'sdk-atfifo/verification.json') for entry,name in (('0x00077f40', 'nrf_atfifo_init'), ('0x00077f30', 'nrf_atfifo_clear'), ('0x00077f66', 'nrf_atfifo_item_alloc'), ('0x00077f7c', 'nrf_atfifo_item_free'), ('0x00077f92', 'nrf_atfifo_item_get'), ('0x00077fa8', 'nrf_atfifo_item_put'), ('0x000272b8', 'nrf_atfifo_wspace_req'), ('0x000272f0', 'nrf_atfifo_wspace_close'), ('0x00027302', 'nrf_atfifo_rspace_req'), ('0x0002733c', 'nrf_atfifo_rspace_close'), ('0x0002734e', 'nrf_atfifo_space_clear'), ('0x00078074', 'nrf_atomic_flag_set_fetch'), ('0x000780a6', 'nrf_atomic_u32_fetch_or'))},
 **{entry:(name,'sdk-fstorage-sd/verification.json') for entry,name in (('0x000710a0', 'r1_sdk_fstorage_sd_init'), ('0x00093ec4', 'r1_sdk_fstorage_sd_uninit'), ('0x00087b20', 'r1_sdk_fstorage_sd_read'), ('0x00096fe0', 'r1_sdk_fstorage_sd_write'), ('0x0005d514', 'r1_sdk_fstorage_sd_erase'), ('0x000883f8', 'r1_sdk_fstorage_sd_rmap'), ('0x00096e08', 'r1_sdk_fstorage_sd_wmap'), ('0x00072b70', 'r1_sdk_fstorage_sd_is_busy'), ('0x0005e644', 'r1_sdk_fstorage_sd_event_send'), ('0x000875dc', 'r1_sdk_fstorage_sd_queue_start'), ('0x00087468', 'r1_sdk_fstorage_sd_queue_free'), ('0x00078d08', 'nrf_fstorage_sys_evt_handler'), ('0x00078cd0', 'nrf_fstorage_sdh_req_handler'), ('0x00078ce8', 'nrf_fstorage_sdh_state_handler'))},
 **{entry:(name,'sdk-fstorage/verification.json') for entry,name in (('0x00078c78','nrf_fstorage_init'),('0x00078c4c','nrf_fstorage_erase'),('0x00078dac','nrf_fstorage_write'),('0x00078c80','nrf_fstorage_is_busy'))},
 **{entry:(name,'native-internal-flash-operations/verification.json') for entry,name in (('0x0005c40c','r1_internal_flash_page_erase'),('0x0005c464','r1_internal_flash_mapped_read'),('0x0005c480','r1_internal_flash_word_write'))},
 **{entry:(name,'native-internal-flash/verification.json') for entry,name in (('0x00054970','r1_internal_flash_callback_configuration'),('0x0005498c','r1_internal_flash_erase_and_geometry_control'),('0x000549f0','r1_internal_flash_fstorage_configuration'),('0x00054a4c','r1_internal_flash_device_read'),('0x00054a8c','r1_internal_flash_device_registration'),('0x00054aa4','r1_internal_flash_device_write'))},
 **{entry:(name,'native-fal-device/verification.json') for entry,name in (('0x00071054','r1_native_fal_device_initialize'),('0x00087af8','r1_native_fal_device_read'),('0x00096fb0','r1_native_fal_device_write'))},
 **{entry:(name,'sdk-fal-partition/verification.json') for entry,name in (('0x00063150','fal_partition_find'),('0x000631c0','fal_partition_init'),('0x00057e1c','check_and_update_part_cache'))},
 **{entry:(name,'sdk-fal-device/verification.json') for entry,name in (('0x00062df4','fal_flash_device_find'),('0x00062e68','fal_flash_init'))},
 '0x00062f40':('fal_init','sdk-fal-core/verification.json'),
 **{entry:(name,'native-kv-scans/verification.json') for entry,name in (('0x00057d0c','r1_kv_flash_erase_scan'),('0x00064b24','r1_latest_valid_flash_slot_scan_adapter'))},
 '0x00095168':('r1_kv_store_get','native-kv-store-get/verification.json'),
 **{entry:(name,'native-kv-class/verification.json') for entry,name in (('0x00073930','r1_kv_class_read'),('0x00073968','r1_kv_class_write'),('0x000738f4','r1_health_record_read'),('0x0007390c','r1_health_record_write'))},
 **{entry:(name,'native-advertising-configuration/verification.json') for entry,name in (('0x000489e6','r1_advertising_params_init'),('0x00048a28','r1_nordic_advertising_configuration'),('0x0007ba24','r1_advertising_configuration_byte_get'),('0x0007ba78','r1_advertising_product_sn_read'),('0x0007cbc8','r1_advertising_event_plan_build'))},
 **{entry:(name,'sdk-advertising-init/verification.json') for entry,name in (('0x00051716','ble_advertising_init'),('0x00051528','ble_advdata_encode'),('0x00051fb8','r1_sdk_adv_device_addr_encode'),('0x00059bde','r1_sdk_adv_conn_int_encode'),('0x00076088','r1_sdk_adv_manuf_encode'),('0x0008aba0','r1_sdk_adv_service_encode'),('0x000770bc','r1_sdk_adv_name_encode'),('0x00095570','r1_sdk_adv_uuid_list_sized_encode'))},
 **{entry:(name,'sdk-advertising/verification.json') for entry,name in (('0x00051806','ble_advertising_on_ble_evt'),('0x00051870','ble_advertising_start'),('0x00051710','ble_advertising_conn_cfg_tag_set'),('0x000517fe','ble_advertising_modes_config_set'),('0x00064f1a','r1_sdk_adv_flags_set'),('0x0007f0c8','r1_sdk_adv_phy_is_valid'),('0x00094dd8','r1_sdk_adv_use_whitelist'),('0x000516aa','ble_advdata_parse'),('0x000516ca','ble_advdata_search'))},
 **{entry:(name,'native-gatt/verification.json') for entry,name in (('0x000781b4','nrf_ble_gatt_on_ble_evt'),('0x0007ce34','r1_gatt_on_mtu_request'),('0x0005a65c','r1_gatt_data_length_update'))},
 **{entry:(name,'sdk-gatt/verification.json') for entry,name in (('0x00078186','nrf_ble_gatt_init'),('0x00074f20','r1_sdk_gatt_link_init'))},
 **{entry:(name,'sdk-qwr/verification.json') for entry,name in (('0x000783b6','nrf_ble_qwr_init'),('0x000783da','nrf_ble_qwr_on_ble_evt'),('0x00095114','r1_sdk_qwr_user_mem_reply'))},
 **{entry:(name,receipt) for entry,name,receipt in (('0x0007a38c','r1_sdk_ble_events_poll','sdk-ble-dispatch/verification.json'),('0x0007a53c','nrf_section_iter_init','sdk-ble-dispatch/iterator-verification.json'),('0x0007a56a','nrf_section_iter_next','sdk-ble-dispatch/iterator-verification.json'))},
 **{entry:(name,'sdk-connection-events/verification.json') for entry,name in (('0x0005380c','r1_sdk_connection_event'),('0x00059ba0','conn_handle_list_get'),('0x00077fbe','nrf_atflags_clear'),('0x00078054','nrf_atflags_set'),('0x00078086','nrf_atomic_u32_and'))},
 **{entry:(name,'sdk-connection-index/verification.json') for entry,name in (('0x00051e04','ble_conn_state_conn_idx'),('0x00051fa4','ble_conn_state_valid'),('0x0007803e','nrf_atflags_get'),('0x00051440','bcs_internal_state_reset'),('0x00051e78','ble_conn_state_init'))},
 '0x000514e0':('blcm_link_ctx_get','sdk-link-context/verification.json'),
 '0x000526cc':('r1_native_bae8_send','native-bae8-send/verification.json'),
 **{entry:(name,'native-ble-send/verification.json') for entry,name in (('0x0003e7a8','r1_native_ble_message_send'),('0x0003e884','r1_ble_error_is_benign'),('0x0003e8ae','r1_ble_flush_one'),('0x0003e8b4','r1_ble_flush_bounded'),('0x0003e8dc','r1_ble_flush_drain'),('0x0003e8fc','r1_ble_link_semaphore'),('0x0003e924','r1_ble_semaphore_take'))},
 **{entry:(name,'native-output/verification.json') for entry,name in (('0x00044f50','r1_native_output_worker'),('0x0004e650','r1_native_ble_send_phone'),('0x0004e65e','r1_native_ble_send_glasses'))},
 '0x0007a594':('nrf_strerror_find','watchdog-logging/strerror-verification.json'),
 '0x0007a5cc':('nrf_strerror_get','watchdog-logging/strerror-verification.json'),
 '0x0004ebec':('app_util_critical_region_enter','sdk-critical/verification.json'),
 '0x0004ec34':('app_util_critical_region_exit','sdk-critical/verification.json'),
 **{address:(name,'integer-runtime/verification.json') for address,name in (('0x000274e8','__aeabi_uldivmod'),('0x0002754a','__aeabi_ldivmod'),('0x000275ac','__aeabi_llsl'),('0x000275ca','__aeabi_llsr'))},
 **{entry:(name,'watchdog-startup/manager-verification.json') for entry,name in [('0x0005da30', 'r1_native_watchdog_expired_task')]},
 **{entry:(name,'watchdog-startup/device-verification.json') for entry,name in [('0x000500c8', 'r1_native_watchdog_hw_close'), ('0x000500d4', 'r1_native_watchdog_hw_handle_init'), ('0x000500fc', 'r1_native_watchdog_hw_feed'), ('0x0005010c', 'r1_native_watchdog_hw_open_feed'), ('0x00095be8', 'r1_native_watchdog_hw_feed_thunk'), ('0x0006623e', 'r1_native_watchdog_port_sample'), ('0x00056638', 'r1_native_named_wdt_feed'), ('0x00056658', 'r1_native_named_wdt_open'), ('0x00056694', 'r1_native_named_wdt_register')]},
 **{entry:(name,'watchdog-logging/verification.json') for entry,name in [('0x00034a7c', 'WDT_IRQHandler'), ('0x0007b470', 'nrfx_wdt_channel_alloc'), ('0x0007b508', 'nrfx_wdt_channel_feed'), ('0x0007b520', 'nrfx_wdt_enable'), ('0x0007b570', 'nrfx_wdt_init')]},

 **{entry:(name,'native-watchdog/verification.json') for entry,name in [('0x0005db14', 'r1_native_watchdog_register'), ('0x0005dbea', 'r1_native_watchdog_arm'), ('0x0005dbbc', 'r1_native_watchdog_disarm'), ('0x0005da00', 'r1_native_watchdog_feed'), ('0x00097730', 'r1_native_watchdog_lock'), ('0x00097748', 'r1_native_watchdog_unlock'), ('0x0005d8e6', 'r1_native_list_head'), ('0x0005d8f6', 'r1_native_list_tail'), ('0x0005d8ee', 'r1_native_list_next'), ('0x00077e30', 'r1_native_list_set_next'), ('0x00077e3c', 'r1_native_list_set_previous'), ('0x0005d8fe', 'r1_native_list_initialize'), ('0x0005d986', 'r1_native_list_empty'), ('0x0005d94a', 'r1_native_list_append'), ('0x0005d90e', 'r1_native_list_prepend'), ('0x0009879c', 'xTaskGetCurrentTaskHandle')]},
 '0x0008d888':('r1_native_event_dispatch','native-event-dispatch/verification.json'),
 **{entry:(name,'native-tasks/verification.json') for entry,name in [('0x000920ec','r1_native_task_gtx'),('0x0009227c','r1_native_task_msgtx'),('0x00092580','r1_native_task_sensor'),('0x000926dc','r1_native_task_service'),('0x00046954','r1_native_task_storage')]},
 **{entry:(name,'native-sync/verification.json') for entry,name in [('0x000923a4','r1_native_suspend_signal'),('0x000923b4','r1_native_sync_wait'),('0x00092440','r1_native_sync_signal'),('0x00045c20','r1_native_worker_park')]},
 **{entry:(name,'native-tx/verification.json') for entry,name in [('0x00034064','r1_ble_tx_queue_dispatch_type0'),('0x00034070','r1_ble_tx_queue_dispatch_type2'),('0x0003407c','r1_ble_tx_queue_dispatch_type1')]},
 '0x0004cb34':('r1_glasses_connection_handle_get','connection-handle/verification.json'),
 '0x0004cba4':('r1_phone_connection_handle_get','connection-handle/verification.json'),
 **{entry:(name,'native-task-lifecycle/verification.json') for entry,name in [('0x00043b8c','r1_thread_create_a'),('0x00043b74','r1_task_stop_668c'),('0x00046924','r1_thread_create_f'),('0x0004690c','r1_task_stop_6608'),('0x00046a44','r1_thread_create_g'),('0x00046a2c','r1_task_stop_66d8'),('0x00044ef0','r1_thread_create_b'),('0x00044ed8','r1_task_stop_65e0'),('0x0004509c','r1_thread_create_e'),('0x00045084','r1_task_stop_65bc')]},
 '0x0008d8fc':('r1_event_publish','native-events/verification.json'),
 '0x000924c0':('r1_event_bus_enqueue','native-events/verification.json'),
 '0x0004cb28':('r1_conn_field6_get','connection-handle/verification.json'),
 '0x00041e80':('r1_structured_log_cache_append','structured-cache/verification.json'),
 '0x00041c5c':('r1_structured_log_cache_copy','structured-cache-copy/verification.json'),
 '0x00027f6c':('r1_log_double_to_float_bits','structured-float/verification.json'),
 '0x00028078':('r1_log_round_float_bits','structured-float/verification.json'),
 **{entry:(name,'rtos-ticks/verification.json') for entry,name in [
 ('0x0007d28c','osKernelGetTickCount'),('0x00095f18','vPortValidateInterruptPriority'),
 ('0x000987a8','xTaskGetSchedulerState'),('0x000987c4','xTaskGetTickCount')]},
 **{entry:(name,'structured-time/verification.json') for entry,name in [
 ('0x000514bc','r1_structured_log_timestamp_adapter'),('0x0008ada4','r1_time_backend_timestamp'),
 ('0x0008ad40','r1_structured_log_local_timestamp')]},
 '0x00046fd4':('r1_structured_log_encode_format','structured-encode/verification.json'),
 '0x000277f0':('strlen','runtime/verification.json'),
 '0x00095cf4':('vPortEnterCritical','rtos-critical/verification.json'),
 '0x00095d24':('vPortExitCritical','rtos-critical/verification.json'),
 **{entry:(name,'structured-log/verification.json') for entry,name in [
 ('0x00091638','r1_structured_log_format'),('0x00091864','r1_structured_log_clock_available'),
 ('0x000590a0','r1_structured_log_export_active')]},
 **{entry:(name,'board-seams/verification.json') for entry,name in [
 ('0x0004e5bc','r1_adc_error'),('0x000914ec','r1_structured_log_mode_get'),
 ('0x000784f0','r1_st25_delay_ms')]},
 '0x000277ae':('memset','runtime/verification.json'),
 '0x000277fe':('strcmp','runtime/verification.json'),
 '0x000277aa':('__aeabi_memclr','runtime/verification.json'),
 **{entry:(name,'adc/sdk-execution.json') for entry,name in [
 ('0x0007af7c','nrfx_saadc_init'),('0x0007aeac','nrfx_saadc_channel_init'),
 ('0x0007af38','nrfx_saadc_channel_uninit'),('0x0007b150','nrfx_saadc_uninit')]},
 **{entry:(name,'adc/verification.json') for entry,name in [
 ('0x0005493c','r1_named_adc_register_all'),('0x00054864','r1_named_adc_open'),
 ('0x000548f0','r1_named_adc_sample'),('0x000547f4','r1_named_adc_close')]},
 **{entry:(name,'gpio/sdk-execution.json') for entry,name in [
 ('0x0007a73c','nrfx_gpiote_in_event_disable'),('0x0007a784','nrfx_gpiote_in_event_enable'),
 ('0x0007a81c','nrfx_gpiote_in_init'),('0x0007a8ec','nrfx_gpiote_in_uninit'),
 ('0x0007a94c','nrfx_gpiote_init'),('0x0007aa18','nrfx_gpiote_is_init')]},
 **{entry:(name,'gpio/verification.json') for entry,name in [
 ('0x00054c24','r1_named_gpio_register_all'),('0x00054afc','r1_named_gpio_callback'),
 ('0x00054ed0','r1_named_gpio_read'),('0x00054b40','r1_named_gpio_close'),
 ('0x00054b90','r1_named_gpio_open'),('0x0006ed94','r1_named_gpio_irq_dispatch')]},
 '0x0007a6dc':('r1_twi_delay_busy','software-twi/delay-verification.json'),
 '0x0007a6ec':('r1_twi_delay_busy','software-twi/delay-verification.json'),
 '0x0007081c':('r1_twi_delay_noop','software-twi/delay-verification.json'),
 '0x00054af0':('r1_twi_delay_noop','software-twi/delay-verification.json'),
 '0x0005547c':('r1_stock_i2c2_read','software-twi/adapter-verification.json'),
 '0x000554b0':('r1_stock_i2c3_read','software-twi/adapter-verification.json'),
 '0x000554e4':('r1_stock_i2c4_read','software-twi/adapter-verification.json'),
 '0x00055518':('r1_stock_i2c5_read','software-twi/adapter-verification.json'),
 '0x00055dbc':('r1_stock_i2c2_write','software-twi/adapter-verification.json'),
 '0x00055e40':('r1_stock_i2c3_write','software-twi/adapter-verification.json'),
 '0x00055ec4':('r1_stock_i2c4_write','software-twi/adapter-verification.json'),
 '0x00055f5c':('r1_stock_i2c5_write','software-twi/adapter-verification.json'),
 '0x00055330':('r1_stock_i2c2_open','software-twi/lifecycle-verification.json'),
 '0x00055360':('r1_stock_i2c3_open','software-twi/lifecycle-verification.json'),
 '0x00055390':('r1_stock_i2c4_open','software-twi/lifecycle-verification.json'),
 '0x000553e4':('r1_stock_i2c5_open','software-twi/lifecycle-verification.json'),
 '0x000551e8':('r1_stock_i2c2_close','software-twi/lifecycle-verification.json'),
 '0x0005520c':('r1_stock_i2c3_close','software-twi/lifecycle-verification.json'),
 '0x00055230':('r1_stock_i2c4_close','software-twi/lifecycle-verification.json'),
 '0x00055254':('r1_stock_i2c5_close','software-twi/lifecycle-verification.json'),
 '0x00079194':('r1_twi_gpio_low','software-twi/gpio-verification.json'),
 '0x0007945c':('r1_twi_gpio_high','software-twi/gpio-verification.json'),
 '0x000790bc':('r1_twi_gpio_output','software-twi/gpio-verification.json'),
 '0x00079062':('r1_twi_gpio_input','software-twi/gpio-verification.json'),
 '0x00078fe4':('r1_twi_gpio_release','software-twi/gpio-verification.json'),
 '0x000793b0':('r1_twi_gpio_read','software-twi/gpio-verification.json'),
 '0x000791a8':('r1_twi_gpio_low','software-twi/gpio-verification.json'),
 '0x00079470':('r1_twi_gpio_high','software-twi/gpio-verification.json'),
 '0x000790d0':('r1_twi_gpio_output','software-twi/gpio-verification.json'),
 '0x00079074':('r1_twi_gpio_input','software-twi/gpio-verification.json'),
 '0x00078ff6':('r1_twi_gpio_release','software-twi/gpio-verification.json'),
 '0x000793c6':('r1_twi_gpio_read','software-twi/gpio-verification.json'),
 '0x000791bc':('r1_twi_gpio_low','software-twi/gpio-verification.json'),
 '0x00079484':('r1_twi_gpio_high','software-twi/gpio-verification.json'),
 '0x000790e4':('r1_twi_gpio_output','software-twi/gpio-verification.json'),
 '0x00079086':('r1_twi_gpio_input','software-twi/gpio-verification.json'),
 '0x00079008':('r1_twi_gpio_release','software-twi/gpio-verification.json'),
 '0x000793dc':('r1_twi_gpio_read','software-twi/gpio-verification.json'),
 '0x000791d0':('r1_twi_gpio_low','software-twi/gpio-verification.json'),
 '0x00079498':('r1_twi_gpio_high','software-twi/gpio-verification.json'),
 '0x000790f8':('r1_twi_gpio_output','software-twi/gpio-verification.json'),
 '0x00079098':('r1_twi_gpio_input','software-twi/gpio-verification.json'),
 '0x0007901a':('r1_twi_gpio_release','software-twi/gpio-verification.json'),
 '0x000793f2':('r1_twi_gpio_read','software-twi/gpio-verification.json'),
 **{entry:('r1_stock_i2c'+str(i+2)+'_register','i2c5/registry-bootstrap-verification.json') for i,entry in enumerate(('0x00056508','0x00056520','0x00056538','0x00056550'))},
 '0x000557f8':('software_twi_read_transaction_reg8','software-twi/transaction-verification.json'),
 '0x00055878':('software_twi_read_transaction_reg8','software-twi/transaction-verification.json'),
 '0x000558f8':('software_twi_read_transaction_reg16','software-twi/transaction-verification.json'),
 '0x00055988':('software_twi_read_transaction_reg16','software-twi/transaction-verification.json'),
 '0x000560dc':('software_twi_write_transaction_reg16_byte','software-twi/transaction-verification.json'),
 '0x0005613e':('software_twi_write_transaction_reg8','software-twi/transaction-verification.json'),
 '0x000561a0':('software_twi_write_transaction_reg8','software-twi/transaction-verification.json'),
 '0x00056202':('software_twi_write_transaction_reg16','software-twi/transaction-verification.json'),
 '0x00055a18':('software_twi_start','software-twi/primitive-verification.json'),
 '0x00055a56':('software_twi_start','software-twi/primitive-verification.json'),
 '0x00055a94':('software_twi_start','software-twi/primitive-verification.json'),
 '0x00055ad2':('software_twi_start','software-twi/primitive-verification.json'),
 '0x00055b10':('software_twi_stop','software-twi/primitive-verification.json'),
 '0x00055b3c':('software_twi_stop','software-twi/primitive-verification.json'),
 '0x00055b68':('software_twi_stop','software-twi/primitive-verification.json'),
 '0x00055b94':('software_twi_stop','software-twi/primitive-verification.json'),
 '0x00055bc0':('software_twi_wait_ack','software-twi/primitive-verification.json'),
 '0x00055c08':('software_twi_wait_ack','software-twi/primitive-verification.json'),
 '0x00055c50':('software_twi_wait_ack','software-twi/primitive-verification.json'),
 '0x00055c98':('software_twi_wait_ack','software-twi/primitive-verification.json'),
 '0x00055548':('software_twi_read_byte','software-twi/primitive-verification.json'),
 '0x000555f4':('software_twi_read_byte','software-twi/primitive-verification.json'),
 '0x000556a0':('software_twi_read_byte','software-twi/primitive-verification.json'),
 '0x0005574c':('software_twi_read_byte','software-twi/primitive-verification.json'),
 '0x00055fa4':('software_twi_write_byte','software-twi/primitive-verification.json'),
 '0x00055ff2':('software_twi_write_byte','software-twi/primitive-verification.json'),
 '0x00056040':('software_twi_write_byte','software-twi/primitive-verification.json'),
 '0x0005608e':('software_twi_write_byte','software-twi/primitive-verification.json'),
 **{entry:('r1_stock_dispatch_'+suffix,'i2c5/registry-dispatch-verification.json') for entry,suffix in [
 ('0x00085d08','00'),('0x00085d1a','08'),('0x00085cba','0c'),('0x00085d2c','10'),
 ('0x00085da8','14'),('0x00085ccc','18'),('0x00085d46','20')]},
 **{entry:(name,'i2c5/registry-bootstrap-verification.json') for entry,name in [
 ('0x00085ce0','r1_stock_registry_find'),('0x00085d58','r1_stock_registry_register'),
 ('0x00050d3c','r1_vnfc_rect_adc_handle_cache'),('0x00050464','r1_i2c5_nfc_resource_registration')]},
 **{entry:(name,'i2c5/verification.json') for entry,name in [
 ('0x00050510','r1_i2c5_read_transfer'),('0x00050534','r1_i2c5_write_transfer'),
 ('0x000504c0','r1_i2c5_nfc_resource_release'),('0x000504d8','r1_i2c5_nfc_resource_acquire')]},
 **{entry:(name,'sensors/st25-bus-verification.json') for entry,name in [
 ('0x00044c58','r1_st25dvxxkc_bus_tick_get'),('0x00044c64','r1_st25dvxxkc_bus_deinitialize'),
 ('0x00044c6e','r1_st25dvxxkc_bus_initialize'),('0x00044c78','r1_st25dvxxkc_bus_is_ready'),
 ('0x00044c84','r1_st25dvxxkc_bus_read'),('0x00044c8a','r1_st25dvxxkc_bus_write')]},
 '0x0005d87c':('r1_stock_crc16_modbus','checksum-verification.json'),
 '0x0005d8a4':('r1_stock_crc32_update','checksum-verification.json'),
 '0x0005d8cc':('r1_stock_hash131','checksum-verification.json'),
 '0x00095bb8':('vApplicationGetIdleTaskMemory','rtos-scheduler-start/verification.json'),
 '0x00095bd0':('vApplicationGetTimerTaskMemory','rtos-scheduler-start/verification.json'),
 '0x00048b02':('r1_stock_two_pass','crypto/verification.json'),
 '0x000891a4':('r1_stock_two_pass_callback','crypto/verification.json'),
 '0x00098e22':('r1_stock_xor','crypto/verification.json')}


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def functions(path):
    data=path.read_bytes();assert data[:6]==b'\x7fELF\x01\x01'
    offset=struct.unpack_from('<I',data,32)[0];size,count=struct.unpack_from('<HH',data,46)
    sections=[struct.unpack_from('<10I',data,offset+i*size) for i in range(count)]
    result=[]
    for section in sections:
        if section[1]!=2:continue
        strings=sections[section[6]];names=data[strings[4]:strings[4]+strings[5]]
        for at in range(section[4],section[4]+section[5],section[9]):
            name,_,extent,info,_,index=struct.unpack_from('<IIIBBH',data,at)
            if name and index and info&15==2:
                result.append((names[name:].split(b'\0',1)[0].decode(),extent))
    return result


def section_bytes(path,wanted,executable=True):
    data=path.read_bytes();assert data[:6]==b'\x7fELF\x01\x01'
    offset=struct.unpack_from('<I',data,32)[0];size,count,names_index=struct.unpack_from('<HHH',data,46)
    headers=[struct.unpack_from('<10I',data,offset+i*size) for i in range(count)];strings=headers[names_index];names=data[strings[4]:strings[4]+strings[5]]
    for index,header in enumerate(headers):
        if names[header[0]:].split(b'\0',1)[0].decode()==wanted:
            assert (header[2]&4 if executable else header[2]&2 and not header[2]&4) and not any(h[1] in (4,9) and h[7]==index and h[5] for h in headers)
            return data[header[4]:header[4]+header[5]]
    raise AssertionError((path,wanted))


def main():
    from audit_rtos_timer_new import audit as audit_timer_new
    audit_timer_new()
    timer_id_correction=json.loads((BASE/'rtos-timer-new/attribution-correction.json').read_text())
    from audit_rtos_timer_controls import audit as audit_timer_controls
    audit_timer_controls()
    candidates=collections.defaultdict(list);input_reports={}
    for relative in REPORTS:
        path=BASE/relative;report=json.loads(path.read_text());input_reports[relative]=sha(path)
        for row in report['units']:
            if row.get('compiled',True) is False:continue
            source=Path(row['source']);source=source if source.is_absolute() else ROOT/source
            assert sha(source)==row['source_sha256'],source
            command=row['command'];obj=Path(command[command.index('-o')+1])
            assert sha(obj)==row['object_sha256'],obj
            for name,extent in functions(obj):
                candidates[name].append(dict(source=str(source.relative_to(ROOT)),object=str(obj.relative_to(ROOT)),bytes=extent,report=relative))
    receipts={name:json.loads((BASE/name).read_text()) for name in ({name for _,name in VERIFIED.values()} | {'watchdog-startup/sdk-execution.json','native-rtc-error/verification.json','rtos/static-memory-verification.json'})}
    from audit_rtos_timer import audit as audit_timers
    timer_ownership_correction=audit_timers()
    from audit_rtos_message_queue import audit as audit_message_queues
    audit_message_queues()
    from audit_rtos_synchronization import audit as audit_synchronization
    audit_synchronization()
    from audit_rtos_notification import audit as audit_notifications
    notification_ownership_mappings=audit_notifications()
    app_hash='0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a'
    for name,receipt in receipts.items():
        assert receipt['application_sha256']==app_hash,name
    for path,expected in receipts['checksum-verification.json']['source_sha256'].items():
        if Path(path).suffix in ('.c','.h','.inc'):
            assert sha(ROOT/path)==expected,path
    static=receipts['rtos/static-memory-verification.json']
    assert sha(ROOT/'r1/components/rtos/static_task_memory.c')==static['source_sha256']
    assert sha(BASE/'rtos/11_static_task_memory.o')==static['object_sha256']
    assert sha(BASE/'crypto/two-pass.bin')==receipts['crypto/verification.json']['candidate_binary_sha256']
    st25=receipts['sensors/st25-bus-verification.json']
    assert sha(ROOT/'r1/components/st25/stock_bus_bindings.c')==st25['source_sha256']
    assert sha(ROOT/'r1/components/st25/stock_bus_bindings.h')==st25['binding_header_sha256']
    assert sha(BASE/'sensors/r1-st25-stock-bus.o')==st25['object_sha256']
    i2c5=receipts['i2c5/verification.json']
    assert sha(BASE/'i2c5/report.json')==i2c5['integration_report_sha256']
    assert sha(BASE/'i2c5/st25-i2c5-registry.o')==i2c5['relocatable_sha256']
    bootstrap=receipts['i2c5/registry-bootstrap-verification.json']
    assert sha(BASE/'i2c5/report.json')==bootstrap['integration_report_sha256']
    assert sha(BASE/'i2c5/st25-i2c5-registry.o')==bootstrap['relocatable_sha256']
    assert sha(ROOT/bootstrap['runtime_archive'])==bootstrap['runtime_archive_sha256']
    dispatch=receipts['i2c5/registry-dispatch-verification.json']
    assert sha(BASE/'i2c5/report.json')==dispatch['integration_report_sha256']
    assert sha(BASE/'i2c5/stock_registry.o')==dispatch['object_sha256']
    for twi_name in ('primitive-verification.json','transaction-verification.json'):
        twi=receipts['software-twi/'+twi_name]
        assert sha(BASE/'report.json')==twi['source_report_sha256']
        assert sha(ROOT/twi['source'])==twi['source_sha256']
        assert sha(ROOT/twi['object'])==twi['object_sha256']
        assert sha(ROOT/'r1/reconstructed/software_twi/software_twi.h')==twi['header_sha256']
    config=json.loads((BASE/'software-twi/board-configuration-verification.json').read_text())
    assert config['application_sha256']==app_hash
    assert sha(BASE/'report.json')==config['source_report_sha256']
    assert sha(BASE/'software-twi/stock-initialization.json')==config['stock_initialization_sha256']
    assert sha(ROOT/'r1/reconstructed/software_twi/software_twi.c')==config['source_sha256']
    gpio=receipts['software-twi/gpio-verification.json']
    gpio_report=json.loads((BASE/'software-twi/gpio-report.json').read_text())
    assert sha(BASE/'software-twi/gpio-report.json')==gpio['gpio_report_sha256']
    assert sha(BASE/'software-twi/stock-initialization.json')==gpio['stock_initialization_sha256']
    assert sha(BASE/'software-twi/sdk_gpio.o')==gpio['object_sha256']
    for path,digest in gpio_report['inputs'].items():assert sha(ROOT/path)==digest,path
    lifecycle=receipts['software-twi/lifecycle-verification.json']
    assert sha(BASE/'i2c5/report.json')==lifecycle['integration_report_sha256']
    assert sha(BASE/'i2c5/st25-i2c5-registry.o')==lifecycle['relocatable_sha256']
    assert sha(BASE/'software-twi/stock-initialization.json')==lifecycle['stock_initialization_sha256']
    adapters=receipts['software-twi/adapter-verification.json']
    assert sha(BASE/'i2c5/report.json')==adapters['integration_report_sha256']
    assert sha(BASE/'i2c5/st25-i2c5-registry.o')==adapters['relocatable_sha256']
    delays=receipts['software-twi/delay-verification.json']
    assert sha(BASE/'software-twi/gpio-report.json')==delays['gpio_report_sha256']
    assert sha(BASE/'software-twi/sdk_gpio.o')==delays['object_sha256']
    native=json.loads((BASE/'software-twi/native-initialization-verification.json').read_text())
    assert native['application_sha256']==app_hash
    assert sha(BASE/'i2c5/report.json')==native['integration_report_sha256']
    assert sha(BASE/'i2c5/st25-i2c5-registry.o')==native['relocatable_sha256']
    null_buffers=json.loads((BASE/'software-twi/null-buffer-verification.json').read_text())
    assert null_buffers['application_sha256']==app_hash
    assert sha(BASE/'i2c5/report.json')==null_buffers['integration_report_sha256']
    assert sha(BASE/'i2c5/st25-i2c5-registry.o')==null_buffers['relocatable_sha256']
    assert null_buffers['fault_comparisons']>0
    named=receipts['gpio/verification.json']
    assert sha(BASE/'gpio/report.json')==named['gpio_report_sha256']
    assert sha(BASE/'i2c5/report.json')==named['integration_report_sha256']
    assert sha(BASE/'gpio/stock_named_gpio.o')==named['object_sha256']
    named_report=json.loads((BASE/'gpio/report.json').read_text())
    for path,digest in {**named_report['headers'],**named_report['inputs']}.items():assert sha(ROOT/path)==digest,path
    gpio_link=json.loads((BASE/'gpio/integration-report.json').read_text())
    assert sha(BASE/'gpio/gpio-native-integration.o')==gpio_link['relocatable_sha256']
    assert sha(BASE/'i2c5/report.json')==gpio_link['i2c5_report_sha256']
    assert sha(BASE/'application-sdk/report.json')==gpio_link['sdk_report_sha256']
    assert sha(BASE/'application-sdk/39_nrfx_gpiote.o')==gpio_link['gpiote_object_sha256']
    assert sha(BASE/'gpio/gpiote_layout_probe.c')==gpio_link['layout_probe_sha256']
    sdk_execution=receipts['gpio/sdk-execution.json']
    assert sha(BASE/'gpio/integration-report.json')==sdk_execution['integration_report_sha256']
    assert sha(BASE/'gpio/gpio-native-integration.o')==sdk_execution['relocatable_sha256']
    adc=receipts['adc/verification.json']
    assert sha(BASE/'adc/report.json')==adc['adc_report_sha256']
    assert sha(BASE/'i2c5/report.json')==adc['integration_report_sha256']
    assert sha(BASE/'adc/stock_named_adc.o')==adc['object_sha256']
    adc_report=json.loads((BASE/'adc/report.json').read_text())
    for path,digest in adc_report['inputs'].items():assert sha(ROOT/path)==digest,path
    adc_link=json.loads((BASE/'adc/integration-report.json').read_text())
    assert sha(BASE/'adc/adc-native-integration.o')==adc_link['relocatable_sha256']
    assert sha(BASE/'application-sdk/report.json')==adc_link['sdk_report_sha256']
    assert sha(BASE/'i2c5/report.json')==adc_link['transport_report_sha256']
    assert sha(BASE/'application-sdk/41_nrfx_saadc.o')==adc_link['sdk_object_sha256']
    adc_execution=receipts['adc/sdk-execution.json']
    assert sha(BASE/'adc/integration-report.json')==adc_execution['integration_report_sha256']
    assert sha(BASE/'adc/adc-native-integration.o')==adc_execution['relocatable_sha256']
    board=json.loads((BASE/'board/report.json').read_text())
    assert sha(BASE/'board/native-board.o')==board['relocatable_sha256']
    for path,digest in board['input_reports'].items():assert sha(BASE/path)==digest,path
    for path,digest in board['objects'].items():assert sha(ROOT/path)==digest,path
    board_test=json.loads((BASE/'board/verification.json').read_text())
    assert board_test['application_sha256']==app_hash
    assert sha(BASE/'board/report.json')==board_test['board_report_sha256']
    assert sha(BASE/'board/native-board.o')==board_test['relocatable_sha256']
    memory=receipts['runtime/verification.json']
    assert sha(BASE/'runtime/report.json')==memory['runtime_report_sha256']
    assert sha(BASE/'runtime/memory-runtime.o')==memory['relocatable_sha256']
    memory_report=json.loads((BASE/'runtime/report.json').read_text())
    for path,digest in memory_report['inputs'].items():assert sha(ROOT/path)==digest,path
    seams=receipts['board-seams/verification.json']
    assert sha(BASE/'board-seams/report.json')==seams['report_sha256']
    assert sha(BASE/'board-seams/stock_seams.o')==seams['object_sha256']
    assert sha(BASE/'software-twi/gpio-report.json')==seams['gpio_report_sha256']
    seam_report=json.loads((BASE/'board-seams/report.json').read_text())
    for path,digest in seam_report['inputs'].items():assert sha(ROOT/path)==digest,path
    structured=receipts['structured-log/verification.json']
    assert sha(BASE/'structured-log/report.json')==structured['report_sha256']
    assert sha(BASE/'structured-log/structured_log.o')==structured['object_sha256']
    assert sha(BASE/'board-seams/report.json')==structured['seam_report_sha256']
    log_report=json.loads((BASE/'structured-log/report.json').read_text())
    for path,digest in log_report['inputs'].items():assert sha(ROOT/path)==digest,path
    critical=receipts['rtos-critical/verification.json']
    assert sha(BASE/'rtos-critical/report.json')==critical['report_sha256']
    assert sha(BASE/'rtos-critical/critical-only.o')==critical['selected_object_sha256']
    critical_report=json.loads((BASE/'rtos-critical/report.json').read_text())
    for path,digest in critical_report['inputs'].items():assert sha(ROOT/path)==digest,path
    ticks=receipts['rtos-ticks/verification.json']
    assert sha(BASE/'rtos-ticks/report.json')==ticks['report_sha256']
    assert sha(BASE/'rtos-ticks/ticks-only.o')==ticks['selected_object_sha256']
    ticks_report=json.loads((BASE/'rtos-ticks/report.json').read_text())
    assert ticks_report['port_report_sha256']==sha(BASE/'rtos-critical/report.json')
    for path,digest in ticks_report['inputs'].items():assert sha(ROOT/path)==digest,path
    critical_log=json.loads((BASE/'structured-log/critical-integration-verification.json').read_text())
    assert critical_log['application_sha256']==app_hash and critical_log['actual_critical_functions']
    assert sha(BASE/'rtos-critical/report.json')==critical_log['critical_report_sha256']
    assert sha(BASE/'structured-log/report.json')==critical_log['report_sha256']
    encode=receipts['structured-encode/verification.json']
    assert sha(BASE/'structured-encode/report.json')==encode['report_sha256']
    assert sha(BASE/'structured-encode/structured_encode.o')==encode['object_sha256']
    for path,digest in encode['provider_reports'].items():assert sha(BASE/path)==digest,path
    encode_report=json.loads((BASE/'structured-encode/report.json').read_text())
    for path,digest in encode_report['inputs'].items():assert sha(ROOT/path)==digest,path
    time=receipts['structured-time/verification.json']
    assert sha(BASE/'structured-time/report.json')==time['report_sha256']
    assert sha(BASE/'structured-time/structured_time.o')==time['object_sha256']
    assert sha(BASE/'i2c5/report.json')==time['registry_report_sha256']
    assert sha(BASE/'runtime/report.json')==time['runtime_report_sha256']
    time_report=json.loads((BASE/'structured-time/report.json').read_text())
    for path,digest in time_report['inputs'].items():assert sha(ROOT/path)==digest,path
    floating=receipts['structured-float/verification.json']
    assert sha(BASE/'structured-float/report.json')==floating['report_sha256']
    assert sha(BASE/'structured-float/structured_float.o')==floating['object_sha256']
    float_report=json.loads((BASE/'structured-float/report.json').read_text())
    for path,digest in float_report['inputs'].items():assert sha(ROOT/path)==digest,path
    for name,object_name in (('structured-cache','structured_cache.o'),('structured-cache-copy','structured_cache_copy.o')):
        receipt=receipts[name+'/verification.json'];report_path=BASE/(name+'/report.json');report=json.loads(report_path.read_text())
        assert sha(report_path)==receipt['report_sha256']
        assert sha(BASE/(name+'/'+object_name))==receipt['object_sha256']
        for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
        for path,digest in receipt.get('provider_reports',{}).items():assert sha(BASE/path)==digest,path
        if 'runtime_report_sha256' in receipt:assert sha(BASE/'runtime/report.json')==receipt['runtime_report_sha256']
    for name in ('structured-encode/float-integration-verification.json','structured-cache/copy-integration-verification.json'):
        receipt=json.loads((BASE/name).read_text());component=name.split('/')[0]
        assert receipt['application_sha256']==app_hash
        assert sha(BASE/(component+'/report.json'))==receipt['report_sha256']
        for path,digest in receipt['provider_reports'].items():assert sha(BASE/path)==digest,path
    for name,object_name in (('native-events','native_events.o'),('connection-handle','connection_handle.o'),('native-tx','native_tx.o'),('native-task-lifecycle','native_task_lifecycle.o'),('native-tasks','native_tasks.o'),('native-sync','native_sync.o'),('native-watchdog','native_watchdog.o'),('native-event-dispatch','native_event_dispatch.o'),('native-delayed-schedule','native_delayed_schedule.o'),('native-delayed-push','native_delayed_push.o'),('native-delayed-reschedule','native_delayed_reschedule.o')):
        receipt=receipts[name+'/verification.json'];report_path=BASE/(name+'/report.json');report=json.loads(report_path.read_text())
        assert sha(report_path)==receipt['report_sha256']
        assert sha(BASE/(name+'/'+object_name))==receipt['object_sha256']
        for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
        if 'runtime_report_sha256' in receipt:assert sha(BASE/'runtime/report.json')==receipt['runtime_report_sha256']
    delayed=receipts['native-delayed-schedule/verification.json'];delayed_dir=BASE/'native-delayed-schedule'
    assert delayed['comparisons']==1200 and delayed['application_sha256']==app_hash
    assert delayed['native_entry']=='0x65b4c' and delayed['native_size']==308
    assert delayed['lower_providers']=='controlled fixtures' and not delayed['application_linked'] and not delayed['instruction_identity']
    assert sha(ROOT/'r1/tools/verify_native_delayed_schedule.py')==delayed['verifier_sha256']
    for filename,key in [('ghidra-memory.json','ghidra_memory_sha256'),('rea-pseudocode.json','rea_sha256')]:assert sha(delayed_dir/filename)==delayed[key]
    assert bytes(json.loads((delayed_dir/'ghidra-memory.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x65b4c-0x27000:0x65c80-0x27000]
    push=receipts['native-delayed-push/verification.json'];push_dir=BASE/'native-delayed-push'
    assert push['comparisons']==2304 and push['schedule_composition_comparisons']==1536
    assert push['application_sha256']==app_hash and push['native_entry']=='0x659e8' and push['native_size']==144
    assert not push['application_linked'] and not push['instruction_identity']
    assert sha(ROOT/'r1/tools/verify_native_delayed_push.py')==push['verifier_sha256']
    assert sha(ROOT/'r1/tools/verify_native_delayed_schedule.py')==push['verifier_import_sha256']
    assert sha(push_dir/'ghidra-memory.json')==push['ghidra_memory_sha256']
    assert sha(BASE/'native-delayed-schedule/rea-659e8.json')==push['rea_sha256']
    assert bytes(json.loads((push_dir/'ghidra-memory.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x659e8-0x27000:0x65a78-0x27000]
    for path,digest in push['provider_reports'].items():assert sha(BASE/path)==digest,path
    reschedule=receipts['native-delayed-reschedule/verification.json'];reschedule_dir=BASE/'native-delayed-reschedule'
    assert reschedule['comparisons']=={'isolated':3840,'composed':3840}
    assert reschedule['application_sha256']==app_hash and reschedule['native_entry']=='0x65f84' and reschedule['native_size']==376
    assert not reschedule['application_linked'] and not reschedule['instruction_identity']
    assert sha(ROOT/'r1/tools/verify_native_delayed_reschedule.py')==reschedule['verifier_sha256']
    assert sha(ROOT/'r1/tools/verify_native_delayed_schedule.py')==reschedule['verifier_import_sha256']
    assert sha(reschedule_dir/'ghidra-memory.json')==reschedule['ghidra_memory_sha256']
    assert sha(BASE/'native-delayed-schedule/rea-65f84.json')==reschedule['rea_sha256']
    assert bytes(json.loads((reschedule_dir/'ghidra-memory.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x65f84-0x27000:0x660fc-0x27000]
    for path,digest in reschedule['provider_reports'].items():assert sha(BASE/path)==digest,path
    delayed_stage_path=BASE/'native-delayed-reschedule/stage-verification.json';delayed_stage=json.loads(delayed_stage_path.read_text())
    assert delayed_stage['driver_sha256']==sha(ROOT/'r1/tools/check_native_delayed_stage.py')
    assert delayed_stage['board_report_sha256']==sha(BASE/'board/report.json') and delayed_stage['board_object_sha256']==sha(BASE/'board/native-board.o')
    assert delayed_stage['selected_object_sha256']==sha(BASE/'native-delayed-reschedule/delayed-stage.o')
    assert not delayed_stage['new_unresolved_symbols'] and not delayed_stage['unresolved_state_anchors']
    assert delayed_stage['source_owned_state_anchors']=={'r1_delayed_context':0x20006718,'r1_delayed_callbacks':0x20015104,'r1_delayed_arguments':0x20015204,'r1_delayed_deadlines':0x20015304}
    assert delayed_stage['resolved_board_symbols']==[] and not delayed_stage['graph_verified'] and delayed_stage['canonical_board_integrated']
    assert list(delayed_stage['objects'])==['r1/research/source-build/board/native-board.o']
    canonical_board=json.loads((BASE/'board/report.json').read_text())
    for module,objname in [('native-delayed-schedule','native_delayed_schedule.o'),('native-delayed-push','native_delayed_push.o'),('native-delayed-reschedule','native_delayed_reschedule.o'),('native-delayed-cancel','native_delayed_cancel.o'),('native-delayed-initialize','native_delayed_initialize.o'),('native-delayed-worker','native_delayed_worker.o'),('native-delayed-state','native_delayed_state.o'),('rtos-timer-controls','timer-controls.o'),('rtos-timer-active','timer-active.o'),('rtos-timer-new','timer-new.o'),('rtos-timer-id','timer-id.o')]:
        assert canonical_board['objects']['r1/research/source-build/'+module+'/'+objname]==sha(BASE/module/objname)
        assert canonical_board['input_reports'][module+'/report.json']==sha(BASE/module/'report.json')
    for group in ('provider_reports','provider_receipts'):
        for path,digest in delayed_stage[group].items():assert sha(BASE/path)==digest,path
    for path,digest in delayed_stage['objects'].items():assert sha(ROOT/path)==digest,path
    delayed_graph=json.loads((BASE/'native-delayed-reschedule/graph-verification.json').read_text())
    assert delayed_graph['stage_sha256']==sha(delayed_stage_path) and delayed_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_delayed_graph.py')
    for path,digest in delayed_graph['input_helpers'].items():assert sha(ROOT/'r1/tools'/path)==digest,path
    assert delayed_graph['application_sha256']==app_hash and delayed_graph['comparisons']==30 and delayed_graph['workflows']==12
    assert delayed_graph['provider_counts']['native']==delayed_graph['provider_counts']['source'] and not delayed_graph['provider_interception']
    assert delayed_graph['provider_counts']['source']=={'vPortEnterCritical':348,'vPortExitCritical':348,'xQueueGenericSend':108,'r1_native_delayed_schedule':18,'osMutexAcquire':48,'osMutexRelease':48,'osTimerStop':18,'xTimerIsTimerActive':18,'r1_native_delayed_reschedule':30,'osTimerStart':30,'xTimerGenericCommand':36,'xQueueReceive':78,'r1_native_delayed_push':12,'osMessageQueuePut':12,'r1_native_delayed_worker':12,'osMessageQueueGet':24}
    assert delayed_graph['source_text_bytes']<0x40000 and delayed_graph['canonical_board_integrated'] and not delayed_graph['instruction_identity']
    initialized_graph=json.loads((BASE/'native-delayed-reschedule/initialization-graph-verification.json').read_text())
    assert initialized_graph['stage_sha256']==sha(delayed_stage_path) and initialized_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_delayed_initialization_graph.py')
    assert initialized_graph['application_sha256']==app_hash and initialized_graph['comparisons']==60 and initialized_graph['workflows']==24
    assert initialized_graph['actual_product_initializer'] and initialized_graph['actual_heap'] and initialized_graph['reinitialized_workflows']==12
    assert initialized_graph['worker_dispatches_per_implementation']==24 and not initialized_graph['provider_interception']
    assert initialized_graph['canonical_board_integrated'] and not initialized_graph['instruction_identity'] and initialized_graph['source_text_bytes']<0x40000
    for path,digest in initialized_graph['input_helpers'].items():assert sha(ROOT/'r1/tools'/path)==digest,path
    assert initialized_graph['provider_counts']['native']==initialized_graph['provider_counts']['source']
    assert initialized_graph['provider_counts']['source']=={'r1_native_delayed_initialize': 36, 'osMessageQueueNew': 24, 'vPortEnterCritical': 948, 'vPortExitCritical': 948, 'osTimerNew': 24, 'pvPortMalloc': 24, 'osMutexNew': 24, 'xQueueGenericSend': 264, 'osThreadNew': 36, 'r1_native_delayed_schedule': 36, 'osMutexAcquire': 120, 'osMutexRelease': 120, 'osTimerStop': 48, 'xTimerIsTimerActive': 48, 'r1_native_delayed_reschedule': 72, 'osTimerStart': 72, 'xTimerGenericCommand': 96, 'xQueueReceive': 192, 'TimerCallback': 24, 'pvTimerGetTimerID': 24, 'r1_native_delayed_push': 24, 'osMessageQueuePut': 24, 'r1_native_delayed_worker': 24, 'osMessageQueueGet': 48, 'osThreadTerminate': 12, 'r1_native_delayed_cancel': 12}
    assert initialized_graph['cancellation_workflows']==12
    cancel_dir=BASE/'native-delayed-cancel';cancel=json.loads((cancel_dir/'verification.json').read_text())
    assert cancel['comparisons']==6912 and cancel['matched_cases']==2735 and cancel['application_sha256']==app_hash
    assert cancel['native_entry']=='0x65d64' and cancel['native_size']==228 and not cancel['application_linked'] and not cancel['instruction_identity']
    assert cancel['report_sha256']==sha(cancel_dir/'report.json') and cancel['object_sha256']==sha(cancel_dir/'native_delayed_cancel.o')
    assert cancel['verifier_sha256']==sha(ROOT/'r1/tools/verify_native_delayed_cancel.py') and cancel['helper_sha256']==sha(ROOT/'r1/tools/verify_native_delayed_schedule.py')
    assert cancel['ghidra_memory_sha256']==sha(cancel_dir/'ghidra-memory.json') and cancel['rea_sha256']==sha(cancel_dir/'rea-pseudocode.json')
    assert bytes(json.loads((cancel_dir/'ghidra-memory.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x65d64-0x27000:0x65e48-0x27000]
    assert json.loads((cancel_dir/'rea-pseudocode.json').read_text())['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
    for path,digest in json.loads((cancel_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    init_logs_dir=BASE/'native-thread-init-logs';init_logs=json.loads((init_logs_dir/'verification.json').read_text())
    assert init_logs['comparisons']==4394 and init_logs['counts']=={'r1_native_service_hardware_initialize':2197,'r1_native_storage_hardware_initialize':2197}
    assert init_logs['application_sha256']==app_hash and init_logs['report_sha256']==sha(init_logs_dir/'report.json')
    assert init_logs['object_sha256']==sha(init_logs_dir/'native_thread_init_logs.o') and init_logs['driver_sha256']==sha(ROOT/'r1/tools/verify_native_thread_init_logs.py')
    assert not init_logs['application_linked'] and not init_logs['instruction_identity']
    for path,digest in json.loads((init_logs_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    for filename,digest in init_logs['ghidra_evidence'].items():
        path=init_logs_dir/filename;assert sha(path)==digest;n=filename.removeprefix('ghidra-').removesuffix('.json');a=init_logs['entries'][n]
        assert bytes(json.loads(path.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+64]
    assert {n:r['address'] for n,r in init_logs['source_descriptor_data'].items()}=={'service_ring':0x45cc4,'service_sdk':0x45ce8,'storage_ring':0x45d40,'storage_sdk':0x45d64}
    for n,row in init_logs['source_descriptor_data'].items():
        a=row['address'];z=row['bytes'];payload=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+z]
        assert hashlib.sha256(payload).hexdigest()==row['sha256'] and z==(27 if n.endswith('ring') else 21)
    thread_logs_graph=json.loads((BASE/'board/thread-init-logs-verification.json').read_text())
    assert thread_logs_graph['comparisons']==2592 and thread_logs_graph['workflows']==384 and thread_logs_graph['wrapper_calls']==768
    assert thread_logs_graph['standard_messages']==384 and thread_logs_graph['accepted_rtt_bytes_per_implementation']==15360
    assert thread_logs_graph['rtt_write_calls_per_implementation']==384 and thread_logs_graph['timestamp_callbacks_per_implementation']==624
    assert thread_logs_graph['application_sha256']==app_hash and thread_logs_graph['board_report_sha256']==sha(BASE/'board/report.json')
    assert thread_logs_graph['verification_driver_sha256']==sha(ROOT/'r1/tools/verify_native_board.py') and thread_logs_graph['pipeline_driver_sha256']==sha(ROOT/'r1/tools/verify_thread_init_logs_graph.py')
    assert thread_logs_graph['wrapper_report_sha256']==sha(init_logs_dir/'report.json') and not thread_logs_graph['provider_interception'] and thread_logs_graph['engine']=='UC_MODE_THUMB|UC_MODE_MCLASS'
    assert canonical_board['objects']['r1/research/source-build/native-thread-init-logs/native_thread_init_logs.o']==sha(init_logs_dir/'native_thread_init_logs.o')
    assert canonical_board['input_reports']['native-thread-init-logs/report.json']==sha(init_logs_dir/'report.json')
    for filename,digest in init_logs['rea_evidence'].items():
        path=init_logs_dir/filename;assert sha(path)==digest;assert json.loads(path.read_text())['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
    status_dir=BASE/'native-status-record';status=json.loads((status_dir/'verification.json').read_text())
    assert status['comparisons']==21008 and status['counts']=={'r1_status_record_ring_publish':17664,'r1_device_state_byte_2d_get':256,'r1_peer_channel_count':16,'r1_charge_state_byte_get':3072}
    assert status['drop_counter_updates']==1759 and status['drain_event_calls']==17664 and status['application_sha256']==app_hash
    assert status['report_sha256']==sha(status_dir/'report.json') and status['object_sha256']==sha(status_dir/'native_status_record.o')
    assert status['driver_sha256']==sha(ROOT/'r1/tools/verify_native_status_record.py') and not status['application_linked'] and not status['instruction_identity']
    for path,digest in json.loads((status_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    for filename,digest in status['ghidra_evidence'].items():
        path=status_dir/filename;assert sha(path)==digest;n=filename.removeprefix('ghidra-').removesuffix('.json');a,z=status['entries'][n]
        assert bytes(json.loads(path.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+z]
    for filename,digest in status['rea_evidence'].items():
        path=status_dir/filename;assert sha(path)==digest;assert json.loads(path.read_text())['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
    status_evidence=json.loads((status_dir/'evidence.json').read_text())
    assert status_evidence['effective_counter_bits']==16 and status_evidence['adjacent_state_bytes_preserved'] and not status_evidence['locked_corpus_modified']
    assert status_evidence['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    battery_dir=BASE/'native-battery-runtime';battery=json.loads((battery_dir/'verification.json').read_text())
    assert battery['comparisons']==2896 and battery['explicit_numeric_rounding_cases']==336
    assert battery['application_sha256']==app_hash and battery['native_entry']=='0x31fd0' and battery['native_size']==406
    assert battery['report_sha256']==sha(battery_dir/'report.json') and battery['object_sha256']==sha(battery_dir/'native_battery_runtime.o')
    assert battery['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_runtime.py') and not battery['application_linked'] and not battery['instruction_identity']
    assert battery['ghidra_memory_sha256']==sha(battery_dir/'ghidra-memory.json') and battery['rea_sha256']==sha(battery_dir/'rea-pseudocode.json')
    assert bytes(json.loads((battery_dir/'ghidra-memory.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x31fd0-0x27000:0x32166-0x27000]
    assert json.loads((battery_dir/'rea-pseudocode.json').read_text())['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
    for path,digest in json.loads((battery_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    battery_evidence=json.loads((battery_dir/'evidence.json').read_text());assert battery_evidence['scale_bits']=='0x3f86c8b4' and battery_evidence['refresh_abi']['arguments']==5
    assert sha(battery_dir/'ghidra-refresh-abi.json')==battery_evidence['refresh_abi']['ghidra_sha256']
    assert bytes(json.loads((battery_dir/'ghidra-refresh-abi.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x3dd0c-0x27000:0x3dd9c-0x27000]
    stats_dir=BASE/'native-battery-statistics';stats=json.loads((stats_dir/'verification.json').read_text())
    assert stats['comparisons']==5536 and stats['counts']=={'r1_battery_charged_state_refresh':1440,'r1_battery_voltage_average':2048,'r1_battery_level_average':2048}
    assert stats['application_sha256']==app_hash and stats['report_sha256']==sha(stats_dir/'report.json')
    assert stats['object_sha256']==sha(stats_dir/'native_battery_statistics.o') and stats['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_statistics.py')
    assert not stats['application_linked'] and not stats['instruction_identity']
    for path,digest in json.loads((stats_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    for filename,digest in stats['ghidra_evidence'].items():
        path=stats_dir/filename;assert sha(path)==digest;n=filename.removeprefix('ghidra-').removesuffix('.json');a,z=stats['entries'][n]
        assert bytes(json.loads(path.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+z]
    for filename,digest in stats['rea_evidence'].items():
        path=stats_dir/filename;assert sha(path)==digest;assert json.loads(path.read_text())['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
    statistics_graph=json.loads((battery_dir/'statistics-integration-verification.json').read_text())
    assert statistics_graph['real_statistics'] and not battery['real_statistics'] and statistics_graph['comparisons']==2896
    assert statistics_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_runtime.py') and statistics_graph['report_sha256']==sha(battery_dir/'report.json')
    assert statistics_graph['object_sha256']==sha(battery_dir/'native_battery_runtime.o') and statistics_graph['application_sha256']==app_hash
    assert statistics_graph['provider_reports']=={'native-battery-statistics/report.json':sha(stats_dir/'report.json')}
    expected_statistics={n:2896 for n in ('r1_battery_charged_state_refresh','r1_battery_voltage_average','r1_battery_level_average')}
    assert statistics_graph['executed_statistics_entry_counts']=={'native':expected_statistics,'source':expected_statistics}
    for module in ('native-battery-runtime','native-battery-statistics'):
        r=json.loads((BASE/module/'report.json').read_text());assert '-munaligned-access' in r['units'][0]['command']
        assert 'r1/components/board/native_battery_memory.h' in r['inputs']
    stacmd_stage_dir=BASE/'native-stacmd-stage';stacmd_stage=json.loads((stacmd_stage_dir/'verification.json').read_text())
    assert stacmd_stage['shared_header_sha256']==sha(ROOT/'r1/components/board/native_stacmd.h')
    assert stacmd_stage['driver_sha256']==sha(ROOT/'r1/tools/check_native_stacmd_stage.py') and stacmd_stage['stage_object_sha256']==sha(stacmd_stage_dir/'stacmd-stage.o')
    assert stacmd_stage['board_report_sha256']==sha(BASE/'board/report.json') and stacmd_stage['board_object_sha256']==sha(BASE/'board/native-board.o')
    assert stacmd_stage['registration_report_sha256']==sha(BASE/'native-stacmd-registration/report.json')
    for path,digest in stacmd_stage['provider_reports'].items():assert sha(BASE/path)==digest,path
    for path,digest in stacmd_stage['objects'].items():assert sha(ROOT/path)==digest,path
    stacmd_board=json.loads((BASE/'board/report.json').read_text());stacmd_closed={'r1_stacmd_open','r1_stacmd_close','r1_stacmd_read','r1_stacmd_write'}
    assert set(stacmd_stage['remaining_symbols'])==set(stacmd_board['remaining_symbols'])-stacmd_closed and len(stacmd_stage['remaining_symbols'])==56
    assert set(stacmd_stage['closed_board_operation_providers'])==stacmd_closed and stacmd_stage['new_unresolved_data']==[]
    assert stacmd_stage['canonical_board_integrated'] and not stacmd_stage['application_linked'] and not stacmd_stage['instruction_identity']
    assert len(stacmd_board['remaining_symbols'])==56 and len(stacmd_stage['objects'])==1
    for module in ('operations','recovery','transmit','receive','frames','delay','write-retry','state'):
        name='native-stacmd-'+module;path='r1/research/source-build/'+name+'/'+name.replace('-','_')+'.o';assert stacmd_board['objects'][path]==sha(ROOT/path) and stacmd_board['input_reports'][name+'/report.json']==sha(BASE/name/'report.json')
    for module in ('native-stacmd-registration','native-stacmd-operations','native-stacmd-recovery','native-stacmd-transmit','native-stacmd-receive','native-stacmd-frames','native-stacmd-delay','native-stacmd-write-retry','native-stacmd-state'):
        assert json.loads((BASE/module/'report.json').read_text())['inputs']['r1/components/board/native_stacmd.h']==stacmd_stage['shared_header_sha256']
    ss_dir=BASE/'native-stacmd-state';ss=json.loads((ss_dir/'verification.json').read_text())
    assert ss['comparisons']==4 and ss['source_initializer_bytes']==4 and ss['source_initializer_sha256']==hashlib.sha256(bytes(4)).hexdigest()
    assert ss['report_sha256']==sha(ss_dir/'report.json') and ss['object_sha256']==sha(ss_dir/'native_stacmd_state.o')
    assert ss['driver_sha256']==sha(ROOT/'r1/tools/verify_native_stacmd_state.py') and ss['application_sha256']==app_hash
    assert not ss['application_linked'] and not ss['instruction_identity'] and ss['scatter_entry']=='0x283a0' and ss['stop_before_runtime']=='0x27208'
    for path,digest in json.loads((ss_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    assert [run['ram_poison'] for run in ss['runs']]==[0xa5,0x5a,0xff,0x3c]
    for run in ss['runs']:
        assert run['native_counter_hex']==run['source_counter_hex']=='00000000' and run['native_configuration_name_pointer']==0xc07c8
        assert run['native_writes']==[{'pc':0x28726,'address':0x200075c0+i,'bytes':1,'value':0} for i in range(4)]
    for filename,row in ss['ghidra_evidence'].items():
        path=ss_dir/filename;assert sha(path)==row['sha256'];address=row['address'];size=row['bytes']
        assert bytes(json.loads(path.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    assert stacmd_stage['state_verification_sha256']==sha(ss_dir/'verification.json')
    owned_graph=json.loads((stacmd_stage_dir/'wire-integration-verification.json').read_text())
    assert owned_graph['comparisons']==192 and owned_graph['counts']=={'read':96,'write':96} and owned_graph['outcomes']=={'success':24,'failure':168}
    assert owned_graph['status_counts']=={'0':24,'11':96,'27':24,'29':24,'30':12,'31':12} and owned_graph['logging_mode']==0 and owned_graph['source_owned_counter_initial_value']==0
    assert owned_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_stacmd_owned_state_graph.py') and owned_graph['application_sha256']==app_hash
    assert not owned_graph['provider_interception'] and not owned_graph['application_linked'] and not owned_graph['instruction_identity']
    owned_modules=('native-stacmd-frames','native-stacmd-transmit','native-stacmd-receive','native-stacmd-delay','native-stacmd-operations','native-stacmd-write-retry','native-stacmd-recovery','native-stacmd-state','native-stacmd-registration')
    assert owned_graph['provider_reports']=={module+'/report.json':sha(BASE/module/'report.json') for module in owned_modules}
    for path,digest in owned_graph['provider_objects'].items():assert sha(BASE/path)==digest,path
    assert len(owned_graph['provider_objects'])==9
    assert owned_graph['executed_provider_entry_counts']['native']==owned_graph['executed_provider_entry_counts']['source']
    assert owned_graph['executed_provider_entry_counts']['source']=={'r1_stacmd_read_frame_native':126,'r1_stacmd_write_frame_native':126,'r1_stacmd_drive_bit_native':2152,'r1_stacmd_write_bits_native':268,'r1_stacmd_idle_native':504,'r1_stacmd_parity_native':168,'r1_stacmd_read_bit_native':396,'r1_stacmd_read_bit_adapter_native':268,'r1_stacmd_recovery_delay_native':1764,'r1_stacmd_read':96,'r1_stacmd_write':96,'r1_stacmd_write_retry_native':24,'r1_stacmd_bus_recovery_native':252}
    assert owned_graph['total_nops']=={'native':1733560,'source':1733560} and owned_graph['gpio_callback_counts']=={'native':124040,'source':124040}
    owned_sections=owned_graph['source_owned_sections'];assert set(owned_sections)=={'counter','configuration','name'}
    for name,address,size in [('counter',0x200075c0,4),('configuration',0x200075c4,108),('name',0xc07c8,14)]:assert owned_sections[name]['address']==address and owned_sections[name]['bytes']==size
    assert owned_sections['counter']['sha256']==ss['source_initializer_sha256'] and owned_sections['name']['sha256']==hashlib.sha256(b'device_stacmd\0').hexdigest()
    registry_graph=json.loads((stacmd_stage_dir/'registry-integration-verification.json').read_text())
    assert registry_graph['comparisons']==192 and registry_graph['counts']=={'read':96,'write':96} and registry_graph['outcomes']=={'success':24,'failure':168}
    assert registry_graph['status_counts']=={'0':24,'11':96,'27':24,'29':24,'30':12,'31':12} and registry_graph['registration_calls_per_case']==2 and registry_graph['logging_mode']==0
    assert registry_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_stacmd_registry_graph.py') and registry_graph['application_sha256']==app_hash
    assert not registry_graph['provider_interception'] and not registry_graph['application_linked'] and not registry_graph['instruction_identity']
    assert registry_graph['provider_reports']=={module+'/report.json':sha(BASE/module/'report.json') for module in (*owned_modules,'i2c5','runtime')}
    for path,digest in registry_graph['provider_objects'].items():assert sha(BASE/path)==digest,path
    assert len(registry_graph['provider_objects'])==11
    assert registry_graph['executed_provider_entry_counts']['native']==registry_graph['executed_provider_entry_counts']['source']
    assert registry_graph['executed_provider_entry_counts']['source']=={**owned_graph['executed_provider_entry_counts']['source'],'r1_yhm2710_stacmd_binding_configuration':384,'r1_stock_registry_register':384,'strcmp':192,'r1_stock_dispatch_08':96,'r1_stock_dispatch_0c':96,'r1_stock_dispatch_10':96,'r1_stock_dispatch_14':96,'r1_stacmd_open':96,'r1_stacmd_close':96}
    assert registry_graph['total_nops']=={'native':1733560,'source':1733560} and registry_graph['gpio_callback_counts']=={'native':124040,'source':124040}
    assert registry_graph['source_owned_sections']==owned_graph['source_owned_sections'] and registry_graph['source_owned_counter_initial_value']==0
    gpio_graph=json.loads((stacmd_stage_dir/'gpio-integration-verification.json').read_text())
    assert gpio_graph['comparisons']==192 and gpio_graph['counts']=={'read':96,'write':96} and gpio_graph['outcomes']=={'success':24,'failure':168}
    assert gpio_graph['status_counts']=={'0':24,'11':96,'27':24,'29':24,'30':12,'31':12} and gpio_graph['registration_calls_per_case']==2 and gpio_graph['logging_mode']==0
    assert gpio_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_stacmd_gpio_graph.py') and gpio_graph['application_sha256']==app_hash
    assert not gpio_graph['provider_interception'] and not gpio_graph['gpio_provider_interception'] and not gpio_graph['application_linked'] and not gpio_graph['instruction_identity']
    assert gpio_graph['provider_reports']=={**registry_graph['provider_reports'],'software-twi/gpio-report.json':sha(BASE/'software-twi/gpio-report.json')}
    for path,digest in gpio_graph['provider_objects'].items():assert sha(BASE/path)==digest,path
    assert len(gpio_graph['provider_objects'])==12
    assert gpio_graph['executed_provider_entry_counts']['native']==gpio_graph['executed_provider_entry_counts']['source']
    assert gpio_graph['executed_provider_entry_counts']['source']=={**registry_graph['executed_provider_entry_counts']['source'],'r1_twi_gpio_low':2908,'r1_twi_gpio_high':8724,'r1_twi_gpio_output':2908,'r1_twi_gpio_input':420,'r1_twi_gpio_read':109080}
    assert gpio_graph['total_nops']=={'native':1733560,'source':1733560} and gpio_graph['gpio_callback_counts']=={'native':124040,'source':124040}
    for name in ('counter','configuration','name'):assert gpio_graph['source_owned_sections'][name]['bytes']==owned_sections[name]['bytes'] and gpio_graph['source_owned_sections'][name]['address']==owned_sections[name]['address']
    assert gpio_graph['source_owned_sections']['counter']['sha256']==ss['source_initializer_sha256'] and gpio_graph['source_owned_counter_initial_value']==0
    rx_dir=BASE/'native-stacmd-receive';rx=json.loads((rx_dir/'verification.json').read_text())
    assert rx['comparisons']==1152 and rx['counts']=={'r1_stacmd_read_bit_native':576,'r1_stacmd_read_bit_adapter_native':576} and rx['edge_boundary_pairs']==24
    assert rx['total_nops']=={'native':119808,'source':119808} and rx['read_callback_counts']=={'native':1633824,'source':1633824}
    assert rx['report_sha256']==sha(rx_dir/'report.json') and rx['object_sha256']==sha(rx_dir/'native_stacmd_receive.o')
    assert rx['driver_sha256']==sha(ROOT/'r1/tools/verify_native_stacmd_receive.py') and rx['application_sha256']==app_hash
    assert not rx['application_linked'] and not rx['instruction_identity']
    rx_report=json.loads((rx_dir/'report.json').read_text());assert '-falign-loops=1' in rx_report['units'][0]['command']
    for path,digest in rx_report['inputs'].items():assert sha(ROOT/path)==digest,path
    rx_entries={'r1_stacmd_read_bit_native':(0x87b30,110),'r1_stacmd_read_bit_adapter_native':(0x969ec,16)}
    for filename,digest in rx['ghidra_evidence'].items():
        path=rx_dir/filename;assert sha(path)==digest;address,size=rx_entries[filename.removeprefix('ghidra-').removesuffix('.json')]
        assert bytes(json.loads(path.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    assert rx['body_evidence_sha256']==sha(rx_dir/'evidence.json');rx_ev=json.loads((rx_dir/'evidence.json').read_text());assert not rx_ev['locked_ownership_changed'] and rx_ev['polls_per_edge']==1000 and rx_ev['nop_iterations']==26 and rx_ev['nops_per_iteration']==4
    assert rx_ev['ownership_rows']==[row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and int(row['entry'],16) in [a for a,z in rx_entries.values()]]
    st_dir=BASE/'native-stacmd-transmit';st=json.loads((st_dir/'verification.json').read_text())
    assert st['comparisons']==5792 and st['counts']=={'r1_stacmd_drive_bit_native':560,'r1_stacmd_write_bits_native':4096,'r1_stacmd_idle_native':112,'r1_stacmd_parity_native':1024}
    assert st['total_nops']=={'native':4225728,'source':4225728}
    assert st['report_sha256']==sha(st_dir/'report.json') and st['object_sha256']==sha(st_dir/'native_stacmd_transmit.o')
    assert st['driver_sha256']==sha(ROOT/'r1/tools/verify_native_stacmd_transmit.py') and st['application_sha256']==app_hash
    assert not st['application_linked'] and not st['instruction_identity']
    st_report=json.loads((st_dir/'report.json').read_text());assert '-falign-loops=1' in st_report['units'][0]['command']
    for path,digest in st_report['inputs'].items():assert sha(ROOT/path)==digest,path
    st_entries={'r1_stacmd_drive_bit_native':(0x5cbe4,126),'r1_stacmd_write_bits_native':(0x5cc68,36),'r1_stacmd_idle_native':(0x5cccc,42),'r1_stacmd_parity_native':(0x968a8,26)}
    for filename,digest in st['ghidra_evidence'].items():
        path=st_dir/filename;assert sha(path)==digest;address,size=st_entries[filename.removeprefix('ghidra-').removesuffix('.json')]
        assert bytes(json.loads(path.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    assert st['body_evidence_sha256']==sha(st_dir/'evidence.json');st_ev=json.loads((st_dir/'evidence.json').read_text());assert not st_ev['locked_ownership_changed'] and st_ev['drive_body_bytes']==118 and st_ev['drive_span_bytes']==126
    assert st_ev['drive_ranges']==[{'start':'0x5cbe4','end':'0x5cbed'},{'start':'0x5cbf0','end':'0x5cc25'},{'start':'0x5cc2c','end':'0x5cc61'}]
    assert st_ev['ownership_rows']==[row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and int(row['entry'],16) in [a for a,z in st_entries.values()]]
    sf_dir=BASE/'native-stacmd-frames';sf=json.loads((sf_dir/'verification.json').read_text())
    assert sf['comparisons']==15360 and sf['counts']=={'r1_stacmd_read_frame_native':7680,'r1_stacmd_write_frame_native':7680}
    assert sf['report_sha256']==sha(sf_dir/'report.json') and sf['object_sha256']==sha(sf_dir/'native_stacmd_frames.o')
    assert sf['driver_sha256']==sha(ROOT/'r1/tools/verify_native_stacmd_frames.py') and sf['application_sha256']==app_hash
    assert not sf['application_linked'] and not sf['instruction_identity']
    for path,digest in json.loads((sf_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    sf_entries={'r1_stacmd_read_frame_native':(0x28bb0,184),'r1_stacmd_write_frame_native':(0x28c6c,130)}
    for filename,digest in sf['ghidra_evidence'].items():
        path=sf_dir/filename;assert sha(path)==digest;address,size=sf_entries[filename.removeprefix('ghidra-').removesuffix('.json')]
        assert bytes(json.loads(path.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    assert sf['body_evidence_sha256']==sha(sf_dir/'evidence.json');sf_ev=json.loads((sf_dir/'evidence.json').read_text());assert not sf_ev['locked_ownership_changed'] and sf_ev['read_partial_byte_stored'] and sf_ev['length_comparison']=='signed32 index versus length'
    assert sf_ev['ownership_rows']==[row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and int(row['entry'],16) in [a for a,z in sf_entries.values()]]
    sf_report=json.loads((sf_dir/'report.json').read_text());assert '-falign-loops=1' in sf_report['units'][0]['command']
    wire_graph=json.loads((sf_dir/'wire-integration-verification.json').read_text())
    assert wire_graph['comparisons']==480 and wire_graph['counts']=={'read':240,'write':240} and wire_graph['outcomes']=={'success':96,'failure':384}
    assert wire_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_stacmd_wire_graph.py') and wire_graph['application_sha256']==app_hash
    assert not wire_graph['provider_interception'] and not wire_graph['application_linked'] and not wire_graph['instruction_identity']
    wire_modules=('native-stacmd-frames','native-stacmd-transmit','native-stacmd-receive','native-stacmd-delay')
    assert wire_graph['provider_reports']=={module+'/report.json':sha(BASE/module/'report.json') for module in wire_modules}
    assert wire_graph['provider_objects']=={module+'/'+module.replace('-','_')+'.o':sha(BASE/module/(module.replace('-','_')+'.o')) for module in wire_modules}
    assert wire_graph['executed_provider_entry_counts']['native']==wire_graph['executed_provider_entry_counts']['source']
    assert set(wire_graph['executed_provider_entry_counts']['source'])=={'r1_stacmd_read_frame_native','r1_stacmd_write_frame_native','r1_stacmd_drive_bit_native','r1_stacmd_write_bits_native','r1_stacmd_idle_native','r1_stacmd_parity_native','r1_stacmd_read_bit_native','r1_stacmd_read_bit_adapter_native','r1_stacmd_recovery_delay_native'}
    assert wire_graph['executed_provider_entry_counts']['source']=={'r1_stacmd_read_frame_native':240,'r1_stacmd_write_frame_native':240,'r1_stacmd_drive_bit_native':2960,'r1_stacmd_write_bits_native':368,'r1_stacmd_idle_native':800,'r1_stacmd_parity_native':240,'r1_stacmd_read_bit_native':672,'r1_stacmd_read_bit_adapter_native':368,'r1_stacmd_recovery_delay_native':800}
    assert wire_graph['total_nops']=={'native':1132224,'source':1132224}
    assert wire_graph['gpio_callback_counts']=={'native':181424,'source':181424}
    sw_dir=BASE/'native-stacmd-write-retry';sw=json.loads((sw_dir/'verification.json').read_text())
    assert sw['comparisons']==2574 and sw['mode_sequences']==13
    assert sw['report_sha256']==sha(sw_dir/'report.json') and sw['object_sha256']==sha(sw_dir/'native_stacmd_write_retry.o')
    assert sw['driver_sha256']==sha(ROOT/'r1/tools/verify_native_stacmd_write_retry.py') and sw['application_sha256']==app_hash
    assert not sw['application_linked'] and not sw['instruction_identity']
    for path,digest in json.loads((sw_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    assert sw['ghidra_memory_sha256']==sha(sw_dir/'ghidra-memory.json') and sw['body_evidence_sha256']==sha(sw_dir/'evidence.json')
    assert bytes(json.loads((sw_dir/'ghidra-memory.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x35698-0x27000:0x35760-0x27000]
    sw_ev=json.loads((sw_dir/'evidence.json').read_text());assert not sw_ev['locked_ownership_changed'] and not sw_ev['rea_structured_metadata_obtained'] and sw_ev['attempts']==9
    assert sw_ev['ownership_row']==next(row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and row['entry']=='0x00035698')
    assert sw['source_descriptor_sections']=={'ring':{'address':0x3570c,'bytes':38,'sha256':'8360562816f894bcfba1a30c75088e75d75bb04a7647d0690cc0ae9c2510a208'},'sdk':{'address':0x3573c,'bytes':32,'sha256':'4badfbf0937764e18e3215ddfebd880295f14ead8a541067c3f8619d5e985147'}}
    sd_dir=BASE/'native-stacmd-delay';sd=json.loads((sd_dir/'verification.json').read_text())
    assert sd['comparisons']==64 and sd['nops_per_call']==836 and sd['total_nops']=={'native':53504,'source':53504}
    assert sd['report_sha256']==sha(sd_dir/'report.json') and sd['object_sha256']==sha(sd_dir/'native_stacmd_delay.o')
    assert sd['driver_sha256']==sha(ROOT/'r1/tools/verify_native_stacmd_delay.py') and sd['application_sha256']==app_hash
    assert not sd['application_linked'] and not sd['instruction_identity']
    sd_report=json.loads((sd_dir/'report.json').read_text());assert '-falign-loops=1' in sd_report['units'][0]['command']
    for path,digest in sd_report['inputs'].items():assert sha(ROOT/path)==digest,path
    assert sd['ghidra_memory_sha256']==sha(sd_dir/'ghidra-memory.json') and sd['body_evidence_sha256']==sha(sd_dir/'evidence.json')
    assert bytes(json.loads((sd_dir/'ghidra-memory.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x5c0fa-0x27000:0x5c10e-0x27000]
    sd_ev=json.loads((sd_dir/'evidence.json').read_text());assert sd_ev['iterations']==209 and sd_ev['nops_per_iteration']==4 and not sd_ev['locked_ownership_changed']
    assert sd_ev['ownership_row']==next(row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and row['entry']=='0x0005c0fa')
    sr_dir=BASE/'native-stacmd-recovery';sr=json.loads((sr_dir/'verification.json').read_text())
    assert sr['comparisons']==240 and sr['report_sha256']==sha(sr_dir/'report.json') and sr['object_sha256']==sha(sr_dir/'native_stacmd_recovery.o')
    assert sr['driver_sha256']==sha(ROOT/'r1/tools/verify_native_stacmd_recovery.py') and sr['application_sha256']==app_hash
    assert not sr['application_linked'] and not sr['instruction_identity']
    for path,digest in json.loads((sr_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    assert sr['ghidra_memory_sha256']==sha(sr_dir/'ghidra-memory.json') and sr['body_evidence_sha256']==sha(sr_dir/'evidence.json')
    assert bytes(json.loads((sr_dir/'ghidra-memory.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x5cc8c-0x27000:0x5ccc6-0x27000]
    sr_ev=json.loads((sr_dir/'evidence.json').read_text());assert not sr_ev['locked_ownership_changed'] and not sr_ev['rea_structured_metadata_obtained']
    assert sr_ev['ownership_row']==next(row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and row['entry']=='0x0005cc8c') and sr_ev['delay_calls']==5
    sr_graph=json.loads((sr_dir/'delay-integration-verification.json').read_text())
    assert sr_graph['real_delay'] and not sr_graph['delay_provider_interception'] and sr_graph['comparisons']==240
    assert sr_graph['provider_reports']=={'native-stacmd-delay/report.json':sha(sd_dir/'report.json')}
    assert sr_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_stacmd_recovery.py') and sr_graph['report_sha256']==sha(sr_dir/'report.json') and sr_graph['object_sha256']==sha(sr_dir/'native_stacmd_recovery.o')
    assert sr_graph['application_sha256']==app_hash and not sr_graph['application_linked'] and not sr_graph['instruction_identity']
    assert sr_graph['total_nops']=={'native':1003200,'source':1003200} and sr_graph['executed_delay_entry_counts']=={'native':1200,'source':1200}
    for field in ('ghidra_memory_sha256','body_evidence_sha256'):assert sr_graph[field]==sr[field]
    so_dir=BASE/'native-stacmd-operations';so=json.loads((so_dir/'verification.json').read_text())
    assert so['comparisons']==1580 and so['counts']=={'r1_stacmd_close':256,'r1_stacmd_open':256,'r1_stacmd_read':960,'r1_stacmd_write':108}
    assert so['report_sha256']==sha(so_dir/'report.json') and so['object_sha256']==sha(so_dir/'native_stacmd_operations.o')
    assert so['driver_sha256']==sha(ROOT/'r1/tools/verify_native_stacmd_operations.py') and so['application_sha256']==app_hash
    assert not so['application_linked'] and not so['instruction_identity']
    for path,digest in json.loads((so_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    so_entries={'r1_stacmd_close':(0x56568,14),'r1_stacmd_open':(0x5657c,16),'r1_stacmd_read':(0x56590,94),'r1_stacmd_write':(0x5660c,40)}
    for filename,digest in so['ghidra_evidence'].items():
        path=so_dir/filename;assert sha(path)==digest;address,size=so_entries[filename.removeprefix('ghidra-').removesuffix('.json')]
        assert bytes(json.loads(path.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    assert so['body_evidence_sha256']==sha(so_dir/'evidence.json');so_ev=json.loads((so_dir/'evidence.json').read_text())
    assert not so_ev['rea_function_metadata_available'] and not so_ev['locked_ownership_changed']
    assert so_ev['ownership_rows']==[row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and int(row['entry'],16) in [a for a,z in so_entries.values()]]
    so_graph=json.loads((so_dir/'retry-integration-verification.json').read_text())
    assert so_graph['real_retry'] and not so_graph['retry_provider_interception'] and so_graph['comparisons']==1580 and so_graph['counts']==so['counts']
    assert so_graph['provider_reports']=={'native-stacmd-write-retry/report.json':sha(sw_dir/'report.json')}
    assert so_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_stacmd_operations.py') and so_graph['report_sha256']==sha(so_dir/'report.json') and so_graph['object_sha256']==sha(so_dir/'native_stacmd_operations.o')
    assert so_graph['application_sha256']==app_hash and not so_graph['application_linked'] and not so_graph['instruction_identity']
    assert so_graph['executed_retry_entry_counts']=={'native':36,'source':36} and so_graph['executed_write_frame_counts']=={'native':132,'source':132}
    for field in ('ghidra_evidence','body_evidence_sha256'):assert so_graph[field]==so[field]
    adapter_wire=json.loads((so_dir/'wire-integration-verification.json').read_text())
    assert adapter_wire['comparisons']==192 and adapter_wire['counts']=={'read':96,'write':96} and adapter_wire['outcomes']=={'success':24,'failure':168}
    assert adapter_wire['status_counts']=={'0':24,'11':96,'27':24,'29':24,'30':12,'31':12} and adapter_wire['logging_mode']==0
    assert adapter_wire['driver_sha256']==sha(ROOT/'r1/tools/verify_native_stacmd_adapter_wire_graph.py') and adapter_wire['application_sha256']==app_hash
    assert not adapter_wire['provider_interception'] and not adapter_wire['application_linked'] and not adapter_wire['instruction_identity']
    adapter_modules=('native-stacmd-frames','native-stacmd-transmit','native-stacmd-receive','native-stacmd-delay','native-stacmd-operations','native-stacmd-write-retry','native-stacmd-recovery')
    assert adapter_wire['provider_reports']=={module+'/report.json':sha(BASE/module/'report.json') for module in adapter_modules}
    assert adapter_wire['provider_objects']=={module+'/'+module.replace('-','_')+'.o':sha(BASE/module/(module.replace('-','_')+'.o')) for module in adapter_modules}
    assert adapter_wire['executed_provider_entry_counts']['native']==adapter_wire['executed_provider_entry_counts']['source']
    assert adapter_wire['executed_provider_entry_counts']['source']=={'r1_stacmd_read_frame_native':126,'r1_stacmd_write_frame_native':126,'r1_stacmd_drive_bit_native':2152,'r1_stacmd_write_bits_native':268,'r1_stacmd_idle_native':504,'r1_stacmd_parity_native':168,'r1_stacmd_read_bit_native':396,'r1_stacmd_read_bit_adapter_native':268,'r1_stacmd_recovery_delay_native':1764,'r1_stacmd_read':96,'r1_stacmd_write':96,'r1_stacmd_write_retry_native':24,'r1_stacmd_bus_recovery_native':252}
    assert adapter_wire['total_nops']=={'native':1733560,'source':1733560}
    assert adapter_wire['gpio_callback_counts']=={'native':124040,'source':124040}
    for module in ('native-stacmd-operations','native-stacmd-write-retry'):assert '-falign-loops=1' in json.loads((BASE/module/'report.json').read_text())['units'][0]['command']
    yi_dir=BASE/'native-yhm-initialize';yi=json.loads((yi_dir/'verification.json').read_text())
    assert yi['comparisons']==1536 and yi['workflows']==512 and yi['calls_per_workflow']==3
    assert yi['report_sha256']==sha(yi_dir/'report.json') and yi['object_sha256']==sha(yi_dir/'native_yhm_initialize.o')
    assert yi['driver_sha256']==sha(ROOT/'r1/tools/verify_native_yhm_initialize.py') and yi['application_sha256']==app_hash
    assert not yi['application_linked'] and not yi['instruction_identity']
    for path,digest in json.loads((yi_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    assert yi['ghidra_memory_sha256']==sha(yi_dir/'ghidra-memory.json') and yi['rea_sha256']==sha(yi_dir/'rea-body.json')
    assert bytes(json.loads((yi_dir/'ghidra-memory.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x50578-0x27000:0x50608-0x27000]
    yi_rea=json.loads((yi_dir/'rea-body.json').read_text())
    assert yi_rea['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and yi_rea['normalized_result']['body']['ranges']==[{'start':'0x50578','end':'0x505bd'}]
    yi_graph=json.loads((yi_dir/'registry-integration-verification.json').read_text())
    assert yi_graph['real_registry'] and not yi_graph['registry_provider_interception'] and yi_graph['comparisons']==3072 and yi_graph['workflows']==1024 and yi_graph['calls_per_workflow']==3
    assert yi_graph['provider_reports']=={'i2c5/report.json':sha(BASE/'i2c5/report.json'),'runtime/report.json':sha(BASE/'runtime/report.json')}
    assert yi_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_yhm_initialize.py') and yi_graph['report_sha256']==sha(yi_dir/'report.json') and yi_graph['object_sha256']==sha(yi_dir/'native_yhm_initialize.o')
    assert yi_graph['application_sha256']==app_hash and not yi_graph['application_linked'] and not yi_graph['instruction_identity']
    yi_counts={'r1_stock_registry_find':4160,'r1_stock_dispatch_08':1024,'r1_stock_dispatch_18':1024,'strcmp':6536}
    assert yi_graph['executed_registry_entry_counts']=={'native':yi_counts,'source':yi_counts}
    for field in ('ghidra_memory_sha256','rea_sha256'):assert yi_graph[field]==yi[field]
    yt_dir=BASE/'native-yhm-transport';yt=json.loads((yt_dir/'verification.json').read_text())
    assert yt['comparisons']==2928 and yt['counts']=={'r1_yhm_transport_acquire':16,'r1_yhm_transport_release':16,'r1_yhm_transport_complete':16,'r1_yhm_register_read_record':960,'r1_yhm_register_write_record':960,'r1_yhm_register_write_native':960}
    assert yt['report_sha256']==sha(yt_dir/'report.json') and yt['object_sha256']==sha(yt_dir/'native_yhm_transport.o')
    assert yt['driver_sha256']==sha(ROOT/'r1/tools/verify_native_yhm_transport.py') and yt['application_sha256']==app_hash
    assert not yt['application_linked'] and not yt['instruction_identity']
    for path,digest in json.loads((yt_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    yt_entries={'r1_yhm_transport_acquire':(0x50608,8),'r1_yhm_transport_release':(0x507a0,8),'r1_yhm_transport_complete':(0x50558,26),'r1_yhm_register_read_record':(0x507cc,46),'r1_yhm_register_write_record':(0x50804,46),'r1_yhm_register_write_native':(0x35760,6)}
    for filename,digest in yt['ghidra_evidence'].items():
        path=yt_dir/filename;assert sha(path)==digest;address,size=yt_entries[filename.removeprefix('ghidra-').removesuffix('.json')]
        assert bytes(json.loads(path.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    for filename,digest in yt['rea_evidence'].items():
        path=yt_dir/filename;assert sha(path)==digest
        assert json.loads(path.read_text())['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
    assert yt['body_evidence_sha256']==sha(yt_dir/'evidence.json');yt_ev=json.loads((yt_dir/'evidence.json').read_text())
    assert yt_ev['write_body']['total_bytes']==78 and yt_ev['write_body']['ranges']==[{'start':'0x35760','end':'0x35765'},{'start':'0x50558','end':'0x50571'},{'start':'0x50804','end':'0x50831'}]
    assert yt_ev['original_write_row']==next(row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and row['entry']=='0x00035760') and not yt_ev['locked_ownership_changed']
    yt_graph=json.loads((yt_dir/'registry-integration-verification.json').read_text())
    assert yt_graph['real_registry'] and not yt_graph['registry_provider_interception'] and yt_graph['comparisons']==11712
    assert yt_graph['counts']=={n:count*4 for n,count in yt['counts'].items()}
    assert yt_graph['provider_reports']=={'i2c5/report.json':sha(BASE/'i2c5/report.json')}
    assert yt_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_yhm_transport.py') and yt_graph['report_sha256']==sha(yt_dir/'report.json') and yt_graph['object_sha256']==sha(yt_dir/'native_yhm_transport.o')
    assert yt_graph['application_sha256']==app_hash and not yt_graph['application_linked'] and not yt_graph['instruction_identity']
    yt_registry_counts={'r1_stock_dispatch_08':11584,'r1_stock_dispatch_0c':23168,'r1_stock_dispatch_10':3840,'r1_stock_dispatch_14':7680}
    assert yt_graph['executed_registry_entry_counts']=={'native':yt_registry_counts,'source':yt_registry_counts}
    for field in ('ghidra_evidence','rea_evidence','body_evidence_sha256'):assert yt_graph[field]==yt[field]
    track_dir=BASE/'native-yhm-system-track';track=json.loads((track_dir/'verification.json').read_text())
    assert track['comparisons']==80184 and track['counts']=={'r1_yhm_system_track_native':40092,'r1_native_charger_initialize':40092} and track['mode_sequences']==13
    assert track['all_read_bytes'] and track['no_write_case'] and track['full_r2_r3_return_checked']
    assert track['report_sha256']==sha(track_dir/'report.json') and track['object_sha256']==sha(track_dir/'native_yhm_system_track.o') and track['driver_sha256']==sha(ROOT/'r1/tools/verify_native_yhm_system_track.py') and track['application_sha256']==app_hash
    assert not track['application_linked'] and not track['instruction_identity']
    for path,digest in json.loads((track_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    for filename,digest in track['ghidra_evidence'].items():
        path=track_dir/filename;assert sha(path)==digest;address,size={'ghidra-r1_yhm_system_track_native.json':(0x355bc,200),'ghidra-r1_native_charger_initialize.json':(0x5079c,4)}[filename]
        assert bytes(json.loads(path.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    for filename,digest in track['rea_evidence'].items():
        path=track_dir/filename;assert sha(path)==digest;q=json.loads(path.read_text());assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
        address=int(filename.removeprefix('rea-').removesuffix('.json'),16);assert q['normalized_result']['entrypoint']==hex(address) and q['normalized_result']['body']['total_bytes']=={0x355bc:106,0x5079c:4}[address]
    assert track['body_evidence_sha256']==sha(track_dir/'evidence.json');track_ev=json.loads((track_dir/'evidence.json').read_text());assert not track_ev['locked_ownership_changed']
    assert track_ev['ownership_rows']==[row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and int(row['entry'],16) in (0x355bc,0x5079c)]
    for name,address in [('ring',0x35628),('sdk',0x3565c)]:
        descriptor=track['source_descriptor_sections'][name];assert descriptor['address']==address
        payload=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+descriptor['bytes']];assert hashlib.sha256(payload).hexdigest()==descriptor['sha256'] and payload.endswith(b'\0')
    decimal_dir=BASE/'native-formatter-decimal';decimal=json.loads((decimal_dir/'verification.json').read_text())
    assert decimal['comparisons']==4818 and decimal['zero_cases']==28 and decimal['result_buffer_alias_cases']==260
    assert decimal['native_math_calls_per_side']=={'multiply':58562,'divide':4878,'add':4882,'to_unsigned':4882}
    assert decimal['all_nonnegative_binary64_exponents'] and decimal['native_math_argument_traces_checked'] and decimal['actual_source_integer_division'] and decimal['r0_stack_and_callee_saved_checked'] and decimal['source_owned_zero_bytes']==4
    assert decimal['precision_modes_tested']==[[1,0],[6,0],[17,0],[0,1],[6,1],[20,1]]
    assert decimal['trace_sha256']=='162d94a37b66ca3fc60eb486a93c9204320d0174854749e0eb3d6a8c7d2668c6'
    assert decimal['report_sha256']==sha(decimal_dir/'report.json') and decimal['object_sha256']==sha(decimal_dir/'native_formatter_decimal.o') and decimal['driver_sha256']==sha(ROOT/'r1/tools/verify_native_formatter_decimal.py') and decimal['application_sha256']==app_hash and not decimal['instruction_identity']
    assert decimal['integer_report_sha256']==sha(BASE/'integer-runtime/report.json') and decimal['integer_object_sha256']==sha(BASE/'integer-runtime/integer-runtime.o')
    for path,digest in json.loads((decimal_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in decimal['evidence'].items():assert sha(decimal_dir/path)==digest,path
    raw=json.loads((decimal_dir/'rea-3f530.json').read_text());q=raw.get('structuredContent') or json.loads(next(c['text'] for c in raw['content'] if c['type']=='text'))
    assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']=='0x3f530' and q['normalized_result']['body']['total_bytes']==366
    for address,size in [(0x3f530,366),(0x3f6a0,20)]:assert bytes(json.loads((decimal_dir/f'ghidra-{address:x}.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    decimal_graph=json.loads((decimal_dir/'graph-verification.json').read_text())
    assert decimal_graph['cases']==225 and decimal_graph['matched']==225 and not decimal_graph['differences'] and not decimal_graph['execution_errors']
    assert decimal_graph['provider_calls']=={'r1_format_width_padding':190,'r1_format_bounded_putc':1880,'r1_format_left_padding':190,'r1_format_decimal_digits':120}
    assert decimal_graph['report_sha256']==sha(decimal_dir/'report.json') and decimal_graph['object_sha256']==sha(decimal_dir/'native_formatter_decimal.o') and decimal_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_formatter_decimal_graph.py') and decimal_graph['application_sha256']==app_hash
    assert decimal_graph['trace_sha256']=='5c2e57b38a08196c82c59cdfad6283e500ff618c103f9c16c437dce72f47f389' and not decimal_graph['native_equivalence_proven'] and not decimal_graph['instruction_identity'] and decimal_graph['evidence']==decimal['evidence']
    assert decimal_graph['actual_native_core'] and decimal_graph['actual_C_output_helpers'] and decimal_graph['callee_saved_registers_checked'] and not decimal_graph['native_sram_reads_outside_arguments_output_and_stack']
    assert decimal_graph['provider_reports']=={path:sha(BASE/path) for path in ['native-formatter-output/report.json','integer-runtime/report.json']}
    unsigned_dir=BASE/'native-formatter-unsigned';unsigned=json.loads((unsigned_dir/'verification.json').read_text())
    assert unsigned['comparisons']==81920 and unsigned['all_binary64_exponents'] and unsigned['both_signs'] and unsigned['fraction_high_patterns']==4 and unsigned['fraction_low_patterns']==4 and unsigned['seeded_random_patterns']==16384 and unsigned['oversized_exponent_nonzero_cases']==3761
    assert unsigned['actual_source_shift_providers'] and unsigned['r0_r1_stack_and_callee_saved_checked'] and not unsigned['instruction_identity']
    assert unsigned['trace_sha256']=='649b506279490bb5b2a7c6ef9ee2fc3881b9725a6c6101e16816cdf6dc1276b7'
    assert unsigned['report_sha256']==sha(unsigned_dir/'report.json') and unsigned['object_sha256']==sha(unsigned_dir/'native_formatter_unsigned.o') and unsigned['driver_sha256']==sha(ROOT/'r1/tools/verify_native_formatter_unsigned.py') and unsigned['application_sha256']==app_hash
    assert unsigned['integer_report_sha256']==sha(BASE/'integer-runtime/report.json') and unsigned['integer_object_sha256']==sha(BASE/'integer-runtime/integer-runtime.o')
    for path,digest in json.loads((unsigned_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in unsigned['evidence'].items():assert sha(unsigned_dir/path)==digest,path
    raw=json.loads((unsigned_dir/'rea-28334.json').read_text());q=raw.get('structuredContent') or json.loads(next(c['text'] for c in raw['content'] if c['type']=='text'))
    assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']=='0x28334' and q['normalized_result']['body']['total_bytes']==48
    assert bytes(json.loads((unsigned_dir/'ghidra-28334.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x1334:0x1364]
    unsigned_decimal=json.loads((unsigned_dir/'decimal-integration-verification.json').read_text())
    for field in ('comparisons','zero_cases','result_buffer_alias_cases','native_math_calls_per_side','all_nonnegative_binary64_exponents','precision_modes_tested','source_owned_zero_bytes','native_math_argument_traces_checked','actual_source_integer_division','r0_stack_and_callee_saved_checked','trace_sha256','integer_report_sha256','integer_object_sha256','application_sha256','evidence','instruction_identity'):assert unsigned_decimal[field]==decimal[field],field
    assert unsigned_decimal['report_sha256']==sha(unsigned_dir/'report.json') and unsigned_decimal['object_sha256']==sha(unsigned_dir/'native_formatter_unsigned.o') and unsigned_decimal['driver_sha256']==sha(ROOT/'r1/tools/verify_native_formatter_unsigned_decimal_graph.py') and unsigned_decimal['decimal_report_sha256']==sha(decimal_dir/'report.json') and unsigned_decimal['decimal_object_sha256']==sha(decimal_dir/'native_formatter_decimal.o')
    unsigned_graph=json.loads((unsigned_dir/'formatter-integration-verification.json').read_text())
    assert unsigned_graph['cases']==225 and unsigned_graph['matched']==225 and not unsigned_graph['differences'] and not unsigned_graph['execution_errors']
    assert unsigned_graph['provider_calls']=={'r1_format_width_padding':190,'r1_format_bounded_putc':1880,'r1_format_left_padding':190,'r1_format_decimal_digits':120,'r1_format_double_to_unsigned_bits':100}
    assert unsigned_graph['report_sha256']==sha(unsigned_dir/'report.json') and unsigned_graph['object_sha256']==sha(unsigned_dir/'native_formatter_unsigned.o') and unsigned_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_formatter_unsigned_formatter_graph.py') and unsigned_graph['application_sha256']==app_hash and unsigned_graph['evidence']==unsigned['evidence']
    assert unsigned_graph['trace_sha256']=='5c2e57b38a08196c82c59cdfad6283e500ff618c103f9c16c437dce72f47f389' and not unsigned_graph['native_equivalence_proven'] and not unsigned_graph['instruction_identity'] and unsigned_graph['actual_native_core'] and unsigned_graph['actual_C_output_helpers']
    assert unsigned_graph['provider_reports']=={path:sha(BASE/path) for path in ['native-formatter-decimal/report.json','native-formatter-output/report.json','integer-runtime/report.json']}
    add_dir=BASE/'native-formatter-add';addition=json.loads((add_dir/'verification.json').read_text())
    assert addition['comparisons']==52778 and addition['counts']=={'add':34752,'shift':7420,'round':174,'normalize':10432}
    assert addition['addition_exponent_distance_boundaries']==[0,1,2,31,32,52,53,63,64,65]
    for flag in ('signed_shift_all_low_byte_counts','normalization_all_leading_bit_positions','normalization_random_sign_exponent_words','rounding_halfway_neighbors','actual_source_shift_providers','r0_r1_stack_and_callee_saved_checked'):assert addition[flag]
    assert addition['trace_sha256']=='df3188067933213e3499f41036d5d8e5535360ccadc87f2ec7c1be5f29596fe3' and not addition['instruction_identity']
    assert addition['report_sha256']==sha(add_dir/'report.json') and addition['object_sha256']==sha(add_dir/'native_formatter_add.o') and addition['driver_sha256']==sha(ROOT/'r1/tools/verify_native_formatter_add.py') and addition['application_sha256']==app_hash
    assert addition['integer_report_sha256']==sha(BASE/'integer-runtime/report.json') and addition['integer_object_sha256']==sha(BASE/'integer-runtime/integer-runtime.o')
    for path,digest in json.loads((add_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in addition['evidence'].items():assert sha(add_dir/path)==digest,path
    for address,size in [(0x27afc,322),(0x27fd0,36),(0x28122,30),(0x28140,156)]:
        raw=json.loads((add_dir/f'rea-{address:x}.json').read_text());q=raw.get('structuredContent') or json.loads(next(c['text'] for c in raw['content'] if c['type']=='text'))
        assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']==hex(address) and q['normalized_result']['body']['total_bytes']==size
        assert bytes(json.loads((add_dir/f'ghidra-{address:x}.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    add_decimal=json.loads((add_dir/'decimal-integration-verification.json').read_text())
    for field in ('comparisons','zero_cases','result_buffer_alias_cases','native_math_calls_per_side','all_nonnegative_binary64_exponents','precision_modes_tested','source_owned_zero_bytes','native_math_argument_traces_checked','actual_source_integer_division','r0_stack_and_callee_saved_checked','trace_sha256','integer_report_sha256','integer_object_sha256','application_sha256','evidence','instruction_identity'):assert add_decimal[field]==decimal[field],field
    assert add_decimal['report_sha256']==sha(add_dir/'report.json') and add_decimal['object_sha256']==sha(add_dir/'native_formatter_add.o') and add_decimal['driver_sha256']==sha(ROOT/'r1/tools/verify_native_formatter_add_decimal_graph.py')
    assert add_decimal['decimal_report_sha256']==sha(decimal_dir/'report.json') and add_decimal['decimal_object_sha256']==sha(decimal_dir/'native_formatter_decimal.o') and add_decimal['unsigned_report_sha256']==sha(unsigned_dir/'report.json') and add_decimal['unsigned_object_sha256']==sha(unsigned_dir/'native_formatter_unsigned.o')
    add_graph=json.loads((add_dir/'formatter-integration-verification.json').read_text())
    assert add_graph['cases']==225 and add_graph['matched']==225 and not add_graph['differences'] and not add_graph['execution_errors']
    assert add_graph['provider_calls']=={'r1_format_width_padding':190,'r1_format_bounded_putc':1880,'r1_format_left_padding':190,'r1_format_decimal_digits':120,'r1_format_double_normalize_bits':1055,'r1_format_double_add_bits':100,'r1_format_double_to_unsigned_bits':100,'r1_format_double_round_bits':80}
    assert add_graph['report_sha256']==sha(add_dir/'report.json') and add_graph['object_sha256']==sha(add_dir/'native_formatter_add.o') and add_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_formatter_add_formatter_graph.py') and add_graph['application_sha256']==app_hash and add_graph['evidence']==addition['evidence']
    assert add_graph['trace_sha256']=='5c2e57b38a08196c82c59cdfad6283e500ff618c103f9c16c437dce72f47f389' and not add_graph['native_equivalence_proven'] and not add_graph['instruction_identity'] and add_graph['actual_native_core'] and add_graph['actual_C_output_helpers']
    assert add_graph['provider_reports']=={path:sha(BASE/path) for path in ['native-formatter-unsigned/report.json','native-formatter-decimal/report.json','native-formatter-output/report.json','integer-runtime/report.json']}
    llvm_add=json.loads((add_dir/'llvm-add-experiment.json').read_text())
    assert llvm_add['cases']==2624 and llvm_add['counts']=={'matched':2441,'different':183} and len(llvm_add['differences'])==183 and not llvm_add['generic_upstream_replacement_admitted']
    assert llvm_add['trace_sha256']=='7aa0be42ce6df46c5d9d7cbfb99ea02032c29f367abc1907130cf65aabca5f99'
    assert llvm_add['source_report_sha256']==sha(BASE/'newlib-stdio/report.json') and llvm_add['driver_sha256']==sha(ROOT/'r1/tools/compare_native_formatter_add_llvm.py') and llvm_add['application_sha256']==app_hash
    for path,digest in json.loads((BASE/'newlib-stdio/report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in llvm_add['objects'].items():assert sha(BASE/'newlib-stdio'/path)==digest,path
    product_dir=BASE/'native-formatter-product';product=json.loads((product_dir/'verification.json').read_text())
    assert product['comparisons']==263712 and product['counts']=={'multiply':131856,'divide':131856}
    for flag in ('all_binary64_exponents','both_signs','source_packing_and_rounding','source_integer_shifts','r0_r1_stack_and_callee_saved_checked'):assert product[flag]
    assert product['operand_exponent_edges']==[0,1023,2047] and product['trace_sha256']=='a3976bfc9a4aacf62cb77a9171a52fd8527cbe7942eeb73c9b808607d040f317' and not product['instruction_identity']
    assert product['report_sha256']==sha(product_dir/'report.json') and product['object_sha256']==sha(product_dir/'native_formatter_product.o') and product['driver_sha256']==sha(ROOT/'r1/tools/verify_native_formatter_product.py') and product['application_sha256']==app_hash
    assert product['addition_report_sha256']==sha(add_dir/'report.json') and product['addition_object_sha256']==sha(add_dir/'native_formatter_add.o') and product['integer_report_sha256']==sha(BASE/'integer-runtime/report.json') and product['integer_object_sha256']==sha(BASE/'integer-runtime/integer-runtime.o')
    for path,digest in json.loads((product_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in product['evidence'].items():assert sha(product_dir/path)==digest,path
    for address,size in [(0x27c4a,228),(0x27d2e,222)]:
        raw=json.loads((product_dir/f'rea-{address:x}.json').read_text());q=raw.get('structuredContent') or json.loads(next(c['text'] for c in raw['content'] if c['type']=='text'))
        assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']==hex(address) and q['normalized_result']['body']['total_bytes']==size
        assert bytes(json.loads((product_dir/f'ghidra-{address:x}.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    product_decimal=json.loads((product_dir/'decimal-integration-verification.json').read_text())
    for field in ('comparisons','zero_cases','result_buffer_alias_cases','native_math_calls_per_side','all_nonnegative_binary64_exponents','precision_modes_tested','source_owned_zero_bytes','native_math_argument_traces_checked','actual_source_integer_division','r0_stack_and_callee_saved_checked','trace_sha256','integer_report_sha256','integer_object_sha256','application_sha256','evidence','instruction_identity'):assert product_decimal[field]==decimal[field],field
    assert product_decimal['report_sha256']==sha(product_dir/'report.json') and product_decimal['object_sha256']==sha(product_dir/'native_formatter_product.o') and product_decimal['driver_sha256']==sha(ROOT/'r1/tools/verify_native_formatter_product_decimal_graph.py')
    assert product_decimal['decimal_report_sha256']==sha(decimal_dir/'report.json') and product_decimal['decimal_object_sha256']==sha(decimal_dir/'native_formatter_decimal.o') and product_decimal['unsigned_report_sha256']==sha(unsigned_dir/'report.json') and product_decimal['unsigned_object_sha256']==sha(unsigned_dir/'native_formatter_unsigned.o') and product_decimal['addition_report_sha256']==sha(add_dir/'report.json') and product_decimal['addition_object_sha256']==sha(add_dir/'native_formatter_add.o')
    product_graph=json.loads((product_dir/'formatter-integration-verification.json').read_text())
    assert product_graph['cases']==225 and product_graph['matched']==225 and not product_graph['differences'] and not product_graph['execution_errors']
    assert product_graph['provider_calls']=={'r1_format_width_padding':190,'r1_format_bounded_putc':1880,'r1_format_left_padding':190,'r1_format_decimal_digits':120,'r1_format_double_multiply_bits':1055,'r1_format_double_add_bits':100,'r1_format_double_to_unsigned_bits':100,'r1_format_double_divide_bits':80}
    assert product_graph['report_sha256']==sha(product_dir/'report.json') and product_graph['object_sha256']==sha(product_dir/'native_formatter_product.o') and product_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_formatter_product_formatter_graph.py') and product_graph['application_sha256']==app_hash and product_graph['evidence']==product['evidence']
    assert product_graph['trace_sha256']=='5c2e57b38a08196c82c59cdfad6283e500ff618c103f9c16c437dce72f47f389' and not product_graph['native_equivalence_proven'] and not product_graph['instruction_identity'] and product_graph['actual_native_core'] and product_graph['actual_C_output_helpers']
    assert product_graph['provider_reports']=={path:sha(BASE/path) for path in ['native-formatter-add/report.json','native-formatter-unsigned/report.json','native-formatter-decimal/report.json','native-formatter-output/report.json','integer-runtime/report.json','native-formatter-math/report.json']}
    math_dir=BASE/'native-formatter-math';math_bundle=json.loads((math_dir/'report.json').read_text())
    assert not math_bundle['undefined_symbols'] and not math_bundle['original_instruction_identity'] and not math_bundle['application_linked'] and math_bundle['linked_sha256']==sha(math_dir/'native-formatter-math.o')
    assert product_graph['math_bundle_no_unresolved'] and product_graph['math_bundle_report_sha256']==sha(math_dir/'report.json') and product_graph['math_bundle_sha256']==sha(math_dir/'native-formatter-math.o')
    assert math_bundle['provider_reports']=={path:sha(BASE/path) for path in ['native-formatter-product/report.json','native-formatter-add/report.json','native-formatter-unsigned/report.json','native-formatter-decimal/report.json','integer-runtime/report.json']}
    for path,digest in math_bundle['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in math_bundle['objects'].items():assert sha(BASE/path)==digest,path
    core_dir=BASE/'native-formatter-core';core=json.loads((core_dir/'verification.json').read_text())
    assert core['comparisons']==39002 and core['counts']=={'integer':36288,'stars':756,'float':1536,'string':96,'literal':255,'count':36,'null-count':9,'unknown':10,'edge':4,'mutation':12}
    assert core['callback_calls_per_side']==303233 and core['matching_faults']==10 and core['callback_mutation_modes']==4
    for flag in ('all_flag_subsets','negative_dynamic_precision','varargs_64bit_alignment','callback_unsigned_byte_arguments_checked','callback_scratch_clobbers_and_returns_ignored','actual_source_math_and_padding','r0_stack_and_callee_saved_checked'):assert core[flag]
    assert core['length_modifiers']==['','h','hh','l','ll','j','t','z','L'] and core['trace_sha256']=='f782870b45d9aa9f3e64237a47c5a6e05f906a5e8025b5a34e4d6e4776888577' and not core['instruction_identity']
    assert core['report_sha256']==sha(core_dir/'report.json') and core['object_sha256']==sha(core_dir/'native_formatter_core.o') and core['driver_sha256']==sha(ROOT/'r1/tools/verify_native_formatter_core.py') and core['application_sha256']==app_hash
    assert core['provider_reports']=={path:sha(BASE/path) for path in ['native-formatter-math/report.json','native-formatter-output/report.json']}
    for path,digest in json.loads((core_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in core['evidence'].items():assert sha(core_dir/path)==digest,path
    raw=json.loads((core_dir/'rea-43080.json').read_text());q=raw.get('structuredContent') or json.loads(next(c['text'] for c in raw['content'] if c['type']=='text'))
    assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']=='0x43080' and q['normalized_result']['body']['total_bytes']==1656 and q['normalized_result']['body']['span_bytes']==1704
    assert q['normalized_result']['body']['ranges']==[{'start':'0x43080','end':'0x43263'},{'start':'0x43266','end':'0x4347d'},{'start':'0x434ac','end':'0x43727'}]
    for address,size in [(0x43080,484),(0x43266,536),(0x434ac,636),(0x43480,44),(0x43728,12)]:assert bytes(json.loads((core_dir/f'ghidra-{address:x}.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    core_ev=json.loads((core_dir/'evidence.json').read_text());assert not core_ev['locked_ownership_changed'] and core_ev['native_body_bytes']==1656 and core_ev['native_span_bytes']==1704 and core_ev['source_owned_literal_bytes']==56
    assert core_ev['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and core_ev['ownership_rows']==[row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and row['entry']=='0x00043080']
    assert core_ev['pseudocode_sha256']==sha(ROOT/core_ev['pseudocode_source']) and core_ev['pseudocode_slice_sha256']==sha(ROOT/core_ev['pseudocode_slice']) and core_ev['byte_callback_counterexample_sha256']==sha(core_dir/'byte-callback-counterexample.json')
    byte_regression=json.loads((core_dir/'byte-callback-counterexample.json').read_text());assert byte_regression['argument']==128 and byte_regression['native_callback_r0']==128 and byte_regression['initial_candidate_callback_r0']==4294967168
    core_graph=json.loads((core_dir/'formatter-integration-verification.json').read_text())
    assert core_graph['cases']==225 and core_graph['matched']==225 and not core_graph['differences'] and not core_graph['execution_errors']
    assert core_graph['provider_calls']=={'r1_format_core':225,'r1_format_bounded_putc':1880,'r1_format_double_multiply_bits':1055,'r1_format_double_add_bits':100,'r1_format_double_to_unsigned_bits':100,'r1_format_double_divide_bits':80}
    assert core_graph['report_sha256']==sha(core_dir/'report.json') and core_graph['object_sha256']==sha(core_dir/'native_formatter_core.o') and core_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_formatter_core_graph.py') and core_graph['application_sha256']==app_hash and core_graph['evidence']==core['evidence']
    assert core_graph['trace_sha256']=='5c2e57b38a08196c82c59cdfad6283e500ff618c103f9c16c437dce72f47f389' and not core_graph['native_equivalence_proven'] and not core_graph['instruction_identity'] and not core_graph['actual_native_core'] and core_graph['actual_C_core'] and core_graph['actual_C_output_helpers']
    assert core_graph['provider_reports']=={path:sha(BASE/path) for path in ['native-formatter-add/report.json','native-formatter-unsigned/report.json','native-formatter-decimal/report.json','native-formatter-output/report.json','integer-runtime/report.json','native-formatter-math/report.json','native-formatter-engine/report.json']}
    assert sum(row['bytes'] for row in core_graph['source_owned_sections'].values())==56
    for row in core_graph['source_owned_sections'].values():assert row['sha256']==hashlib.sha256((ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[row['address']-0x27000:row['address']-0x27000+row['bytes']]).hexdigest()
    engine_dir=BASE/'native-formatter-engine';engine=json.loads((engine_dir/'report.json').read_text())
    assert not engine['undefined_symbols'] and not engine['original_instruction_identity'] and not engine['application_linked'] and engine['linked_sha256']==sha(engine_dir/'native-formatter-engine.o')
    assert core_graph['engine_no_unresolved'] and core_graph['engine_report_sha256']==sha(engine_dir/'report.json') and core_graph['engine_sha256']==sha(engine_dir/'native-formatter-engine.o')
    assert engine['provider_reports']=={path:sha(BASE/path) for path in ['native-formatter-core/report.json','native-formatter-math/report.json','native-formatter-output/report.json']}
    for path,digest in engine['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in engine['objects'].items():assert sha(BASE/path)==digest,path
    wrappers_dir=BASE/'native-formatter-wrappers';wrappers=json.loads((wrappers_dir/'verification.json').read_text())
    assert wrappers['comparisons']==2532 and wrappers['counts']=={'snprintf':1266,'vsnprintf':1266} and wrappers['matching_faults']==1096 and wrappers['alias_cases']==36 and wrappers['r1_scratch_differences']==24
    for flag in ('r1_zero_for_nonzero_capacity','r0_r2_r3_and_callee_saved_checked','native_argument_stream_and_context_checked','actual_source_engine'):assert wrappers[flag]
    assert wrappers['native_outer_frames_checked']=={'snprintf':40,'vsnprintf':24} and wrappers['actual_source_provider_calls_per_side']=={'core':2532,'output':16492}
    assert wrappers['trace_sha256']=='e80beb6fc5873fc891d5b6c71e653fc1225c3ef81b4884514e796b935ccfe24c' and not wrappers['instruction_identity']
    assert wrappers['report_sha256']==sha(wrappers_dir/'report.json') and wrappers['object_sha256']==sha(wrappers_dir/'native_formatter_wrappers.o') and wrappers['driver_sha256']==sha(ROOT/'r1/tools/verify_native_formatter_wrappers.py') and wrappers['application_sha256']==app_hash
    assert wrappers['engine_report_sha256']==sha(engine_dir/'report.json') and wrappers['engine_object_sha256']==sha(engine_dir/'native-formatter-engine.o')
    for path,digest in json.loads((wrappers_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in wrappers['evidence'].items():assert sha(wrappers_dir/path)==digest,path
    for address,size in [(0x38080,48),(0x380dc,46)]:
        raw=json.loads((wrappers_dir/f'rea-{address:x}.json').read_text());q=raw.get('structuredContent') or json.loads(next(c['text'] for c in raw['content'] if c['type']=='text'))
        assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']==hex(address) and q['normalized_result']['body']['total_bytes']==size
        assert bytes(json.loads((wrappers_dir/f'ghidra-{address:x}.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    wrappers_graph=json.loads((wrappers_dir/'formatter-integration-verification.json').read_text())
    assert wrappers_graph['cases']==225 and wrappers_graph['matched']==225 and not wrappers_graph['differences'] and not wrappers_graph['execution_errors']
    assert wrappers_graph['provider_calls']=={'r1_native_snprintf':225,'r1_format_core':225,'r1_format_bounded_putc':1880,'r1_format_double_multiply_bits':1055,'r1_format_double_add_bits':100,'r1_format_double_to_unsigned_bits':100,'r1_format_double_divide_bits':80}
    assert wrappers_graph['report_sha256']==sha(wrappers_dir/'report.json') and wrappers_graph['object_sha256']==sha(wrappers_dir/'native_formatter_wrappers.o') and wrappers_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_formatter_wrappers_graph.py') and wrappers_graph['application_sha256']==app_hash and wrappers_graph['evidence']==wrappers['evidence']
    assert wrappers_graph['trace_sha256']=='5c2e57b38a08196c82c59cdfad6283e500ff618c103f9c16c437dce72f47f389' and not wrappers_graph['native_equivalence_proven'] and not wrappers_graph['instruction_identity'] and not wrappers_graph['actual_native_core'] and wrappers_graph['actual_C_core'] and wrappers_graph['actual_C_output_helpers']
    assert wrappers_graph['provider_reports']==core_graph['provider_reports']
    runtime_dir=BASE/'native-formatter-runtime';formatter_runtime=json.loads((runtime_dir/'report.json').read_text())
    assert not formatter_runtime['undefined_symbols'] and not formatter_runtime['original_instruction_identity'] and not formatter_runtime['application_linked'] and formatter_runtime['linked_sha256']==sha(runtime_dir/'native-formatter-runtime.o')
    assert {'snprintf','vsnprintf','r1_native_snprintf','r1_native_vsnprintf'}<=set(formatter_runtime['defined_symbols'])
    assert formatter_runtime['provider_reports']=={path:sha(BASE/path) for path in ['native-formatter-engine/report.json','native-formatter-wrappers/report.json']}
    for path,digest in formatter_runtime['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in formatter_runtime['objects'].items():assert sha(BASE/path)==digest,path
    info_format_dir=BASE/'native-protocol-device-info';info_format=json.loads((info_format_dir/'formatting-integration-verification.json').read_text())
    assert info_format['comparisons']==65637 and info_format['counts']=={'info':65637,'wrapper':0} and info_format['provider_calls_per_side']=={'clear':65637,'format':131274,'lower':65606} and info_format['r1_scratch_differences']==65636 and info_format['null_header_faults']==1
    assert info_format['actual_source_formatting'] and not info_format['formatting_boundary_fixture'] and info_format['actual_upstream_clear'] and info_format['actual_connection_getter_and_header'] and info_format['r0_r2_r3_checked'] and info_format['all_info_sequence_halfwords']
    assert info_format['trace_sha256']=='e87510cfd06a05ac8198f136f9059ee90a75d1dedb4f2a4667e16b7e08ce3da4' and info_format['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_device_info_formatting.py') and info_format['application_sha256']==app_hash and not info_format['instruction_identity'] and not info_format['application_linked']
    for path,digest in info_format['provider_reports'].items():assert sha(BASE/path)==digest,path
    for path,digest in info_format['evidence'].items():assert sha(info_format_dir/path)==digest,path
    info_old=json.loads((BASE/'native-battery-runtime/device-info-integration-verification.json').read_text());info_source=json.loads((BASE/'native-battery-runtime/source-formatting-integration-verification.json').read_text())
    assert info_source['actual_source_formatter'] and not info_source['formatting_boundary_fixture'] and info_source['formatter_runtime_report_sha256']==sha(runtime_dir/'report.json')
    assert set(info_source)-set(info_old)=={'actual_source_formatter','formatting_boundary_fixture','formatter_runtime_report_sha256'}
    for field in set(info_old)-{'provider_reports','driver_sha256','limitations'}:assert info_source[field]==info_old[field],field
    assert info_source['provider_reports']=={**info_old['provider_reports'],'native-formatter-runtime/report.json':sha(runtime_dir/'report.json')} and info_source['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_source_formatter_graph.py')
    assert info_source['limitations']==[value.replace('snprintf0x38080 remains a named toolchain formatter boundary fixture; fixed%s calls do not close generic formatter source','Actual source snprintf wrapper, C parser/arithmetic and bounded output execute; generic formatter and wrapper evidence is separately bound to native-formatter-runtime; private frame and raw r1 scratch identity remain gated') for value in info_old['limitations']]
    stream_dir=BASE/'native-formatter-stream';stream_receipt=json.loads((stream_dir/'verification.json').read_text())
    assert stream_receipt['comparisons']==4212 and stream_receipt['counts']=={'sprintf':168,'printf':168,'buffer_putc':1554,'stdout_putc':2322} and stream_receipt['backend_calls']=={'native':3978,'source':3978} and stream_receipt['matching_faults']==343 and stream_receipt['r1_scratch_differences']==18 and stream_receipt['backend_record_mutation_modes']==3
    for flag in ('sprintf_and_buffer_full_r0_r1_r2_r3_checked','stdout_leaf_r0_r2_r3_and_frame16_checked','printf_r0_frame24_checked','sprintf_frame24_checked','unbounded_putc_instruction_bytes_equal'):assert stream_receipt[flag]
    assert stream_receipt['unbounded_putc_instruction_bytes']==10 and stream_receipt['unbounded_putc_section_sha256']=='b912c7eaa8c5681214454c4ed558609e9c943358cf5a15f44f97bb061232fcd7'
    assert stream_receipt['trace_sha256']=='cb063f1ba054c1ea616df0bf893251ee4ef9f9c1ad591ae43e6675df8c7cf7dc' and not stream_receipt['instruction_identity']
    assert stream_receipt['report_sha256']==sha(stream_dir/'report.json') and stream_receipt['object_sha256']==sha(stream_dir/'native_formatter_stream.o') and stream_receipt['driver_sha256']==sha(ROOT/'r1/tools/verify_native_formatter_stream.py') and stream_receipt['application_sha256']==app_hash
    assert stream_receipt['engine_report_sha256']==sha(engine_dir/'report.json') and stream_receipt['engine_object_sha256']==sha(engine_dir/'native-formatter-engine.o')
    for path,digest in json.loads((stream_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in stream_receipt['evidence'].items():assert sha(stream_dir/path)==digest,path
    for address,size in [(0x38060,22),(0x380b4,34),(0x44a6c,10),(0x6570a,16)]:
        raw=json.loads((stream_dir/f'rea-{address:x}.json').read_text());q=raw.get('structuredContent') or json.loads(next(c['text'] for c in raw['content'] if c['type']=='text'))
        assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']==hex(address) and q['normalized_result']['body']['total_bytes']==size
        assert bytes(json.loads((stream_dir/f'ghidra-{address:x}.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    putc_bytes=section_bytes(stream_dir/'native_formatter_stream.o','.text.r1_format_unbounded_putc');assert len(putc_bytes)==10 and hashlib.sha256(putc_bytes).hexdigest()==stream_receipt['unbounded_putc_section_sha256'] and putc_bytes==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x44a6c-0x27000:0x44a76-0x27000]
    assert ('r1_format_unbounded_putc',10) in functions(stream_dir/'native_formatter_stream.o')
    rtt_write_dir=BASE/'native-rtt-write';rtt_write=json.loads((rtt_write_dir/'verification.json').read_text())
    assert rtt_write['comparisons']==3538 and rtt_write['initializations_per_side']==54 and rtt_write['no_lock_calls_per_side']==3538 and rtt_write['control_mode_cases']=={'0':1897,'1':1641}
    for flag in ('all_basepri_byte_values','actual_source_initializer','actual_pinned_segger_ring','actual_source_memory_copy','r0_r1_basepri_control_and_callee_saved_checked'):assert rtt_write[flag]
    assert rtt_write['trace_sha256']=='db11e3fd5bec42c1d3655e3a2d9a0155b27a32a56507f88154aa0681557193f8' and not rtt_write['instruction_identity']
    assert rtt_write['report_sha256']==sha(rtt_write_dir/'report.json') and rtt_write['object_sha256']==sha(rtt_write_dir/'native_rtt_write.o') and rtt_write['driver_sha256']==sha(ROOT/'r1/tools/verify_native_rtt_write.py') and rtt_write['application_sha256']==app_hash
    assert rtt_write['provider_reports']=={path:sha(BASE/path) for path in ['sdk-segger-rtt/report.json','runtime/report.json']}
    for path,digest in json.loads((rtt_write_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in rtt_write['evidence'].items():assert sha(rtt_write_dir/path)==digest,path
    raw=json.loads((rtt_write_dir/'rea-319e0.json').read_text());q=raw.get('structuredContent') or json.loads(next(c['text'] for c in raw['content'] if c['type']=='text'))
    assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']=='0x319e0' and q['normalized_result']['body']['total_bytes']==52
    assert bytes(json.loads((rtt_write_dir/'ghidra-319e0.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x319e0-0x27000:0x31a14-0x27000]
    rtt_write_ev=json.loads((rtt_write_dir/'evidence.json').read_text());assert not rtt_write_ev['locked_ownership_changed'] and rtt_write_ev['native_body_bytes']==52
    assert rtt_write_ev['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and rtt_write_ev['ownership_rows']==[row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and row['entry']=='0x000319e0']
    assert rtt_write_ev['pinned_ring_report_sha256']==sha(BASE/rtt_write_ev['pinned_ring_provider'])
    stdout_graph=json.loads((rtt_write_dir/'stdout-integration-verification.json').read_text())
    assert stdout_graph['comparisons']==972 and stdout_graph['initializations_per_side']==162 and stdout_graph['no_lock_calls_per_side']==9900 and stdout_graph['control_mode_cases']=={'0':486,'1':486} and stdout_graph['basepri_values']==[0,32,255] and stdout_graph['r1_scratch_differences']==108
    assert stdout_graph['actual_source_printf'] and not stdout_graph['stdout_backend_fixture'] and stdout_graph['actual_source_initializer'] and stdout_graph['actual_pinned_segger_ring'] and stdout_graph['actual_source_memory_copy'] and stdout_graph['r0_basepri_control_and_callee_saved_checked']
    assert stdout_graph['trace_sha256']=='e5f0398eb2cd09680df004eee6f8e8ab7a59733f076047047ef34f578cc6f61b' and not stdout_graph['instruction_identity']
    assert stdout_graph['report_sha256']==sha(rtt_write_dir/'report.json') and stdout_graph['object_sha256']==sha(rtt_write_dir/'native_rtt_write.o') and stdout_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_formatter_stdout_graph.py') and stdout_graph['application_sha256']==app_hash and stdout_graph['evidence']==rtt_write['evidence']
    assert stdout_graph['provider_reports']=={path:sha(BASE/path) for path in ['sdk-segger-rtt/report.json','runtime/report.json','native-formatter-engine/report.json','native-formatter-stream/report.json','native-formatter-stdio/report.json']}
    stdio_dir=BASE/'native-formatter-stdio';stdio=json.loads((stdio_dir/'report.json').read_text())
    assert not stdio['undefined_symbols'] and not stdio['original_instruction_identity'] and not stdio['application_linked'] and stdio['linked_sha256']==sha(stdio_dir/'native-formatter-stdio.o')
    assert {'printf','sprintf','snprintf','vsnprintf','r1_stdout_write','SEGGER_RTT_WriteNoLock','SEGGER_RTT_Init'}<=set(stdio['defined_symbols'])
    assert stdout_graph['stdio_no_unresolved'] and stdout_graph['stdio_report_sha256']==sha(stdio_dir/'report.json') and stdout_graph['stdio_object_sha256']==sha(stdio_dir/'native-formatter-stdio.o')
    assert stdio['provider_reports']=={path:sha(BASE/path) for path in ['native-formatter-runtime/report.json','native-formatter-stream/report.json','native-rtt-write/report.json','sdk-segger-rtt/report.json','runtime/report.json']}
    for path,digest in stdio['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in stdio['objects'].items():assert sha(BASE/path)==digest,path
    fp_bits_dir=BASE/'native-float-bits';fp_bits_receipt=json.loads((fp_bits_dir/'verification.json').read_text())
    assert fp_bits_receipt['comparisons']==459814 and fp_bits_receipt['counts']=={'class64':69632,'class32':6144,'signed_to64':73731,'unsigned_to64':73731,'to_signed':69632,'to_unsigned':69632,'from32':6144,'subtract':8592,'reverse_subtract':8592,'scale':73728,'environment':256}
    assert fp_bits_receipt['class_tags']=={'class64':{'0':2,'4':31,'5':69564,'3':2,'7':33},'class32':{'0':2,'4':18,'5':6102,'3':2,'7':20}}
    for flag in ('all_binary32_and_binary64_exponents','both_signs','all_low16_integer_words','seeded_random_patterns','classifier_r0_r1_r2_r3_checked','return_values_stack_callee_saved_and_fpscr_checked','source_math_and_shifts','environment_instruction_bytes_equal'):assert fp_bits_receipt[flag]
    assert fp_bits_receipt['environment_instruction_bytes']==4 and fp_bits_receipt['environment_section_sha256']=='a7ddd513d149ea16fdd4db3f82267f83087aeaddd06b5dde5468adb704205fc4'
    assert fp_bits_receipt['trace_sha256']=='1d41932ed41a3eed24145f6bda6d1e67d88fb0208904755f88d1cc0079579a86' and not fp_bits_receipt['instruction_identity']
    assert fp_bits_receipt['report_sha256']==sha(fp_bits_dir/'report.json') and fp_bits_receipt['object_sha256']==sha(fp_bits_dir/'native_float_bits.o') and fp_bits_receipt['driver_sha256']==sha(ROOT/'r1/tools/verify_native_float_bits.py') and fp_bits_receipt['application_sha256']==app_hash
    assert fp_bits_receipt['math_report_sha256']==sha(BASE/'native-formatter-math/report.json') and fp_bits_receipt['math_object_sha256']==sha(BASE/'native-formatter-math/native-formatter-math.o')
    for path,digest in json.loads((fp_bits_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in fp_bits_receipt['evidence'].items():assert sha(fp_bits_dir/path)==digest,path
    for address,size in [(0x38110,48),(0x38140,38),(0x27e38,34),(0x27e5a,26),(0x27e74,62),(0x27eb2,50),(0x27ee4,38),(0x27c3e,6),(0x27c44,6),(0x281dc,46),(0x2839a,4)]:
        raw=json.loads((fp_bits_dir/f'rea-{address:x}.json').read_text());q=raw.get('structuredContent') or json.loads(next(c['text'] for c in raw['content'] if c['type']=='text'))
        assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']==hex(address) and q['normalized_result']['body']['total_bytes']==size
        assert bytes(json.loads((fp_bits_dir/f'ghidra-{address:x}.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    fp_bits_ev=json.loads((fp_bits_dir/'evidence.json').read_text());assert not fp_bits_ev['locked_ownership_changed'] and fp_bits_ev['body_count']==11 and fp_bits_ev['native_body_bytes']==358
    fp_entries={0x38110,0x38140,0x27e38,0x27e5a,0x27e74,0x27eb2,0x27ee4,0x27c3e,0x27c44,0x281dc,0x2839a}
    assert fp_bits_ev['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and fp_bits_ev['ownership_rows']==[row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and int(row['entry'],16) in fp_entries]
    assert fp_bits_ev['pseudocode_sha256']==sha(ROOT/fp_bits_ev['pseudocode_source']) and fp_bits_ev['interface_header_sha256']==sha(ROOT/fp_bits_ev['interface_header'])
    assert len(fp_bits_ev['pseudocode_slices'])==11 and {int(row['entry'],16) for row in fp_bits_ev['pseudocode_slices']}==fp_entries
    for row in fp_bits_ev['pseudocode_slices']:assert row['sha256']==sha(fp_bits_dir/f"pseudocode-{int(row['entry'],16):x}.c.txt")
    assert fp_bits_ev['register_counterexample_sha256']==sha(fp_bits_dir/'classifier-register-counterexample.json');fp_register_regression=json.loads((fp_bits_dir/'classifier-register-counterexample.json').read_text());assert fp_register_regression['incoming_r3']==fp_register_regression['native_r3']=='0xfedcba98' and fp_register_regression['initial_candidate_r3']=='0x0'
    environment_bytes=section_bytes(fp_bits_dir/'native_float_bits.o','.text.r1_native_floating_environment_control');assert len(environment_bytes)==4 and hashlib.sha256(environment_bytes).hexdigest()==fp_bits_receipt['environment_section_sha256'] and environment_bytes==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x2839a-0x27000:0x2839e-0x27000]
    fp_consumers=json.loads((fp_bits_dir/'consumer-verification.json').read_text())
    assert fp_consumers['comparisons']==1552 and fp_consumers['consumer_counts']=={'atan':56,'atan2f':144,'atanf':56,'ceil':56,'ceilf':56,'cosf':56,'exp':56,'expf':56,'floor':56,'floorf':56,'log':56,'log10f':56,'logf':56,'pow':144,'powf':144,'round':56,'roundf':56,'sinf':56,'sqrt':56,'sqrtf':56,'tanf':56,'tanh':56,'tanhf':56}
    assert fp_consumers['source_helper_calls']=={'class64':40,'class32':152,'signed_to64':84,'unsigned_to64':0,'to_signed':24,'to_unsigned':0,'from32':0,'subtract':856,'reverse_subtract':508,'scale':0,'environment':264}
    for flag in ('consumer_bodies_remain_native','all_four_fpscr_rounding_modes','return_fpscr_callee_saved_integer_fp_registers_and_nonstack_writes_checked','native_initialized_state_fixture','runtime_no_unresolved'):assert fp_consumers[flag]
    assert fp_consumers['trace_sha256']=='b03c1a30f4b57bd5b828e6a66f8e1328d873e4cc37ce7f22465ffb935991f8ff' and not fp_consumers['instruction_identity']
    assert fp_consumers['report_sha256']==sha(fp_bits_dir/'report.json') and fp_consumers['object_sha256']==sha(fp_bits_dir/'native_float_bits.o') and fp_consumers['driver_sha256']==sha(ROOT/'r1/tools/verify_native_float_bit_consumers.py') and fp_consumers['application_sha256']==app_hash
    assert fp_consumers['math_report_sha256']==sha(BASE/'native-formatter-math/report.json') and fp_consumers['math_object_sha256']==sha(BASE/'native-formatter-math/native-formatter-math.o')
    fp_runtime_dir=BASE/'native-float-bits-runtime';fp_runtime=json.loads((fp_runtime_dir/'report.json').read_text())
    assert not fp_runtime['undefined_symbols'] and not fp_runtime['original_instruction_identity'] and not fp_runtime['application_linked'] and fp_runtime['linked_sha256']==sha(fp_runtime_dir/'native-float-bits-runtime.o')
    assert fp_consumers['runtime_report_sha256']==sha(fp_runtime_dir/'report.json') and fp_consumers['runtime_object_sha256']==sha(fp_runtime_dir/'native-float-bits-runtime.o')
    assert fp_runtime['provider_reports']=={path:sha(BASE/path) for path in ['native-float-bits/report.json','native-formatter-math/report.json']}
    for path,digest in fp_runtime['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in fp_runtime['objects'].items():assert sha(BASE/path)==digest,path
    poly_dir=BASE/'native-polynomial';poly=json.loads((poly_dir/'verification.json').read_text())
    assert poly['comparisons']==3840 and set(poly['coefficient_count_cases'])=={str(n) for n in range(1,33)} and sum(poly['coefficient_count_cases'].values())==3840
    assert poly['source_helper_calls']=={'multiply':59748,'add':59748} and poly['trace_sha256']=='6dda713685e292c28f2a5e5fa04cc666bb5a7614343a101cd4fb66b363b41af9'
    for flag in ('all_four_fpscr_rounding_modes','return_fpscr_stack_callee_saved_integer_fp_and_coefficients_checked','source_arithmetic','runtime_no_unresolved'):assert poly[flag]
    assert not poly['instruction_identity'] and poly['application_sha256']==app_hash and poly['driver_sha256']==sha(ROOT/'r1/tools/verify_native_polynomial.py')
    assert poly['report_sha256']==sha(poly_dir/'report.json') and poly['object_sha256']==sha(poly_dir/'native_polynomial.o') and poly['runtime_object_sha256']==sha(poly_dir/'native-polynomial-runtime.o')
    assert poly['provider_report_sha256']==sha(BASE/'native-float-bits-runtime/report.json') and poly['provider_object_sha256']==sha(BASE/'native-float-bits-runtime/native-float-bits-runtime.o')
    for path,digest in json.loads((poly_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in poly['evidence'].items():assert sha(poly_dir/path)==digest,path
    assert bytes(json.loads((poly_dir/'ghidra-3b40c.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x1440c:0x14504]
    poly_raw=json.loads((poly_dir/'rea-3b40c.json').read_text());poly_meta=poly_raw.get('structuredContent') or json.loads(poly_raw['content'][0]['text'])
    assert poly_meta['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and poly_meta['normalized_result']['entrypoint']=='0x3b40c' and poly_meta['normalized_result']['body']['total_bytes']==248
    poly_ev=json.loads((poly_dir/'evidence.json').read_text());assert not poly_ev['locked_ownership_changed'] and poly_ev['body_count']==1 and poly_ev['native_body_bytes']==248
    assert poly_ev['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and poly_ev['ownership_row']==next(row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and row['entry']=='0x0003b40c')
    assert poly_ev['pseudocode_sha256']==sha(ROOT/poly_ev['pseudocode_source']) and poly_ev['pseudocode_slice_sha256']==sha(poly_dir/'pseudocode-3b40c.c.txt')
    poly_consumers=json.loads((poly_dir/'consumer-verification.json').read_text())
    assert poly_consumers['comparisons']==1552 and len(poly_consumers['consumer_counts'])==23 and poly_consumers['consumer_counts']==fp_consumers['consumer_counts']
    assert poly_consumers['source_helper_calls']=={**fp_consumers['source_helper_calls'],'polynomial':148} and poly_consumers['trace_sha256']=='2fa898d473ed18852402f313cec200c82d2d69d89873be6fe7869f5e5dbd76d4'
    for flag in ('consumer_bodies_remain_native','all_four_fpscr_rounding_modes','return_fpscr_callee_saved_integer_fp_registers_and_nonstack_writes_checked','native_initialized_state_fixture','runtime_no_unresolved'):assert poly_consumers[flag]
    assert not poly_consumers['instruction_identity'] and poly_consumers['driver_sha256']==sha(ROOT/'r1/tools/verify_native_polynomial_consumers.py') and poly_consumers['application_sha256']==app_hash
    assert poly_consumers['runtime_report_sha256']==sha(poly_dir/'verification.json') and poly_consumers['runtime_object_sha256']==sha(poly_dir/'native-polynomial-runtime.o')
    assert poly_consumers['report_sha256']==sha(fp_bits_dir/'report.json') and poly_consumers['object_sha256']==sha(fp_bits_dir/'native_float_bits.o')
    assert poly_consumers['math_report_sha256']==sha(BASE/'native-formatter-math/report.json') and poly_consumers['math_object_sha256']==sha(BASE/'native-formatter-math/native-formatter-math.o')
    fr_dir=BASE/'native-float-rounding';fr=json.loads((fr_dir/'verification.json').read_text())
    assert fr['comparisons']==232492 and fr['counts']=={'signed_to32':139456,'pack32':9032,'remainder32':8228,'integral32':6144,'integral64':69632}
    for flag in ('all_binary32_and_binary64_exponents','both_signs','all_positive_negative_low16_integer_words','seeded_random_patterns','return_values_stack_callee_saved_and_fpscr_checked','source_round_and_shifts','round_one_literal_bytes_equal'):assert fr[flag]
    assert fr['reused_remainder_report_sha256']==sha(BASE/'structured-float/report.json') and fr['reused_remainder_object_sha256']==sha(BASE/'structured-float/structured_float.o')
    assert fr['trace_sha256']=='6f046fbd8f49221ba5cbcc4ac9c9eecf2044a41c6a9fff299a42ce4a07dd2794' and not fr['instruction_identity']
    assert fr['application_sha256']==app_hash and fr['driver_sha256']==sha(ROOT/'r1/tools/verify_native_float_rounding.py') and fr['report_sha256']==sha(fr_dir/'report.json') and fr['object_sha256']==sha(fr_dir/'native_float_rounding.o')
    assert fr['math_report_sha256']==sha(BASE/'native-formatter-math/report.json') and fr['math_object_sha256']==sha(BASE/'native-formatter-math/native-formatter-math.o')
    for path,digest in json.loads((fr_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in fr['evidence'].items():assert sha(fr_dir/path)==digest,path
    fr_ev=json.loads((fr_dir/'evidence.json').read_text());assert not fr_ev['locked_ownership_changed'] and fr_ev['body_entries']==5 and fr_ev['unique_native_body_bytes']==346 and fr_ev['new_source_routes']==4 and fr_ev['reused_source_routes']==1 and fr_ev['unique_new_native_body_bytes']==328
    assert fr_ev['shared_entry']=='0x0002808a' and fr_ev['shared_entry_owner']=='0x00027e0c' and fr_ev['shared_entry_bytes']==92
    for address,size in [(0x27e0c,44),(0x28078,18),(0x2808a,92),(0x280e6,60),(0x282ac,132),(0x28330,4)]:assert bytes(json.loads((fr_dir/f'ghidra-{address:x}.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    for address,size,owner in [(0x27e0c,136,0x27e0c),(0x28078,18,0x28078),(0x2808a,136,0x27e0c),(0x280e6,60,0x280e6),(0x282ac,132,0x282ac)]:
        raw=json.loads((fr_dir/f'rea-{address:x}.json').read_text());q=raw.get('structuredContent') or json.loads(raw['content'][0]['text'])
        assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']==hex(owner) and q['normalized_result']['body']['total_bytes']==size
    assert fr_ev['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and fr_ev['ownership_rows']==[row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and int(row['entry'],16) in [0x27e0c,0x28078,0x2808a,0x280e6,0x282ac]]
    assert fr_ev['pseudocode_sha256']==sha(ROOT/fr_ev['pseudocode_source']) and fr_ev['instrumentation_regression_sha256']==sha(fr_dir/'consumer-instrumentation-counterexample.json')
    for path,digest in fr_ev['pseudocode_slices'].items():assert sha(fr_dir/path)==digest,path
    literal=section_bytes(fr_dir/'native_float_rounding.o','.r1.float.round_one',executable=False);assert literal==bytes.fromhex('0000f03f') and hashlib.sha256(literal).hexdigest()==fr['round_one_literal_sha256']
    fr_bundle_dir=BASE/'native-float-rounding-runtime';fr_bundle=json.loads((fr_bundle_dir/'report.json').read_text())
    assert not fr_bundle['undefined_symbols'] and fr_bundle['linked_sha256']==sha(fr_bundle_dir/'native-float-rounding-runtime.o')
    assert fr_bundle['provider_reports']=={path:sha(BASE/path) for path in ['native-float-rounding/report.json','structured-float/report.json','native-polynomial/report.json','native-float-bits-runtime/report.json']}
    for path,digest in fr_bundle['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in fr_bundle['objects'].items():assert sha(BASE/path)==digest,path
    fr_consumers=json.loads((fr_dir/'consumer-verification.json').read_text());assert fr_consumers['comparisons']==1552 and fr_consumers['consumer_counts']==fp_consumers['consumer_counts']
    for flag in ('internal_helper_counts_are_not_equivalence_claim','consumer_bodies_remain_native','all_four_fpscr_rounding_modes','return_fpscr_callee_saved_integer_fp_registers_and_nonstack_writes_checked','native_initialized_state_fixture','runtime_no_unresolved'):assert fr_consumers[flag]
    assert fr_consumers['trace_sha256']=='a32770c228231ad86b6b333571609f9969790782f8c5870252eeb2d3b8b822a1' and not fr_consumers['instruction_identity']
    assert fr_consumers['helper_observations']['native']=={**poly_consumers['source_helper_calls'],'signed_to32':0,'pack32':0,'remainder32':16,'integral32':56,'integral64':56}
    assert fr_consumers['helper_observations']['redirected']=={**fr_consumers['helper_observations']['native'],'remainder32':0} and fr_consumers['helper_observations']['compiled_entries']=={**fr_consumers['helper_observations']['redirected'],'remainder32':16}
    assert fr_consumers['runtime_report_sha256']==sha(fr_bundle_dir/'report.json') and fr_consumers['runtime_object_sha256']==sha(fr_bundle_dir/'native-float-rounding-runtime.o') and fr_consumers['application_sha256']==app_hash
    assert fr_consumers['driver_sha256']==sha(ROOT/'r1/tools/verify_native_float_rounding_consumers.py') and fr_consumers['report_sha256']==sha(fp_bits_dir/'report.json') and fr_consumers['object_sha256']==sha(fp_bits_dir/'native_float_bits.o')
    assert fr_consumers['math_report_sha256']==sha(BASE/'native-formatter-math/report.json') and fr_consumers['math_object_sha256']==sha(BASE/'native-formatter-math/native-formatter-math.o')
    llvm_l2f_dir=BASE/'llvm-signed64-float32';llvm_l2f=json.loads((llvm_l2f_dir/'verification.json').read_text())
    assert llvm_l2f['comparisons']==139456 and llvm_l2f['counts']=={'signed_to32':139456} and llvm_l2f['candidate_unchanged'] and not llvm_l2f['selected_native_provider'] and not llvm_l2f['instruction_identity']
    assert llvm_l2f['trace_sha256']=='5269ab65bdebe4f802ddd778ea749a2e83fc236268490a3de90a32c42c6baee9' and llvm_l2f['application_sha256']==app_hash
    assert llvm_l2f['driver_sha256']==sha(ROOT/'r1/tools/verify_llvm_signed64_float32.py') and llvm_l2f['report_sha256']==sha(llvm_l2f_dir/'report.json') and llvm_l2f['object_sha256']==sha(llvm_l2f_dir/'llvm.o')
    llvm_l2f_report=json.loads((llvm_l2f_dir/'report.json').read_text());assert not llvm_l2f_report['units'][0]['undefined']
    for path,digest in llvm_l2f_report['inputs'].items():assert sha(ROOT/path)==digest,path
    llvm_l2f_provenance=json.loads((llvm_l2f_dir/'provenance.json').read_text());assert llvm_l2f_provenance['commit']=='87f0227cb60147a26a1eeb4fb06e3b505e9c7261'
    for item in llvm_l2f_provenance['files']:assert sha(ROOT/item['path'])==item['sha256']
    assert sha(ROOT/llvm_l2f_provenance['license'])==llvm_l2f_provenance['license_sha256'] and sha(ROOT/llvm_l2f_provenance['shared_headers_provenance'])==llvm_l2f_provenance['shared_headers_provenance_sha256']
    for path,digest in llvm_l2f['evidence'].items():assert sha(BASE/path)==digest,path
    from audit_native_math_sqrt import audit as audit_native_math_sqrt
    audit_native_math_sqrt()
    from audit_native_math_selection import audit as audit_native_math_selection
    audit_native_math_selection()
    from audit_native_double_flags import audit as audit_native_double_flags
    audit_native_double_flags()
    from audit_native_double_directed import audit as audit_native_double_directed
    audit_native_double_directed()
    from audit_native_math_round import audit as audit_native_math_round
    audit_native_math_round()
    from audit_native_math_special import audit as audit_native_math_special
    math_special_spans=audit_native_math_special()
    from audit_native_expf_tanhf import audit as audit_native_expf_tanhf
    audit_native_expf_tanhf()
    from audit_native_float_logs import audit as audit_native_float_logs
    audit_native_float_logs()
    from audit_native_atanf import audit as audit_native_atanf
    audit_native_atanf()
    from audit_native_sqrt_core_abi import audit as audit_native_sqrt_core_abi
    audit_native_sqrt_core_abi()
    from audit_native_gxt310_bus import audit as audit_native_gxt310_bus
    audit_native_gxt310_bus()
    from audit_native_gxt310_id import audit as audit_native_gxt310_id
    audit_native_gxt310_id()
    from audit_native_yhm_chip_id import audit as audit_native_yhm_chip_id
    audit_native_yhm_chip_id()
    from audit_native_device_checks import audit as audit_native_device_checks
    audit_native_device_checks()
    from audit_native_dfu_vector_set import audit as audit_native_dfu_vector_set
    audit_native_dfu_vector_set()
    from audit_native_dfu_svci_init import audit as audit_native_dfu_svci_init
    audit_native_dfu_svci_init()
    from audit_native_cmbacktrace_init import audit as audit_native_cmbacktrace_init
    audit_native_cmbacktrace_init()
    from audit_native_device_reset_startup import audit as audit_native_device_reset_startup
    audit_native_device_reset_startup()
    from audit_native_startup_modules import audit as audit_native_startup_modules
    audit_native_startup_modules()
    from audit_native_application_entry import audit as audit_native_application_entry
    audit_native_application_entry()
    from audit_native_scatter_dispatch import audit as audit_native_scatter_dispatch
    audit_native_scatter_dispatch()
    from audit_native_scatter_data import audit as audit_native_scatter_data
    audit_native_scatter_data()
    from audit_native_sscanf import audit as audit_native_sscanf
    audit_native_sscanf()
    from audit_native_ctype import audit as audit_native_ctype
    audit_native_ctype()
    from audit_native_scanf_conversion import audit as audit_native_scanf_conversion
    audit_native_scanf_conversion()
    from audit_native_libc_sequences import audit as audit_native_libc_sequences
    audit_native_libc_sequences()
    from audit_native_libc_primitives import audit as audit_native_libc_primitives
    audit_native_libc_primitives()
    from audit_native_pow import audit as audit_native_pow
    audit_native_pow()
    from audit_native_powf import audit as audit_native_powf
    audit_native_powf()
    from audit_native_log import audit as audit_native_log
    audit_native_log()
    from audit_native_exp import audit as audit_native_exp
    audit_native_exp()
    from audit_native_expm1 import audit as audit_native_expm1
    audit_native_expm1()
    from audit_native_atan import audit as audit_native_atan
    audit_native_atan()
    from audit_native_tanf import audit as audit_native_tanf
    audit_native_tanf()
    from audit_native_sinf import audit as audit_native_sinf
    audit_native_sinf()
    from audit_native_cosf import audit as audit_native_cosf
    audit_native_cosf()
    from audit_native_trig_reduce import audit as audit_native_trig_reduce
    audit_native_trig_reduce()
    from audit_native_atan2f import audit as audit_native_atan2f
    audit_native_atan2f()
    fmt_dir=BASE/'native-formatter-output';fmt=json.loads((fmt_dir/'verification.json').read_text())
    assert fmt['comparisons']==145407 and fmt['counts']=={'left':65581,'width':65581,'putc':14245}
    assert fmt['callback_calls_per_side']==196818 and fmt['callback_prefix_only_cases']==10 and fmt['prefix_callback_limit']==16 and fmt['matching_faults']==1036
    for flag in ('all_low16_flag_patterns','all_byte_values','context_aliases_checked','callback_scratch_clobbers_and_results_ignored','r0_stack_and_callee_saved_checked'):assert fmt[flag]
    assert fmt['trace_sha256']=='5f642b9f983a14dc06bb3aa1379121fb4c09c8110182de6ccf393bcc8270078d'
    assert fmt['report_sha256']==sha(fmt_dir/'report.json') and fmt['object_sha256']==sha(fmt_dir/'native_formatter_output.o') and fmt['driver_sha256']==sha(ROOT/'r1/tools/verify_native_formatter_output.py') and fmt['application_sha256']==app_hash and not fmt['instruction_identity']
    for path,digest in json.loads((fmt_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in fmt['evidence'].items():assert sha(fmt_dir/path)==digest,path
    for address,size in [(0x43734,36),(0x43758,46),(0x43bbc,22)]:
        raw=json.loads((fmt_dir/f'rea-{address:x}.json').read_text());q=raw.get('structuredContent') or json.loads(next(c['text'] for c in raw['content'] if c['type']=='text'))
        if address==0x43bbc:assert q['error']['code']=='invalid_request'
        else:assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']==hex(address) and q['normalized_result']['body']['total_bytes']==size
        assert bytes(json.loads((fmt_dir/f'ghidra-{address:x}.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    fmt_graph=json.loads((fmt_dir/'graph-verification.json').read_text())
    assert fmt_graph['cases']==225 and fmt_graph['matched']==225 and not fmt_graph['differences'] and not fmt_graph['execution_errors']
    assert fmt_graph['provider_calls']=={'r1_format_width_padding':190,'r1_format_bounded_putc':1880,'r1_format_left_padding':190}
    assert fmt_graph['actual_native_core'] and fmt_graph['actual_C_output_helpers'] and fmt_graph['callee_saved_registers_checked'] and not fmt_graph['native_sram_reads_outside_arguments_output_and_stack']
    assert fmt_graph['report_sha256']==sha(fmt_dir/'report.json') and fmt_graph['object_sha256']==sha(fmt_dir/'native_formatter_output.o') and fmt_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_formatter_output_graph.py') and fmt_graph['application_sha256']==app_hash
    assert fmt_graph['trace_sha256']=='5c2e57b38a08196c82c59cdfad6283e500ff618c103f9c16c437dce72f47f389'
    assert not fmt_graph['native_equivalence_proven'] and not fmt_graph['instruction_identity'] and fmt_graph['evidence']==fmt['evidence']
    info_dir=BASE/'native-protocol-device-info';device_info=json.loads((info_dir/'verification.json').read_text())
    assert device_info['comparisons']==133597 and device_info['counts']=={'info':67197,'wrapper':66400}
    assert device_info['provider_calls_per_side']=={'clear':67197,'format':134394,'lower':132480} and device_info['all_info_sequence_halfwords'] and device_info['all_wrapper_sequence_halfwords'] and device_info['format_boundary_modes']==4 and device_info['actual_upstream_clear'] and device_info['actual_connection_getter_and_header'] and device_info['r0_r2_r3_checked'] and device_info['r1_scratch_differences']==133560 and device_info['native_info_frame40'] and device_info['null_header_faults']==1
    assert device_info['trace_sha256']=='e71e1640a32c6e3859312dcf72f6b9d599779e84f0b352c233ac101dd2f17445'
    assert device_info['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and device_info['ownership_rows']==[row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and row['entry'] in ('0x00083d5c','0x00083872')]
    assert device_info['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_device_info.py') and device_info['application_sha256']==app_hash
    for path,digest in device_info['provider_reports'].items():assert sha(BASE/path)==digest,path
    for path,digest in device_info['evidence'].items():assert sha(info_dir/path)==digest,path
    for address,size in [(0x83d5c,54),(0x83872,36),(0x38080,48)]:
        q=json.loads((info_dir/('rea-'+format(address,'x')+'.json')).read_text())
        if address==0x83d5c:assert q['error']['code']=='invalid_request' and any('No procedure exists at the requested address: 0x83d5c' in issue['message'] for issue in q['error']['issues'])
        else:assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']==hex(address) and q['normalized_result']['body']['total_bytes']==size
        assert bytes(json.loads((info_dir/('ghidra-'+format(address,'x')+'.json')).read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    assert sum(row['bytes'] for row in device_info['source_owned_metadata'].values())==25
    for row in device_info['source_owned_metadata'].values():assert row['sha256']==hashlib.sha256((ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[row['address']-0x27000:row['address']-0x27000+row['bytes']]).hexdigest()
    info_graph=json.loads((BASE/'native-battery-runtime/device-info-integration-verification.json').read_text())
    assert info_graph['comparisons']==2896 and info_graph['executed_device_info_counts']=={side:{'entry':9,'clear':9,'format':18,'operation':9} for side in ('native','source')} and info_graph['executed_actual_clear_counts']=={'native':2905,'source':2905} and info_graph['source_owned_info_metadata']==device_info['source_owned_metadata']
    assert info_graph['executed_encoder_counts']=={side:{'entry':655,'memmove':655,'crc':655} for side in ('native','source')} and info_graph['executed_fragment_counts']=={side:{'entry':655,'crc32':655,'memmove':655} for side in ('native','source')}
    assert info_graph['executed_response_counts']=={side:{'entry':820,'gate_a':820,'gate_b':275,'malloc':726,'allocated':655,'encode':655,'send':655,'free':655} for side in ('native','source')}
    assert info_graph['response_status_counts']=={side:{'0':655,'3':71,'5':94} for side in ('native','source')}
    assert info_graph['executed_operation_header_counts']=={side:{'operation':1089,'header':1089,'phone_getter':1613,'lower':820,'lower_zero':655,'lower_nonzero':165} for side in ('native','source')}
    assert info_graph['executed_tx_producer_counts']=={side:{'dispatch':2583,'malloc':1551,'put':1328,'accepted':337,'free':991,'allocation_failed':223,'queue_missing':516,'connection_rejected':516} for side in ('native','source')}
    assert info_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_device_info_graph.py') and info_graph['application_sha256']==app_hash and info_graph['report_sha256']==sha(BASE/'native-battery-runtime/report.json') and info_graph['object_sha256']==sha(BASE/'native-battery-runtime/native_battery_runtime.o')
    for path,digest in info_graph['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert not device_info['application_linked'] and not device_info['instruction_identity'] and not info_graph['application_linked'] and not info_graph['instruction_identity']
    device_status_dir=BASE/'native-protocol-device-status';device_status=json.loads((device_status_dir/'verification.json').read_text())
    assert device_status['comparisons']==381191 and device_status['counts']=={'full':65541,'active':65541,'status':250109}
    assert device_status['provider_calls_per_side']=={'r1_advertising_configuration_byte_get':250109,'r1_native_charger_state_get':631300,'r1_battery_runtime_update_service':61440,'r1_phone_cmd_send_op1':250108}
    assert device_status['predicate_entries']=={side:{'full':315650,'active':315650,'byte':250109} for side in ('native','source')}
    assert device_status['all_predicate_state_halfwords'] and device_status['all_status_sequence_halfwords'] and device_status['all_status_charge_bytes'] and device_status['live_distinct_charger_calls'] and device_status['live_header_and_cell_mutation'] and device_status['full_r0_r1_r2_r3'] and device_status['native_status_frame24'] and device_status['record_mutation_and_header_aliases'] and device_status['null_header_faults']==1 and device_status['actual_shared_byte_getter']
    assert device_status['trace_sha256']=='d3fa447177bb7e2becde31a7b7e5ede66a7b788faa56e318fc33fa48aef64da1'
    assert device_status['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and device_status['ownership_rows']==[row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and row['entry'] in ('0x00083de4','0x00091244','0x00091256')]
    assert device_status['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_device_status.py') and device_status['application_sha256']==app_hash
    for path,digest in device_status['provider_reports'].items():assert sha(BASE/path)==digest,path
    for path,digest in device_status['evidence'].items():assert sha(device_status_dir/path)==digest,path
    for address,size in [(0x83de4,66),(0x91244,18),(0x91256,14)]:
        q=json.loads((device_status_dir/('rea-'+format(address,'x')+'.json')).read_text());assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']==hex(address) and q['normalized_result']['body']['total_bytes']==size
        assert bytes(json.loads((device_status_dir/('ghidra-'+format(address,'x')+'.json')).read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    assert device_status['source_owned_default_record']=={'address':632004,'bytes':8,'sha256':'dbbe5d6e52fac8a7699e9331ff4962379c095603956f40334cf15c86fe8e0b10'}
    device_status_graph=json.loads((BASE/'native-battery-runtime/device-status-integration-verification.json').read_text())
    assert device_status_graph['comparisons']==2896 and device_status_graph['executed_device_status_counts']=={side:{'entry':9,'byte_getter':9,'active':9,'full':9,'operation':9} for side in ('native','source')}
    assert device_status_graph['source_owned_status_default']==device_status['source_owned_default_record']
    assert device_status_graph['executed_encoder_counts']=={side:{'entry':650,'memmove':650,'crc':650} for side in ('native','source')} and device_status_graph['executed_fragment_counts']=={side:{'entry':650,'crc32':650,'memmove':650} for side in ('native','source')}
    assert device_status_graph['executed_response_counts']=={side:{'entry':815,'gate_a':815,'gate_b':274,'malloc':721,'allocated':650,'encode':650,'send':650,'free':650} for side in ('native','source')}
    assert device_status_graph['response_status_counts']=={side:{'0':650,'3':71,'5':94} for side in ('native','source')}
    assert device_status_graph['executed_operation_header_counts']=={side:{'operation':1080,'header':1080,'phone_getter':1599,'lower':815,'lower_zero':650,'lower_nonzero':165} for side in ('native','source')}
    assert device_status_graph['executed_tx_producer_counts']=={side:{'dispatch':2578,'malloc':1547,'put':1324,'accepted':337,'free':987,'allocation_failed':223,'queue_missing':516,'connection_rejected':515} for side in ('native','source')}
    assert device_status_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_device_status_graph.py') and device_status_graph['application_sha256']==app_hash and device_status_graph['report_sha256']==sha(BASE/'native-battery-runtime/report.json') and device_status_graph['object_sha256']==sha(BASE/'native-battery-runtime/native_battery_runtime.o')
    for path,digest in device_status_graph['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert not device_status['application_linked'] and not device_status['instruction_identity'] and not device_status_graph['application_linked'] and not device_status_graph['instruction_identity']
    event_leaf_dir=BASE/'native-protocol-event-handlers';event_leaves=json.loads((event_leaf_dir/'verification.json').read_text())
    assert event_leaves['comparisons']==154378 and event_leaves['counts']=={'special':65633,'activity':88745} and event_leaves['event_calls_per_side']=={'special':65571,'activity':71336}
    assert event_leaves['fault_boundaries']=={'special':[19,8,2],'activity':[19,5,1]} and event_leaves['all_special_length_halfwords'] and event_leaves['all_activity_sequence_halfwords'] and event_leaves['all_activity_flag_bytes'] and event_leaves['full_r0_r1_r2_r3'] and event_leaves['activity_native_frame16'] and event_leaves['activity_incoming_r3_word_preserved'] and event_leaves['special_tail_stack_and_lr'] and event_leaves['wrapped_payload_pointer_zero_checked'] and event_leaves['record_mutation_and_header_aliases'] and not event_leaves['rea_boundary_available']
    assert event_leaves['trace_sha256']=='48ccb429e45d255276ef1196e129cd7e49f475dc2654f7547515b0a76410b02c'
    assert event_leaves['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and event_leaves['activity_ownership_row']==next(row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and row['entry']=='0x00082c10')
    assert not any(row['image']=='application' and row['entry']=='0x00084cc0' for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()))
    assert event_leaves['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_event_handlers.py') and event_leaves['application_sha256']==app_hash and event_leaves['report_sha256']==sha(event_leaf_dir/'report.json') and event_leaves['object_sha256']==sha(event_leaf_dir/'native_protocol_event_handlers.o')
    assert event_leaves['target_attribution_sha256']==sha(event_leaf_dir/'target-attribution.json');event_attribution=json.loads((event_leaf_dir/'target-attribution.json').read_text())
    assert event_attribution['native_entry']=='0x84cc0' and event_attribution['native_end']=='0x84cd7' and event_attribution['native_body_bytes']==24 and event_attribution['symbol']=='r1_protocol_command_00084cc0' and not event_attribution['locked_ownership_row'] and event_attribution['registration_address']=='0x9a588' and event_attribution['registration_key']==1 and event_attribution['registration_pointer']=='0x84cc1'
    for path,digest in event_leaves['evidence'].items():assert sha(event_leaf_dir/path)==digest,path
    for address,size in [(0x84cc0,24),(0x82c10,52)]:
        gap=json.loads((event_leaf_dir/('rea-'+format(address,'x')+'.json')).read_text());assert gap['error']['code']=='invalid_request' and any('No procedure exists at the requested address: '+hex(address) in issue['message'] for issue in gap['error']['issues'])
        assert bytes(json.loads((event_leaf_dir/('ghidra-'+format(address,'x')+'.json')).read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    assert bytes(json.loads((event_leaf_dir/'ghidra-special-registration.json').read_text())['data'])==struct.pack('<HHI',1,0,0x84cc1)
    event_leaf_graph=json.loads((BASE/'native-battery-runtime/event-handlers-integration-verification.json').read_text())
    assert event_leaf_graph['comparisons']==2896 and event_leaf_graph['executed_event_leaf_calls']['native']==event_leaf_graph['executed_event_leaf_calls']['source'] and all(n>0 for n in event_leaf_graph['executed_event_leaf_calls']['native'].values())
    assert event_leaf_graph['executed_leaf_counts']['native']==event_leaf_graph['executed_leaf_counts']['source'] and len(event_leaf_graph['executed_leaf_counts']['native'])==35 and sum(event_leaf_graph['executed_leaf_counts']['native'].values())==528
    assert event_leaf_graph['executed_leaf_counts']['native']['r1_protocol_command_00084cc0']==226 and event_leaf_graph['executed_leaf_counts']['native']['r1_activity_refresh_handler']==10 and event_leaf_graph['executed_lookup_counts']=={'native':528,'source':528}
    assert event_leaf_graph['executed_ingress_counts']=={side:{'entry':1804,'system':151,'health':151,'special':226} for side in ('native','source')}
    assert event_leaf_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_event_handlers_graph.py') and event_leaf_graph['application_sha256']==app_hash and event_leaf_graph['report_sha256']==sha(BASE/'native-battery-runtime/report.json') and event_leaf_graph['object_sha256']==sha(BASE/'native-battery-runtime/native_battery_runtime.o')
    for path,digest in event_leaf_graph['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert not event_leaves['application_linked'] and not event_leaves['instruction_identity'] and not event_leaf_graph['application_linked'] and not event_leaf_graph['instruction_identity']
    modules_dir=BASE/'native-protocol-modules';modules=json.loads((modules_dir/'verification.json').read_text())
    assert modules['helper_comparisons']==196818 and modules['helper_returned']==196560 and modules['helper_faulted']==258 and modules['all_command_halfwords_per_stock_table'] and modules['full_word_command_inputs']
    assert modules['helper_trace_sha256']=='3647a59fbdb76328f508fc37e5646dded9e13242c4eaef209c263b1a63099ba0' and modules['fault_trace_sha256']=='21d71ab17d5f43ff646a4168004ad208c3d1df33aef2890335db4509563d0900'
    assert modules['underflow_mapped_predecessor']=={'input':[536903688,8,0,0],'registers':[305419897,4294967295,2147483647,0],'reads':[[536903712,2],[536903696,2],[536903688,2],[536903680,2],[536903684,4]]}
    assert modules['wrapper_comparisons']==4104 and modules['wrapper_counts']=={'health':1620,'system':2268,'special':216} and modules['callback_calls_per_side']==1890 and modules['full_r0_r1_r2_r3'] and modules['tail_stack_and_lr'] and modules['actual_shared_search'] and not modules['rea_boundary_available']
    assert modules['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and modules['ownership_rows']==[row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and row['entry'] in ('0x00082be8','0x00083ca8','0x00084c98','0x00083298')]
    assert modules['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_modules.py') and modules['application_sha256']==app_hash and modules['report_sha256']==sha(modules_dir/'report.json') and modules['object_sha256']==sha(modules_dir/'native_protocol_modules.o')
    assert modules['command_targets_sha256']==sha(modules_dir/'command-targets.json');command_targets=json.loads((modules_dir/'command-targets.json').read_text())
    assert len(command_targets['targets'])==35 and modules['unowned_target_entries']==command_targets['unowned_target_entries']==['0x84b24','0x846dc','0x83e2c','0x83e50','0x844ec','0x843c8','0x844b0','0x84860','0x84cc0']
    assert set(json.loads((modules_dir/'report.json').read_text())['units'][0]['undefined'])=={row['symbol'] for row in command_targets['targets']}
    assert sum(row['bytes'] for row in modules['source_owned_command_tables'].values())==280
    for label,row in modules['source_owned_command_tables'].items():
        assert row['sha256_at_native_targets']==hashlib.sha256((ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[row['address']-0x27000:row['address']-0x27000+row['bytes']]).hexdigest()
        assert row['symbolic_targets']=={str(target['key']):target['symbol'] for target in command_targets['targets'] if target['table']==label}
    for path,digest in modules['evidence'].items():assert sha(modules_dir/path)==digest,path
    for address in (0x82be8,0x83ca8,0x84c98,0x83298):
        gap=json.loads((modules_dir/('rea-'+format(address,'x')+'.json')).read_text());assert gap['error']['code']=='invalid_request' and any('No procedure exists at the requested address: '+hex(address) in issue['message'] for issue in gap['error']['issues'])
        length=58 if address==0x83298 else 40;assert bytes(json.loads((modules_dir/('ghidra-'+format(address,'x')+'.json')).read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+length]
    modules_graph=json.loads((BASE/'native-battery-runtime/modules-integration-verification.json').read_text())
    assert modules_graph['comparisons']==2896 and modules_graph['command_targets_sha256']==modules['command_targets_sha256'] and modules_graph['executed_lookup_counts']=={'native':528,'source':528}
    assert modules_graph['executed_leaf_counts']['native']==modules_graph['executed_leaf_counts']['source'] and set(modules_graph['executed_leaf_counts']['native'])=={row['symbol'] for row in command_targets['targets']} and sum(modules_graph['executed_leaf_counts']['native'].values())==528
    assert modules_graph['executed_ingress_counts']=={side:{'entry':1804,'system':151,'health':151,'special':226} for side in ('native','source')}
    assert modules_graph['executed_receive_counts']=={side:{'entry':2896,'callback':1804,'invalid':911,'missing':181} for side in ('native','source')}
    assert modules_graph['executed_tx_producer_counts']=={side:{'dispatch':2573,'malloc':1544,'put':1321,'accepted':336,'free':985,'allocation_failed':223,'queue_missing':516,'connection_rejected':513} for side in ('native','source')}
    for name,section in modules_graph['compiled_command_sections'].items():assert section['address']==modules['source_owned_command_tables'][name]['address'] and section['bytes']==modules['source_owned_command_tables'][name]['bytes'] and section['pointer_normalized'] and len(section['source_data_sha256'])==64
    assert modules_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_modules_graph.py') and modules_graph['application_sha256']==app_hash and modules_graph['report_sha256']==sha(BASE/'native-battery-runtime/report.json') and modules_graph['object_sha256']==sha(BASE/'native-battery-runtime/native_battery_runtime.o')
    for path,digest in modules_graph['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert not modules['application_linked'] and not modules['instruction_identity'] and not modules_graph['application_linked'] and not modules_graph['instruction_identity']
    ingress_dir=BASE/'native-protocol-ingress';ingress=json.loads((ingress_dir/'verification.json').read_text())
    assert ingress['comparisons']==72220 and ingress['path_counts']=={'rejected':2409,'null_module':1630,'module':66996,'special':1185}
    assert ingress['provider_calls_per_side']=={'r1_structured_log_mode_get':207489,'r1_structured_log_format':2916,'nrf_log_frontend_std_4':2592,'r1_eus_system_dispatch_plan_build':65967,'r1_health_registration_dispatcher':1029,'r1_ble_event_dispatch':1185}
    assert ingress['all_length_halfwords'] and ingress['mode_sequences']==13 and ingress['full_r0_r1_r2_r3'] and ingress['exact_saved_frame32'] and ingress['tail_stack_and_lr'] and ingress['header_and_table_mutation_modes']==6 and ingress['preserving_mode_scratch_cases']==936 and not ingress['rea_boundary_available']
    assert ingress['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and ingress['ownership_row']==next(row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and row['entry']=='0x0008316c')
    assert ingress['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_ingress.py') and ingress['application_sha256']==app_hash and ingress['report_sha256']==sha(ingress_dir/'report.json') and ingress['object_sha256']==sha(ingress_dir/'native_protocol_ingress.o')
    for path,digest in ingress['evidence'].items():assert sha(ingress_dir/path)==digest,path
    gap=json.loads((ingress_dir/'rea-boundary-gap.json').read_text());assert gap['error']['code']=='invalid_request' and any('No procedure exists at the requested address: 0x8316c' in issue['message'] for issue in gap['error']['issues'])
    assert bytes(json.loads((ingress_dir/'ghidra-body-data.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x8316c-0x27000:0x8316c-0x27000+300]
    assert sum(row['bytes'] for row in ingress['source_descriptor_sections'].values())==110
    for row in ingress['source_descriptor_sections'].values():assert row['sha256']==hashlib.sha256((ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[row['address']-0x27000:row['address']-0x27000+row['bytes']]).hexdigest()
    assert ingress['source_owned_module_section']=={'address':536898448,'bytes':16,'sha256_at_native_targets':'368332a0386c5ba30a310488de2894bdee978d5b916e592c5201804187a91be9','symbolic_targets':{'1':'r1_eus_system_dispatch_plan_build','2':'r1_health_registration_dispatcher'}}
    assert [run['poison'] for run in ingress['cold_runs']]==[165,90,255,60]
    table=struct.pack('<4I',0,0x83ca9,0x82be9,0)
    expected_writes=[{'pc':165652 if value else 165670,'address':536898448+i,'bytes':1,'value':value} for i,value in enumerate(table)]
    assert all(run['writes']==expected_writes for run in ingress['cold_runs'])
    ingress_graph=json.loads((BASE/'native-battery-runtime/ingress-integration-verification.json').read_text())
    assert ingress_graph['comparisons']==2896 and ingress_graph['compiled_ingress_sections']==ingress['source_descriptor_sections']
    assert ingress_graph['executed_ingress_counts']=={side:{'entry':1804,'system':151,'health':151,'special':226} for side in ('native','source')}
    assert ingress_graph['executed_receive_counts']=={side:{'entry':2896,'callback':1804,'invalid':911,'missing':181} for side in ('native','source')}
    assert ingress_graph['source_owned_module_table']=={'address':536898448,'bytes':16,'symbolic_targets':{'1':'r1_eus_system_dispatch_plan_build','2':'r1_health_registration_dispatcher'},'pointer_normalized':True}
    assert ingress_graph['executed_tx_producer_counts']=={side:{'dispatch':2573,'malloc':1544,'put':1321,'accepted':336,'free':985,'allocation_failed':223,'queue_missing':516,'connection_rejected':513} for side in ('native','source')}
    assert ingress_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_ingress_graph.py') and ingress_graph['application_sha256']==app_hash and ingress_graph['report_sha256']==sha(BASE/'native-battery-runtime/report.json') and ingress_graph['object_sha256']==sha(BASE/'native-battery-runtime/native_battery_runtime.o')
    for path,digest in ingress_graph['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert not ingress['application_linked'] and not ingress['instruction_identity'] and not ingress_graph['application_linked'] and not ingress_graph['instruction_identity']
    receive_dir=BASE/'native-protocol-receive';receive=json.loads((receive_dir/'verification.json').read_text())
    assert receive['comparisons']==16848 and receive['callback_calls_per_side']==4680 and receive['path_counts']=={'invalid':9828,'missing':2340,'callback':4680}
    assert receive['provider_calls_per_side']=={'r1_structured_log_mode_get':30888,'r1_structured_log_format':8424,'nrf_log_frontend_std_0':7488} and receive['mode_sequences']==13
    assert receive['tail_stack_lr_and_register_forwarding'] and receive['full_callback_return_registers'] and receive['raw_invalid_return_r0'] and receive['short_circuit_no_recheck'] and receive['live_callback_mutation'] and not receive['rea_boundary_available']
    assert receive['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and receive['ownership_row']==next(row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and row['entry']=='0x000826b4')
    assert receive['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_receive.py') and receive['application_sha256']==app_hash and receive['report_sha256']==sha(receive_dir/'report.json') and receive['object_sha256']==sha(receive_dir/'native_protocol_receive.o')
    for path,digest in receive['evidence'].items():assert sha(receive_dir/path)==digest,path
    gap=json.loads((receive_dir/'rea-boundary-gap.json').read_text());assert gap['error']['code']=='invalid_request' and any('No procedure exists at the requested address: 0x826b4' in issue['message'] for issue in gap['error']['issues'])
    assert bytes(json.loads((receive_dir/'ghidra-body-data.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x826b4-0x27000:0x826b4-0x27000+324]
    assert sum(row['bytes'] for row in receive['source_descriptor_sections'].values())==172
    for row in receive['source_descriptor_sections'].values():assert row['sha256']==hashlib.sha256((ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[row['address']-0x27000:row['address']-0x27000+row['bytes']]).hexdigest()
    receive_graph=json.loads((BASE/'native-battery-runtime/receive-integration-verification.json').read_text())
    assert receive_graph['comparisons']==2896 and receive_graph['compiled_receive_sections']==receive['source_descriptor_sections']
    assert receive_graph['executed_receive_counts']=={side:{'entry':2896,'callback':1804,'invalid':911,'missing':181} for side in ('native','source')}
    assert receive_graph['executed_port_counts']=={side:{'init':2896,'receive_register':2896} for side in ('native','source')} and receive_graph['executed_registration_counts']=={'native':2896,'source':2896}
    assert receive_graph['executed_fragment_counts']=={side:{'entry':645,'crc32':645,'memmove':645} for side in ('native','source')}
    assert receive_graph['executed_tx_producer_counts']=={side:{'dispatch':2573,'malloc':1544,'put':1321,'accepted':336,'free':985,'allocation_failed':223,'queue_missing':516,'connection_rejected':513} for side in ('native','source')}
    assert receive_graph['response_status_counts']=={side:{'3':71,'0':645,'5':94} for side in ('native','source')}
    assert receive_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_receive_graph.py') and receive_graph['application_sha256']==app_hash and receive_graph['report_sha256']==sha(BASE/'native-battery-runtime/report.json') and receive_graph['object_sha256']==sha(BASE/'native-battery-runtime/native_battery_runtime.o')
    for path,digest in receive_graph['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert not receive['application_linked'] and not receive['instruction_identity'] and not receive_graph['application_linked'] and not receive_graph['instruction_identity']
    port_dir=BASE/'native-protocol-port';protocol_port=json.loads((port_dir/'verification.json').read_text())
    assert protocol_port['comparisons']==66472 and protocol_port['counts']=={'receive':66160,'init':312}
    assert protocol_port['provider_calls_per_side']=={'r1_structured_log_mode_get':199776,'r1_structured_log_format':864,'nrf_log_frontend_std_0':768}
    assert protocol_port['all_callback_halfwords'] and protocol_port['mode_sequences']==13 and protocol_port['actual_send_and_receive_registration'] and protocol_port['reset_and_registration_store_order'] and protocol_port['raw_initializer_r0_checked'] and protocol_port['live_callback_mutation'] and not protocol_port['rea_boundary_available']
    assert protocol_port['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and protocol_port['ownership_rows']==[row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and row['entry'] in ('0x000830a8','0x000832d4')]
    assert protocol_port['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_port.py') and protocol_port['application_sha256']==app_hash
    for path,digest in protocol_port['provider_reports'].items():assert sha(BASE/path)==digest,path
    for path,digest in protocol_port['evidence'].items():assert sha(port_dir/path)==digest,path
    for filename,address,length in [('ghidra-init-body-data.json',0x830a8,196),('ghidra-receive-body-data.json',0x832d4,372)]:assert bytes(json.loads((port_dir/filename).read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+length]
    for address in (0x830a8,0x832d4):
        gap=json.loads((port_dir/('rea-'+format(address,'x')+'.json')).read_text());assert gap['error']['code']=='invalid_request' and any('No procedure exists at the requested address: '+hex(address) in issue['message'] for issue in gap['error']['issues'])
    assert sum(row['bytes'] for row in protocol_port['source_descriptor_sections'].values())==320
    for row in protocol_port['source_descriptor_sections'].values():assert row['sha256']==hashlib.sha256((ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[row['address']-0x27000:row['address']-0x27000+row['bytes']]).hexdigest()
    assert protocol_port['source_owned_receive_section']=={'address':536898596,'bytes':4,'sha256':'df3f619804a92fdb4057192dc43dd748ea778adc52bc498ce80524c014b81119'}
    assert [run['poison'] for run in protocol_port['cold_runs']]==[165,90,255,60]
    assert all(run['writes']==[{'pc':165690,'address':address,'bytes':1,'value':0} for address in range(536898596,536898600)] for run in protocol_port['cold_runs'])
    port_graph=json.loads((BASE/'native-battery-runtime/port-integration-verification.json').read_text())
    assert port_graph['comparisons']==2896 and port_graph['executed_port_counts']=={side:{'init':2896,'receive_register':2896} for side in ('native','source')}
    assert port_graph['compiled_port_sections']==protocol_port['source_descriptor_sections'] and port_graph['source_owned_encoder_sections']['protocol_receive_hook']==protocol_port['source_owned_receive_section']
    assert port_graph['executed_registration_counts']=={'native':2896,'source':2896} and port_graph['executed_send_hook_counts']=={'native':645,'source':645} and port_graph['executed_fragment_tx_entries']=={'native':645,'source':645}
    assert port_graph['executed_fragment_counts']=={side:{'entry':645,'crc32':645,'memmove':645} for side in ('native','source')}
    assert port_graph['executed_tx_producer_counts']=={side:{'dispatch':2573,'malloc':1544,'put':1321,'accepted':336,'free':985,'allocation_failed':223,'queue_missing':516,'connection_rejected':513} for side in ('native','source')}
    assert port_graph['response_status_counts']=={side:{'3':71,'0':645,'5':94} for side in ('native','source')}
    assert port_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_port_graph.py') and port_graph['application_sha256']==app_hash and port_graph['report_sha256']==sha(BASE/'native-battery-runtime/report.json') and port_graph['object_sha256']==sha(BASE/'native-battery-runtime/native_battery_runtime.o')
    for path,digest in port_graph['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert not protocol_port['application_linked'] and not protocol_port['instruction_identity'] and not port_graph['application_linked'] and not port_graph['instruction_identity']
    fragment_dir=BASE/'native-protocol-fragment';fragment=json.loads((fragment_dir/'verification.json').read_text())
    assert fragment['comparisons']==4957 and fragment['status_counts']=={'0':4800,'4294967295':157}
    assert fragment['provider_calls_per_side']=={'crc':4957,'memmove':40593,'callback':40924,'mode':399,'ring':108,'std1':0,'std2':96}
    assert fragment['all_lengths_0_through_4097'] and fragment['null_empty_input'] and fragment['mode_sequences']==13 and fragment['actual_crc32_and_memmove'] and fragment['extra_empty_fragment_preserved'] and fragment['callback_returns_ignored'] and fragment['live_callback_and_input_mutation']
    assert fragment['native_body_ranges']==[{'start':'0x32408','end':'0x32485','bytes':126},{'start':'0x32488','end':'0x32519','bytes':146}] and fragment['native_body_bytes']==272 and fragment['native_span_bytes']==274 and fragment['excluded_nop_bytes']==2 and not fragment['rea_boundary_available']
    assert fragment['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and fragment['ownership_row']==next(row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and row['entry']=='0x00032408')
    assert fragment['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_fragment.py') and fragment['application_sha256']==app_hash
    for path,digest in fragment['provider_reports'].items():assert sha(BASE/path)==digest,path
    for path,digest in fragment['evidence'].items():assert sha(fragment_dir/path)==digest,path
    for filename,address,length in [('ghidra-body-data.json',0x32408,400),('ghidra-registration-target.json',0x830a8,96)]:assert bytes(json.loads((fragment_dir/filename).read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+length]
    assert sum(row['bytes'] for row in fragment['source_descriptor_sections'].values())==106
    for row in fragment['source_descriptor_sections'].values():assert row['sha256']==hashlib.sha256((ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[row['address']-0x27000:row['address']-0x27000+row['bytes']]).hexdigest()
    fragment_state_dir=BASE/'native-protocol-fragment-state';fragment_state=json.loads((fragment_state_dir/'verification.json').read_text())
    assert fragment_state['source_owned_section']=={'address':536897888,'bytes':4,'sha256_at_native_target':'5fa860b7dd0a76bc1df602dc7703a215e27161aeebbd9acfd9ffe6777a0aef3e','native_target':'0x3407c','source_target':'r1_ble_tx_queue_dispatch_type1','symbolic_relocation':'R_ARM_ABS32'}
    assert [run['poison'] for run in fragment_state['cold_runs']]==[165,90,255,60]
    expected_writes=[{'pc':pc,'address':536897888+i,'bytes':1,'value':value} for i,(pc,value) in enumerate([(165652,125),(165652,64),(165690,3),(165690,0)])]
    assert all(run['writes']==expected_writes for run in fragment_state['cold_runs'])
    assert fragment_state['report_sha256']==sha(fragment_state_dir/'report.json') and fragment_state['object_sha256']==sha(fragment_state_dir/'native_protocol_fragment_state.o') and fragment_state['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_fragment_state.py') and fragment_state['application_sha256']==app_hash
    for filename,driver in [('fragment-integration-verification.json','verify_native_protocol_fragment_graph.py'),('fragment-tx-integration-verification.json','verify_native_protocol_fragment_tx_graph.py')]:
        graph=json.loads((BASE/'native-battery-runtime'/filename).read_text())
        assert graph['comparisons']==2896 and graph['executed_fragment_counts']=={side:{'entry':645,'crc32':645,'memmove':645} for side in ('native','source')}
        assert graph['executed_send_hook_counts']=={'native':645,'source':645} and graph['executed_registration_counts']=={'native':5792,'source':5792}
        assert graph['response_status_counts']=={side:{'3':71,'0':645,'5':94} for side in ('native','source')}
        assert graph['driver_sha256']==sha(ROOT/'r1/tools'/driver) and graph['application_sha256']==app_hash and graph['report_sha256']==sha(BASE/'native-battery-runtime/report.json') and graph['object_sha256']==sha(BASE/'native-battery-runtime/native_battery_runtime.o')
        for path,digest in graph['provider_reports'].items():assert sha(BASE/path)==digest,path
        assert not graph['application_linked'] and not graph['instruction_identity']
        if filename=='fragment-tx-integration-verification.json':
            assert graph['compiled_fragment_sections']==fragment['source_descriptor_sections'] and graph['executed_fragment_tx_entries']=={'native':645,'source':645}
            assert graph['source_owned_fragment_callback']=={'address':536897888,'bytes':4,'native_target':'0x3407c','source_target':'r1_ble_tx_queue_dispatch_type1','pointer_normalized':True}
            assert graph['executed_tx_producer_counts']=={side:{'dispatch':2573,'malloc':1544,'put':1321,'accepted':336,'free':985,'allocation_failed':223,'queue_missing':516,'connection_rejected':513} for side in ('native','source')}
            assert graph['executed_frame_entry_counts']=={'native':2893,'source':2893} and graph['frame_provider_counts']=={side:{'reads':6364,'dispatches':1928,'skipped':965} for side in ('native','source')}
    assert not fragment['application_linked'] and not fragment['instruction_identity'] and not fragment_state['application_linked'] and not fragment_state['instruction_identity']
    registration_dir=BASE/'native-protocol-send-registration';registration=json.loads((registration_dir/'verification.json').read_text())
    assert registration['comparisons']==65544 and registration['successful_registrations']==65542 and registration['null_rejections']==2 and registration['null_preserves_previous'] and registration['full_r0_r1_r2_r3_checked']
    assert not registration['rea_boundary_available'] and registration['native_entry']=='0x83448' and registration['native_size']==16 and registration['native_callsite']=='0x830b4'
    assert registration['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv')
    assert registration['ownership_row']==next(row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and row['entry']=='0x00083448')
    assert registration['report_sha256']==sha(registration_dir/'report.json') and registration['object_sha256']==sha(registration_dir/'native_protocol_send_registration.o') and registration['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_send_registration.py') and registration['application_sha256']==app_hash
    for path,digest in registration['evidence'].items():assert sha(registration_dir/path)==digest,path
    for filename,address,length in [('ghidra-body.json',0x83448,20),('ghidra-callsite.json',0x830a8,20)]:assert bytes(json.loads((registration_dir/filename).read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+length]
    call=(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x830b4-0x27000:0x830b8-0x27000];assert call==bytes.fromhex('00f0c8f9')
    registration_graph=json.loads((BASE/'native-battery-runtime/registration-integration-verification.json').read_text())
    assert registration_graph['comparisons']==2896 and registration_graph['executed_registration_counts']=={'native':5792,'source':5792} and registration_graph['executed_send_hook_counts']=={'native':645,'source':645}
    assert registration_graph['executed_response_counts']=={side:{'entry':810,'gate_a':810,'gate_b':272,'malloc':716,'allocated':645,'encode':645,'send':645,'free':645} for side in ('native','source')}
    assert registration_graph['response_status_counts']=={side:{'3':71,'4':431,'5':94,'0':214} for side in ('native','source')}
    assert registration_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_send_registration_graph.py') and registration_graph['application_sha256']==app_hash and registration_graph['report_sha256']==sha(BASE/'native-battery-runtime/report.json') and registration_graph['object_sha256']==sha(BASE/'native-battery-runtime/native_battery_runtime.o')
    for path,digest in registration_graph['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert not registration['application_linked'] and not registration['instruction_identity'] and not registration_graph['application_linked'] and not registration_graph['instruction_identity']
    hook_dir=BASE/'native-protocol-send-hook';send_hook=json.loads((hook_dir/'verification.json').read_text())
    assert send_hook['comparisons']==8232 and send_hook['callback_calls_per_side']==5488
    assert send_hook['full_r0_r1_r2_r3_checked'] and send_hook['tail_stack_and_lr_checked'] and send_hook['live_registration_mutation']
    assert send_hook['report_sha256']==sha(hook_dir/'report.json') and send_hook['object_sha256']==sha(hook_dir/'native_protocol_send_hook.o') and send_hook['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_send_hook.py') and send_hook['application_sha256']==app_hash
    assert send_hook['source_owned_section']=={'address':536898592,'bytes':4,'sha256':'df3f619804a92fdb4057192dc43dd748ea778adc52bc498ce80524c014b81119'}
    assert [x['poison'] for x in send_hook['cold_runs']]==[165,90,255,60]
    assert all(x['writes']==[{'pc':165690,'address':a,'bytes':1,'value':0} for a in range(536898592,536898596)] for x in send_hook['cold_runs'])
    gate_dir=BASE/'native-protocol-connection-gates';connection_gates=json.loads((gate_dir/'verification.json').read_text())
    assert connection_gates['comparisons']==131072 and connection_gates['counts']=={'r1_authenticated_phone_connection_gate':65536,'r1_peer_channel_b_valid':65536} and connection_gates['all_handle_halfwords'] and connection_gates['full_r0_r1_r2_r3_checked']
    assert connection_gates['report_sha256']==sha(gate_dir/'report.json') and connection_gates['object_sha256']==sha(gate_dir/'native_protocol_connection_gates.o') and connection_gates['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_connection_gates.py') and connection_gates['application_sha256']==app_hash
    for directory,receipt,entries in [(hook_dir,send_hook,[(0x827f8,14,20)]),(gate_dir,connection_gates,[(0x4cbb0,20,24),(0x4cb40,20,24)])]:
        for path,digest in receipt['evidence'].items():assert sha(directory/path)==digest,path
        for address,body,window in entries:
            q=json.loads((directory/('rea-'+format(address,'x')+'.json')).read_text());assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']==hex(address) and q['normalized_result']['body']['total_bytes']==body
            filename='ghidra-body.json' if address==0x827f8 else 'ghidra-'+format(address,'x')+'.json'
            assert bytes(json.loads((directory/filename).read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+window]
        assert not receipt['application_linked'] and not receipt['instruction_identity']
    for filename,driver in [('send-hook-integration-verification.json','verify_native_protocol_send_hook_graph.py'),('connection-gates-integration-verification.json','verify_native_protocol_connection_gates_graph.py')]:
        graph=json.loads((BASE/'native-battery-runtime'/filename).read_text())
        assert graph['comparisons']==2896 and graph['executed_send_hook_counts']=={'native':645,'source':645}
        assert graph['executed_encoder_counts']=={side:{'entry':645,'memmove':645,'crc':645} for side in ('native','source')}
        assert graph['source_owned_encoder_sections']['protocol_send_hook']==send_hook['source_owned_section']
        assert graph['executed_response_counts']=={side:{'entry':810,'gate_a':810,'gate_b':272,'malloc':716,'allocated':645,'encode':645,'send':645,'free':645} for side in ('native','source')}
        assert graph['response_status_counts']=={side:{'3':71,'4':431,'5':94,'0':214} for side in ('native','source')}
        assert graph['driver_sha256']==sha(ROOT/'r1/tools'/driver) and graph['application_sha256']==app_hash and graph['report_sha256']==sha(BASE/'native-battery-runtime/report.json') and graph['object_sha256']==sha(BASE/'native-battery-runtime/native_battery_runtime.o')
        for path,digest in graph['provider_reports'].items():assert sha(BASE/path)==digest,path
        assert not graph['application_linked'] and not graph['instruction_identity']
    encoder_dir=BASE/'native-protocol-encoder';encoder=json.loads((encoder_dir/'verification.json').read_text())
    assert encoder['comparisons']==6600 and encoder['status_counts']=={'2':3074,'0':3328,'1':198} and encoder['actual_memmove_and_crc']
    assert encoder['provider_calls_per_side']=={'memmove':1664,'crc':3328}
    assert encoder['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_encoder.py') and encoder['application_sha256']==app_hash
    for path,digest in encoder['provider_reports'].items():assert sha(BASE/path)==digest,path
    for path,digest in encoder['evidence'].items():assert sha(encoder_dir/path)==digest,path
    eq=json.loads((encoder_dir/'rea-82f9c.json').read_text());assert eq['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and eq['normalized_result']['entrypoint']=='0x82f9c' and eq['normalized_result']['body']['total_bytes']==136
    assert bytes(json.loads((encoder_dir/'ghidra-body.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x82f9c-0x27000:0x82f9c-0x27000+140]
    assert [x['poison'] for x in encoder['cold_runs']]==[165,90,255,60]
    expected_writes=[{'pc':165670,'address':a,'bytes':1,'value':0} for a in (536898440,536898441,536898464)]+[{'pc':165652,'address':a,'bytes':1,'value':100} for a in (536898465,536898466,536898467)]
    assert all(x['writes']==expected_writes for x in encoder['cold_runs'])
    eg=json.loads((BASE/'native-battery-runtime/encoder-integration-verification.json').read_text())
    assert eg['comparisons']==2896 and eg['executed_encoder_counts']=={side:{'entry':645,'memmove':645,'crc':645} for side in ('native','source')}
    assert eg['source_owned_encoder_sections']=={'protocol_sequence':encoder['source_owned_sections']['sequence'],'protocol_versions':encoder['source_owned_sections']['version_map']}
    assert eg['executed_response_counts']=={side:{'entry':810,'gate_a':810,'gate_b':272,'malloc':716,'allocated':645,'encode':645,'send':645,'free':645} for side in ('native','source')}
    assert eg['response_status_counts']=={side:{'3':71,'4':431,'5':94,'0':214} for side in ('native','source')}
    assert eg['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_encoder_graph.py') and eg['application_sha256']==app_hash
    for path,digest in eg['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert not encoder['application_linked'] and not encoder['instruction_identity'] and not eg['application_linked'] and not eg['instruction_identity']
    response_dir=BASE/'native-protocol-response';response=json.loads((response_dir/'verification.json').read_text())
    assert response['comparisons']==100480 and response['all_length_halfwords'] and response['allocation_wrap_bits']==16 and response['full_length_forwarded'] and response['mode_sequences']==13
    assert response['status_counts']=={'7':65536,'2':17472,'5':4368,'3':6552,'0':1092,'4':2184,'2147483655':3276}
    assert response['provider_calls_per_side']=={'r1_authenticated_phone_connection_gate':83008,'r1_peer_channel_b_valid':8736,'pvPortMalloc':78640,'vPortFree':72088,'r1_model_encode':72088,'r1_protocol_send_hook_call':3276,'r1_structured_log_mode_get':30324,'r1_structured_log_format':8652,'nrf_log_frontend_std_1':1176,'nrf_log_frontend_std_2':3528,'nrf_log_frontend_std_4':1764}
    assert response['report_sha256']==sha(response_dir/'report.json') and response['object_sha256']==sha(response_dir/'native_protocol_response.o') and response['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_response.py') and response['application_sha256']==app_hash
    assert not response['application_linked'] and not response['instruction_identity']
    for path,digest in response['evidence'].items():assert sha(response_dir/path)==digest,path
    rq=json.loads((response_dir/'rea-828b4.json').read_text());assert rq['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and rq['normalized_result']['entrypoint']=='0x828b4' and rq['normalized_result']['body']['total_bytes']==364
    assert bytes(json.loads((response_dir/'ghidra-body-data.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x828b4-0x27000:0x828b4-0x27000+672]
    assert sum(row['bytes'] for row in response['source_descriptor_sections'].values())==290
    for name,row in response['source_descriptor_sections'].items():assert row['sha256']==hashlib.sha256((ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[row['address']-0x27000:row['address']-0x27000+row['bytes']]).hexdigest()
    response_graph=json.loads((BASE/'native-battery-runtime/response-integration-verification.json').read_text())
    assert response_graph['comparisons']==2896 and response_graph['compiled_response_sections']==response['source_descriptor_sections']
    assert response_graph['executed_response_counts']=={side:{'entry':810,'gate_a':810,'gate_b':272,'malloc':716,'allocated':645,'encode':645,'send':308,'free':645} for side in ('native','source')}
    assert response_graph['response_status_counts']=={side:{'3':71,'4':205,'5':94,'7':161,'4294967295':176,'0':103} for side in ('native','source')}
    assert response_graph['executed_operation_header_counts']=={side:{'operation':1071,'header':1071,'phone_getter':1071,'lower':810,'lower_zero':103,'lower_nonzero':707} for side in ('native','source')}
    assert response_graph['executed_frame_entry_counts']=={'native':2878,'source':2878} and response_graph['frame_provider_counts']=={side:{'reads':6323,'dispatches':1915,'skipped':963} for side in ('native','source')}
    assert response_graph['executed_tx_producer_counts']=={side:{'dispatch':1915,'malloc':1145,'put':981,'accepted':245,'free':736,'allocation_failed':164,'queue_missing':385,'connection_rejected':385} for side in ('native','source')}
    assert response_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_protocol_response_graph.py') and response_graph['application_sha256']==app_hash and response_graph['report_sha256']==sha(BASE/'native-battery-runtime/report.json') and response_graph['object_sha256']==sha(BASE/'native-battery-runtime/native_battery_runtime.o')
    assert response_graph['provider_reports']=={name+'/report.json':sha(BASE/name/'report.json') for name in ('native-protocol-response','native-phone-operation','native-protocol-response-header','native-battery-protocol','native-tx','connection-handle','native-battery-frame','native-battery-voltage','native-kv-device-fields','native-battery-low','native-battery-diagnostic','native-battery-initial-curve','native-battery-recovery','native-battery-cadence','native-battery-configuration','native-kv-class','runtime','native-battery-discharge','native-battery-filter','native-battery-statistics','native-battery-control')}
    assert response_graph['service_prefix_nops']=={'native':2896,'source':2896} and response_graph['executed_voltage_entry_counts']=={'native':920,'source':920} and response_graph['executed_device_field_counts']=={side:{'setter':920,'read':920,'write':920} for side in ('native','source')}
    assert response_graph['executed_control_entry_counts']['native']==response_graph['executed_control_entry_counts']['source'] and response_graph['executed_statistics_entry_counts']['native']==response_graph['executed_statistics_entry_counts']['source'] and all(n==2896 for n in response_graph['executed_statistics_entry_counts']['source'].values())
    assert not response_graph['application_linked'] and not response_graph['instruction_identity']
    operation_dir=BASE/'native-phone-operation';operation=json.loads((operation_dir/'verification.json').read_text())
    assert operation['comparisons']==98176 and operation['counts']=={'r1_phone_cmd_send_op1':3840,'r1_protocol_response_send_0x100':94336} and operation['lower_calls']==90976 and operation['null_wrapper_inputs']==1920
    assert operation['all_operation_halfwords'] and operation['actual_connection_getter'] and operation['actual_header_wrapper'] and operation['incoming_stack_arguments_unchanged'] and operation['full_r2_r3_checked'] and operation['raw_lower_zero_maps_to_one']
    assert operation['driver_sha256']==sha(ROOT/'r1/tools/verify_native_phone_operation.py') and operation['application_sha256']==app_hash
    assert operation['provider_reports']=={name+'/report.json':sha(BASE/name/'report.json') for name in ('native-phone-operation','native-protocol-response-header','connection-handle')}
    assert not operation['application_linked'] and not operation['instruction_identity']
    for path,digest in operation['evidence'].items():assert sha(operation_dir/path)==digest,path
    for a,z in [(0x83896,36),(0x84c0c,82)]:
        q=json.loads((operation_dir/f'rea-{a:x}.json').read_text());assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']==hex(a) and q['normalized_result']['body']['total_bytes']==z
        assert bytes(json.loads((operation_dir/f'ghidra-{a:x}.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+z]
    operation_graph=json.loads((BASE/'native-battery-runtime/phone-operation-integration-verification.json').read_text())
    assert operation_graph['comparisons']==2896 and operation_graph['executed_operation_header_counts']=={side:{'operation':1071,'header':1071,'phone_getter':1071,'lower':810,'lower_zero':207,'lower_nonzero':603} for side in ('native','source')}
    assert operation_graph['executed_protocol_entry_counts']==operation_graph['protocol_dispatch_counts']=={'native':1071,'source':1071} and operation_graph['executed_frame_entry_counts']=={'native':2836,'source':2836}
    assert operation_graph['executed_tx_producer_counts']=={side:{'dispatch':1886,'malloc':1126,'put':965,'accepted':241,'free':724,'allocation_failed':161,'queue_missing':375,'connection_rejected':385} for side in ('native','source')}
    assert operation_graph['frame_provider_counts']=={side:{'reads':6233,'dispatches':1886,'skipped':950} for side in ('native','source')}
    assert operation_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_phone_operation_graph.py') and operation_graph['application_sha256']==app_hash and operation_graph['report_sha256']==sha(BASE/'native-battery-runtime/report.json') and operation_graph['object_sha256']==sha(BASE/'native-battery-runtime/native_battery_runtime.o')
    assert operation_graph['provider_reports']=={name+'/report.json':sha(BASE/name/'report.json') for name in ('native-phone-operation','native-protocol-response-header','native-battery-protocol','native-tx','connection-handle','native-battery-frame','native-battery-voltage','native-kv-device-fields','native-battery-low','native-battery-diagnostic','native-battery-initial-curve','native-battery-recovery','native-battery-cadence','native-battery-configuration','native-kv-class','runtime','native-battery-discharge','native-battery-filter','native-battery-statistics','native-battery-control')}
    assert operation_graph['service_prefix_nops']=={'native':2896,'source':2896} and operation_graph['executed_voltage_entry_counts']=={'native':920,'source':920} and operation_graph['executed_device_field_counts']=={side:{'setter':920,'read':920,'write':920} for side in ('native','source')}
    assert operation_graph['executed_configuration_entry_counts']=={side:{'r1_batcfg_word1_signed_get':2896,'r1_batcfg_byte0_get':2990,'r1_kv_class_read':6806} for side in ('native','source')}
    assert operation_graph['executed_control_entry_counts']['native']==operation_graph['executed_control_entry_counts']['source'] and operation_graph['executed_statistics_entry_counts']['native']==operation_graph['executed_statistics_entry_counts']['source'] and all(n==2896 for n in operation_graph['executed_statistics_entry_counts']['source'].values())
    assert not operation_graph['application_linked'] and not operation_graph['instruction_identity']
    protocol_dir=BASE/'native-battery-protocol';protocol=json.loads((protocol_dir/'verification.json').read_text())
    assert protocol['comparisons']==160992 and protocol['all_percentage_bytes'] and protocol['full_word_percentage_logs'] and protocol['mode_sequences']==13 and protocol['full_r1_r2_r3_checked'] and protocol['raw_return_checked']
    assert protocol['provider_calls_per_side']=={'r1_structured_log_mode_get':408672,'r1_structured_log_format':111456,'nrf_log_frontend_std_2':86688,'r1_phone_cmd_send_op1':160992}
    assert protocol['report_sha256']==sha(protocol_dir/'report.json') and protocol['object_sha256']==sha(protocol_dir/'native_battery_protocol.o') and protocol['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_protocol.py') and protocol['application_sha256']==app_hash
    assert not protocol['application_linked'] and not protocol['instruction_identity']
    for path,digest in protocol['evidence'].items():assert sha(protocol_dir/path)==digest,path
    pq=json.loads((protocol_dir/'rea-8345c.json').read_text());assert pq['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and pq['normalized_result']['entrypoint']=='0x8345c' and pq['normalized_result']['body']['total_bytes']==108
    for file,address,size in [('ghidra-body.json',0x8345c,180),('ghidra-ring.json',0xc0234,66)]:assert bytes(json.loads((protocol_dir/file).read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    assert sum(row['bytes'] for row in protocol['source_descriptor_sections'].values())==126
    for name,row in protocol['source_descriptor_sections'].items():assert row['sha256']==hashlib.sha256((ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[row['address']-0x27000:row['address']-0x27000+row['bytes']]).hexdigest()
    protocol_graph=json.loads((BASE/'native-battery-runtime/protocol-integration-verification.json').read_text())
    assert protocol_graph['comparisons']==2896 and protocol_graph['executed_protocol_entry_counts']==protocol_graph['protocol_dispatch_counts']=={'native':1071,'source':1071} and protocol_graph['compiled_protocol_sections']==protocol['source_descriptor_sections']
    assert protocol_graph['executed_tx_producer_counts']=={side:{'dispatch':1873,'malloc':1126,'put':965,'accepted':241,'free':724,'allocation_failed':161,'queue_missing':373,'connection_rejected':374} for side in ('native','source')}
    assert protocol_graph['executed_frame_entry_counts']=={'native':2823,'source':2823} and protocol_graph['frame_provider_counts']=={side:{'reads':6196,'dispatches':1873,'skipped':950} for side in ('native','source')}
    assert protocol_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_protocol_graph.py') and protocol_graph['application_sha256']==app_hash and protocol_graph['report_sha256']==sha(BASE/'native-battery-runtime/report.json') and protocol_graph['object_sha256']==sha(BASE/'native-battery-runtime/native_battery_runtime.o')
    assert protocol_graph['provider_reports']=={name+'/report.json':sha(BASE/name/'report.json') for name in ('native-battery-protocol','native-tx','connection-handle','native-battery-frame','native-battery-voltage','native-kv-device-fields','native-battery-low','native-battery-diagnostic','native-battery-initial-curve','native-battery-recovery','native-battery-cadence','native-battery-configuration','native-kv-class','runtime','native-battery-discharge','native-battery-filter','native-battery-statistics','native-battery-control')}
    assert protocol_graph['service_prefix_nops']=={'native':2896,'source':2896} and protocol_graph['executed_voltage_entry_counts']=={'native':920,'source':920} and protocol_graph['executed_device_field_counts']=={side:{'setter':920,'read':920,'write':920} for side in ('native','source')}
    assert protocol_graph['executed_control_entry_counts']['native']==protocol_graph['executed_control_entry_counts']['source'] and protocol_graph['executed_statistics_entry_counts']['native']==protocol_graph['executed_statistics_entry_counts']['source'] and all(n==2896 for n in protocol_graph['executed_statistics_entry_counts']['source'].values())
    assert not protocol_graph['application_linked'] and not protocol_graph['instruction_identity']
    frame_tx=json.loads((BASE/'native-battery-runtime/frame-tx-integration-verification.json').read_text())
    assert frame_tx['comparisons']==2896 and frame_tx['tx_cold_poison']==165
    assert frame_tx['executed_tx_producer_counts']=={side:{'dispatch':1873,'malloc':1126,'put':965,'accepted':241,'free':724,'allocation_failed':161,'queue_missing':373,'connection_rejected':374} for side in ('native','source')}
    assert frame_tx['executed_frame_entry_counts']=={'native':2823,'source':2823} and frame_tx['frame_provider_counts']=={side:{'reads':6196,'dispatches':1873,'skipped':950} for side in ('native','source')}
    assert frame_tx['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_frame_tx_graph.py') and frame_tx['application_sha256']==app_hash and frame_tx['report_sha256']==sha(BASE/'native-battery-runtime/report.json') and frame_tx['object_sha256']==sha(BASE/'native-battery-runtime/native_battery_runtime.o')
    assert frame_tx['provider_reports']=={name+'/report.json':sha(BASE/name/'report.json') for name in ('native-tx','connection-handle','native-battery-frame','native-battery-voltage','native-kv-device-fields','native-battery-low','native-battery-diagnostic','native-battery-initial-curve','native-battery-recovery','native-battery-cadence','native-battery-configuration','native-kv-class','runtime','native-battery-discharge','native-battery-filter','native-battery-statistics','native-battery-control')}
    assert frame_tx['service_prefix_nops']=={'native':2896,'source':2896} and frame_tx['executed_voltage_entry_counts']=={'native':920,'source':920}
    assert frame_tx['executed_device_field_counts']=={side:{'setter':920,'read':920,'write':920} for side in ('native','source')} and frame_tx['executed_control_entry_counts']['native']==frame_tx['executed_control_entry_counts']['source']
    assert frame_tx['executed_statistics_entry_counts']['native']==frame_tx['executed_statistics_entry_counts']['source'] and all(n==2896 for n in frame_tx['executed_statistics_entry_counts']['source'].values())
    assert sum(row['bytes'] for row in frame_tx['source_owned_tx_sections'].values())==38 and frame_tx['source_owned_tx_sections']['connection10']=={'address':0x200064bc,'bytes':2,'sha256':hashlib.sha256(b'\xff\xff').hexdigest()}
    for path,digest in frame_tx['tx_evidence'].items():assert sha(BASE/'native-battery-runtime'/path)==digest,path
    tq=json.loads((BASE/'native-battery-runtime/rea-frame-tx-3e274.json').read_text());assert tq['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and tq['normalized_result']['entrypoint']=='0x34070' and tq['normalized_result']['body']['total_bytes']==548 and {'start':'0x3e274','end':'0x3e48b'} in tq['normalized_result']['body']['ranges']
    for a,z in [(0x34064,12),(0x3e274,536)]:assert bytes(json.loads((BASE/f'native-battery-runtime/ghidra-frame-tx-{a:x}.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+z]
    attribution=json.loads((BASE/'native-battery-runtime/frame-tx-attribution.json').read_text());assert not attribution['locked_ownership_changed'] and attribution['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and attribution['graph_receipt_sha256']==sha(BASE/'native-battery-runtime/frame-tx-integration-verification.json') and attribution['candidate_symbol']=='dispatch' and attribution['native_shared_range']=={'start':'0x3e274','end':'0x3e48b','bytes':536}
    assert not frame_tx['application_linked'] and not frame_tx['instruction_identity']
    frame_dir=BASE/'native-battery-frame';frame=json.loads((frame_dir/'verification.json').read_text())
    assert frame['comparisons']==66536 and frame['connection_reads']==132872 and frame['sends']==66336 and frame['sentinel']==200 and frame['all_payload_byte_pairs'] and frame['full_r1_r2_r3_checked'] and frame['raw_return_checked']
    assert frame['report_sha256']==sha(frame_dir/'report.json') and frame['object_sha256']==sha(frame_dir/'native_battery_frame.o') and frame['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_frame.py') and frame['application_sha256']==app_hash
    assert not frame['application_linked'] and not frame['instruction_identity']
    for path,digest in frame['evidence'].items():assert sha(frame_dir/path)==digest,path
    fq=json.loads((frame_dir/'rea-913fc.json').read_text());assert fq['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and fq['normalized_result']['entrypoint']=='0x913fc' and fq['normalized_result']['body']['total_bytes']==62
    assert bytes(json.loads((frame_dir/'ghidra-body.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x913fc-0x27000:0x913fc-0x27000+62]
    frame_graph=json.loads((BASE/'native-battery-runtime/frame-integration-verification.json').read_text())
    assert frame_graph['comparisons']==2896 and frame_graph['executed_frame_entry_counts']=={'native':2823,'source':2823} and frame_graph['frame_provider_counts']=={side:{'reads':4696,'sends':1873,'skipped':950} for side in ('native','source')}
    assert frame_graph['service_prefix_nops']=={'native':2896,'source':2896} and frame_graph['executed_voltage_entry_counts']=={'native':920,'source':920} and frame_graph['executed_device_field_counts']=={side:{'setter':920,'read':920,'write':920} for side in ('native','source')}
    assert frame_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_frame_graph.py') and frame_graph['application_sha256']==app_hash and frame_graph['report_sha256']==sha(BASE/'native-battery-runtime/report.json') and frame_graph['object_sha256']==sha(BASE/'native-battery-runtime/native_battery_runtime.o')
    assert frame_graph['provider_reports']=={name+'/report.json':sha(BASE/name/'report.json') for name in ('native-battery-frame','native-battery-voltage','native-kv-device-fields','native-battery-low','native-battery-diagnostic','native-battery-initial-curve','native-battery-recovery','native-battery-cadence','native-battery-configuration','native-kv-class','runtime','native-battery-discharge','native-battery-filter','native-battery-statistics','native-battery-control')}
    assert frame_graph['executed_configuration_entry_counts']=={side:{'r1_batcfg_word1_signed_get':2896,'r1_batcfg_byte0_get':2990,'r1_kv_class_read':6806} for side in ('native','source')}
    assert frame_graph['executed_control_entry_counts']['native']==frame_graph['executed_control_entry_counts']['source'] and frame_graph['executed_control_entry_counts']['source']['r1_battery_charging_progress_reset']==2316
    assert frame_graph['executed_statistics_entry_counts']['native']==frame_graph['executed_statistics_entry_counts']['source'] and all(n==2896 for n in frame_graph['executed_statistics_entry_counts']['source'].values())
    assert not frame_graph['application_linked'] and not frame_graph['instruction_identity']
    voltage_dir=BASE/'native-battery-voltage';voltage=json.loads((voltage_dir/'verification.json').read_text())
    assert voltage['comparisons']==262384 and voltage['counts']=={'r1_battery_voltage_get':262264,'r1_battery_runtime_service':120} and voltage['all_voltage_halfwords']
    assert voltage['prefix_nops']=={'native':131222,'source':131222} and voltage['provider_calls_per_side']=={'r1_advertising_configuration_byte_get':262264,'r1_battery_runtime_update_service':131222}
    assert voltage['native_service_declared_body_bytes']==4 and voltage['overlapping_ownership_span_bytes']==412 and voltage['updater_body_bytes']==406 and voltage['trailing_padding_bytes']==2
    assert voltage['report_sha256']==sha(voltage_dir/'report.json') and voltage['object_sha256']==sha(voltage_dir/'native_battery_voltage.o') and voltage['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_voltage.py') and voltage['application_sha256']==app_hash
    assert not voltage['application_linked'] and not voltage['instruction_identity']
    for path,digest in voltage['evidence'].items():assert sha(voltage_dir/path)==digest,path
    for a,z in [(0x91290,20),(0x31fcc,4)]:
        q=json.loads((voltage_dir/f'rea-{a:x}.json').read_text());assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']==hex(a) and q['normalized_result']['body']['total_bytes']==z
    for file,address,size in [('ghidra-getter.json',0x91290,24),('ghidra-service.json',0x31fcc,412)]:assert bytes(json.loads((voltage_dir/file).read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    voltage_graph=json.loads((BASE/'native-battery-runtime/voltage-integration-verification.json').read_text())
    assert voltage_graph['comparisons']==2896 and voltage_graph['native_service_entry']=='0x31fcc' and voltage_graph['service_ownership_span_bytes']==412 and voltage_graph['service_prefix_nops']=={'native':2896,'source':2896} and voltage_graph['executed_voltage_entry_counts']=={'native':920,'source':920}
    assert voltage_graph['executed_device_field_counts']=={side:{'setter':920,'read':920,'write':920} for side in ('native','source')} and voltage_graph['low_downstream_counts']=={side:{'record':920,'event':5} for side in ('native','source')}
    assert voltage_graph['executed_configuration_entry_counts']=={side:{'r1_batcfg_word1_signed_get':2896,'r1_batcfg_byte0_get':2990,'r1_kv_class_read':6806} for side in ('native','source')}
    assert voltage_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_voltage_graph.py') and voltage_graph['application_sha256']==app_hash and voltage_graph['report_sha256']==sha(BASE/'native-battery-runtime/report.json') and voltage_graph['object_sha256']==sha(BASE/'native-battery-runtime/native_battery_runtime.o')
    assert voltage_graph['provider_reports']=={name+'/report.json':sha(BASE/name/'report.json') for name in ('native-battery-voltage','native-kv-device-fields','native-battery-low','native-battery-diagnostic','native-battery-initial-curve','native-battery-recovery','native-battery-cadence','native-battery-configuration','native-kv-class','runtime','native-battery-discharge','native-battery-filter','native-battery-statistics','native-battery-control')}
    assert voltage_graph['record_high_half_observations']=={side:{'count':920,'distinct':[0,43707,65535],'sha256':'1b36d17db24eab8a24309f4aa3133488c225515bf06747d09355bdc1060d5ddb'} for side in ('native','source')}
    assert voltage_graph['executed_control_entry_counts']['native']==voltage_graph['executed_control_entry_counts']['source'] and voltage_graph['executed_control_entry_counts']['source']['r1_battery_charging_progress_reset']==2316
    assert voltage_graph['executed_statistics_entry_counts']['native']==voltage_graph['executed_statistics_entry_counts']['source'] and all(n==2896 for n in voltage_graph['executed_statistics_entry_counts']['source'].values())
    assert not voltage_graph['application_linked'] and not voltage_graph['instruction_identity']
    fields_dir=BASE/'native-kv-device-fields';fields=json.loads((fields_dir/'verification.json').read_text())
    assert fields['comparisons']==72017 and fields['read_calls']==fields['write_calls']==72016 and fields['null_inputs']==1 and fields['all_packed_halfwords']
    assert fields['native_frame_bytes']==52 and fields['native_frame_offset']==-64 and fields['partial_read_widths']==[0,1,4,36,40,41,42,44,51,52]
    assert fields['report_sha256']==sha(fields_dir/'report.json') and fields['object_sha256']==sha(fields_dir/'native_kv_device_fields.o') and fields['driver_sha256']==sha(ROOT/'r1/tools/verify_native_kv_device_fields.py') and fields['application_sha256']==app_hash
    assert not fields['application_linked'] and not fields['instruction_identity']
    for path,digest in fields['evidence'].items():assert sha(fields_dir/path)==digest,path
    fq=json.loads((fields_dir/'rea-73710.json').read_text());assert fq['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and fq['normalized_result']['entrypoint']=='0x73710' and fq['normalized_result']['body']['total_bytes']==60
    assert bytes(json.loads((fields_dir/'ghidra-body.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x73710-0x27000:0x73710-0x27000+64]
    fields_graph=json.loads((BASE/'native-battery-runtime/device-fields-integration-verification.json').read_text())
    assert fields_graph['comparisons']==2896 and fields_graph['executed_device_field_counts']=={side:{'setter':920,'read':920,'write':920} for side in ('native','source')}
    assert fields_graph['executed_low_entry_counts']=={'native':2896,'source':2896} and fields_graph['low_downstream_counts']=={side:{'record':920,'event':5} for side in ('native','source')}
    assert fields_graph['executed_configuration_entry_counts']=={side:{'r1_batcfg_word1_signed_get':2896,'r1_batcfg_byte0_get':2990,'r1_kv_class_read':6806} for side in ('native','source')}
    assert fields_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_kv_device_fields_graph.py') and fields_graph['application_sha256']==app_hash and fields_graph['report_sha256']==sha(BASE/'native-battery-runtime/report.json') and fields_graph['object_sha256']==sha(BASE/'native-battery-runtime/native_battery_runtime.o')
    assert fields_graph['provider_reports']=={name+'/report.json':sha(BASE/name/'report.json') for name in ('native-kv-device-fields','native-battery-low','native-battery-diagnostic','native-battery-initial-curve','native-battery-recovery','native-battery-cadence','native-battery-configuration','native-kv-class','runtime','native-battery-discharge','native-battery-filter','native-battery-statistics','native-battery-control')}
    assert fields_graph['record_high_half_observations']=={side:{'count':920,'distinct':[0,43707,65535],'sha256':'1b36d17db24eab8a24309f4aa3133488c225515bf06747d09355bdc1060d5ddb'} for side in ('native','source')}
    assert fields_graph['executed_control_entry_counts']['native']==fields_graph['executed_control_entry_counts']['source'] and fields_graph['executed_control_entry_counts']['source']['r1_battery_charging_progress_reset']==2316
    assert fields_graph['executed_statistics_entry_counts']['native']==fields_graph['executed_statistics_entry_counts']['source'] and all(n==2896 for n in fields_graph['executed_statistics_entry_counts']['source'].values())
    assert not fields_graph['application_linked'] and not fields_graph['instruction_identity']
    low_dir=BASE/'native-battery-low';low=json.loads((low_dir/'verification.json').read_text())
    assert low['comparisons']==53248 and low['all_counter_bytes'] and low['mode_sequences']==13 and low['full_r2_r3_checked'] and low['event_tail_raw_return_checked']
    assert low['outcomes']=={'reset':26624,'ordinary':936,'event':104,'record':25584}
    assert low['provider_calls_per_side']=={'r1_structured_log_mode_get':67584,'r1_structured_log_format':18432,'nrf_log_frontend_std_2':14336,'r1_battery_voltage_get':25584,'time_backend_timestamp_thunk':25584,'r1_kv_dev_info_fields_set':25584,'osThreadFlagsSet':25584,'r1_event_publish':104}
    assert low['report_sha256']==sha(low_dir/'report.json') and low['object_sha256']==sha(low_dir/'native_battery_low.o') and low['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_low.py') and low['application_sha256']==app_hash
    assert not low['application_linked'] and not low['instruction_identity']
    for path,digest in low['evidence'].items():assert sha(low_dir/path)==digest,path
    lq=json.loads((low_dir/'rea-3d88c.json').read_text());assert lq['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and lq['normalized_result']['entrypoint']=='0x3d88c' and lq['normalized_result']['body']['total_bytes']==176
    assert bytes(json.loads((low_dir/'ghidra-body-data.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x3d88c-0x27000:0x3d88c-0x27000+300]
    assert sum(row['bytes'] for row in low['source_descriptor_sections'].values())==104
    for name,row in low['source_descriptor_sections'].items():assert row['sha256']==hashlib.sha256((ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[row['address']-0x27000:row['address']-0x27000+row['bytes']]).hexdigest()
    low_graph=json.loads((BASE/'native-battery-runtime/low-integration-verification.json').read_text())
    assert low_graph['comparisons']==2896 and low_graph['executed_low_entry_counts']=={'native':2896,'source':2896} and low_graph['low_downstream_counts']=={side:{'record':920,'event':5} for side in ('native','source')}
    assert low_graph['record_high_half_observations']=={side:{'count':920,'distinct':[0,43707,65535],'sha256':'1b36d17db24eab8a24309f4aa3133488c225515bf06747d09355bdc1060d5ddb'} for side in ('native','source')}
    assert low_graph['compiled_low_sections']==low['source_descriptor_sections'] and low_graph['executed_diagnostic_entry_counts']=={'native':2896,'source':2896} and low_graph['executed_recovery_entry_counts']=={'native':2896,'source':2896}
    assert low_graph['executed_initial_curve_entry_counts']=={'native':312,'source':312} and low_graph['executed_cadence_entry_counts']=={'native':1113,'source':1113}
    assert low_graph['executed_configuration_entry_counts']=={side:{'r1_batcfg_word1_signed_get':2896,'r1_batcfg_byte0_get':2990,'r1_kv_class_read':5886} for side in ('native','source')}
    assert low_graph['native_kv_consumer_evidence_sha256']==sha(BASE/'native-battery-runtime/low-kv-consumer-ghidra.json')
    assert bytes(json.loads((BASE/'native-battery-runtime/low-kv-consumer-ghidra.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x73710-0x27000:0x73710-0x27000+64]
    assert low_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_low_graph.py') and low_graph['application_sha256']==app_hash and low_graph['report_sha256']==sha(BASE/'native-battery-runtime/report.json') and low_graph['object_sha256']==sha(BASE/'native-battery-runtime/native_battery_runtime.o')
    assert low_graph['provider_reports']=={name+'/report.json':sha(BASE/name/'report.json') for name in ('native-battery-low','native-battery-diagnostic','native-battery-initial-curve','native-battery-recovery','native-battery-cadence','native-battery-configuration','native-kv-class','runtime','native-battery-discharge','native-battery-filter','native-battery-statistics','native-battery-control')}
    assert low_graph['executed_control_entry_counts']['native']==low_graph['executed_control_entry_counts']['source'] and low_graph['executed_control_entry_counts']['source']['r1_battery_charging_progress_reset']==2316
    assert low_graph['executed_statistics_entry_counts']['native']==low_graph['executed_statistics_entry_counts']['source'] and all(n==2896 for n in low_graph['executed_statistics_entry_counts']['source'].values())
    assert not low_graph['application_linked'] and not low_graph['instruction_identity']
    diagnostic_dir=BASE/'native-battery-diagnostic';diagnostic=json.loads((diagnostic_dir/'verification.json').read_text())
    assert diagnostic['comparisons']==39936 and diagnostic['all_counter_bytes'] and diagnostic['mode_sequences']==13 and diagnostic['counter_aliases']==[0x20002000,0x20016bb0]
    assert diagnostic['provider_calls_per_side']=={'r1_structured_log_mode_get':196182,'r1_batcfg_byte0_get':9984,'r1_batcfg_word1_signed_get':44466,'r1_structured_log_format':60366,'nrf_log_frontend_std_1':18978,'nrf_log_frontend_std_4':22800}
    assert diagnostic['report_sha256']==sha(diagnostic_dir/'report.json') and diagnostic['object_sha256']==sha(diagnostic_dir/'native_battery_diagnostic.o') and diagnostic['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_diagnostic.py') and diagnostic['application_sha256']==app_hash
    assert not diagnostic['application_linked'] and not diagnostic['instruction_identity']
    for path,digest in diagnostic['evidence'].items():assert sha(diagnostic_dir/path)==digest,path
    dq=json.loads((diagnostic_dir/'rea-3d9b8.json').read_text());assert dq['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and dq['normalized_result']['entrypoint']=='0x3d9b8' and dq['normalized_result']['body']['total_bytes']==268
    for file,address,size in [('ghidra-body.json',0x3d9b8,440),('ghidra-charge_ring.json',0xc00bc,73),('ghidra-charge_sdk.json',0xc0108,67)]:assert bytes(json.loads((diagnostic_dir/file).read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    assert len(diagnostic['source_descriptor_sections'])==6 and sum(row['bytes'] for row in diagnostic['source_descriptor_sections'].values())==286
    for name,row in diagnostic['source_descriptor_sections'].items():assert row['sha256']==hashlib.sha256((ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[row['address']-0x27000:row['address']-0x27000+row['bytes']]).hexdigest()
    diagnostic_graph=json.loads((BASE/'native-battery-runtime/diagnostic-integration-verification.json').read_text())
    assert diagnostic_graph['comparisons']==2896 and diagnostic_graph['executed_diagnostic_entry_counts']=={'native':2896,'source':2896} and diagnostic_graph['compiled_diagnostic_sections']==diagnostic['source_descriptor_sections']
    assert diagnostic_graph['executed_initial_curve_entry_counts']=={'native':312,'source':312} and diagnostic_graph['executed_recovery_entry_counts']=={'native':2896,'source':2896} and diagnostic_graph['executed_cadence_entry_counts']=={'native':1113,'source':1113}
    assert diagnostic_graph['executed_configuration_entry_counts']=={side:{'r1_batcfg_word1_signed_get':2896,'r1_batcfg_byte0_get':2717,'r1_kv_class_read':5613} for side in ('native','source')}
    assert diagnostic_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_diagnostic_graph.py') and diagnostic_graph['application_sha256']==app_hash and diagnostic_graph['report_sha256']==sha(BASE/'native-battery-runtime/report.json') and diagnostic_graph['object_sha256']==sha(BASE/'native-battery-runtime/native_battery_runtime.o')
    assert diagnostic_graph['provider_reports']=={name+'/report.json':sha(BASE/name/'report.json') for name in ('native-battery-diagnostic','native-battery-initial-curve','native-battery-recovery','native-battery-cadence','native-battery-configuration','native-kv-class','runtime','native-battery-discharge','native-battery-filter','native-battery-statistics','native-battery-control')}
    assert diagnostic_graph['executed_control_entry_counts']['native']==diagnostic_graph['executed_control_entry_counts']['source'] and diagnostic_graph['executed_control_entry_counts']['source']['r1_battery_charging_progress_reset']==2316
    assert diagnostic_graph['executed_statistics_entry_counts']['native']==diagnostic_graph['executed_statistics_entry_counts']['source'] and all(n==2896 for n in diagnostic_graph['executed_statistics_entry_counts']['source'].values())
    assert not diagnostic_graph['application_linked'] and not diagnostic_graph['instruction_identity']
    initial_dir=BASE/'native-battery-initial-curve';initial=json.loads((initial_dir/'verification.json').read_text())
    assert initial['comparisons']==262538 and initial['halfword_comparisons']==262144 and initial['getter_calls']==262538
    assert initial['report_sha256']==sha(initial_dir/'report.json') and initial['object_sha256']==sha(initial_dir/'native_battery_initial_curve.o') and initial['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_initial_curve.py') and initial['application_sha256']==app_hash
    assert initial['table_bytes']==480 and initial['table_sha256']=='fa7c8e78ea948cada194d4c8b4a770390ba98de001beaac5f63a67ad9371fa19'
    assert initial['table_maxima']==[4310,4350,4350,4350] and initial['first_table_last_interval']==[4340,4310,5,0]
    assert not initial['application_linked'] and not initial['instruction_identity']
    for path,digest in initial['evidence'].items():assert sha(initial_dir/path)==digest,path
    iq=json.loads((initial_dir/'rea-4ff3c-body.json').read_text());assert iq['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and iq['normalized_result']['entrypoint']=='0x4ff3c' and iq['normalized_result']['body']['total_bytes']==190 and iq['normalized_result']['body']['span_bytes']==200
    assert iq['normalized_result']['body']['ranges']==[{'start':'0x4ff3c','end':'0x4ff73'},{'start':'0x4ff7c','end':'0x4ffb5'},{'start':'0x4ffb8','end':'0x50003'}]
    for file,address,size in [('ghidra-body.json',0x4ff3c,200),('ghidra-tables.json',0x99ef6,480)]:assert bytes(json.loads((initial_dir/file).read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    initial_graph=json.loads((BASE/'native-battery-runtime/initial-curve-integration-verification.json').read_text())
    assert initial_graph['comparisons']==2896 and initial_graph['executed_initial_curve_entry_counts']=={'native':312,'source':312} and initial_graph['executed_recovery_entry_counts']=={'native':2896,'source':2896}
    assert initial_graph['executed_cadence_entry_counts']=={'native':1113,'source':1113} and initial_graph['executed_discharge_entry_counts']=={'native':1783,'source':1783} and initial_graph['executed_filter_entry_counts']=={'native':2896,'source':2896}
    assert initial_graph['executed_configuration_entry_counts']=={side:{'r1_batcfg_word1_signed_get':2896,'r1_batcfg_byte0_get':2717,'r1_kv_class_read':5613} for side in ('native','source')}
    assert initial_graph['compiled_initial_charge_table_sha256']==initial['table_sha256'] and initial_graph['compiled_discharge_table_sha256']=='fdd47849f270e0fcba16ef4464ffcba8d8307de7154d0ce48794bf8f2a0f87ac'
    assert initial_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_initial_curve_graph.py') and initial_graph['application_sha256']==app_hash and initial_graph['report_sha256']==sha(BASE/'native-battery-runtime/report.json') and initial_graph['object_sha256']==sha(BASE/'native-battery-runtime/native_battery_runtime.o')
    assert initial_graph['provider_reports']=={name+'/report.json':sha(BASE/name/'report.json') for name in ('native-battery-initial-curve','native-battery-recovery','native-battery-cadence','native-battery-configuration','native-kv-class','runtime','native-battery-discharge','native-battery-filter','native-battery-statistics','native-battery-control')}
    assert initial_graph['executed_control_entry_counts']['native']==initial_graph['executed_control_entry_counts']['source'] and initial_graph['executed_control_entry_counts']['source']['r1_battery_charging_progress_reset']==2316
    assert initial_graph['executed_statistics_entry_counts']['native']==initial_graph['executed_statistics_entry_counts']['source'] and all(n==2896 for n in initial_graph['executed_statistics_entry_counts']['source'].values())
    assert not initial_graph['application_linked'] and not initial_graph['instruction_identity']
    recovery_dir=BASE/'native-battery-recovery';recovery=json.loads((recovery_dir/'verification.json').read_text())
    assert recovery['comparisons']==11460 and recovery['mode_sequences']==13 and recovery['full_r1_r2_r3_checked']
    assert recovery['provider_calls_per_side']=={'osKernelGetTickCount':3684,'osKernelGetTickFreq':3684,'r1_battery_charging_progress_reset':1108,'r1_battery_charging_initial_curve':1108,'r1_structured_log_mode_get':2820,'r1_structured_log_format':756,'nrf_log_frontend_std_4':588}
    assert recovery['report_sha256']==sha(recovery_dir/'report.json') and recovery['object_sha256']==sha(recovery_dir/'native_battery_recovery.o') and recovery['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_recovery.py') and recovery['application_sha256']==app_hash
    assert recovery['source_descriptor_sections']=={'ring':{'address':0x3dc88,'bytes':64,'sha256':'03e7e3f78a752339ebefb651df6db66f58a3f6313a9557c9b87f094cc0e777f8'},'sdk':{'address':0x3dcd0,'bytes':58,'sha256':'589d8ca1680984591d1ef6452bdf879cd759aa44dafa2341e6b38f6ffc7a7263'}}
    assert not recovery['application_linked'] and not recovery['instruction_identity']
    for path,digest in recovery['evidence'].items():assert sha(recovery_dir/path)==digest,path
    rq=json.loads((recovery_dir/'rea-3db70-body.json').read_text());assert rq['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and rq['normalized_result']['entrypoint']=='0x3db70' and rq['normalized_result']['body']['total_bytes']==272
    assert bytes(json.loads((recovery_dir/'ghidra-body-data.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x3db70-0x27000:0x3db70-0x27000+412]
    recovery_graph=json.loads((BASE/'native-battery-runtime/recovery-integration-verification.json').read_text())
    assert recovery_graph['comparisons']==2896 and recovery_graph['executed_recovery_entry_counts']=={'native':2896,'source':2896} and recovery_graph['recovery_initial_curve_calls']=={'native':312,'source':312}
    assert recovery_graph['executed_cadence_entry_counts']=={'native':1113,'source':1113} and recovery_graph['executed_discharge_entry_counts']=={'native':1783,'source':1783} and recovery_graph['executed_filter_entry_counts']=={'native':2896,'source':2896}
    assert recovery_graph['executed_configuration_entry_counts']=={side:{'r1_batcfg_word1_signed_get':2896,'r1_batcfg_byte0_get':2678,'r1_kv_class_read':5574} for side in ('native','source')}
    assert recovery_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_recovery_graph.py') and recovery_graph['application_sha256']==app_hash and recovery_graph['report_sha256']==sha(BASE/'native-battery-runtime/report.json') and recovery_graph['object_sha256']==sha(BASE/'native-battery-runtime/native_battery_runtime.o')
    assert recovery_graph['provider_reports']=={name+'/report.json':sha(BASE/name/'report.json') for name in ('native-battery-recovery','native-battery-cadence','native-battery-configuration','native-kv-class','runtime','native-battery-discharge','native-battery-filter','native-battery-statistics','native-battery-control')}
    assert recovery_graph['executed_control_entry_counts']['native']==recovery_graph['executed_control_entry_counts']['source'] and recovery_graph['executed_control_entry_counts']['source']['r1_battery_charging_progress_reset']==2316
    assert recovery_graph['executed_statistics_entry_counts']['native']==recovery_graph['executed_statistics_entry_counts']['source'] and all(n==2896 for n in recovery_graph['executed_statistics_entry_counts']['source'].values())
    assert not recovery_graph['application_linked'] and not recovery_graph['instruction_identity']
    cadence_dir=BASE/'native-battery-cadence';cadence=json.loads((cadence_dir/'verification.json').read_text())
    assert cadence['comparisons']==6616 and cadence['provider_calls_per_side']=={'osKernelGetTickCount':4152,'osKernelGetTickFreq':2579,'r1_batcfg_byte0_get':2579} and cadence['native_division_helper_calls']==1992
    assert cadence['semantic_arguments']==['voltage','charge_start_timestamp'] and cadence['threshold_bytes']==48 and cadence['threshold_stride']==12
    assert cadence['report_sha256']==sha(cadence_dir/'report.json') and cadence['object_sha256']==sha(cadence_dir/'native_battery_cadence.o') and cadence['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_cadence.py') and cadence['application_sha256']==app_hash
    assert not cadence['application_linked'] and not cadence['instruction_identity']
    for path,digest in cadence['evidence'].items():assert sha(cadence_dir/path)==digest,path
    cq=json.loads((cadence_dir/'rea-4fe70.json').read_text());assert cq['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and cq['normalized_result']['entrypoint']=='0x4fe70' and cq['normalized_result']['body']['total_bytes']==194
    assert bytes(json.loads((cadence_dir/'ghidra-body.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x4fe70-0x27000:0x4fe70-0x27000+204]
    cadence_graph=json.loads((BASE/'native-battery-runtime/cadence-integration-verification.json').read_text())
    assert cadence_graph['comparisons']==2896 and cadence_graph['executed_cadence_entry_counts']=={'native':1113,'source':1113}
    assert cadence_graph['executed_configuration_entry_counts']=={side:{'r1_batcfg_word1_signed_get':2896,'r1_batcfg_byte0_get':2685,'r1_kv_class_read':5581} for side in ('native','source')}
    assert cadence_graph['executed_discharge_entry_counts']=={'native':1783,'source':1783} and cadence_graph['executed_filter_entry_counts']=={'native':2896,'source':2896}
    assert cadence_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_cadence_graph.py') and cadence_graph['application_sha256']==app_hash and cadence_graph['report_sha256']==sha(BASE/'native-battery-runtime/report.json') and cadence_graph['object_sha256']==sha(BASE/'native-battery-runtime/native_battery_runtime.o')
    assert cadence_graph['provider_reports']=={name+'/report.json':sha(BASE/name/'report.json') for name in ('native-battery-cadence','native-battery-configuration','native-kv-class','runtime','native-battery-discharge','native-battery-filter','native-battery-statistics','native-battery-control')}
    assert cadence_graph['executed_statistics_entry_counts']['native']==cadence_graph['executed_statistics_entry_counts']['source'] and all(n==2896 for n in cadence_graph['executed_statistics_entry_counts']['source'].values())
    assert cadence_graph['executed_control_entry_counts']['native']==cadence_graph['executed_control_entry_counts']['source'] and not cadence_graph['application_linked'] and not cadence_graph['instruction_identity']
    cfg_dir=BASE/'native-battery-configuration'
    for file,number,per_entry,real,callbacks in [('verification.json',196752,65584,False,0),('kv-integration-verification.json',23040,7680,True,9216)]:
        cfg=json.loads((cfg_dir/file).read_text());assert cfg['comparisons']==number and cfg['counts']=={n:per_entry for n in ('r1_batcfg_byte0_get','r1_batcfg_flag1_get','r1_batcfg_word1_signed_get')}
        assert cfg['actual_kv_class_and_memory']==real and cfg['full_r3_checked'] and cfg['kv_entry_counts']=={'native':number,'source':number} and cfg['port_callback_counts']=={'native':callbacks,'source':callbacks}
        assert cfg['report_sha256']==sha(cfg_dir/'report.json') and cfg['object_sha256']==sha(cfg_dir/'native_battery_configuration.o') and cfg['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_configuration.py') and cfg['application_sha256']==app_hash
        assert not cfg['application_linked'] and not cfg['instruction_identity']
        assert cfg['provider_reports']==({path:sha(BASE/path) for path in ('native-kv-class/report.json','runtime/report.json')} if real else {})
        for path,digest in cfg['evidence'].items():assert sha(cfg_dir/path)==digest,path
    for address,size in [(0x7bb44,20),(0x7bb5c,26),(0x7bb7c,20)]:
        q=json.loads((cfg_dir/f'rea-{address:x}.json').read_text());assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and q['normalized_result']['entrypoint']==hex(address) and q['normalized_result']['body']['total_bytes']==size
        assert bytes(json.loads((cfg_dir/f'ghidra-{address:x}.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+32]
    cfg_graph=json.loads((BASE/'native-battery-runtime/configuration-integration-verification.json').read_text())
    assert cfg_graph['comparisons']==2896 and cfg_graph['executed_configuration_entry_counts']=={side:{'r1_batcfg_word1_signed_get':2896,'r1_batcfg_byte0_get':1783,'r1_kv_class_read':4679} for side in ('native','source')}
    assert cfg_graph['executed_discharge_entry_counts']=={'native':1783,'source':1783} and cfg_graph['executed_filter_entry_counts']=={'native':2896,'source':2896}
    assert cfg_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_configuration_graph.py') and cfg_graph['application_sha256']==app_hash and cfg_graph['report_sha256']==sha(BASE/'native-battery-runtime/report.json') and cfg_graph['object_sha256']==sha(BASE/'native-battery-runtime/native_battery_runtime.o')
    assert cfg_graph['compiled_discharge_table_sha256']=='fdd47849f270e0fcba16ef4464ffcba8d8307de7154d0ce48794bf8f2a0f87ac'
    assert cfg_graph['provider_reports']=={name+'/report.json':sha(BASE/name/'report.json') for name in ('native-battery-configuration','native-kv-class','runtime','native-battery-discharge','native-battery-filter','native-battery-statistics','native-battery-control')}
    assert cfg_graph['executed_statistics_entry_counts']['native']==cfg_graph['executed_statistics_entry_counts']['source'] and all(n==2896 for n in cfg_graph['executed_statistics_entry_counts']['source'].values())
    assert cfg_graph['executed_control_entry_counts']['native']==cfg_graph['executed_control_entry_counts']['source'] and not cfg_graph['application_linked'] and not cfg_graph['instruction_identity']
    discharge_dir=BASE/'native-battery-discharge';discharge=json.loads((discharge_dir/'verification.json').read_text())
    assert discharge['comparisons']==262687 and discharge['halfword_comparisons']==262144 and discharge['getter_calls']==262687
    assert discharge['report_sha256']==sha(discharge_dir/'report.json') and discharge['object_sha256']==sha(discharge_dir/'native_battery_discharge.o')
    assert discharge['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_discharge.py') and discharge['application_sha256']==app_hash
    assert discharge['table_bytes']==480 and discharge['table_sha256']=='fdd47849f270e0fcba16ef4464ffcba8d8307de7154d0ce48794bf8f2a0f87ac'
    assert discharge['table_maximum']==4310 and discharge['unreachable_override_threshold']==4340 and discharge['device_context_reads']=={'native':0,'source':0}
    assert discharge['high_override_counts']=={'native':0,'source':0} and not discharge['application_linked'] and not discharge['instruction_identity']
    for path,digest in discharge['evidence'].items():assert sha(discharge_dir/path)==digest,path
    dq=json.loads((discharge_dir/'rea-50004-body.json').read_text());assert dq['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and dq['normalized_result']['body']['total_bytes']==180 and dq['normalized_result']['body']['span_bytes']==182
    for file,address,size in [('ghidra-body.json',0x50004,196),('ghidra-tables.json',0x99d16,480)]:assert bytes(json.loads((discharge_dir/file).read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    discharge_graph=json.loads((BASE/'native-battery-runtime/discharge-integration-verification.json').read_text())
    assert discharge_graph['comparisons']==2896 and discharge_graph['executed_discharge_entry_counts']=={'native':1783,'source':1783} and discharge_graph['executed_filter_entry_counts']=={'native':2896,'source':2896}
    assert discharge_graph['compiled_discharge_table_sha256']==discharge['table_sha256'] and discharge_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_discharge_graph.py')
    assert discharge_graph['application_sha256']==app_hash and discharge_graph['report_sha256']==sha(BASE/'native-battery-runtime/report.json') and discharge_graph['object_sha256']==sha(BASE/'native-battery-runtime/native_battery_runtime.o')
    assert not discharge_graph['application_linked'] and not discharge_graph['instruction_identity']
    assert discharge_graph['provider_reports']=={name+'/report.json':sha(BASE/name/'report.json') for name in ('native-battery-discharge','native-battery-filter','native-battery-statistics','native-battery-control')}
    assert discharge_graph['executed_statistics_entry_counts']['native']==discharge_graph['executed_statistics_entry_counts']['source'] and all(n==2896 for n in discharge_graph['executed_statistics_entry_counts']['source'].values())
    assert discharge_graph['executed_control_entry_counts']['native']==discharge_graph['executed_control_entry_counts']['source']
    filter_dir=BASE/'native-battery-filter';filter_receipt=json.loads((filter_dir/'verification.json').read_text())
    assert filter_receipt['comparisons']==7104 and filter_receipt['adc_reads']==35520 and filter_receipt['sample_patterns']==148
    assert filter_receipt['busy_delays']==12432 and filter_receipt['rtos_delays']==23088 and filter_receipt['incoming_seeds']==3 and filter_receipt['live_context_mutation']
    assert filter_receipt['report_sha256']==sha(filter_dir/'report.json') and filter_receipt['object_sha256']==sha(filter_dir/'native_battery_filter.o')
    assert filter_receipt['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_filter.py') and filter_receipt['application_sha256']==app_hash
    assert not filter_receipt['application_linked'] and not filter_receipt['instruction_identity']
    for path,digest in filter_receipt['evidence'].items():assert sha(filter_dir/path)==digest,path
    fq=json.loads((filter_dir/'rea-next-91184-body.json').read_text());assert fq['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and fq['normalized_result']['body']['total_bytes']==182 and fq['normalized_result']['entrypoint']=='0x91184'
    assert bytes(json.loads((filter_dir/'ghidra-next-91184.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x91184-0x27000:0x91184-0x27000+192]
    filter_graph=json.loads((BASE/'native-battery-runtime/filter-integration-verification.json').read_text())
    assert filter_graph['comparisons']==2896 and filter_graph['real_statistics'] and filter_graph['real_control'] and filter_graph['executed_filter_entry_counts']=={'native':2896,'source':2896}
    assert filter_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_filter_graph.py') and filter_graph['report_sha256']==sha(BASE/'native-battery-runtime/report.json') and filter_graph['application_sha256']==app_hash
    assert filter_graph['object_sha256']==sha(BASE/'native-battery-runtime/native_battery_runtime.o') and not filter_graph['application_linked'] and not filter_graph['instruction_identity']
    assert filter_graph['executed_statistics_entry_counts']['native']==filter_graph['executed_statistics_entry_counts']['source'] and all(n==2896 for n in filter_graph['executed_statistics_entry_counts']['source'].values())
    assert filter_graph['executed_control_entry_counts']['native']==filter_graph['executed_control_entry_counts']['source']
    assert filter_graph['provider_reports']=={name+'/report.json':sha(BASE/name/'report.json') for name in ('native-battery-filter','native-battery-statistics','native-battery-control')}
    raw_dir=BASE/'native-yhm-status';raw_status=json.loads((raw_dir/'verification.json').read_text())
    assert raw_status['comparisons']==55296 and raw_status['counts']=={'r1_yhm_status_native':18432,'r1_yhm_charge_state_native':18432,'r1_native_charger_state_get':18432}
    assert raw_status['read_callback_counts']=={'native':36864,'source':36864} and raw_status['full_r3_return_checked'] and raw_status['all_low_bytes'] and raw_status['high_word_patterns']==3
    assert raw_status['report_sha256']==sha(raw_dir/'report.json') and raw_status['object_sha256']==sha(raw_dir/'native_yhm_status.o')
    assert raw_status['classifier_report_sha256']==sha(BASE/'native-charger-state/report.json') and raw_status['classifier_object_sha256']==sha(BASE/'native-charger-state/native_charger_state.o')
    assert raw_status['driver_sha256']==sha(ROOT/'r1/tools/verify_native_yhm_status.py') and raw_status['application_sha256']==app_hash and not raw_status['application_linked'] and not raw_status['instruction_identity']
    for path,digest in json.loads((raw_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    raw_entries={'r1_yhm_status_native':(0x3529a,112),'r1_yhm_charge_state_native':(0x35272,40),'r1_native_charger_state_get':(0x50618,4)}
    for filename,digest in raw_status['ghidra_evidence'].items():
        path=raw_dir/filename;assert sha(path)==digest;address,size=raw_entries[filename.removeprefix('ghidra-').removesuffix('.json')]
        assert bytes(json.loads(path.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    for filename,digest in raw_status['rea_evidence'].items():
        path=raw_dir/filename;assert sha(path)==digest and json.loads(path.read_text())['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
    assert raw_status['body_evidence_sha256']==sha(raw_dir/'evidence.json');raw_ev=json.loads((raw_dir/'evidence.json').read_text());assert not raw_ev['locked_ownership_changed'] and raw_ev['jump_table_bytes']==16
    assert raw_ev['ownership_row']==next(row for row in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if row['image']=='application' and row['entry']=='0x0003529a')
    assert raw_ev['body']==json.loads((raw_dir/'rea-body.json').read_text())['normalized_result']['body'] and raw_ev['body']['total_bytes']==96 and raw_ev['body']['span_bytes']==112 and raw_ev['body']['ranges']==[{'start':'0x3529a','end':'0x352b9'},{'start':'0x352ca','end':'0x35309'}]
    ys_dir=BASE/'native-yhm-state';ys=json.loads((ys_dir/'verification.json').read_text())
    assert ys['comparisons']==4 and ys['report_sha256']==sha(ys_dir/'report.json') and ys['object_sha256']==sha(ys_dir/'native_yhm_state.o')
    assert ys['driver_sha256']==sha(ROOT/'r1/tools/verify_native_yhm_state.py') and ys['application_sha256']==app_hash and not ys['application_linked'] and not ys['instruction_identity']
    for path,digest in json.loads((ys_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    assert [run['ram_poison'] for run in ys['runs']]==[0xa5,0x5a,0xff,0x3c]
    for run in ys['runs']:
        assert run['native_hex']=={'transport_context':'00'*20,'request':'00'*20}
        assert run['native_writes']==[{'pc':0x28726,'address':0x2000687c+i,'bytes':1,'value':0} for i in range(20)]+[{'pc':0x3bc6c,'address':0x20016b70+i,'bytes':4,'value':0} for i in range(0,20,4)]
    for name,address in [('transport_context',0x2000687c),('request',0x20016b70)]:assert ys['source_sections'][name]=={'address':address,'bytes':20,'sha256':hashlib.sha256(bytes(20)).hexdigest()}
    for filename,row in ys['ghidra_evidence'].items():
        path=ys_dir/filename;assert sha(path)==row['sha256'];address=row['address'];size=row['bytes']
        assert bytes(json.loads(path.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    ystage_dir=BASE/'native-yhm-stage';ystage=json.loads((ystage_dir/'verification.json').read_text())
    assert ystage['driver_sha256']==sha(ROOT/'r1/tools/check_native_yhm_stage.py') and ystage['stage_object_sha256']==sha(ystage_dir/'yhm-stage.o') and ystage['state_verification_sha256']==sha(ys_dir/'verification.json')
    assert ystage['shared_stacmd_header_sha256']==sha(ROOT/'r1/components/board/native_stacmd.h') and not ystage['new_unresolved_symbols']
    assert ystage['remaining_symbols']==json.loads((BASE/'board/report.json').read_text())['remaining_symbols'] and len(ystage['remaining_symbols'])==56
    assert not ystage['canonical_board_integrated'] and not ystage['application_linked'] and not ystage['instruction_identity']
    for path,digest in ystage['provider_reports'].items():assert sha(BASE/path)==digest,path
    for path,digest in ystage['objects'].items():assert sha(ROOT/path)==digest,path
    yfront=json.loads((BASE/'native-yhm-frontend/report.json').read_text());assert 'r1_stacmd' in yfront['units'][0]['undefined'] and 'r1_yhm_callback_context' not in yfront['units'][0]['undefined'] and yfront['inputs']['r1/components/board/native_stacmd.h']==ystage['shared_stacmd_header_sha256']
    yg=json.loads((ystage_dir/'transport-integration-verification.json').read_text())
    assert yg['comparisons']==192 and yg['counts']=={'read':96,'write':96} and yg['status_counts']=={'0':48,'1':48,'2147483655':96} and yg['completion_return_counts']=={'zero':48,'nonzero':144}
    assert yg['driver_sha256']==sha(ROOT/'r1/tools/verify_native_yhm_transport_graph.py') and yg['application_sha256']==app_hash and yg['logging_mode']==0
    assert not yg['provider_interception'] and not yg['gpio_provider_interception'] and not yg['application_linked'] and not yg['instruction_identity']
    assert yg['provider_reports']=={**gpio_graph['provider_reports'],**{'native-yhm-'+name+'/report.json':sha(BASE/('native-yhm-'+name)/'report.json') for name in ('transport','frontend','initialize','state')}}
    assert len(yg['provider_objects'])==16
    for path,digest in yg['provider_objects'].items():assert sha(BASE/path)==digest,path
    assert yg['inlined_yhm_helpers']==['r1_yhm_transport_acquire','r1_yhm_transport_release','r1_yhm_transport_complete']
    expected_yhm_counts={'r1_stacmd_read_frame_native':252,'r1_stacmd_write_frame_native':252,'r1_stacmd_drive_bit_native':4304,'r1_stacmd_write_bits_native':536,'r1_stacmd_idle_native':1008,'r1_stacmd_parity_native':336,'r1_stacmd_read_bit_native':792,'r1_stacmd_read_bit_adapter_native':536,'r1_stacmd_recovery_delay_native':3528,'r1_stacmd_read':48,'r1_stacmd_write':48,'r1_stacmd_write_retry_native':48,'r1_stacmd_bus_recovery_native':504,'r1_yhm2710_stacmd_binding_configuration':192,'r1_stock_registry_register':192,'strcmp':768,'r1_stock_dispatch_08':576,'r1_stock_dispatch_0c':384,'r1_stock_dispatch_10':96,'r1_stock_dispatch_14':96,'r1_stacmd_open':96,'r1_stacmd_close':96,'r1_twi_gpio_low':5816,'r1_twi_gpio_high':17448,'r1_twi_gpio_output':5816,'r1_twi_gpio_input':840,'r1_twi_gpio_read':218160,'r1_yhm_device_handles_initialize':384,'r1_yhm_register_read_native':96,'r1_yhm_register_write_native':96,'r1_yhm_register_read_record':96,'r1_yhm_register_write_record':96,'r1_yhm_transport_acquire':192,'r1_yhm_transport_release':192,'r1_yhm_transport_complete':192,'r1_stock_registry_find':1440,'r1_stock_dispatch_18':384}
    assert yg['executed_provider_entry_counts']['native']==expected_yhm_counts
    assert yg['executed_provider_entry_counts']['source']=={**expected_yhm_counts,**{name:0 for name in yg['inlined_yhm_helpers']}}
    assert yg['total_nops']=={'native':3545744,'source':3545744} and yg['gpio_callback_counts']=={'native':248080,'source':248080}
    for name,address in [('yhm_context',0x2000687c),('yhm_request',0x20016b70)]:assert yg['source_owned_sections'][name]=={'address':address,'bytes':20,'sha256':hashlib.sha256(bytes(20)).hexdigest()}
    status_graph=json.loads((ystage_dir/'status-integration-verification.json').read_text())
    assert status_graph['comparisons']==144 and status_graph['counts']=={'read':144,'write':0} and status_graph['full_r3_checked']
    assert status_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_yhm_status_graph.py') and status_graph['application_sha256']==app_hash
    assert status_graph['status_counts']=={'12':24,'17':6,'11':6,'10':2,'13':2,'15':8,'1':64,'0':28,'2':4}
    assert status_graph['total_nops']=={'native':1605072,'source':1605072} and status_graph['gpio_callback_counts']=={'native':122028,'source':122028}
    assert status_graph['provider_reports']=={**yg['provider_reports'],**{name+'/report.json':sha(BASE/name/'report.json') for name in ('native-yhm-status','native-charger-state')}}
    assert len(status_graph['provider_objects'])==18
    for path,digest in status_graph['provider_objects'].items():assert sha(BASE/path)==digest,path
    for field in ('provider_interception','gpio_provider_interception','application_linked','instruction_identity'):assert not status_graph[field]
    native_counts=status_graph['executed_provider_entry_counts']['native'];source_counts=status_graph['executed_provider_entry_counts']['source']
    assert native_counts['r1_yhm_status_native']==native_counts['r1_yhm_ready_native']==144 and native_counts['r1_yhm_register_read_native']==72 and native_counts['r1_stacmd_read_frame_native']==228
    assert native_counts['r1_yhm_charge_state_native']==96 and source_counts['r1_yhm_charge_state_native']==48
    assert all(native_counts[name]==source_counts[name] for name in native_counts if name not in status_graph['inlined_yhm_helpers'])
    yhm_dir=BASE/'native-yhm-frontend';yhm=json.loads((yhm_dir/'verification.json').read_text())
    assert yhm['comparisons']==832 and yhm['counts']=={'r1_yhm_ready_native':160,'r1_yhm_register_read_native':336,'r1_yhm_register_read_byte_native':336}
    assert yhm['report_sha256']==sha(yhm_dir/'report.json') and yhm['object_sha256']==sha(yhm_dir/'native_yhm_frontend.o')
    assert yhm['driver_sha256']==sha(ROOT/'r1/tools/verify_native_yhm_frontend.py') and yhm['application_sha256']==app_hash
    assert not yhm['application_linked'] and not yhm['instruction_identity']
    for path,digest in json.loads((yhm_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    for filename,digest in yhm['ghidra_evidence'].items():
        path=yhm_dir/filename;assert sha(path)==digest
        address,size={'ghidra-r1_yhm_ready_native.json':(0x3541c,28),'ghidra-r1_yhm_register_read_native.json':(0x3540c,6),'ghidra-r1_yhm_register_read_byte_native.json':(0x35412,8)}[filename]
        assert bytes(json.loads(path.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    for filename,digest in yhm['rea_evidence'].items():
        path=yhm_dir/filename;assert sha(path)==digest;q=json.loads(path.read_text())
        assert q['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
        address=int(filename.removeprefix('rea-').removesuffix('.json'),16)
        assert q['normalized_result']['entrypoint']==hex(address) and q['normalized_result']['body']['total_bytes']=={0x3541c:28,0x3540c:6,0x35412:8}[address]
    charger_dir=BASE/'native-charger-state';charger=json.loads((charger_dir/'verification.json').read_text())
    assert charger['comparisons']==4616 and charger['counts']=={'r1_yhm_charge_state_native':2308,'r1_native_charger_state_get':2308}
    assert charger['report_sha256']==sha(charger_dir/'report.json') and charger['object_sha256']==sha(charger_dir/'native_charger_state.o')
    assert charger['driver_sha256']==sha(ROOT/'r1/tools/verify_native_charger_state.py') and charger['application_sha256']==app_hash
    assert not charger['application_linked'] and not charger['instruction_identity']
    for path,digest in json.loads((charger_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    assert charger['classifier_body_bytes']==26 and charger['classifier_span_bytes']==40 and charger['table_bytes']==14
    for filename,digest in charger['ghidra_evidence'].items():
        path=charger_dir/filename;assert sha(path)==digest
        address,size={'ghidra-r1_yhm_charge_state_native.json':(0x35272,40),'ghidra-r1_native_charger_state_get.json':(0x50618,4)}[filename]
        assert bytes(json.loads(path.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[address-0x27000:address-0x27000+size]
    for filename,digest in charger['rea_evidence'].items():
        path=charger_dir/filename;assert sha(path)==digest
        assert json.loads(path.read_text())['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
    charger_body=json.loads((charger_dir/'rea-classifier-body.json').read_text())['normalized_result']['body']
    assert charger_body['ranges']==[{'start':'0x35272','end':'0x3527f'},{'start':'0x3528e','end':'0x35299'}] and charger_body['total_bytes']==26
    control_dir=BASE/'native-battery-control';control=json.loads((control_dir/'verification.json').read_text())
    assert control['comparisons']==4504 and control['counts']=={'r1_battery_charging_progress_reset':1024,'r1_battery_task_flags_set':96,'r1_shared_power_client_acquire':1680,'r1_shared_power_client_release':1680,'r1_yhm_shared_power_active':12,'r1_yhm_shared_power_inactive':12}
    assert control['application_sha256']==app_hash and control['report_sha256']==sha(control_dir/'report.json') and control['object_sha256']==sha(control_dir/'native_battery_control.o')
    assert control['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_control.py') and not control['application_linked'] and not control['instruction_identity']
    for path,digest in json.loads((control_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    for filename,digest in control['ghidra_evidence'].items():
        path=control_dir/filename;assert sha(path)==digest;n=filename.removeprefix('ghidra-').removesuffix('.json');a,z=control['entries'][n]
        assert bytes(json.loads(path.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+z]
    for filename,digest in control['rea_evidence'].items():
        path=control_dir/filename;assert sha(path)==digest;assert json.loads(path.read_text())['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
    assert control['body_evidence_sha256']==sha(control_dir/'evidence.json');ce=json.loads((control_dir/'evidence.json').read_text())
    assert ce['total_body_bytes']==48 and ce['release_entry_span_bytes']==28 and ce['inactive_command_bytes']==20 and not ce['locked_ownership_changed']
    assert ce['body_ranges']==[{'start':'0x35594','end':'0x355a7'},{'start':'0x50758','end':'0x50773'}]
    original_release=next(r for r in csv.DictReader((ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv').open()) if r['image']=='application' and r['entry']=='0x00050758');assert ce['original_row']==original_release
    control_graph=json.loads((battery_dir/'control-integration-verification.json').read_text())
    assert control_graph['real_control'] and control_graph['real_statistics'] and control_graph['comparisons']==2896
    assert control_graph['driver_sha256']==sha(ROOT/'r1/tools/verify_native_battery_runtime.py') and control_graph['report_sha256']==sha(battery_dir/'report.json') and control_graph['object_sha256']==sha(battery_dir/'native_battery_runtime.o')
    assert control_graph['provider_reports']=={'native-battery-statistics/report.json':sha(stats_dir/'report.json'),'native-battery-control/report.json':sha(control_dir/'report.json')}
    assert control_graph['executed_statistics_entry_counts']=={'native':expected_statistics,'source':expected_statistics}
    assert control_graph['executed_control_entry_counts']['native']==control_graph['executed_control_entry_counts']['source']
    assert control_graph['executed_control_entry_counts']['source']=={'r1_shared_power_client_acquire':1825,'r1_battery_charging_progress_reset':2004,'r1_shared_power_client_release':1825,'r1_battery_task_flags_set':528}
    assert control_graph['application_sha256']==app_hash and not control_graph['application_linked'] and not control_graph['instruction_identity']
    worker_dir=BASE/'native-delayed-worker';worker=json.loads((worker_dir/'verification.json').read_text())
    assert worker['comparisons']==1512 and worker['callback_invocations_per_implementation']==912 and worker['null_callback_faults']==12
    assert worker['application_sha256']==app_hash and worker['supplemental_entry']=='0x65ea8' and worker['native_size']==96 and not worker['locked_ownership_row']
    assert worker['report_sha256']==sha(worker_dir/'report.json') and worker['object_sha256']==sha(worker_dir/'native_delayed_worker.o')
    assert worker['verifier_sha256']==sha(ROOT/'r1/tools/verify_native_delayed_worker.py') and worker['ghidra_memory_sha256']==sha(worker_dir/'ghidra-memory.json')
    assert bytes(json.loads((worker_dir/'ghidra-memory.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x65ea8-0x27000:0x65f08-0x27000]
    for path,digest in json.loads((worker_dir/'report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    assert delayed_graph['worker_dispatches_per_implementation']==12
    delayed_init_dir=BASE/'native-delayed-initialize';delayed_init=json.loads((delayed_init_dir/'verification.json').read_text())
    assert delayed_init['comparisons']==3072 and delayed_init['initialization_sequences']==1536
    assert delayed_init['application_sha256']==app_hash and delayed_init['supplemental_entry']=='0x65740' and not delayed_init['locked_ownership_row']
    assert delayed_init['verifier_sha256']==sha(ROOT/'r1/tools/verify_native_delayed_initialize.py')
    assert delayed_init['source_state_compiled'] and delayed_init['source_attributes_compiled'] and not delayed_init['application_linked'] and not delayed_init['instruction_identity']
    for path,digest in delayed_init['provider_reports'].items():
        assert sha(BASE/path)==digest,path
        report=json.loads((BASE/path).read_text())
        for filename,h in report['inputs'].items():assert sha(ROOT/filename)==h,filename
    for filename,e in delayed_init['ghidra_evidence'].items():
        path=delayed_init_dir/filename;assert sha(path)==e['sha256'];a=e['address'];z=e['length']
        assert bytes(json.loads(path.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+z]
    for name in ('native-tx','native-task-lifecycle','native-tasks'):
        for path,digest in receipts[name+'/verification.json']['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert sha(BASE/'native-task-lifecycle/configuration-evidence.json')==receipts['native-task-lifecycle/verification.json']['configuration_sha256']
    task_sync=json.loads((BASE/'native-tasks/sync-integration-verification.json').read_text())
    assert task_sync['application_sha256']==app_hash and task_sync['actual_sync_bodies']
    assert sha(BASE/'native-tasks/report.json')==task_sync['report_sha256']
    assert sha(BASE/'native-tasks/native_tasks.o')==task_sync['object_sha256']
    for path,digest in task_sync['provider_reports'].items():assert sha(BASE/path)==digest,path
    watchdog=receipts['native-watchdog/verification.json'];watchdog_report=json.loads((BASE/'native-watchdog/report.json').read_text())
    assert sha(BASE/'native-watchdog/current-task-only.o')==watchdog['selected_current_task_sha256']==watchdog_report['selected_current_task_sha256']
    assert sha(BASE/'rtos-ticks/report.json')==watchdog_report['upstream_report_sha256']
    watchdog_tasks=json.loads((BASE/'native-tasks/watchdog-integration-verification.json').read_text())
    assert watchdog_tasks['application_sha256']==app_hash and watchdog_tasks['actual_watchdog_bodies'] and watchdog_tasks['actual_sync_bodies']
    assert sha(BASE/'native-tasks/report.json')==watchdog_tasks['report_sha256']
    assert sha(BASE/'native-tasks/native_tasks.o')==watchdog_tasks['object_sha256']
    for path,digest in watchdog_tasks['provider_reports'].items():assert sha(BASE/path)==digest,path
    startup_report_path=BASE/'watchdog-startup/report.json';startup_report=json.loads(startup_report_path.read_text())
    assert sha(BASE/'application-sdk/report.json')==startup_report['sdk_report_sha256']
    assert sha(BASE/'application-sdk/44_nrfx_wdt.o')==startup_report['sdk_object_sha256']
    for path,digest in startup_report['inputs'].items():assert sha(ROOT/path)==digest,path
    for name in ('watchdog-startup/manager-verification.json','watchdog-startup/device-verification.json','watchdog-startup/sdk-execution.json'):
        receipt=receipts[name];assert sha(startup_report_path)==receipt['report_sha256']
        if 'relocatable_sha256' in receipt:assert sha(BASE/'watchdog-startup/native-watchdog-startup.o')==startup_report['relocatable_sha256']==receipt['relocatable_sha256']
        if 'registry_report_sha256' in receipt:assert sha(BASE/'i2c5/report.json')==receipt['registry_report_sha256']
        if 'runtime_report_sha256' in receipt:assert sha(BASE/'runtime/report.json')==receipt['runtime_report_sha256']
        if 'watchdog_report_sha256' in receipt:assert sha(BASE/'native-watchdog/report.json')==receipt['watchdog_report_sha256']
    integer=receipts['integer-runtime/verification.json']
    assert sha(BASE/'integer-runtime/report.json')==integer['runtime_report_sha256']
    assert sha(BASE/'integer-runtime/integer-runtime.o')==integer['relocatable_sha256']
    for path,digest in json.loads((BASE/'integer-runtime/report.json').read_text())['inputs'].items():assert sha(ROOT/path)==digest,path
    integrated=json.loads((BASE/'watchdog-startup/sdk-division-integration.json').read_text())
    assert integrated['application_sha256']==app_hash and integrated['actual_sdk_executed'] and integrated['actual_integer_runtime_executed']
    assert sha(BASE/'integer-runtime/report.json')==integrated['integer_runtime_report_sha256']
    assert sha(startup_report_path)==integrated['report_sha256']
    assert sha(BASE/'watchdog-startup/native-watchdog-startup.o')==integrated['relocatable_sha256']
    assert sha(BASE/'runtime/report.json')==integrated['runtime_report_sha256']
    assert sha(BASE/'i2c5/report.json')==integrated['registry_report_sha256']
    sdk_critical=receipts['sdk-critical/verification.json'];critical_path=BASE/'sdk-critical/report.json';critical_report=json.loads(critical_path.read_text())
    assert sha(critical_path)==sdk_critical['report_sha256']
    assert sha(BASE/'sdk-critical/critical-only.o')==sdk_critical['selected_object_sha256']==critical_report['selected_object_sha256']
    assert sha(BASE/'application-sdk/report.json')==critical_report['sdk_report_sha256']
    for path,digest in critical_report['inputs'].items():assert sha(ROOT/path)==digest,path
    critical_integration=json.loads((BASE/'watchdog-startup/sdk-critical-integration.json').read_text())
    assert critical_integration['application_sha256']==app_hash and critical_integration['actual_sdk_executed'] and critical_integration['actual_integer_runtime_executed'] and critical_integration['actual_critical_regions_executed']
    for path,field in (('sdk-critical/report.json','critical_report_sha256'),('integer-runtime/report.json','integer_runtime_report_sha256'),('watchdog-startup/report.json','report_sha256'),('runtime/report.json','runtime_report_sha256'),('i2c5/report.json','registry_report_sha256')):assert sha(BASE/path)==critical_integration[field],path
    assert sha(BASE/'watchdog-startup/native-watchdog-startup.o')==critical_integration['relocatable_sha256']
    ticks_integration=json.loads((BASE/'watchdog-startup/sdk-ticks-integration.json').read_text())
    assert ticks_integration['application_sha256']==app_hash and ticks_integration['actual_sdk_executed'] and ticks_integration['actual_integer_runtime_executed'] and ticks_integration['actual_critical_regions_executed'] and ticks_integration['actual_tick_getter_executed']
    for path,field in (('rtos-ticks/report.json','ticks_report_sha256'),('sdk-critical/report.json','critical_report_sha256'),('integer-runtime/report.json','integer_runtime_report_sha256'),('watchdog-startup/report.json','report_sha256'),('runtime/report.json','runtime_report_sha256'),('i2c5/report.json','registry_report_sha256')):assert sha(BASE/path)==ticks_integration[field],path
    assert sha(BASE/'watchdog-startup/native-watchdog-startup.o')==ticks_integration['relocatable_sha256']
    assert board_test['nvic_initial_zero_bytes_compared']==12 and board_test['rtos_tick_critical_initial_zero_bytes_compared']==21
    log_report_path=BASE/'watchdog-logging/report.json';log_report=json.loads(log_report_path.read_text())
    assert sha(BASE/'watchdog-startup/report.json')==log_report['parent_report_sha256']
    assert sha(BASE/'application-sdk/report.json')==log_report['sdk_report_sha256']
    assert sha(BASE/'board-seams/report.json')==log_report['getter_report_sha256']
    assert sha(BASE/'watchdog-logging/mode-getter-only.o')==log_report['selected_getter_sha256']
    for path,digest in log_report['inputs'].items():assert sha(ROOT/path)==digest,path
    log_check=receipts['watchdog-logging/verification.json']
    assert sha(log_report_path)==log_check['report_sha256'] and log_check['native_sdk_logging_executed']
    assert sha(BASE/'watchdog-logging/native-watchdog-logging.o')==log_report['relocatable_sha256']==log_check['relocatable_sha256']
    for path,field in (('rtos-ticks/report.json','ticks_report_sha256'),('sdk-critical/report.json','critical_report_sha256'),('integer-runtime/report.json','integer_runtime_report_sha256'),('runtime/report.json','runtime_report_sha256'),('i2c5/report.json','registry_report_sha256')):assert sha(BASE/path)==log_check[field],path
    strings=receipts['watchdog-logging/strerror-verification.json']
    assert sha(log_report_path)==strings['report_sha256'] and sha(BASE/'watchdog-logging/nrf_strerror.o')==strings['object_sha256']
    assert log_check['mode_values_tested']==256 and log_check['mode_transition_sequences_tested']==512
    assert board_test['watchdog_log_descriptor_bytes_compared']==log_check['descriptor_initial_bytes_compared']==87
    output_receipt=receipts['native-output/verification.json'];output_report_path=BASE/'native-output/report.json';output_report=json.loads(output_report_path.read_text())
    assert sha(output_report_path)==output_receipt['report_sha256']
    assert sha(BASE/'native-output/native_output.o')==output_receipt['object_sha256']
    for path,digest in output_report['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in output_receipt['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert sha(BASE/'watchdog-logging/mode-getter-only.o')==output_receipt['selected_getter_sha256']
    assert board_test['output_descriptor_bytes_compared']==output_receipt['descriptor_bytes_compared']==68
    output_integration=json.loads((BASE/'native-tasks/output-integration-verification.json').read_text())
    assert output_integration['application_sha256']==app_hash and output_integration['actual_output_bodies'] and output_integration['actual_sync_bodies'] and output_integration['actual_watchdog_bodies']
    assert all(output_integration['output_execution_counts'].values())
    assert sha(BASE/'native-tasks/report.json')==output_integration['report_sha256']
    assert sha(BASE/'native-tasks/native_tasks.o')==output_integration['object_sha256']
    for path,digest in output_integration['provider_reports'].items():assert sha(BASE/path)==digest,path
    sender=receipts['native-ble-send/verification.json'];sender_report_path=BASE/'native-ble-send/report.json';sender_report=json.loads(sender_report_path.read_text())
    assert sha(sender_report_path)==sender['report_sha256'] and sha(BASE/'native-ble-send/native_ble_send.o')==sender['object_sha256']
    assert sha(BASE/'connection-handle/report.json')==sender['connection_report_sha256']
    for path,digest in sender_report['inputs'].items():assert sha(ROOT/path)==digest,path
    assert board_test['ble_semaphore_initial_zero_bytes_compared']==sender['initial_semaphore_zero_bytes_compared']==8
    assert board['unresolved_data_anchors']['r1_native_bae8_service']=='0x20006504'
    sender_output=json.loads((BASE/'native-output/sender-integration-verification.json').read_text())
    assert sender_output['application_sha256']==app_hash and sender_output['actual_sender_executed'] and all(sender_output['sender_execution_counts'].values())
    assert sha(output_report_path)==sender_output['report_sha256'] and sha(BASE/'native-output/native_output.o')==sender_output['object_sha256']
    for path,digest in sender_output['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert sha(BASE/'watchdog-logging/mode-getter-only.o')==sender_output['selected_getter_sha256']
    sender_tasks=json.loads((BASE/'native-tasks/sender-integration-verification.json').read_text())
    assert sender_tasks['application_sha256']==app_hash and sender_tasks['actual_sender_executed'] and sender_tasks['actual_output_bodies'] and sender_tasks['actual_sync_bodies'] and sender_tasks['actual_watchdog_bodies']
    assert all(sender_tasks['output_execution_counts'].values())
    assert sha(BASE/'native-tasks/report.json')==sender_tasks['report_sha256'] and sha(BASE/'native-tasks/native_tasks.o')==sender_tasks['object_sha256']
    for path,digest in sender_tasks['provider_reports'].items():assert sha(BASE/path)==digest,path
    bae8=receipts['native-bae8-send/verification.json'];bae8_path=BASE/'native-bae8-send/report.json';bae8_report=json.loads(bae8_path.read_text())
    assert sha(bae8_path)==bae8['report_sha256'] and sha(BASE/'native-bae8-send/native_bae8_send.o')==bae8['object_sha256']
    assert sha(BASE/'application-sdk/report.json')==bae8_report['sdk_report_sha256']
    for path,digest in bae8_report['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in bae8['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert sha(BASE/'watchdog-logging/mode-getter-only.o')==bae8['selected_getter_sha256']
    assert board_test['bae8_descriptor_bytes_compared']==bae8['descriptor_bytes_compared']==806
    assert bae8['svc174_calls']>0
    bae8_output=json.loads((BASE/'native-output/bae8-integration-verification.json').read_text())
    assert bae8_output['application_sha256']==app_hash and bae8_output['actual_sender_executed'] and bae8_output['actual_bae8_executed'] and bae8_output['svc174_calls']>0
    assert sha(output_report_path)==bae8_output['report_sha256'] and sha(BASE/'native-output/native_output.o')==bae8_output['object_sha256']
    for path,digest in bae8_output['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert sha(BASE/'watchdog-logging/mode-getter-only.o')==bae8_output['selected_getter_sha256']
    context=receipts['sdk-link-context/verification.json'];context_path=BASE/'sdk-link-context/report.json';context_report=json.loads(context_path.read_text())
    assert sha(context_path)==context['report_sha256'] and sha(BASE/'sdk-link-context/blcm_link_ctx_get.o')==context['object_sha256']
    assert sha(BASE/'application-sdk/report.json')==context_report['sdk_report_sha256']
    for path,digest in context_report['inputs'].items():assert sha(ROOT/path)==digest,path
    assert context_report['provider_aliases']=={'r1_native_bae8_context_get':'blcm_link_ctx_get'} and board['provider_aliases']=={**context_report['provider_aliases'],'xTaskCreate':'r1_native_task_create','xTaskCreateStatic':'r1_native_task_create_static','r1_rtc_driver_error':'r1_adc_error'}
    context_bae8=json.loads((BASE/'native-bae8-send/context-integration-verification.json').read_text())
    assert context_bae8['application_sha256']==app_hash and context_bae8['actual_link_context_executed'] and context_bae8['svc174_calls']>0
    assert sha(bae8_path)==context_bae8['report_sha256'] and sha(BASE/'native-bae8-send/native_bae8_send.o')==context_bae8['object_sha256']
    for path,digest in context_bae8['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert sha(BASE/'watchdog-logging/mode-getter-only.o')==context_bae8['selected_getter_sha256']
    context_output=json.loads((BASE/'native-output/context-integration-verification.json').read_text())
    assert context_output['application_sha256']==app_hash and context_output['actual_link_context_executed'] and context_output['actual_sender_executed'] and context_output['actual_bae8_executed'] and context_output['svc174_calls']>0
    assert sha(output_report_path)==context_output['report_sha256'] and sha(BASE/'native-output/native_output.o')==context_output['object_sha256']
    for path,digest in context_output['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert sha(BASE/'watchdog-logging/mode-getter-only.o')==context_output['selected_getter_sha256']
    index=receipts['sdk-connection-index/verification.json'];index_path=BASE/'sdk-connection-index/report.json';index_report=json.loads(index_path.read_text())
    assert sha(index_path)==index['report_sha256'] and sha(BASE/'sdk-connection-index/connection-index-only.o')==index['selected_object_sha256']==index_report['selected_object_sha256']
    assert sha(BASE/'application-sdk/report.json')==index_report['sdk_report_sha256']
    for path,digest in index_report['inputs'].items():assert sha(ROOT/path)==digest,path
    assert sha(BASE/'runtime/report.json')==index['memory_report_sha256']
    assert index['authenticated_native_reset_bytes']==index_report['authenticated_native_reset_bytes']==124
    assert board_test['connection_state_candidate_initial_zero_bytes_compared']==index['candidate_state_initial_zero_bytes_compared']==124
    index_lookup=json.loads((BASE/'sdk-link-context/index-integration-verification.json').read_text())
    assert index_lookup['application_sha256']==app_hash and index_lookup['actual_connection_index_executed']
    assert sha(index_path)==index_lookup['index_report_sha256'] and sha(context_path)==index_lookup['report_sha256'] and sha(BASE/'sdk-link-context/blcm_link_ctx_get.o')==index_lookup['object_sha256']
    for parent,object_name in (('native-bae8-send','native_bae8_send.o'),('native-output','native_output.o')):
        check=json.loads((BASE/parent/'index-integration-verification.json').read_text())
        assert check['application_sha256']==app_hash and check['actual_connection_index_executed'] and check['actual_link_context_executed'] and check['svc174_calls']>0
        assert sha(BASE/parent/'report.json')==check['report_sha256'] and sha(BASE/parent/object_name)==check['object_sha256']
        for path,digest in check['provider_reports'].items():assert sha(BASE/path)==digest,path
        assert sha(BASE/'watchdog-logging/mode-getter-only.o')==check['selected_getter_sha256']
    events=receipts['sdk-connection-events/verification.json'];events_path=BASE/'sdk-connection-events/report.json';events_report=json.loads(events_path.read_text())
    assert sha(events_path)==events['report_sha256'] and sha(BASE/'sdk-connection-events/connection-events.o')==events['selected_object_sha256']==events_report['selected_object_sha256']
    assert sha(BASE/'application-sdk/report.json')==events_report['sdk_report_sha256'] and sha(BASE/'runtime/report.json')==events['memory_report_sha256']
    for path,digest in events_report['inputs'].items():assert sha(ROOT/path)==digest,path
    assert events['injected_failed_store_exclusives']>0 and board_test['registry_observer_record_bytes_pointer_normalized']==8
    events_index=json.loads((BASE/'sdk-connection-events/index-verification.json').read_text())
    assert events_index['application_sha256']==app_hash and events_index['events_provider'] and sha(events_path)==events_index['report_sha256']
    assert sha(BASE/'sdk-connection-events/connection-events.o')==events_index['selected_object_sha256']
    assert sha(BASE/'runtime/report.json')==events_index['memory_report_sha256']
    for parent,object_name in (('native-bae8-send','native_bae8_send.o'),('native-output','native_output.o')):
        check=json.loads((BASE/parent/'events-integration-verification.json').read_text())
        assert check['application_sha256']==app_hash and check['events_provider'] and check['actual_registry_events_executed'] and check['actual_connection_index_executed'] and check['svc174_calls']>0
        assert sha(BASE/parent/'report.json')==check['report_sha256'] and sha(BASE/parent/object_name)==check['object_sha256']
        for path,digest in check['provider_reports'].items():assert sha(BASE/path)==digest,path
        assert sha(BASE/'watchdog-logging/mode-getter-only.o')==check['selected_getter_sha256']
    dispatch_path=BASE/'sdk-ble-dispatch/report.json';dispatch=json.loads(dispatch_path.read_text())
    for receipt_name in ('verification.json','iterator-verification.json','registry-integration-verification.json'):
        check=json.loads((dispatch_path.parent/receipt_name).read_text())
        assert check['application_sha256']==app_hash and check['report_sha256']==sha(dispatch_path)
        assert check['comparisons']>0
        if 'selected_object_sha256' in check:
            assert check['selected_object_sha256']==dispatch['selected_object_sha256']==sha(dispatch_path.parent/'ble-dispatch.o')
        else:assert check['object_sha256']==sha(dispatch_path.parent/'nrf_section_iter.o')
        for path,digest in check.get('provider_reports',{}).items():assert sha(BASE/path)==digest,path
        if receipt_name=='registry-integration-verification.json':assert check['actual_registry_handler'] and check['observer_calls']>0
    for path,digest in dispatch['inputs'].items():assert sha(ROOT/path)==digest,path
    assert board_test['ble_observer_table_bytes_pointer_normalized']==96
    assert board_test['ble_observer_range_set_bytes_compared']==44 and board_test['ble_stack_initial_zero_bytes_compared']==1
    qwr_path=BASE/'sdk-qwr/report.json';qwr=json.loads(qwr_path.read_text());qwr_test=receipts['sdk-qwr/verification.json']
    assert qwr_test['report_sha256']==sha(qwr_path) and qwr_test['selected_object_sha256']==qwr['selected_object_sha256']==sha(qwr_path.parent/'qwr.o')
    assert sha(BASE/'application-sdk/report.json')==qwr['sdk_report_sha256']
    for path,digest in qwr['inputs'].items():assert sha(ROOT/path)==digest,path
    assert qwr_test['invalid_bool_byte_2_diverges'] and qwr_test['context_initial_zero_bytes_compared']==36 and qwr_test['svc_calls']>0
    assert board_test['qwr_context_initial_zero_bytes_compared']==36
    qwr_integration=json.loads((BASE/'sdk-ble-dispatch/qwr-integration-verification.json').read_text())
    assert qwr_integration['application_sha256']==app_hash and qwr_integration['report_sha256']==sha(dispatch_path)
    assert qwr_integration['selected_object_sha256']==dispatch['selected_object_sha256'] and qwr_integration['actual_qwr_handler'] and qwr_integration['actual_registry_handler'] and qwr_integration['qwr_svc_calls']>0
    for path,digest in qwr_integration['provider_reports'].items():assert sha(BASE/path)==digest,path
    gatt_path=BASE/'sdk-gatt/report.json';gatt=json.loads(gatt_path.read_text());gatt_test=receipts['sdk-gatt/verification.json']
    assert gatt_test['report_sha256']==sha(gatt_path) and gatt_test['selected_object_sha256']==gatt['selected_object_sha256']==sha(gatt_path.parent/'gatt-init.o')
    assert sha(BASE/'application-sdk/report.json')==gatt['sdk_report_sha256']
    for path,digest in gatt['inputs'].items():assert sha(ROOT/path)==digest,path
    assert gatt_test['context_initial_zero_bytes_compared']==36 and board_test['gatt_context_initial_zero_bytes_compared']==36
    assert not gatt_test['observer_contract_proven'] and not gatt['observer_selected'] and not gatt['role_split_proven']
    assert sum(not row['equivalent'] for row in gatt_test['observer_counterexamples'])==4
    native_gatt_path=BASE/'native-gatt/report.json';native_gatt=json.loads(native_gatt_path.read_text());native_gatt_test=receipts['native-gatt/verification.json']
    assert native_gatt_test['report_sha256']==sha(native_gatt_path) and native_gatt_test['object_sha256']==native_gatt['units'][0]['object_sha256']==sha(native_gatt_path.parent/'native_gatt_observer.o')
    assert sha(BASE/'application-sdk/report.json')==native_gatt['sdk_report_sha256']
    for path,digest in native_gatt['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in native_gatt_test['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert native_gatt_test['selected_getter_sha256']==sha(BASE/'watchdog-logging/mode-getter-only.o')
    assert native_gatt_test['strerror_object_sha256']==sha(BASE/'watchdog-logging/nrf_strerror.o')
    assert native_gatt_test['svc_calls']>0 and native_gatt_test['descriptor_bytes_compared']==board_test['gatt_log_descriptor_bytes_compared']
    gatt_dispatch=json.loads((BASE/'sdk-ble-dispatch/gatt-integration-verification.json').read_text())
    assert gatt_dispatch['application_sha256']==app_hash and gatt_dispatch['report_sha256']==sha(dispatch_path) and gatt_dispatch['selected_object_sha256']==dispatch['selected_object_sha256']
    assert gatt_dispatch['actual_gatt_handler'] and gatt_dispatch['actual_qwr_handler'] and gatt_dispatch['actual_registry_handler'] and gatt_dispatch['gatt_svc_calls']>0
    for path,digest in gatt_dispatch['provider_reports'].items():assert sha(BASE/path)==digest,path
    advertising_path=BASE/'sdk-advertising/report.json';advertising=json.loads(advertising_path.read_text());advertising_test=receipts['sdk-advertising/verification.json']
    assert advertising_test['report_sha256']==sha(advertising_path) and advertising_test['selected_object_sha256']==advertising['selected_object_sha256']==sha(advertising_path.parent/'advertising.o')
    assert sha(BASE/'application-sdk/report.json')==advertising['sdk_report_sha256'] and sha(BASE/'runtime/report.json')==advertising_test['memory_report_sha256']
    for path,digest in advertising['inputs'].items():assert sha(ROOT/path)==digest,path
    assert advertising_test['svc_calls']>0 and advertising_test['compatible_context_initial_zero_bytes_compared']==board_test['advertising_compatible_context_zero_bytes_compared']==2152
    assert not advertising['initialization_provider_selected']
    advertising_dispatch=json.loads((BASE/'sdk-ble-dispatch/advertising-integration-verification.json').read_text())
    assert advertising_dispatch['application_sha256']==app_hash and advertising_dispatch['report_sha256']==sha(dispatch_path) and advertising_dispatch['selected_object_sha256']==dispatch['selected_object_sha256']
    assert advertising_dispatch['actual_advertising_handler'] and advertising_dispatch['actual_gatt_handler'] and advertising_dispatch['actual_qwr_handler'] and advertising_dispatch['actual_registry_handler'] and advertising_dispatch['advertising_svc_calls']>0
    for path,digest in advertising_dispatch['provider_reports'].items():assert sha(BASE/path)==digest,path
    advertising_init_path=BASE/'sdk-advertising-init/report.json';advertising_init=json.loads(advertising_init_path.read_text());advertising_init_test=receipts['sdk-advertising-init/verification.json']
    assert advertising_init_test['report_sha256']==sha(advertising_init_path) and advertising_init_test['selected_object_sha256']==advertising_init['selected_object_sha256']==sha(advertising_init_path.parent/'advertising.o')
    assert sha(BASE/'application-sdk/report.json')==advertising_init['sdk_report_sha256'] and sha(BASE/'runtime/report.json')==advertising_init_test['memory_report_sha256']
    for path,digest in advertising_init['inputs'].items():assert sha(ROOT/path)==digest,path
    assert advertising_init['initialization_provider_selected'] and advertising_init_test['svc_calls']>0 and advertising_init_test['native_capacity_overrun_cases']>0
    advertising_legacy=json.loads((advertising_init_path.parent/'legacy-verification.json').read_text())
    assert advertising_legacy['application_sha256']==app_hash and advertising_legacy['report_sha256']==sha(advertising_init_path) and advertising_legacy['selected_object_sha256']==advertising_init['selected_object_sha256'] and advertising_legacy['memory_report_sha256']==sha(BASE/'runtime/report.json')
    advertising_init_dispatch=json.loads((BASE/'sdk-ble-dispatch/advertising-init-integration-verification.json').read_text())
    assert advertising_init_dispatch['application_sha256']==app_hash and advertising_init_dispatch['report_sha256']==sha(dispatch_path) and advertising_init_dispatch['selected_object_sha256']==dispatch['selected_object_sha256']
    assert advertising_init_dispatch['actual_advertising_init'] and advertising_init_dispatch['advertising_init_calls']==2*advertising_init_dispatch['comparisons']
    for path,digest in advertising_init_dispatch['provider_reports'].items():assert sha(BASE/path)==digest,path
    advertising_configuration_path=BASE/'native-advertising-configuration/report.json';advertising_configuration=json.loads(advertising_configuration_path.read_text());advertising_configuration_test=receipts['native-advertising-configuration/verification.json']
    assert advertising_configuration_test['report_sha256']==sha(advertising_configuration_path) and advertising_configuration_test['object_sha256']==advertising_configuration['units'][0]['object_sha256']==sha(advertising_configuration_path.parent/'native_advertising_configuration.o')
    assert sha(BASE/'application-sdk/report.json')==advertising_configuration['sdk_report_sha256']
    for path,digest in advertising_configuration['inputs'].items():assert sha(ROOT/path)==digest,path
    for path,digest in advertising_configuration_test['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert advertising_configuration_test['selected_getter_sha256']==sha(BASE/'watchdog-logging/mode-getter-only.o')
    assert advertising_configuration_test['actual_product_config_start_callback_cases']==72
    assert advertising_configuration_test['svc_calls']>0 and advertising_configuration_test['descriptor_and_interval_bytes_compared']==board_test['advertising_product_descriptor_bytes_compared']
    assert advertising_configuration_test['product_payload_initial_zero_bytes_compared']==board_test['advertising_product_payload_zero_bytes_compared']==21
    kv_scans_path=BASE/'native-kv-scans/report.json';kv_scans=json.loads(kv_scans_path.read_text());kv_scans_test=receipts['native-kv-scans/verification.json'];kv_scans_evidence=json.loads((kv_scans_path.parent/'evidence.json').read_text())
    assert kv_scans_test['application_sha256']==app_hash and kv_scans_test['report_sha256']==sha(kv_scans_path) and kv_scans_test['object_sha256']==kv_scans['units'][0]['object_sha256']==sha(kv_scans_path.parent/'native_kv_scans.o')
    assert kv_scans_test['memory_report_sha256']==sha(BASE/'runtime/report.json') and kv_scans['sdk_report_sha256']==sha(BASE/'application-sdk/report.json') and board_test['kv_scan_descriptor_bytes_compared']>0
    for path,digest in kv_scans['inputs'].items():assert sha(ROOT/path)==digest,path
    assert kv_scans_evidence['application_sha256']==app_hash and kv_scans_evidence['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for row in kv_scans_evidence['functions']:
        gh=kv_scans_path.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'] and sha(kv_scans_path.parent/row['pseudocode_file'])==row['pseudocode_sha256']
        a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['body_bytes']]
    kv_scan_init=json.loads((BASE/'native-kv-initialize/scan-integration-verification.json').read_text())
    assert kv_scan_init['application_sha256']==app_hash and kv_scan_init['report_sha256']==sha(BASE/'native-kv-initialize/report.json') and kv_scan_init['actual_native_scans_executed'] and kv_scan_init['scan_report_sha256']==sha(kv_scans_path) and kv_scan_init['memory_report_sha256']==sha(BASE/'runtime/report.json')
    ov=BASE/'native-stack-overflow/report.json';ovr=json.loads(ov.read_text());ovv=receipts['native-stack-overflow/verification.json'];assert ovv['application_sha256']==app_hash and ovv['report_sha256']==sha(ov) and ovv['driver_sha256']==sha(ROOT/'r1/tools/verify_native_stack_overflow.py') and ovv['comparisons']==12360 and ovv['terminal_loop_comparisons']==12336 and ovv['busy_drain_boundaries']==24 and ovv['string_bytes']==62 and ovr['selected_object_sha256']==sha(ov.parent/'stack-overflow.o') and ovr['rtos_report_sha256']==sha(BASE/'rtos/report.json')
    for p,d in ovr['inputs'].items():assert sha(ROOT/p)==d,p
    assert ovr['source_configuration']['ring_severity']=='0x0c400000' and ovr['source_configuration']['nordic_severity']=='0x001c0003' and ovr['source_configuration']['nordic_module']==28 and ovr['remaining_symbols']==['nrf_log_frontend_dequeue','nrf_log_frontend_std_1','r1_structured_log_format','r1_structured_log_mode_get']
    ove=json.loads((ov.parent/'evidence.json').read_text());assert ove['application_sha256']==app_hash and ove['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and ove['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and ove['native_contract']['terminal_loop']=='0x95c42' and not ove['native_contract']['explicit_basepri_change'] and ove['native_contract']['nordic_module']==(int(ove['native_contract']['module_record'],16)-int(ove['native_contract']['module_base'],16))//ove['native_contract']['module_stride']==28
    for row in ove['spans']:
        gh=ov.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']];assert sha(ov.parent/row['thumb_file'])==row['thumb_sha256']
    inventory=json.loads((ROOT/ove['rea_inventory']).read_text());assert sha(ROOT/ove['rea_inventory'])==ove['rea_inventory_sha256'] and ove['rea_registered_rows']==[r for r in inventory['normalized_result'] if int(r['address'],16)==0x95bfc]
    ovg=json.loads((BASE/'board/stack-overflow-verification.json').read_text());assert ovg['application_sha256']==app_hash and ovg['board_report_sha256']==sha(BASE/'board/report.json') and ovg['verification_driver_sha256']==sha(ROOT/'r1/tools/verify_native_board.py') and ovg['overflow_driver_sha256']==sha(ROOT/'r1/tools/verify_stack_overflow_graph.py') and ovg['overflow_report_sha256']==sha(ov) and ovg['comparisons']==256 and ovg['accepted_rtt_bytes_per_implementation']==8064 and ovg['dequeue_calls_per_implementation']==320 and not ovg['provider_interception']
    cp=BASE/'rtos-context-port/report.json';cpr=json.loads(cp.read_text());cpv=receipts['rtos-context-port/verification.json'];assert cpv['application_sha256']==app_hash and cpv['report_sha256']==sha(cp) and cpv['driver_sha256']==sha(ROOT/'r1/tools/verify_rtos_context_port.py') and cpv['comparisons']==2232 and cpv['fault_comparisons']==72 and cpv['overflow_hook_boundaries']==480 and cpv['switch_context_fixture_calls_per_implementation']==48 and cpv['comparisons_by_function']=={'vPortStartFirstTask':12,'SVC_Handler':12,'PendSV_Handler':48,'vTaskSwitchContext':2160} and cpv['source_owned_vector_words']==3 and not cpv['full_vector_table_proven']
    assert cpr['selected_object_sha256']==sha(cp.parent/'context-port.o') and cpr['rtos_report_sha256']==sha(BASE/'rtos/report.json') and cpr['sdk_source_sha256']==sha(ROOT/cpr['sdk_source'])=='907413ddea63fa5fb0e4ff463288893060fb7909a3ae8e87134e0e81efb0fb82' and cpr['sdk_zip_sha256']==sha(ROOT/'vendor-cache/r1/sdk.zip')=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061' and not cpr['full_vector_table_proven']
    for p,d in cpr['inputs'].items():assert sha(ROOT/p)==d,p
    raw=(ROOT/cpr['upstream_source']).read_bytes();assert sha(ROOT/cpr['upstream_source'])==cpr['upstream_sha256'];license_part=raw[:cpr['license_bytes']];assert hashlib.sha256(license_part).hexdigest()==cpr['license_sha256'];parts={}
    for row in cpr['source_slices']:
        part=raw[row['start']:row['end']];assert hashlib.sha256(part).hexdigest()==row['sha256'];parts[row['name']]=part
    assert (cp.parent/'selection.c').read_bytes()==license_part+b'\n#include "context_contract.h"\n'+b'\n'.join(parts[n] for n in ('taskSELECT_HIGHEST_PRIORITY_TASK','vTaskSwitchContext'))
    cpe=json.loads((cp.parent/'evidence.json').read_text());assert cpe['application_sha256']==app_hash and cpe['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and cpe['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and cpe['kernel_pin']=='def7d2df2b0506d3d249334974f51e427c17a41c' and cpe['source_owned_vector_words']==3 and not cpe['full_vector_table_proven'] and cpe['native_vector_values']=={'0x27000':'0x2003beb8','0x2702c':'0x27219','0x27038':'0x2725d'}
    for row in cpe['spans']:
        gh=cp.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']];assert sha(cp.parent/row['thumb_file'])==row['thumb_sha256']
    inventory=json.loads((ROOT/cpe['rea_inventory']).read_text());assert sha(ROOT/cpe['rea_inventory'])==cpe['rea_inventory_sha256'];assert cpe['rea_registered_rows']==[r for r in inventory['normalized_result'] if int(r['address'],16) in {0x27218,0x27238,0x2725c,0x965ac}]
    cpg=json.loads((BASE/'board/context-start-verification.json').read_text());assert cpg['application_sha256']==app_hash and cpg['board_report_sha256']==sha(BASE/'board/report.json') and cpg['verification_driver_sha256']==sha(ROOT/'r1/tools/verify_native_board.py') and cpg['context_driver_sha256']==sha(ROOT/'r1/tools/verify_context_start_graph.py') and cpg['context_report_sha256']==sha(cp) and cpg['startup_report_sha256']==sha(BASE/'rtos-scheduler-start/report.json') and cpg['port_report_sha256']==sha(BASE/'rtos-port-start/report.json') and cpg['comparisons']==224 and cpg['workflows']==32 and not cpg['provider_interception'] and not cpg['exception_return_executed'] and cpg['svc_dispatch_fixture_per_workflow']==1 and cpg['pendsv_calls_per_workflow']==4
    ps=BASE/'rtos-port-start/report.json';psr=json.loads(ps.read_text());psv=receipts['rtos-port-start/verification.json'];assert psv['application_sha256']==app_hash and psv['report_sha256']==sha(ps) and psv['driver_sha256']==sha(ROOT/'r1/tools/verify_rtos_port_start.py') and psv['comparisons']==5220 and psv['fault_comparisons']==4536 and psv['bounded_first_task_cases']==648 and psv['comparisons_by_function']=={'xPortStartScheduler':5184,'vPortSetupTimerInterrupt':36}
    port_configuration={'raw_max_syscall_priority':2,'kernel_priority':15,'rtc_prescaler':31,'rtc_irq':17,'cpuid':'0x410fc241'};assert psr['source_configuration']==port_configuration and psr['selected_object_sha256']==sha(ps.parent/'port-start.o') and psr['rtos_report_sha256']==sha(BASE/'rtos/report.json') and psr['remaining_symbols']==['nrf_drv_clock_lfclk_request','vPortStartFirstTask']
    for p,d in psr['inputs'].items():assert sha(ROOT/p)==d,p
    for origin in psr['origins']:
        raw=(ROOT/origin['source']).read_bytes();assert sha(ROOT/origin['source'])==origin['sha256'];license_part=raw[:origin['license_bytes']];assert hashlib.sha256(license_part).hexdigest()==origin['license_sha256'];parts={}
        for row in origin['slices']:
            part=raw[row['start']:row['end']];assert hashlib.sha256(part).hexdigest()==row['sha256'];parts[row['name']]=part
        names=('portTOP_BIT_OF_BYTE','portMAX_8_BIT_VALUE','portCORTEX_M4_r0p1_ID','vPortEnableVFP','prvTaskExitError','xPortStartScheduler') if origin['target']=='port' else ('vPortSetupTimerInterrupt',)
        assert (ps.parent/(origin['target']+'.c')).read_bytes()==license_part+b'\n#include "port_start_contract.h"\n'+b'\n'.join(parts[n] for n in names)
    pse=json.loads((ps.parent/'evidence.json').read_text());assert pse['application_sha256']==app_hash and pse['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and pse['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and pse['sdk_zip_sha256']==sha(ROOT/'vendor-cache/r1/sdk.zip')=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061' and pse['source_configuration']==port_configuration and pse['private_state']=={'ucMaxSysCallPriority':'0x20007810','uxCriticalNesting':'0x20007814','ulMaxPRIGROUPValue':'0x20007818'}
    for row in pse['spans']:
        gh=ps.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']];assert sha(ps.parent/row['thumb_file'])==row['thumb_sha256']
    inventory=json.loads((ROOT/pse['rea_inventory']).read_text());assert sha(ROOT/pse['rea_inventory'])==pse['rea_inventory_sha256'];addresses={int(r['entry'],16) for r in pse['spans']};assert pse['rea_registered_rows']==[r for r in inventory['normalized_result'] if int(r['address'],16) in addresses]
    psg=json.loads((BASE/'board/port-start-verification.json').read_text());assert psg['application_sha256']==app_hash and psg['board_report_sha256']==sha(BASE/'board/report.json') and psg['verification_driver_sha256']==sha(ROOT/'r1/tools/verify_native_board.py') and psg['startup_driver_sha256']==sha(ROOT/'r1/tools/verify_scheduler_start_graph.py') and psg['startup_report_sha256']==sha(BASE/'rtos-scheduler-start/report.json') and psg['port_report_sha256']==sha(ps) and psg['application_configuration_sha256']==sha(BASE/'native-task-lifecycle/configuration-evidence.json') and psg['comparisons']==24 and psg['workflows']==16 and psg['real_port'] and not psg['provider_interception'] and psg['unexecuted_providers']==['vPortStartFirstTask','r1_native_timer_task']
    ss=BASE/'rtos-scheduler-start/report.json';ssr=json.loads(ss.read_text());ssv=receipts['rtos-scheduler-start/verification.json'];assert ssv['application_sha256']==app_hash and ssv['report_sha256']==sha(ss) and ssv['driver_sha256']==sha(ROOT/'r1/tools/verify_rtos_scheduler_start.py') and ssv['comparisons']==312 and ssv['fault_comparisons']==102 and ssv['comparisons_by_function']=={'vTaskStartScheduler':96,'xTimerCreateTimerTask':96,'r1_native_timer_infrastructure':96,'vApplicationGetIdleTaskMemory':12,'vApplicationGetTimerTaskMemory':12} and ssr['selected_object_sha256']==sha(ss.parent/'scheduler-start.o') and ssr['rtos_report_sha256']==sha(BASE/'rtos/report.json')
    startup_configuration={'static_tcb_bytes':112,'stack_words':256,'timer_priority':53,'timer_queue_length':32,'timer_message_bytes':16,'queue_registry_size':0};assert ssr['source_configuration']==startup_configuration
    for p,d in ssr['inputs'].items():assert sha(ROOT/p)==d,p
    for origin in ssr['origins']:
        raw=(ROOT/origin['source']).read_bytes();assert sha(ROOT/origin['source'])==origin['sha256'];license_part=raw[:origin['license_bytes']];assert hashlib.sha256(license_part).hexdigest()==origin['license_sha256'];parts=[]
        for row in origin['slices']:
            part=raw[row['start']:row['end']];assert hashlib.sha256(part).hexdigest()==row['sha256'];parts.append(part)
        if origin['target']=='scheduler':header='startup_task_contract.h';extra=b'\nTaskHandle_t xIdleTaskHandle;\n';assert [r['name'] for r in origin['slices']]==['vTaskStartScheduler']
        else:header='startup_timer_contract.h';extra=b'\nvoid r1_native_timer_infrastructure(void) __attribute__((alias("prvCheckForValidListAndQueue")));\n_Static_assert(sizeof(DaemonTaskMessage_t)==16,"native timer queue message");\n';assert [r['name'] for r in origin['slices']]==['timer_message_types','prvCheckForValidListAndQueue','xTimerCreateTimerTask']
        assert (ss.parent/(origin['target']+'.c')).read_bytes()==license_part+('\n#include "'+header+'"\n').encode()+b'\n'.join(parts)+extra
    sse=json.loads((ss.parent/'evidence.json').read_text());assert sse['application_sha256']==app_hash and sse['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and sse['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and sse['kernel_pin']=='def7d2df2b0506d3d249334974f51e427c17a41c' and sse['source_configuration']==startup_configuration
    for row in sse['spans']:
        gh=ss.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']];assert sha(ss.parent/row['thumb_file'])==row['thumb_sha256']
    inventory=json.loads((ROOT/sse['rea_inventory']).read_text());assert sha(ROOT/sse['rea_inventory'])==sse['rea_inventory_sha256'];addresses={int(r['entry'],16) for r in sse['spans']};assert sse['rea_registered_rows']==[r for r in inventory['normalized_result'] if int(r['address'],16) in addresses]
    ssg=json.loads((BASE/'board/scheduler-start-verification.json').read_text());assert ssg['application_sha256']==app_hash and ssg['board_report_sha256']==sha(BASE/'board/report.json') and ssg['verification_driver_sha256']==sha(ROOT/'r1/tools/verify_native_board.py') and ssg['startup_driver_sha256']==sha(ROOT/'r1/tools/verify_scheduler_start_graph.py') and ssg['startup_report_sha256']==sha(ss) and ssg['application_configuration_sha256']==sha(BASE/'native-task-lifecycle/configuration-evidence.json') and ssg['comparisons']==24 and ssg['workflows']==16 and not ssg['provider_interception'] and ssg['unexecuted_providers']==['xPortStartScheduler','r1_native_timer_task']
    sk=BASE/'rtos-sleep-kernel/report.json';skr=json.loads(sk.read_text());skv=receipts['rtos-sleep-kernel/verification.json'];assert skv['application_sha256']==app_hash and skv['report_sha256']==sha(sk) and skv['driver_sha256']==sha(ROOT/'r1/tools/verify_rtos_sleep_kernel.py') and skv['comparisons']==4048 and skv['assertion_comparisons']==1588 and skv['comparisons_by_function']=={'eTaskConfirmSleepModeStatus':1024,'vTaskStepTick':3024} and skv['critical_fixture_calls_per_implementation']==256
    assert skr['selected_object_sha256']==sha(sk.parent/'sleep-kernel.o') and skr['rtos_report_sha256']==sha(BASE/'rtos/report.json')
    for p,d in skr['inputs'].items():assert sha(ROOT/p)==d,p
    raw=(ROOT/skr['upstream_source']).read_bytes();assert sha(ROOT/skr['upstream_source'])==skr['upstream_sha256'];license_part=raw[:skr['license_bytes']];assert hashlib.sha256(license_part).hexdigest()==skr['license_sha256'];parts=[]
    for row in skr['source_slices']:
        part=raw[row['start']:row['end']];assert hashlib.sha256(part).hexdigest()==row['sha256'];parts.append(part)
    assert [r['name'] for r in skr['source_slices']]==['eTaskConfirmSleepModeStatus','vTaskStepTick'] and (sk.parent/'sleep-kernel.c').read_bytes()==license_part+b'\n#include "sleep_kernel_contract.h"\n'+b'\n'.join(parts)
    tp=BASE/'rtos-tickless-port/report.json';tpr=json.loads(tp.read_text());tpv=receipts['rtos-tickless-port/verification.json'];assert tpv['application_sha256']==app_hash and tpv['report_sha256']==sha(tp) and tpv['driver_sha256']==sha(ROOT/'r1/tools/verify_rtos_tickless_port.py') and tpv['comparisons']==2640 and tpv['svc65_fixture_calls_per_implementation']==672 and tpv['wfe_fixture_calls_per_implementation']==672 and tpv['pending_fpu_sleep_cases']==288
    assert tpr['selected_object_sha256']==sha(tp.parent/'tickless-port.o') and tpr['rtos_report_sha256']==sha(BASE/'rtos/report.json') and tpr['remaining_symbols']==['eTaskConfirmSleepModeStatus','nrf_nvic_state','nrf_sdh_is_enabled','r1_adc_error','vTaskStepTick'] and tpr['source_configuration']=={'configTICK_SOURCE':'RTC1','configUSE_TICKLESS_IDLE':1,'configUSE_TICKLESS_IDLE_SIMPLE_DEBUG':1,'configEXPECTED_IDLE_TIME_BEFORE_SLEEP':2}
    for p,d in tpr['inputs'].items():assert sha(ROOT/p)==d,p
    for path,pin in [(sk,'def7d2df2b0506d3d249334974f51e427c17a41c'),(tp,'nRF5_SDK_17.1.0_ddde560')]:
        evidence=json.loads((path.parent/'evidence.json').read_text());assert evidence['application_sha256']==app_hash and evidence['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and evidence['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and evidence['upstream_pin']==pin
        for row in evidence['spans']:
            gh=path.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']];assert sha(path.parent/row['thumb_file'])==row['thumb_sha256']
        inventory=json.loads((ROOT/evidence['rea_inventory']).read_text());assert sha(ROOT/evidence['rea_inventory'])==evidence['rea_inventory_sha256'];addresses={int(r['entry'],16) for r in evidence['spans']};assert evidence['rea_registered_rows']==[r for r in inventory['normalized_result'] if int(r['address'],16) in addresses]
        if path==tp:assert evidence['sdk_zip_sha256']==sha(ROOT/'vendor-cache/r1/sdk.zip')=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061' and evidence['native_configuration']['rtc_base']=='0x40011000' and evidence['native_configuration']['nvic_state']=='0x2002c2fc'
    real_sleep=json.loads((BASE/'board/idle-real-sleep-verification.json').read_text());assert real_sleep['application_sha256']==app_hash and real_sleep['board_report_sha256']==sha(BASE/'board/report.json') and real_sleep['verification_driver_sha256']==sha(ROOT/'r1/tools/verify_native_board.py') and real_sleep['idle_driver_sha256']==sha(ROOT/'r1/tools/verify_idle_loop_graph.py') and real_sleep['idle_report_sha256']==sha(BASE/'rtos-idle/report.json') and real_sleep['termination_report_sha256']==sha(BASE/'rtos-task-termination/report.json') and real_sleep['tickless_report_sha256']==sha(tp) and real_sleep['sleep_kernel_report_sha256']==sha(sk) and real_sleep['real_sleep'] and real_sleep['comparisons']==1200 and real_sleep['assertion_comparisons']==66 and real_sleep['actual_sleep_calls_per_implementation']==96 and real_sleep['actual_watchdog_feed_calls_per_implementation']==1156 and real_sleep['actual_tick_step_calls_per_implementation']==96 and real_sleep['rtc_read_fixtures_per_implementation']==192 and real_sleep['wfe_fixtures_per_implementation']==96 and not real_sleep['intercepted_providers'] and not real_sleep['provider_interception']
    ip=BASE/'rtos-idle/report.json';ir=json.loads(ip.read_text());iv=json.loads((ip.parent/'verification.json').read_text());assert iv['application_sha256']==app_hash and iv['report_sha256']==sha(ip) and iv['driver_sha256']==sha(ROOT/'r1/tools/verify_rtos_idle.py') and iv['comparisons']==10800 and iv['assertion_comparisons']==2160 and iv['fixture_calls_per_implementation']==91584 and ir['selected_object_sha256']==sha(ip.parent/'idle.o') and ir['rtos_report_sha256']==sha(BASE/'rtos/report.json')
    for p,d in ir['inputs'].items():assert sha(ROOT/p)==d,p
    raw=(ROOT/ir['upstream_source']).read_bytes();assert sha(ROOT/ir['upstream_source'])==ir['upstream_sha256'];license_part=raw[:ir['license_bytes']];assert hashlib.sha256(license_part).hexdigest()==ir['license_sha256'];row=ir['source_slices'][0];part=raw[row['start']:row['end']];assert row['name']=='prvIdleTask' and hashlib.sha256(part).hexdigest()==row['sha256']
    assert (ip.parent/'idle.c').read_bytes()==license_part+b'\n#include "idle_contract.h"\n'+part+b'\nvoid r1_native_idle_watchdog_hook(void) { (void)r1_native_watchdog_hw_feed_thunk(); }\nvoid r1_native_idle_task(void *) __attribute__((alias("prvIdleTask")));\n'
    expected_idle_configuration={'configUSE_IDLE_HOOK':1,'configUSE_PREEMPTION':1,'configIDLE_SHOULD_YIELD':1,'configUSE_TICKLESS_IDLE':1,'configEXPECTED_IDLE_TIME_BEFORE_SLEEP':2};assert ir['source_configuration']==expected_idle_configuration and ir['provider_binding']=={'vApplicationIdleHook':'r1_native_idle_watchdog_hook','r1_native_idle_watchdog_hook':'r1_native_watchdog_hw_feed_thunk'}
    ie=json.loads((ip.parent/'evidence.json').read_text());assert ie['application_sha256']==app_hash and ie['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and ie['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and ie['kernel_pin']=='def7d2df2b0506d3d249334974f51e427c17a41c' and ie['source_configuration']==expected_idle_configuration and ie['native_region']==['0x84fe8','0x8506c'] and not ie['native_standalone_return_abi_claimed']
    gh=ip.parent/ie['ghidra_file'];assert sha(gh)==ie['ghidra_sha256'] and bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x84fe8-0x27000:0x8507c-0x27000] and sha(ip.parent/ie['thumb_file'])==ie['thumb_sha256']
    inventory=json.loads((ROOT/ie['rea_inventory']).read_text());assert sha(ROOT/ie['rea_inventory'])==ie['rea_inventory_sha256'] and inventory['evidence_id']==ie['rea_evidence_id'] and not ie['rea_entry_registered'] and not any(int(r['address'],16)==0x84fe8 for r in inventory['normalized_result'])
    ig=json.loads((BASE/'board/idle-loop-verification.json').read_text());assert ig['application_sha256']==app_hash and ig['board_report_sha256']==sha(BASE/'board/report.json') and ig['verification_driver_sha256']==sha(ROOT/'r1/tools/verify_native_board.py') and ig['idle_driver_sha256']==sha(ROOT/'r1/tools/verify_idle_loop_graph.py') and ig['idle_report_sha256']==sha(ip) and ig['termination_report_sha256']==sha(BASE/'rtos-task-termination/report.json') and ig['comparisons']==1200 and ig['assertion_comparisons']==66 and ig['sleep_fixture_calls_per_implementation']==108 and ig['actual_watchdog_feed_calls_per_implementation']==1156 and ig['intercepted_providers']==['vPortSuppressTicksAndSleep']
    tt=BASE/'rtos-task-termination/report.json';ttr=json.loads(tt.read_text());ttv=receipts['rtos-task-termination/verification.json'];assert ttv['application_sha256']==app_hash and ttv['report_sha256']==sha(tt) and ttv['driver_sha256']==sha(ROOT/'r1/tools/verify_rtos_task_termination.py') and ttv['comparisons']==2953 and ttv['assertion_comparisons']==584 and ttv['tcb_bytes_compared']==112 and ttv['comparisons_by_function']=={'vTaskDelete':1260,'eTaskGetState':129,'r1_native_task_reclaim':256,'osThreadTerminate':240,'vListInsertEnd':18,'r1_native_task_idle_cleanup':150,'r1_native_expected_idle_time':900}
    assert ttr['selected_object_sha256']==sha(tt.parent/'task-termination.o') and ttr['rtos_report_sha256']==sha(BASE/'rtos/report.json') and ttr['list_report_sha256']==sha(BASE/'rtos-task-wait/report.json') and ttr['list_input_object_sha256']==sha(BASE/'rtos-task-wait/list.o') and ttr['list_selected_object_sha256']==sha(tt.parent/'list-end.o')==ttr['units'][2]['object_sha256']
    for p,d in ttr['inputs'].items():assert sha(ROOT/p)==d,p
    for origin in ttr['origins']:
        raw=(ROOT/origin['source']).read_bytes();assert sha(ROOT/origin['source'])==origin['sha256'];license_part=raw[:origin['license_bytes']];assert hashlib.sha256(license_part).hexdigest()==origin['license_sha256'];parts={}
        for row in origin['slices']:
            part=raw[row['start']:row['end']];assert hashlib.sha256(part).hexdigest()==row['sha256'];parts[row['name']]=part
        if origin['target']=='termination':
            names=('prvGetTCBFromHandle','taskRESET_READY_PRIORITY','prvResetNextTaskUnblockTime','prvDeleteTCB','vTaskDelete','eTaskGetState','prvCheckTasksWaitingTermination','prvGetExpectedIdleTime');header='task_termination_contract.h';extra=b'\nvoid r1_native_task_reclaim(TCB_t *) __attribute__((alias("prvDeleteTCB")));\nvoid r1_native_task_idle_cleanup(void) __attribute__((alias("prvCheckTasksWaitingTermination")));\nTickType_t r1_native_expected_idle_time(void) __attribute__((alias("prvGetExpectedIdleTime")));\n'
        else:names=('IS_IRQ_MODE','IS_IRQ_MASKED','IRQ_Context','osThreadTerminate');header='thread_contract.h';extra=b''
        assert (tt.parent/(origin['target']+'.c')).read_bytes()==license_part+('\n#include "'+header+'"\n').encode()+b'\n'.join(parts[n] for n in names)+extra
    tte=json.loads((tt.parent/'evidence.json').read_text());assert tte['application_sha256']==app_hash and tte['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and tte['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and tte['kernel_pin']=='def7d2df2b0506d3d249334974f51e427c17a41c' and tte['cmsis_pin']=='d213f261b5be6bb29a7cce8b84071706b72f4d53' and tte['native_contract']['tcb_bytes']==112 and tte['native_contract']['allocation_mode_offset']==109 and tte['native_contract']['deleted_pending_address']=='0x20007820'
    for row in tte['spans']:
        gh=tt.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']];assert sha(tt.parent/row['thumb_file'])==row['thumb_sha256']
    assert tte['rea_function_request']['sha256']==sha(tt.parent/'rea-delete-function.json');failed_rea=json.loads((tt.parent/'rea-delete-function.json').read_text());assert failed_rea['code']=='execution_failure' and not failed_rea['retryable'] and failed_rea['details']['diagnostics']['target_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf')
    assert tte['idle_cleanup_discovery']['thumb_sha256']==sha(tt.parent/'idle-cleanup-discovery.txt') and tte['idle_cleanup_discovery']['cleanup_loop_start']=='0x84fea' and tte['idle_cleanup_discovery']['cleanup_loop_exit']=='0x8501a'
    idle_inv=json.loads((tt.parent/'rea-idle-inventory-binding.json').read_text());assert idle_inv['inventory_sha256']==sha(ROOT/idle_inv['inventory']);inventory=json.loads((ROOT/idle_inv['inventory']).read_text());assert idle_inv['evidence_id']==inventory['evidence_id'] and idle_inv['subject']==inventory['subject'] and idle_inv['rows']==[r for r in inventory['normalized_result'] if 0x84f00<=int(r['address'],16)<0x85100]
    ttg=json.loads((BASE/'board/task-termination-verification.json').read_text());assert ttg['application_sha256']==app_hash and ttg['board_report_sha256']==sha(BASE/'board/report.json') and ttg['verification_driver_sha256']==sha(ROOT/'r1/tools/verify_native_board.py') and ttg['termination_driver_sha256']==sha(ROOT/'r1/tools/verify_task_termination_graph.py') and ttg['termination_report_sha256']==sha(tt) and ttg['thread_report_sha256']==sha(BASE/'rtos-thread-new/report.json') and ttg['comparisons']==432 and ttg['workflows']==72 and not ttg['provider_interception']
    tn=BASE/'rtos-thread-new/report.json';tnr=json.loads(tn.read_text());tnt=receipts['rtos-thread-new/verification.json'];assert tnt['application_sha256']==app_hash and tnt['report_sha256']==sha(tn) and tnt['driver_sha256']==sha(ROOT/'r1/tools/verify_rtos_thread_new.py') and tnt['comparisons']==42048 and tnt['backend_calls_per_implementation']==43848 and tnr['selected_object_sha256']==sha(tn.parent/'thread-new.o') and tnr['rtos_report_sha256']==sha(BASE/'rtos/report.json') and tnr['constructor_report_sha256']==sha(BASE/'native-task-construction/report.json')
    for p,d in tnr['inputs'].items():assert sha(ROOT/p)==d,p
    ts=(ROOT/tnr['upstream_source']).read_bytes();assert sha(ROOT/tnr['upstream_source'])==tnr['upstream_sha256'];tparts={}
    for row in tnr['source_slices']:
        part=ts[row['start']:row['end']];assert hashlib.sha256(part).hexdigest()==row['sha256'];tparts[row['name']]=part
    tlicense=ts[:tnr['license_bytes']];assert hashlib.sha256(tlicense).hexdigest()==tnr['license_sha256'] and b'Arm Limited' in tlicense
    assert (tn.parent/'thread-new.c').read_bytes()==tlicense+b'\n#include "thread_contract.h"\n'+b'\n'.join(tparts[n] for n in ('IS_IRQ_MODE','IS_IRQ_MASKED','IRQ_Context','osThreadNew'))
    tne=json.loads((tn.parent/'evidence.json').read_text());assert tne['application_sha256']==app_hash and tne['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and tne['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and tne['cmsis_pin']=='d213f261b5be6bb29a7cce8b84071706b72f4d53' and tne['native_contract']['static_tcb_bytes']==112 and tne['native_contract']['dynamic_stack_depth_bits']==16 and tne['native_contract']['static_stack_depth_bits']==32
    for row in tne['spans']:
        gh=tn.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']];assert sha(tn.parent/row['thumb_file'])==row['thumb_sha256']
    tng=json.loads((BASE/'board/thread-construction-verification.json').read_text());assert tng['application_sha256']==app_hash and tng['board_report_sha256']==sha(BASE/'board/report.json') and tng['verification_driver_sha256']==sha(ROOT/'r1/tools/verify_native_board.py') and tng['construction_driver_sha256']==sha(ROOT/'r1/tools/verify_task_construction_graph.py') and tng['thread_report_sha256']==sha(tn) and tng['cmsis_wrapper_executed'] and tng['comparisons']==144 and tng['workflows']==72 and not tng['provider_interception']
    at=json.loads((BASE/'board/application-thread-verification.json').read_text());assert at['application_sha256']==app_hash and at['board_report_sha256']==sha(BASE/'board/report.json') and at['verification_driver_sha256']==sha(ROOT/'r1/tools/verify_native_board.py') and at['creation_driver_sha256']==sha(ROOT/'r1/tools/verify_application_thread_creation.py') and at['thread_report_sha256']==sha(tn) and at['configuration_sha256']==sha(BASE/'native-task-lifecycle/configuration-evidence.json') and at['comparisons']==2400 and at['workflows']==480 and at['thread_creators']==5 and at['creation_orders']==120 and at['tcb_bytes_compared_per_snapshot']==560 and at['stack_bytes_compared_per_snapshot']==27648 and not at['provider_interception']
    tc=BASE/'native-task-construction/report.json';tcr=json.loads(tc.read_text());tct=receipts['native-task-construction/verification.json'];assert tct['application_sha256']==app_hash and tct['report_sha256']==sha(tc) and tct['driver_sha256']==sha(ROOT/'r1/tools/verify_native_task_construction.py') and tct['comparisons']==788 and tct['assertion_comparisons']==150 and tct['tcb_bytes_compared']==112 and tct['initial_xpsr_bytes_compared']==4 and tcr['selected_object_sha256']==sha(tc.parent/'task-construction.o') and tcr['rtos_report_sha256']==sha(BASE/'rtos/report.json') and tcr['sdk_port_report_sha256']==sha(BASE/'rtos-critical/report.json') and tcr['list_report_sha256']==sha(BASE/'rtos-task-wait/report.json')
    assert tct['comparisons_by_function']=={'r1_native_task_initialize':360,'r1_native_task_create':144,'r1_native_task_create_static':147,'prvAddNewTaskToReadyList':120,'pxPortInitialiseStack':12,'prvTaskExitError':4,'vListInitialiseItem':1} and tcr['provider_aliases']=={'xTaskCreate':'r1_native_task_create','xTaskCreateStatic':'r1_native_task_create_static'}
    for p,d in tcr['inputs'].items():assert sha(ROOT/p)==d,p
    for p,d in tct['provider_reports'].items():assert sha(BASE/p)==d,p
    assert tcr['list_input_object_sha256']==sha(BASE/'rtos-task-wait/list.o') and tcr['list_selected_object_sha256']==sha(tc.parent/'list-item.o')==tcr['units'][3]['object_sha256']
    for origin in tcr['origins']:
        data=(ROOT/origin['source']).read_bytes();assert sha(ROOT/origin['source'])==origin['sha256'];parts={}
        for row in origin['slices']:
            part=data[row['start']:row['end']];assert hashlib.sha256(part).hexdigest()==row['sha256'];parts[row['name']]=part
        license_part=data[:origin['license_bytes']];assert hashlib.sha256(license_part).hexdigest()==origin['license_sha256'];target=origin['target']
        order=('prvAddTaskToReadyList','taskRECORD_READY_PRIORITY','prvAddNewTaskToReadyList','prvInitialiseTaskLists') if target=='ready' else ('pxPortInitialiseStack','prvTaskExitError');header='task_construction_contract.h' if target=='ready' else 'task_stack_contract.h';extra=b'\nvoid r1_native_task_add_ready(r1_native_tcb *) __attribute__((alias("prvAddNewTaskToReadyList")));\n' if target=='ready' else b''
        assert (tc.parent/(target+'.c')).read_bytes()==license_part+('\n#include "'+header+'"\n').encode()+b'\n'.join(parts[n] for n in order)+extra
    tce=json.loads((tc.parent/'evidence.json').read_text());assert tce['application_sha256']==app_hash and tce['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and tce['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and tce['kernel_pin']=='def7d2df2b0506d3d249334974f51e427c17a41c' and tce['sdk_archive_sha256']==sha(ROOT/'vendor-cache/r1/sdk.zip') and tce['native_layout']['bytes']==112 and tce['native_layout']['allocation_mode_offset']==109
    for row in tce['spans']:
        gh=tc.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']];assert sha(tc.parent/row['thumb_file'])==row['thumb_sha256']
    rr=tce['rea_query'];assert not rr['analysis_success'] and rr['code']=='execution_failure' and sha(tc.parent/rr['file'])==rr['sha256'];rd=tce['rea_doctor'];assert sha(tc.parent/rd['file'])==rd['sha256'];ri=tce['rea_inventory_gate'];assert sha(ROOT/ri['file'])==ri['sha256'] and any(int(r['address'],16)==int(ri['registered_address'],16) for r in json.loads((ROOT/ri['file']).read_text())['normalized_result'])
    tcg=json.loads((BASE/'board/task-construction-verification.json').read_text());assert tcg['application_sha256']==app_hash and tcg['board_report_sha256']==sha(BASE/'board/report.json') and tcg['verification_driver_sha256']==sha(ROOT/'r1/tools/verify_native_board.py') and tcg['construction_driver_sha256']==sha(ROOT/'r1/tools/verify_task_construction_graph.py') and tcg['comparisons']==144 and tcg['workflows']==72 and tcg['tcb_bytes_compared']==112 and not tcg['provider_interception']
    tw=BASE/'rtos-task-wait/report.json';twr=json.loads(tw.read_text());twt=receipts['rtos-task-wait/verification.json'];assert twt['application_sha256']==app_hash and twt['report_sha256']==sha(tw) and twt['driver_sha256']==sha(ROOT/'r1/tools/verify_rtos_task_wait.py') and twt['comparisons']==18675 and twt['assertion_comparisons']==323 and twt['accessed_tcb_prefix_bytes']==104 and twt['top_used_priority_bytes_compared']==4 and twr['selected_object_sha256']==sha(tw.parent/'task-wait.o') and twr['rtos_report_sha256']==sha(BASE/'rtos/report.json')
    assert twt['comparisons_by_function']=={'vTaskInternalSetTimeOutState':20,'vTaskMissedYield':20,'vTaskPlaceOnEventList':5041,'xTaskCheckForTimeOut':2702,'xTaskPriorityDisinherit':768,'prvAddCurrentTaskToDelayedList':10080,'uxListRemove':8,'vListInsert':36}
    for p,d in twr['inputs'].items():assert sha(ROOT/p)==d,p
    assert sha(tw.parent/'task-wait-raw.o')==twr['units'][0]['object_sha256'] and sha(tw.parent/'list.o')==twr['units'][1]['object_sha256']==twr['list_unit']['object_sha256']
    wup=(ROOT/twr['upstream_source']).read_bytes();assert sha(ROOT/twr['upstream_source'])==twr['upstream_sha256'];wp={}
    for row in twr['source_slices']:
        part=wup[row['start']:row['end']];assert hashlib.sha256(part).hexdigest()==row['sha256'];wp[row['name']]=part
    wl=wup[:twr['license_bytes']];assert hashlib.sha256(wl).hexdigest()==twr['license_sha256'] and b'Copyright (C) 2021 Amazon.com' in wl
    assert (tw.parent/'task-wait.c').read_bytes()==wl+b'\n#include "task_wait_contract.h"\n'+b'\n'.join(wp[n] for n in ('uxTopUsedPriority','portRESET_READY_PRIORITY','prvAddTaskToReadyList','taskRECORD_READY_PRIORITY','vTaskInternalSetTimeOutState','vTaskMissedYield','vTaskPlaceOnEventList','xTaskCheckForTimeOut','xTaskPriorityDisinherit','prvAddCurrentTaskToDelayedList'))
    twe=json.loads((tw.parent/'evidence.json').read_text());assert twe['application_sha256']==app_hash and twe['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and twe['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and twe['upstream_pin']=='def7d2df2b0506d3d249334974f51e427c17a41c' and twe['accessed_tcb_prefix_bytes']==104 and not twe['full_tcb_layout_admitted'] and twe['layout_reference']['sha256']==sha(BASE/twe['layout_reference']['report'])
    for row in twe['spans']:
        gh=tw.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']];assert sha(tw.parent/row['thumb_file'])==row['thumb_sha256']
    assert twe['debugger_priority_constant']['address']=='0x2000784c' and twe['debugger_priority_constant']['value']==55 and twe['new_storage']['xSuspendedTaskList']=='0x2002b244' and twe['new_storage']['bytes']==20
    qt=json.loads((BASE/'board/queue-timeout-verification.json').read_text());assert qt['application_sha256']==app_hash and qt['board_report_sha256']==sha(BASE/'board/report.json') and qt['verification_driver_sha256']==sha(ROOT/'r1/tools/verify_native_board.py') and qt['timeout_driver_sha256']==sha(ROOT/'r1/tools/verify_queue_timeout.py') and qt['comparisons']==2016 and qt['workflows']==216 and qt['tick_calls_per_implementation']==720 and qt['pend_sv_pauses_per_implementation']==216 and not qt['provider_interception']
    qo=BASE/'rtos-queue-operations/report.json';qor=json.loads(qo.read_text());qot=receipts['rtos-queue-operations/verification.json'];assert qot['application_sha256']==app_hash and qot['report_sha256']==sha(qo) and qot['driver_sha256']==sha(ROOT/'r1/tools/verify_rtos_queue_operations.py') and qot['comparisons']==4875 and qot['assertion_comparisons']==699 and qot['backend_calls_per_implementation']==22973 and qot['comparisons_by_function']=={'xQueueGenericSend':2526,'vQueueDelete':5,'prvCopyDataToQueue':1462,'prvUnlockQueue':882} and qor['selected_object_sha256']==sha(qo.parent/'queue-operations.o') and qor['rtos_report_sha256']==sha(BASE/'rtos/report.json') and qot['memory_report_sha256']==sha(BASE/'runtime/report.json') and qot['memory_object_sha256']==sha(BASE/'runtime/memory-runtime.o')
    for p,d in qor['inputs'].items():assert sha(ROOT/p)==d,p
    for p,d in qot['memory_provider_reports'].items():assert sha(BASE/p)==d,p
    for p,d in qot['memory_provider_objects'].items():assert sha(BASE/p)==d,p
    qoe=json.loads((qo.parent/'evidence.json').read_text());assert qoe['application_sha256']==app_hash and qoe['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and qoe['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and qoe['upstream_pin']=='def7d2df2b0506d3d249334974f51e427c17a41c' and qoe['source_variant']['queue_registry_size']==0 and qoe['source_variant']['baseline_kernel_registry_size_preserved']==2
    for row in qoe['spans']:
        gh=qo.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']];assert sha(qo.parent/row['thumb_file'])==row['thumb_sha256']
    assert qoe['native_tcb_extension_gate']['stack_depth_words_offset']==84 and not qoe['native_tcb_extension_gate']['initializer_promoted'] and not qoe['native_tcb_extension_gate']['full_tcb_layout_admitted']
    ql=json.loads((BASE/'board/queue-lifecycle-verification.json').read_text());assert ql['application_sha256']==app_hash and ql['board_report_sha256']==sha(BASE/'board/report.json') and ql['verification_driver_sha256']==sha(ROOT/'r1/tools/verify_native_board.py') and ql['lifecycle_driver_sha256']==sha(ROOT/'r1/tools/verify_queue_lifecycle.py') and ql['comparisons']==1088 and ql['workflows']==192 and ql['overlap_calls_per_implementation']==360 and not ql['provider_interception'] and ql['heap_bytes_compared_per_call']==51212
    tk=BASE/'rtos-scheduler-tick/report.json';tkr=json.loads(tk.read_text());tkt=receipts['rtos-scheduler-tick/verification.json'];assert tkt['application_sha256']==app_hash and tkt['report_sha256']==sha(tk) and tkt['driver_sha256']==sha(ROOT/'r1/tools/verify_rtos_scheduler_tick.py') and tkt['comparisons']==40193 and tkt['assertion_comparisons']==2049 and tkt['comparisons_by_function']=={'xTaskIncrementTick':38400,'xTaskRemoveFromEventList':1793} and not tkt['provider_interception'] and tkr['selected_object_sha256']==sha(tk.parent/'scheduler-tick.o') and tkr['rtos_report_sha256']==sha(BASE/'rtos/report.json') and '-fwrapv' in tkr['units'][0]['command']
    for p,d in tkr['inputs'].items():assert sha(ROOT/p)==d,p
    tup=(ROOT/tkr['upstream_source']).read_bytes();assert sha(ROOT/tkr['upstream_source'])==tkr['upstream_sha256'];tpieces={}
    for row in tkr['source_slices']:
        part=tup[row['start']:row['end']];assert hashlib.sha256(part).hexdigest()==row['sha256'];tpieces[row['name']]=part
    tl=tup[:tkr['license_bytes']];assert hashlib.sha256(tl).hexdigest()==tkr['license_sha256'] and b'Copyright (C) 2021 Amazon.com' in tl
    assert (tk.parent/'scheduler-tick.c').read_bytes()==tl+b'\n#include "scheduler_tick_contract.h"\n'+b'\n'.join(tpieces[n] for n in ('taskSWITCH_DELAYED_LISTS','prvAddTaskToReadyList','taskRECORD_READY_PRIORITY','xTaskIncrementTick','xTaskRemoveFromEventList','prvResetNextTaskUnblockTime'))
    te=json.loads((tk.parent/'evidence.json').read_text());assert te['application_sha256']==app_hash and te['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and te['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and te['upstream_pin']=='def7d2df2b0506d3d249334974f51e427c17a41c' and te['accessed_tcb_prefix_bytes']==48 and not te['full_tcb_size_admitted']
    for row in te['spans']:
        gh=tk.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']];assert sha(tk.parent/row['thumb_file'])==row['thumb_sha256']
    assert te['list_storage_authentication']['initializer_entry']=='0x84d68' and te['list_storage_authentication']['delayed_base_literal']=='0x84e50' and te['list_storage_authentication']['delayed_base']=='0x2002b1f4' and te['list_storage_authentication']['list_bytes']==20 and struct.unpack_from('<I',(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes(),0x84e50-0x27000)[0]==0x2002b1f4
    tri=json.loads((BASE/'rtos-scheduler-resume/tick-integration-verification.json').read_text());assert tri['application_sha256']==app_hash and tri['report_sha256']==sha(BASE/'rtos-scheduler-resume/report.json') and tri['driver_sha256']==sha(ROOT/'r1/tools/verify_rtos_scheduler_resume.py') and tri['tick_report_sha256']==sha(tk) and tri['tick_object_sha256']==sha(tk.parent/'scheduler-tick.o') and tri['actual_tick_executed'] and tri['comparisons']==10770 and tri['assertion_comparisons']==2688 and tri['tick_calls_per_implementation']==3360
    sr=BASE/'rtos-scheduler-resume/report.json';srr=json.loads(sr.read_text());srt=receipts['rtos-scheduler-resume/verification.json'];assert srt['application_sha256']==app_hash and srt['report_sha256']==sha(sr) and srt['driver_sha256']==sha(ROOT/'r1/tools/verify_rtos_scheduler_resume.py') and srt['comparisons']==32274 and srt['assertion_comparisons']==8064 and srt['tick_calls_per_implementation']==10080 and srr['selected_object_sha256']==sha(sr.parent/'scheduler.o') and srr['rtos_report_sha256']==sha(BASE/'rtos/report.json')
    for p,d in srr['inputs'].items():assert sha(ROOT/p)==d,p
    upstream=(ROOT/srr['upstream_source']).read_bytes();assert sha(ROOT/srr['upstream_source'])==srr['upstream_sha256'];pieces={}
    for row in srr['source_slices']:
        part=upstream[row['start']:row['end']];assert hashlib.sha256(part).hexdigest()==row['sha256'];pieces[row['name']]=part
    license_part=upstream[:srr['license_bytes']];assert hashlib.sha256(license_part).hexdigest()==srr['license_sha256'] and b'Copyright (C) 2021 Amazon.com' in license_part
    assert (sr.parent/'scheduler.c').read_bytes()==license_part+b'\n#include "scheduler_contract.h"\n'+b'\n'.join(pieces[n] for n in ('prvAddTaskToReadyList','taskRECORD_READY_PRIORITY','vTaskSuspendAll','xTaskResumeAll','prvResetNextTaskUnblockTime'))
    se=json.loads((sr.parent/'evidence.json').read_text());assert se['application_sha256']==app_hash and se['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and se['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and se['upstream_pin']=='def7d2df2b0506d3d249334974f51e427c17a41c' and se['accessed_tcb_prefix_bytes']==48 and not se['full_tcb_size_admitted']
    for row in se['spans']:
        gh=sr.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']];assert sha(sr.parent/row['thumb_file'])==row['thumb_sha256']
    sis=json.loads((BASE/'board/initcall-scheduler-verification.json').read_text());assert sis['application_sha256']==app_hash and sis['board_report_sha256']==sha(BASE/'board/report.json') and sis['verification_driver_sha256']==sha(ROOT/'r1/tools/verify_native_board.py') and sis['stage_driver_sha256']==sha(ROOT/'r1/tools/verify_initcall_stage.py') and sis['heap_report_sha256']==sha(BASE/'native-heap/report.json') and sis['scheduler_report_sha256']==sha(sr) and sis['actual_heap_executed'] and sis['actual_scheduler_suspend_resume_executed'] and sis['comparisons']==8 and sis['allocations_per_implementation']==16 and sis['registry_records']==25 and sis['registrars_executed_per_case']==13 and sis['distinct_changed_bytes_compared']>=51200
    hp=BASE/'native-heap/report.json';hr=json.loads(hp.read_text());ht=receipts['native-heap/verification.json'];assert ht['application_sha256']==app_hash and ht['report_sha256']==sha(hp) and ht['driver_sha256']==sha(ROOT/'r1/tools/verify_native_heap.py') and ht['comparisons']==3165 and ht['assertion_comparisons']==561 and ht['backend_calls_per_implementation']==6316 and ht['heap_bytes_compared_per_call']==51232 and ht['state_bytes_compared_per_call']==20 and hr['selected_object_sha256']==sha(hp.parent/'heap.o') and hr['structured_time_report_sha256']==sha(BASE/'structured-time/report.json')
    for p,d in hr['inputs'].items():assert sha(ROOT/p)==d,p
    he=json.loads((hp.parent/'evidence.json').read_text());assert he['application_sha256']==app_hash and he['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and he['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and he['upstream_lineage']['pin']=='def7d2df2b0506d3d249334974f51e427c17a41c' and sha(ROOT/he['upstream_lineage']['path'])==he['upstream_lineage']['sha256'] and he['layout']['sentinel_bytes']==12 and he['layout']['header_bytes']==16
    for row in he['spans']:
        gh=hp.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']];assert sha(hp.parent/row['thumb_file'])==row['thumb_sha256'] and sha(hp.parent/row['pseudocode_file'])==row['pseudocode_sha256']
    his=json.loads((BASE/'board/initcall-heap-verification.json').read_text());assert his['application_sha256']==app_hash and his['board_report_sha256']==sha(BASE/'board/report.json') and his['verification_driver_sha256']==sha(ROOT/'r1/tools/verify_native_board.py') and his['stage_driver_sha256']==sha(ROOT/'r1/tools/verify_initcall_stage.py') and his['heap_report_sha256']==sha(hp) and his['actual_heap_executed'] and his['comparisons']==8 and his['allocations_per_implementation']==16 and his['registry_records']==25 and his['registrars_executed_per_case']==13 and his['distinct_changed_bytes_compared']>=51200
    qc=BASE/'rtos-queue-create/report.json';qcr=json.loads(qc.read_text());qct=receipts['rtos-queue-create/verification.json'];assert qct['application_sha256']==app_hash and qct['report_sha256']==sha(qc) and qct['driver_sha256']==sha(ROOT/'r1/tools/verify_rtos_queue_create.py') and qct['comparisons']==372 and qct['assertion_comparisons']==10 and qcr['selected_object_sha256']==sha(qc.parent/'queue-create.o') and qcr['rtos_report_sha256']==sha(BASE/'rtos/report.json')
    for p,d in qcr['inputs'].items():assert sha(ROOT/p)==d,p
    qce=json.loads((qc.parent/'evidence.json').read_text());assert qce['application_sha256']==app_hash and qce['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and qce['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for row in qce['spans']:
        gh=qc.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']];assert sha(qc.parent/row['thumb_file'])==row['thumb_sha256']
    stage=json.loads((BASE/'board/initcall-stage-verification.json').read_text());assert stage['application_sha256']==app_hash and stage['board_report_sha256']==sha(BASE/'board/report.json') and stage['verification_driver_sha256']==sha(ROOT/'r1/tools/verify_native_board.py') and stage['stage_driver_sha256']==sha(ROOT/'r1/tools/verify_initcall_stage.py') and stage['comparisons']==32 and stage['allocations_per_implementation']==64 and stage['registry_records']==25 and stage['registrars_executed_per_case']==13 and stage['ram_bytes_monitored_per_case']==196608 and stage['distinct_changed_bytes_compared']>0 and stage['name_pointer_fields_compared']>0
    qre=qce['rea_query'];assert not qre['analysis_success'] and qre['code']=='execution_failure' and sha(qc.parent/qre['file'])==qre['sha256']
    qrd=qce['rea_doctor'];assert sha(qc.parent/qrd['file'])==qrd['sha256']
    qci=json.loads((BASE/'rtos-semaphore-new/queue-integration-verification.json').read_text());assert qci['application_sha256']==app_hash and qci['report_sha256']==sha(BASE/'rtos-semaphore-new/report.json') and qci['queue_report_sha256']==sha(qc) and qci['queue_object_sha256']==sha(qc.parent/'queue-create.o') and qci['driver_sha256']==sha(ROOT/'r1/tools/verify_rtos_semaphore_new.py') and qci['actual_queue_constructors_executed'] and qci['comparisons']==38400 and qci['backend_calls_per_implementation']==23808
    sn=BASE/'rtos-semaphore-new/report.json';snr=json.loads(sn.read_text());snt=receipts['rtos-semaphore-new/verification.json'];assert snt['application_sha256']==app_hash and snt['report_sha256']==sha(sn) and snt['comparisons']==38400 and snt['backend_calls_per_implementation']==21540 and snr['selected_object_sha256']==sha(sn.parent/'semaphore-new.o') and snr['rtos_report_sha256']==sha(BASE/'rtos/report.json')
    for p,d in snr['inputs'].items():assert sha(ROOT/p)==d,p
    sne=json.loads((sn.parent/'evidence.json').read_text());assert sne['application_sha256']==app_hash and sne['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and sne['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and sne['cmsis_pin']=='d213f261b5be6bb29a7cce8b84071706b72f4d53'
    for row in sne['spans']:
        gh=sn.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']];assert sha(sn.parent/row['thumb_file'])==row['thumb_sha256']
    dr=receipts['native-stacmd-registration/verification.json'];assert dr['application_sha256']==app_hash and dr['registrar_comparisons']==408 and dr['primitive_comparisons']==1158 and dr['cold_configuration_bytes_pointer_normalized']==448 and dr['name_bytes']==78
    for p,d in dr['provider_reports'].items():assert sha(BASE/p)==d,p
    for p,d in dr['provider_objects'].items():assert sha(BASE/p)==d,p
    for directory,file in [('native-output-gpio-registration','output-gpio-registration.o'),('native-stacmd-registration','stacmd-registration.o')]:
        path=BASE/directory/'report.json';report=json.loads(path.read_text());assert report['selected_object_sha256']==sha(path.parent/file)
        for p,d in report['inputs'].items():assert sha(ROOT/p)==d,p
    de=BASE/'native-stacmd-registration/evidence.json';dee=json.loads(de.read_text());assert dee['application_sha256']==app_hash and dee['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and dee['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for row in dee['spans']:
        gh=de.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']];assert sha(de.parent/row['thumb_file'])==row['thumb_sha256']
    ht=BASE/'native-hw-twi-registration/report.json' ;htr=json.loads(ht.read_text());htt=receipts['native-hw-twi-registration/verification.json'];assert htt['application_sha256']==app_hash and htt['report_sha256']==sha(ht) and htt['comparisons']==864 and htt['semaphore_calls_per_implementation']==864 and htt['cold_configuration_bytes_pointer_normalized']==216 and htt['name_bytes']==12 and htr['selected_object_sha256']==sha(ht.parent/'hw-twi-registration.o')
    for p,d in htr['inputs'].items():assert sha(ROOT/p)==d,p
    for p,d in htt['provider_reports'].items():assert sha(BASE/p)==d,p
    for p,d in htt['provider_objects'].items():assert sha(BASE/p)==d,p
    hte=json.loads((ht.parent/'evidence.json').read_text());assert hte['application_sha256']==app_hash and hte['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and hte['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and 'not PWM' in hte['classification_correction']
    for row in hte['spans']:
        gh=ht.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']];assert sha(ht.parent/row['thumb_file'])==row['thumb_sha256']
    ic=BASE/'native-initcalls/report.json' ;icr=json.loads(ic.read_text());ict=receipts['native-initcalls/verification.json'];assert ict['application_sha256']==app_hash and ict['report_sha256']==sha(ic) and ict['comparisons']==54 and ict['null_target_fault_comparisons']==12 and ict['callbacks_per_implementation']==540 and ict['device_entries']==13 and ict['device_table_bytes_pointer_normalized']==52 and ict['empty_ranges']==3 and icr['selected_object_sha256']==sha(ic.parent/'initcalls.o')
    for p,d in icr['inputs'].items():assert sha(ROOT/p)==d,p
    ice=json.loads((ic.parent/'evidence.json').read_text());assert ice['application_sha256']==app_hash and ice['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and ice['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and ice['device_range']==[0xc4534,0xc4568] and ice['empty_ranges']==[[0,0],[0,0],[0,0]] and 'size40' in ice['boot_wrapper_boundary_gate']
    assert set(ice['unresolved_registrars'])<=set(board['remaining_symbols']) and len(ice['unresolved_registrars'])==0
    assert set(ice['resolved_registrar_reports'])=={'r1_twi_primary_device_binding_configuration','r1_twi_secondary_device_binding_configuration','r1_native_output_gpio_registration','r1_yhm2710_stacmd_binding_configuration'}
    for symbol,path in ice['resolved_registrar_reports'].items():assert symbol not in board['remaining_symbols'] and board['input_reports'][path]==sha(BASE/path)
    for row in ice['spans']:
        gh=ic.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']];assert sha(ic.parent/row['thumb_file'])==row['thumb_sha256']
    rea=ice['rea_post_init'];reaf=ic.parent/rea['file'];readoc=json.loads(reaf.read_text());assert sha(reaf)==rea['sha256'] and readoc['evidence_id']==rea['evidence_id'] and readoc['analysis_profile']['digest']==rea['analysis_profile']=='7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de' and readoc['normalized_result']['procedure']['body']['total_bytes']==22 and readoc['normalized_result']['procedure']['address']=='0x5cb4c'
    dc=BASE/'native-rtc-discovery/report.json' ;dcr=json.loads(dc.read_text());dct=receipts['board/rtc-startup-verification.json'];assert dct['application_sha256']==app_hash and dct['board_report_sha256']==sha(BASE/'board/report.json') and dct['cache_report_sha256']==sha(dc) and dct['comparisons']==960 and dct['cache_comparisons']==240 and dct['workflows']==48 and dct['publish_calls_per_implementation']==14 and dct['cache_name_bytes_compared']==8 and dct['verification_driver_sha256']==sha(ROOT/'r1/tools/verify_native_board.py') and dct['startup_driver_sha256']==sha(ROOT/'r1/tools/verify_rtc_startup.py') and dcr['selected_object_sha256']==sha(dc.parent/'rtc-discovery.o')
    for p,d in dcr['inputs'].items():assert sha(ROOT/p)==d,p
    dce=json.loads((dc.parent/'evidence.json').read_text());assert dce['application_sha256']==app_hash and dce['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and dce['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for row in dce['spans']:
        gh=dc.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']];assert sha(dc.parent/row['thumb_file'])==row['thumb_sha256']
    re=BASE/'native-rtc-error/report.json' ;rer=json.loads(re.read_text());ret=receipts['native-rtc-error/verification.json'];assert ret['application_sha256']==app_hash and ret['report_sha256']==sha(re) and ret['comparisons']==2560 and ret['descriptor_bytes']==66 and rer['reference_only'] and rer['canonical_symbol']=='r1_adc_error' and 'r1/research/source-build/native-rtc-error/rtc-error.o' not in board['objects'] and rer['selected_object_sha256']==sha(re.parent/'rtc-error.o')
    for p,d in rer['inputs'].items():assert sha(ROOT/p)==d,p
    ree=json.loads((re.parent/'evidence.json').read_text());assert ree['application_sha256']==app_hash and ree['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and ree['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for row in ree['spans']:
        gh=re.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']];assert sha(re.parent/row['thumb_file'])==row['thumb_sha256']
    sr=BASE/'sdk-nrfx-rtc/report.json' ;srr=json.loads(sr.read_text());srt=receipts['sdk-nrfx-rtc/verification.json'];assert srt['application_sha256']==app_hash and srt['report_sha256']==sha(sr) and srt['comparisons']==6272 and srt['cold_zero_bytes']==8 and srr['selected_object_sha256']==sha(sr.parent/'nrfx-rtc.o') and srr['sdk_report_sha256']==sha(BASE/'application-sdk/report.json') and srr['configuration_object_sha256']==sha(sr.parent/'configuration.o') and srr['bridge_object_sha256']==sha(sr.parent/'driver-bridge.o') and srr['vector_object_sha256']==sha(sr.parent/'rtc-vector.o')
    for p,d in srr['inputs'].items():assert sha(ROOT/p)==d,p
    import zipfile
    archive=ROOT/'vendor-cache/r1/sdk.zip';assert sha(archive)=='5bfe38e744c39fd7f30e10077ba12df306ef91f368894795d6a3e7a62dc68061'
    with zipfile.ZipFile(archive) as bundle:
        prefix='vendor-cache/r1/nRF5_SDK_17.1.0_ddde560/'
        for p,d in srr['inputs'].items():
            if p.startswith(prefix):assert hashlib.sha256(bundle.read('nRF5_SDK_17.1.0_ddde560/'+p[len(prefix):])).hexdigest()==d,p
    sre=json.loads((sr.parent/'evidence.json').read_text());assert sre['application_sha256']==app_hash and sre['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and sre['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for row in sre['spans']:
        gh=sr.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']];assert sha(sr.parent/row['thumb_file'])==row['thumb_sha256']
    sri=receipts['sdk-nrfx-rtc/irq-verification.json'];assert sri['application_sha256']==app_hash and sri['report_sha256']==sha(sr) and sri['comparisons']==65536 and sri['callbacks_per_implementation']==82660 and sri['vector_bytes_pointer_normalized']==4 and not sri['actual_native_tick']
    srit=json.loads((sr.parent/'irq-real-tick-verification.json').read_text());assert srit['application_sha256']==app_hash and srit['report_sha256']==sha(sr) and srit['comparisons']==16384 and srit['callbacks_per_implementation']==16245 and srit['actual_native_tick'] and srit['vector_bytes_pointer_normalized']==4
    for p,d in srit['provider_reports'].items():assert sha(BASE/p)==d,p
    missing=sre['irq_wrapper_function_lookup'];missingfile=sr.parent/missing['file'];assert sha(missingfile)==missing['sha256'] and 'Function not found' in json.loads(missingfile.read_text())['error'] and 'claims162' in sre['irq_wrapper_boundary_gate']
    inv=sre['irq_rea_inventory_gate'];invfile=ROOT/inv['file'];assert sha(invfile)==inv['sha256'] and inv['absent_observed_addresses']==['0x31750','0x7294c']
    assert not any(int(row['address'],16) in (0x31750,0x7294c) for row in json.loads(invfile.read_text())['normalized_result'])
    rlrp=json.loads((BASE/'native-rtc-lifecycle/real-driver-verification.json').read_text());assert rlrp['application_sha256']==app_hash and rlrp['report_sha256']==sha(BASE/'native-rtc-lifecycle/report.json') and rlrp['comparisons']==51592 and rlrp['actual_sdk_driver'] and rlrp['actual_native_error_logger'] and rlrp['driver_calls_per_implementation']==11
    for p,d in rlrp['provider_reports'].items():assert sha(BASE/p)==d,p
    for p,d in rlrp['provider_objects'].items():assert sha(BASE/p)==d,p
    rl=BASE/'native-rtc-lifecycle/report.json' ;rlr=json.loads(rl.read_text());rlt=receipts['native-rtc-lifecycle/verification.json'];assert rlt['application_sha256']==app_hash and rlt['report_sha256']==sha(rl) and rlt['comparisons']==51592 and rlt['device_callbacks_per_implementation']==75 and rlt['driver_calls_per_implementation']==11 and rlr['selected_object_sha256']==sha(rl.parent/'rtc-lifecycle.o') and rlt['shared_breakdown_bytes']==32 and rlt['ops_bytes_pointer_normalized']==36 and rlt['config_bytes']==8
    for p,d in rlr['inputs'].items():assert sha(ROOT/p)==d,p
    for p,d in rlt['provider_reports'].items():assert sha(BASE/p)==d,p
    for p,d in rlt['provider_objects'].items():assert sha(BASE/p)==d,p
    rle=json.loads((rl.parent/'evidence.json').read_text());assert rle['application_sha256']==app_hash and rle['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and rle['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for row in rle['spans']:
        gh=rl.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']];assert sha(rl.parent/row['thumb_file'])==row['thumb_sha256']
    miss=rle['rea_breakdown_unindexed'];missfile=rl.parent/miss['file'];missdoc=json.loads(missfile.read_text());assert sha(missfile)==miss['sha256'] and missdoc['code']==miss['code']=='invalid_request' and 'No procedure exists at the requested address: 0x276c8' in str(missdoc) and '46 code bytes' in rle['registrar_boundary_gate']
    rd=BASE/'native-rtc-device/report.json' ;rdr=json.loads(rd.read_text());rdt=receipts['native-rtc-device/verification.json'];assert rdt['application_sha256']==app_hash and rdt['report_sha256']==sha(rd) and rdt['comparisons']==5344 and rdt['direct_memmove_comparisons']==1820 and rdr['selected_object_sha256']==sha(rd.parent/'rtc-device.o') and (rdt['cold_zero_bytes'],rdt['cold_record_bytes'],rdt['name_bytes'])==(8,88,8)
    for p,d in rdr['inputs'].items():assert sha(ROOT/p)==d,p
    for p,d in rdt['provider_reports'].items():assert sha(BASE/p)==d,p
    for p,d in rdt['provider_objects'].items():assert sha(BASE/p)==d,p
    mm=BASE/'runtime-memmove/report.json';mmr=json.loads(mm.read_text());assert mmr['upstream']['commit']=='0784374d561435f7c787a555aeab8ede699ed298' and sha(mm.parent/'memmove.o')==mmr['units'][0]['object_sha256'] and mmr['runtime_report_sha256']==sha(BASE/'runtime/report.json')
    for p,d in mmr['inputs'].items():assert sha(ROOT/p)==d,p
    rde=json.loads((rd.parent/'evidence.json').read_text());assert rde['application_sha256']==app_hash and rde['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and rde['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for row in rde['spans']:
        gh=rd.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']];assert sha(rd.parent/row['thumb_file'])==row['thumb_sha256']
    cc=BASE/'native-clock-calendar/report.json' ;ccr=json.loads(cc.read_text());cct=receipts['native-clock-calendar/verification.json'];assert cct['application_sha256']==app_hash and cct['report_sha256']==sha(cc) and cct['comparisons']==45233 and cct['device_callbacks_per_implementation']==19677 and ccr['selected_object_sha256']==sha(cc.parent/'clock-calendar.o')
    for p,d in ccr['inputs'].items():assert sha(ROOT/p)==d,p
    for p,d in cct['provider_reports'].items():assert sha(BASE/p)==d,p
    for p,d in cct['provider_objects'].items():assert sha(BASE/p)==d,p
    original=(ROOT/'r1/reconstructed/time_calendar/time_calendar.c').read_text();parts=[original[:original.index('void time_calendar_initialize(')]]
    for row in ccr['selected_function_slices']:
        part=original[row['start']:row['end']];assert hashlib.sha256(part.encode()).hexdigest()==row['sha256'] and row['name']+'(' in part;parts.append(part)
    assert (cc.parent/'selected-calendar.c').read_text()=='\n'.join(parts)+'\n' and sha(cc.parent/'selected-calendar.c')==ccr['selected_source_sha256']
    cce=json.loads((cc.parent/'evidence.json').read_text());assert cce['application_sha256']==app_hash and cce['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and cce['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for row in cce['spans']:
        gh=cc.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']];assert sha(cc.parent/row['thumb_file'])==row['thumb_sha256']
    rea=cce['rea_inverse'];reaf=cc.parent/rea['file'];assert sha(reaf)==rea['sha256'];readoc=json.loads(reaf.read_text());assert readoc['evidence_id']==rea['evidence_id'] and readoc['analysis_profile']['digest']==rea['analysis_profile']=='7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de' and readoc['normalized_result']['procedure']['body']['total_bytes']==216 and readoc['normalized_result']['procedure']['address']=='0x5a8ac'
    cp=BASE/'native-clock-port/report.json' ;cpr=json.loads(cp.read_text());cpt=receipts['native-clock-port/verification.json'];assert cpt['application_sha256']==app_hash and cpt['report_sha256']==sha(cp) and cpt['comparisons']==720 and cpr['selected_object_sha256']==sha(cp.parent/'clock-port.o')
    for p,d in cpr['inputs'].items():assert sha(ROOT/p)==d,p
    for p,d in cpt['provider_reports'].items():assert sha(BASE/p)==d,p
    for p,d in cpt['provider_objects'].items():assert sha(BASE/p)==d,p
    cpe=json.loads((cp.parent/'evidence.json').read_text());assert cpe['application_sha256']==app_hash and cpe['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and cpe['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for row in cpe['spans']:
        gh=cp.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']];assert sha(cp.parent/row['thumb_file'])==row['thumb_sha256']
    cb=BASE/'native-clock-bootstrap/report.json' ;cbr=json.loads(cb.read_text());cbt=receipts['native-clock-bootstrap/verification.json'];assert cbt['application_sha256']==app_hash and cbt['report_sha256']==sha(cb) and cbr['selected_object_sha256']==sha(cb.parent/'clock-bootstrap.o') and cbr['structured_time_report_sha256']==sha(BASE/'structured-time/report.json') and cbt['comparisons']==2501 and cbt['callback_calls_per_implementation']==1452
    for p,d in cbr['inputs'].items():assert sha(ROOT/p)==d,p
    for p,d in cbt['provider_reports'].items():assert sha(BASE/p)==d,p
    assert cbt['default_backend_bytes_pointer_normalized']==board_test['clock_default_backend_bytes_pointer_normalized']==32 and cbt['default_config_bytes']==board_test['clock_default_config_bytes_compared']==8
    cbe=json.loads((cb.parent/'evidence.json').read_text());assert cbe['application_sha256']==app_hash and cbe['wrapper_sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and cbe['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for row in cbe['spans']:
        gh=cb.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']]
        if row.get('thumb_file'):assert sha(cb.parent/row['thumb_file'])==row['thumb_sha256']
    miss=cbe['missing_bootstrap_function'];assert sha(cb.parent/miss['file'])==miss['sha256'] and 'Function not found' in json.loads((cb.parent/miss['file']).read_text())['error']
    cbrp=json.loads((BASE/'native-clock-bootstrap/real-ports-verification.json').read_text());assert cbrp['application_sha256']==app_hash and cbrp['report_sha256']==sha(cb) and cbrp['comparisons']==2501 and cbrp['callback_calls_per_implementation']==300 and cbrp['actual_calendar_and_rtc_request_ports']
    for p,d in cbrp['provider_reports'].items():assert sha(BASE/p)==d,p
    search=json.loads((BASE/'sdk-logger-frontend/string-push-search.json').read_text());assert search['application_sha256']==app_hash
    for r in search['xrefs'].values():assert sha(ROOT/r['file'])==r['sha256']
    pipeline=json.loads((BASE/'board/logger-pipeline-verification.json').read_text());assert pipeline['application_sha256']==app_hash and pipeline['board_report_sha256']==sha(BASE/'board/report.json') and pipeline['verification_driver_sha256']==sha(ROOT/'r1/tools/verify_native_board.py') and pipeline['pipeline_driver_sha256']==sha(ROOT/'r1/tools/verify_logger_pipeline.py') and pipeline['actual_rtc_snapshot_and_default_clock_get'] and pipeline['comparisons']==2034 and pipeline['workflows']==36 and pipeline['standard_messages']==756 and pipeline['hexdump_messages']==504 and pipeline['accepted_rtt_bytes_per_implementation']==76396 and pipeline['rtt_write_calls_per_implementation']==3144 and pipeline['timestamp_callbacks_per_implementation']==1968
    dp=BASE/'native-rtt-delay/report.json';dr=json.loads(dp.read_text());dt=receipts['native-rtt-delay/verification.json'];assert dt['application_sha256']==app_hash and dt['report_sha256']==sha(dp) and dr['selected_object_sha256']==sha(dp.parent/'rtt-delay.o') and dt['ownership_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and dt['comparisons']==1215 and len(dt['clone_entries'])==21 and dt['body_bytes_identical'] and dt['identical_body_bytes_per_entry']==6 and dr['sdk_instruction_contract_sha256']==sha(dp.parent/'sdk-instruction-contract.txt')
    for p,d in dr['inputs'].items():assert sha(ROOT/p)==d,p
    de=json.loads((dp.parent/'evidence.json').read_text());assert de['application_sha256']==app_hash and de['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c');assert [r['entry'] for r in de['functions']]==dt['clone_entries']
    for row in de['functions']:
        gh=dp.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+6]
        if row.get('pseudocode_file'):assert sha(dp.parent/row['pseudocode_file'])==row['pseudocode_sha256']
    di=json.loads((BASE/'sdk-rtt-backend/delay-integration-verification.json').read_text());assert di['application_sha256']==app_hash and di['report_sha256']==sha(BASE/'sdk-rtt-backend/report.json') and di['actual_delay'] and di['delay_report_sha256']==sha(dp) and di['comparisons']==141
    lc=BASE/'native-log-calendar/report.json';lcr=json.loads(lc.read_text());lct=receipts['native-log-calendar/verification.json'];assert lct['application_sha256']==app_hash and lct['report_sha256']==sha(lc) and lcr['selected_object_sha256']==sha(lc.parent/'log-calendar.o') and lcr['structured_time_report_sha256']==sha(BASE/'structured-time/report.json') and lct['comparisons']==2257 and lct['timestamp_callbacks_per_implementation']==3441 and lct['output_bytes']==8
    for p,d in lcr['inputs'].items():assert sha(ROOT/p)==d,p
    for p,d in lct['provider_reports'].items():assert sha(BASE/p)==d,p
    lce=json.loads((lc.parent/'evidence.json').read_text());assert lce['application_sha256']==app_hash and lce['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c');gh=lc.parent/lce['ghidra_file'];assert sha(gh)==lce['ghidra_sha256'] and bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x8ac28-0x27000:0x8ac28-0x27000+202] and sha(lc.parent/lce['pseudocode_file'])==lce['pseudocode_sha256']
    lci=json.loads((BASE/'sdk-log-formatter/calendar-integration-verification.json').read_text());assert lci['application_sha256']==app_hash and lci['report_sha256']==sha(BASE/'sdk-log-formatter/report.json') and lci['actual_calendar'] and lci['actual_modules'] and lci['actual_printf'] and lci['calendar_report_sha256']==sha(lc) and lci['structured_time_report_sha256']==sha(BASE/'structured-time/report.json') and lci['integer_report_sha256']==sha(BASE/'integer-runtime/report.json') and lci['module_report_sha256']==sha(BASE/'sdk-log-modules/report.json') and lci['printf_report_sha256']==sha(BASE/'sdk-fprintf/report.json') and lci['memory_report_sha256']==sha(BASE/'runtime/report.json') and lci['comparisons']==1625 and lci['timestamp_callbacks_per_implementation']>0 and lci['output_bytes_per_implementation']==83470 and lci['output_callbacks_per_implementation']==1192
    lm=BASE/'sdk-log-modules/report.json';lmr=json.loads(lm.read_text());lmt=receipts['sdk-log-modules/verification.json'];assert lmt['application_sha256']==app_hash and lmt['report_sha256']==sha(lm) and lmr['selected_object_sha256']==sha(lm.parent/'log-modules.o') and lmr['sdk_report_sha256']==sha(BASE/'application-sdk/report.json') and lmt['comparisons']==33056 and lmt['configuration_evidence_sha256']==sha(lm.parent/'configuration-evidence.json')
    for p,d in lmr['inputs'].items():assert sha(ROOT/p)==d,p
    assert lmt['record_bytes_compared']==board_test['log_module_record_bytes_compared']==256 and lmt['name_bytes_compared']==board_test['log_module_name_bytes_compared']==311
    lme=json.loads((lm.parent/'evidence.json').read_text());assert lme['application_sha256']==app_hash and lme['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and sha(lm.parent/lme['pseudocode_file'])==lme['pseudocode_sha256']
    for row in lme['spans']:
        gh=lm.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['body_bytes']]
    lmi=json.loads((BASE/'sdk-log-formatter/modules-integration-verification.json').read_text());assert lmi['application_sha256']==app_hash and lmi['report_sha256']==sha(BASE/'sdk-log-formatter/report.json') and lmi['actual_modules'] and lmi['actual_printf'] and lmi['module_report_sha256']==sha(lm) and lmi['printf_report_sha256']==sha(BASE/'sdk-fprintf/report.json') and lmi['memory_report_sha256']==sha(BASE/'runtime/report.json') and lmi['comparisons']==1625 and lmi['output_bytes_per_implementation']==83470 and lmi['output_callbacks_per_implementation']==1192
    pf=BASE/'sdk-fprintf/report.json';pr=json.loads(pf.read_text());pt=receipts['sdk-fprintf/verification.json'];assert pt['application_sha256']==app_hash and pt['report_sha256']==sha(pf) and pr['selected_object_sha256']==sha(pf.parent/'fprintf.o') and pr['sdk_report_sha256']==sha(BASE/'application-sdk/report.json') and pt['memory_report_sha256']==sha(BASE/'runtime/report.json') and pt['comparisons']==3949 and pt['callback_bytes_per_implementation']==53516
    for p,d in pr['inputs'].items():assert sha(ROOT/p)==d,p
    pe=json.loads((pf.parent/'evidence.json').read_text());assert pe['application_sha256']==app_hash and pe['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for row in pe['functions']:
        gh=pf.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['body_bytes']];assert sha(pf.parent/row['pseudocode_file'])==row['pseudocode_sha256']
    pi=json.loads((BASE/'sdk-log-formatter/printf-integration-verification.json').read_text());assert pi['application_sha256']==app_hash and pi['report_sha256']==sha(BASE/'sdk-log-formatter/report.json') and pi['actual_printf'] and pi['printf_report_sha256']==sha(pf) and pi['memory_report_sha256']==sha(BASE/'runtime/report.json') and pi['comparisons']==1625 and pi['output_bytes_per_implementation']==84010 and pi['output_callbacks_per_implementation']==1196
    fm=BASE/'sdk-log-formatter/report.json';fr=json.loads(fm.read_text());ft=receipts['sdk-log-formatter/verification.json'];assert ft['application_sha256']==app_hash and ft['report_sha256']==sha(fm) and fr['selected_object_sha256']==sha(fm.parent/'log-formatter.o') and fr['sdk_report_sha256']==sha(BASE/'application-sdk/report.json') and ft['comparisons']==1894 and ft['printf_calls_per_implementation']==17298 and board_test['formatter_colors_bytes_pointer_normalized']==36
    for p,d in fr['inputs'].items():assert sha(ROOT/p)==d,p
    unit=fr['units'][0];original=(ROOT/unit['original_source']).read_bytes();patch=unit['prefix_replacement'];start=patch['offset'];end=start+patch['length'];assert hashlib.sha256(original).hexdigest()==unit['original_source_sha256'] and hashlib.sha256(original[start:end]).hexdigest()==patch['sha256'];assert (ROOT/unit['source']).read_bytes()==original[:start]+b'extern void r1_log_prefix_process(nrf_log_str_formatter_entry_params_t *, nrf_fprintf_ctx_t *);\n#define prefix_process r1_log_prefix_process\n'+original[end:]
    fe=json.loads((fm.parent/'evidence.json').read_text());assert fe['application_sha256']==app_hash and fe['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for row in fe['functions']:
        gh=fm.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['body_bytes']];assert sha(fm.parent/row['pseudocode_file'])==row['pseudocode_sha256']
    fi=json.loads((BASE/'sdk-log-serial/formatter-integration-verification.json').read_text());assert fi['application_sha256']==app_hash and fi['report_sha256']==sha(BASE/'sdk-log-serial/report.json') and fi['actual_formatter'] and fi['comparisons']==2496
    for p,d in fi['provider_reports'].items():assert sha(BASE/p)==d,p
    lp=BASE/'sdk-log-serial/report.json';lr=json.loads(lp.read_text());lt=receipts['sdk-log-serial/verification.json'];assert lt['application_sha256']==app_hash and lt['report_sha256']==sha(lp) and lr['selected_object_sha256']==sha(lp.parent/'log-serial.o') and lr['sdk_report_sha256']==sha(BASE/'application-sdk/report.json') and lt['comparisons']==3312 and lt['formatter_callbacks_per_implementation']==7680
    for p,d in lr['inputs'].items():assert sha(ROOT/p)==d,p
    for p,d in lt['provider_reports'].items():assert sha(BASE/p)==d,p
    le=json.loads((lp.parent/'evidence.json').read_text());assert le['application_sha256']==app_hash and le['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c');gh=lp.parent/le['ghidra_file'];assert sha(gh)==le['ghidra_sha256'] and bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x79598-0x27000:0x79598-0x27000+194] and sha(lp.parent/le['pseudocode_file'])==le['pseudocode_sha256']
    sg=BASE/'sdk-segger-rtt/report.json';sr=json.loads(sg.read_text());sv=receipts['sdk-segger-rtt/verification.json'];assert sv['application_sha256']==app_hash and sv['report_sha256']==sha(sg) and sv['memory_report_sha256']==sha(BASE/'runtime/report.json') and sr['selected_object_sha256']==sha(sg.parent/'segger-rtt.o') and sv['comparisons']==3230 and sr['sdk_report_sha256']==sha(BASE/'application-sdk/report.json')
    for p,d in sr['inputs'].items():assert sha(ROOT/p)==d,p
    assert sv['cold_zero_bytes']==board_test['segger_initial_zero_bytes_compared']==696 and sv['reverse_identifier_bytes']==board_test['segger_reverse_identifier_bytes_compared']==16
    se=json.loads((sg.parent/'evidence.json').read_text());assert se['application_sha256']==app_hash and se['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for row in se['functions']:
        gh=sg.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['body_bytes']];assert sha(sg.parent/row['pseudocode_file'])==row['pseudocode_sha256']
    si=json.loads((BASE/'sdk-rtt-backend/segger-integration-verification.json').read_text());assert si['application_sha256']==app_hash and si['report_sha256']==sha(BASE/'sdk-rtt-backend/report.json') and si['actual_segger'] and si['segger_report_sha256']==sha(sg) and si['memory_report_sha256']==sha(BASE/'runtime/report.json') and si['comparisons']==141
    rt=BASE/'sdk-rtt-backend/report.json';rr=json.loads(rt.read_text());rv=receipts['sdk-rtt-backend/verification.json'];assert rv['application_sha256']==app_hash and rv['report_sha256']==sha(rt) and rv['frontend_report_sha256']==sha(BASE/'sdk-logger-frontend/report.json') and rr['selected_object_sha256']==sha(rt.parent/'rtt-backend.o') and rv['comparisons']==141 and rr['sdk_report_sha256']==sha(BASE/'application-sdk/report.json')
    for p,d in rr['inputs'].items():assert sha(ROOT/p)==d,p
    assert rv['initial_zero_bytes']==board_test['rtt_initial_zero_bytes_compared']==4097 and rv['backend_record_bytes']==board_test['rtt_backend_record_bytes_compared']==16 and rv['api_bytes_pointer_normalized']==board_test['rtt_backend_api_bytes_pointer_normalized']==12
    re=json.loads((rt.parent/'evidence.json').read_text());assert re['application_sha256']==app_hash and re['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for row in re['functions']:
        gh=rt.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['body_bytes']]
        if row.get('pseudocode_file'):assert sha(rt.parent/row['pseudocode_file'])==row['pseudocode_sha256']
    mp=BASE/'sdk-memobj/report.json';mr=json.loads(mp.read_text());mt=receipts['sdk-memobj/verification.json'];assert mt['application_sha256']==app_hash and mt['report_sha256']==sha(mp) and mr['selected_object_sha256']==sha(mp.parent/'memobj.o') and mt['comparisons']==3870
    for p,d in mr['inputs'].items():assert sha(ROOT/p)==d,p
    for p,d in mt['provider_reports'].items():assert sha(BASE/p)==d,p
    me=json.loads((mp.parent/'evidence.json').read_text());assert me['application_sha256']==app_hash and me['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for row in me['functions']:
        gh=mp.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['body_bytes']];assert sha(mp.parent/row['pseudocode_file'])==row['pseudocode_sha256']
    mi=json.loads((BASE/'sdk-logger-frontend/memobj-integration-verification.json').read_text());assert mi['actual_memobj'] and mi['application_sha256']==app_hash and mi['report_sha256']==sha(BASE/'sdk-logger-frontend/report.json') and mi['memobj_report_sha256']==sha(mp) and mi['memory_report_sha256']==sha(BASE/'runtime/report.json') and mi['comparisons']==8922
    logger_path=BASE/'sdk-logger-frontend/report.json';logger=json.loads(logger_path.read_text());logger_test=receipts['sdk-logger-frontend/panic-verification.json'];logger_ep=logger_path.parent/'evidence.json';logger_e=json.loads(logger_ep.read_text())
    assert logger_test['application_sha256']==app_hash and logger_test['report_sha256']==sha(logger_path) and logger_test['native_evidence_sha256']==sha(logger_ep) and logger['selected_object_sha256']==sha(logger_path.parent/'logger.o') and logger['sdk_report_sha256']==sha(BASE/'application-sdk/report.json')
    init=receipts['sdk-logger-frontend/initialization-verification.json'];assert init['application_sha256']==app_hash and init['report_sha256']==sha(logger_path) and init['comparisons']==427 and init['push_ring_cold_zero_bytes']==board_test['logger_push_ring_initial_zero_bytes_compared']==152 and init['push_ring_descriptor_bytes']==board_test['logger_push_ring_descriptor_bytes_compared']==12
    for p,d in init['provider_reports'].items():assert sha(BASE/p)==d,p
    assert logger['configuration']['NRF_LOG_DEFERRED']==0 and logger['configuration']['NRF_LOG_STR_PUSH_BUFFER_SIZE']==128
    frontend=receipts['sdk-logger-frontend/frontend-verification.json'];assert frontend['application_sha256']==app_hash and frontend['report_sha256']==sha(logger_path) and frontend['critical_report_sha256']==sha(BASE/'sdk-critical/report.json') and frontend['atomic_store_report_sha256']==sha(BASE/'sdk-power-management/report.json') and frontend['comparisons']==8922 and frontend['memory_report_sha256']==sha(BASE/'runtime/report.json')
    assert frontend['source_owned_zero_bytes']==4336 and board_test['logger_pool_initial_zero_bytes_compared']==208 and board_test['logger_pool_descriptor_bytes_compared']==20 and board_test['logger_warning_bytes_compared']==40
    for path,digest in logger['inputs'].items():assert sha(ROOT/path)==digest,path
    assert logger_test['source_owned_cold_zero_bytes']==board_test['logger_frontend_initial_zero_bytes_compared']==4128 and logger['configuration']['NRF_LOG_BUFSIZE']==4096 and logger_e['application_sha256']==app_hash and logger_e['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for row in logger_e['functions']:
        gh=logger_path.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['body_bytes']]
        if row.get('pseudocode_file'):assert sha(logger_path.parent/row['pseudocode_file'])==row['pseudocode_sha256']
    rr=logger_path.parent/logger_e['rea_panic_receipt']['file'];assert sha(rr)==logger_e['rea_panic_receipt']['sha256'];rea=json.loads(rr.read_text());assert rea['subject']['digest']['sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and rea['normalized_result']['procedure']['body']['total_bytes']==38
    logger_power=json.loads((logger_path.parent/'power-integration-verification.json').read_text());assert logger_power['application_sha256']==app_hash and logger_power['report_sha256']==sha(BASE/'sdk-power-management/report.json') and logger_power['dfu_report_sha256']==sha(BASE/'sdk-dfu-state/report.json') and logger_power['logger_report_sha256']==sha(logger_path) and logger_power['actual_logger_panic'] and logger_power['panic_backend_callbacks_per_implementation']>0 and logger_power['actual_sdk_dfu_callback_executed']
    dfu_path=BASE/'sdk-dfu-state/report.json';dfu=json.loads(dfu_path.read_text());dfu_test=json.loads((dfu_path.parent/'verification.json').read_text());power_path=BASE/'sdk-power-management/report.json';power=json.loads(power_path.read_text());power_test=receipts['sdk-power-management/verification.json']
    for component,report,test,obj in (('sdk-dfu-state',dfu,dfu_test,'dfu-state.o'),('sdk-power-management',power,power_test,'power-management.o')):
        folder=BASE/component;ep=folder/'evidence.json';e=json.loads(ep.read_text());assert test['application_sha256']==app_hash and test['report_sha256']==sha(folder/'report.json') and test['native_evidence_sha256']==sha(ep) and report['selected_object_sha256']==sha(folder/obj) and report['sdk_report_sha256']==sha(BASE/'application-sdk/report.json')
        for path,digest in report['inputs'].items():assert sha(ROOT/path)==digest,path
        assert e['application_sha256']==app_hash and e['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
        for row in e['functions']:
            gh=folder/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['body_bytes']]
            if row.get('pseudocode_file'):assert sha(folder/row['pseudocode_file'])==row['pseudocode_sha256']
    extraction=dfu['extraction'];original=ROOT/dfu['units'][0]['source'];assert hashlib.sha256(original.read_bytes()[extraction['offset']:extraction['offset']+extraction['length']]).hexdigest()==extraction['sha256'] and sha(ROOT/extraction['generated_source'])==extraction['generated_sha256'] and not extraction['compile_anchor_selected']
    assert power['configuration_object_sha256']==sha(power_path.parent/'configuration.o') and power_test['iterator_report_sha256']==sha(BASE/'sdk-ble-dispatch/report.json') and power_test['forced_exclusive_failures_per_implementation']>0 and power_test['source_owned_cold_zero_bytes']==board_test['power_initial_zero_bytes_compared']==18 and power_test['terminal_cases']['off']>0 and power_test['terminal_cases']['reset']>0
    dfu_power=json.loads((dfu_path.parent/'power-integration-verification.json').read_text());assert dfu_power['application_sha256']==app_hash and dfu_power['report_sha256']==sha(power_path) and dfu_power['dfu_report_sha256']==sha(dfu_path) and dfu_power['actual_sdk_dfu_callback_executed'] and dfu_power['native_evidence_sha256']==sha(power_path.parent/'evidence.json') and dfu_power['iterator_report_sha256']==sha(BASE/'sdk-ble-dispatch/report.json')
    nrfx_clock_path=BASE/'sdk-nrfx-clock/report.json';nrfx_clock=json.loads(nrfx_clock_path.read_text());nrfx_clock_test=receipts['sdk-nrfx-clock/verification.json'];nrfx_ep=nrfx_clock_path.parent/'evidence.json';nrfx_e=json.loads(nrfx_ep.read_text())
    assert nrfx_clock_test['application_sha256']==app_hash and nrfx_clock_test['report_sha256']==sha(nrfx_clock_path) and nrfx_clock_test['native_evidence_sha256']==sha(nrfx_ep)
    assert nrfx_clock['sdk_report_sha256']==sha(BASE/'application-sdk/report.json') and nrfx_clock['selected_object_sha256']==nrfx_clock_test['selected_object_sha256']==sha(nrfx_clock_path.parent/'nrfx-clock.o') and not nrfx_clock['remaining_symbols']
    assert nrfx_clock_test['source_owned_cold_zero_bytes']==board_test['nrfx_clock_initial_zero_bytes_compared']==8 and nrfx_clock['configuration']['NRFX_CLOCK_CONFIG_LF_CAL_ENABLED']==1 and nrfx_clock['configuration']['NRFX_CLOCK_CONFIG_LF_SRC']==0
    for path,digest in nrfx_clock['inputs'].items():assert sha(ROOT/path)==digest,path
    assert nrfx_e['application_sha256']==app_hash and nrfx_e['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for row in nrfx_e['functions']:
        gh=nrfx_clock_path.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['body_bytes']]
        if row.get('pseudocode_file'):assert sha(nrfx_clock_path.parent/row['pseudocode_file'])==row['pseudocode_sha256']
    clock_hardware=json.loads((BASE/'sdk-clock/hardware-integration-verification.json').read_text());assert clock_hardware['application_sha256']==app_hash and clock_hardware['report_sha256']==sha(BASE/'sdk-clock/report.json') and clock_hardware['real_nrfx_hardware'] and clock_hardware['real_critical'] and clock_hardware['critical_report_sha256']==sha(BASE/'sdk-critical/report.json') and clock_hardware['nrfx_hardware_report_sha256']==sha(nrfx_clock_path) and clock_hardware['hardware_context_pointer_bytes_normalized']==4
    irq_ep=nrfx_clock_path.parent/'irq-evidence.json';irq_e=json.loads(irq_ep.read_text());irq_test=receipts['sdk-nrfx-clock/irq-verification.json'];irq_legacy=json.loads((nrfx_clock_path.parent/'irq-legacy-integration-verification.json').read_text())
    assert irq_e['application_sha256']==app_hash and irq_e['ownership_ledger_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and irq_e['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and irq_e['pseudocode_sha256']==sha(nrfx_clock_path.parent/irq_e['pseudocode_file'])
    for row in irq_e['rows']:
        gh=nrfx_clock_path.parent/row['file'];assert sha(gh)==row['sha256'];a=int(row['address'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']]
    assert nrfx_clock['configuration_object_sha256']==sha(nrfx_clock_path.parent/'configuration.o')
    for test in (irq_test,irq_legacy):assert test['application_sha256']==app_hash and test['report_sha256']==sha(nrfx_clock_path) and test['native_evidence_sha256']==sha(irq_ep) and test['selected_object_sha256']==nrfx_clock['selected_object_sha256'] and test['vector_bytes_pointer_normalized']==board_test['clock_irq0_vector_bytes_pointer_normalized']==4 and test['comparisons']>0
    assert irq_legacy['real_legacy_clock_callback'] and irq_legacy['legacy_report_sha256']==sha(BASE/'sdk-clock/report.json') and irq_legacy['handler_pointer_bytes_normalized']==4
    clock_path=BASE/'sdk-clock/report.json';clock=json.loads(clock_path.read_text());clock_test=receipts['sdk-clock/critical-integration-verification.json'];clock_ep=clock_path.parent/'evidence.json';clock_e=json.loads(clock_ep.read_text())
    assert clock_test['application_sha256']==app_hash and clock_test['report_sha256']==sha(clock_path) and clock_test['native_evidence_sha256']==sha(clock_ep) and clock_test['real_critical'] and clock_test['critical_report_sha256']==sha(BASE/'sdk-critical/report.json')
    assert clock['sdk_report_sha256']==sha(BASE/'application-sdk/report.json') and clock['selected_object_sha256']==sha(clock_path.parent/'clock.o') and clock['configuration_object_sha256']==sha(clock_path.parent/'configuration.o')
    for path,digest in clock['inputs'].items():assert sha(ROOT/path)==digest,path
    assert clock_e['application_sha256']==app_hash and clock_e['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and clock_test['source_owned_cold_zero_bytes']==board_test['clock_initial_zero_bytes_compared']==20
    for row in clock_e['functions']:
        gh=clock_path.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['body_bytes']]
        if row.get('pseudocode_file'):assert sha(clock_path.parent/row['pseudocode_file'])==row['pseudocode_sha256']
    rr=clock_path.parent/clock_e['rea_notify_receipt']['file'];assert sha(rr)==clock_e['rea_notify_receipt']['sha256'];rea=json.loads(rr.read_text());assert rea['subject']['digest']['sha256']==sha(BASE/'i2c5/stock-analysis-exec.elf') and rea['normalized_result']['procedure']['body']['total_bytes']==34
    assert not clock_e['boundary_discrepancy']['inventory_row_promoted'] and not clock_e['boundary_discrepancy']['ownership_ledger_changed'] and '0x000584ac' not in VERIFIED
    clock_flash=json.loads((BASE/'sdk-clock/fstorage-integration-verification.json').read_text());assert clock_flash['application_sha256']==app_hash and clock_flash['via_actual_soc_poll'] and clock_flash['via_actual_clock_observer'] and clock_flash['workflows']>0 and clock_flash['soc_svc_calls_per_implementation']>0
    for path,digest in clock_flash['provider_reports'].items():assert sha(BASE/path)==digest,path
    soc_path=BASE/'sdk-soc/report.json';soc=json.loads(soc_path.read_text());soc_test=receipts['sdk-soc/verification.json'];soc_evidence_path=soc_path.parent/'evidence.json';soc_evidence=json.loads(soc_evidence_path.read_text())
    assert soc_test['application_sha256']==app_hash and soc_test['report_sha256']==sha(soc_path) and soc_test['native_evidence_sha256']==sha(soc_evidence_path) and soc_test['iterator_report_sha256']==sha(BASE/'sdk-ble-dispatch/report.json')
    assert soc['sdk_report_sha256']==sha(BASE/'application-sdk/report.json') and soc['selected_object_sha256']==sha(soc_path.parent/'soc.o') and soc['configuration_object_sha256']==sha(soc_path.parent/'configuration.o')
    for path,digest in soc['inputs'].items():assert sha(ROOT/path)==digest,path
    assert soc_evidence['application_sha256']==app_hash and soc_test['range_set_bytes_compared']==board_test['soc_range_set_bytes_compared']==28 and soc_test['typed_observer_bytes_compared']==board_test['soc_observer_bytes_pointer_normalized']==16
    for row in soc_evidence['rows']:
        gh=soc_path.parent/row['file'];assert sha(gh)==row['sha256'];a=int(row['address'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['bytes']]
    soc_flash=json.loads((BASE/'sdk-soc/fstorage-integration-verification.json').read_text());assert soc_flash['application_sha256']==app_hash and soc_flash['via_actual_soc_poll'] and soc_flash['soc_svc_calls_per_implementation']>0 and soc_flash['workflows']>0
    for path,digest in soc_flash['provider_reports'].items():assert sha(BASE/path)==digest,path
    sdh_path=BASE/'sdk-sdh/report.json';sdh=json.loads(sdh_path.read_text());sdh_test=receipts['sdk-sdh/irq-integration-verification.json'];sdh_evidence_path=sdh_path.parent/'evidence.json';sdh_evidence=json.loads(sdh_evidence_path.read_text())
    assert sdh_test['application_sha256']==app_hash and sdh_test['report_sha256']==sha(sdh_path) and sdh_test['native_evidence_sha256']==sha(sdh_evidence_path)
    assert sdh_test['real_irq_and_critical'] and sdh_test['comparisons']>0 and sdh_test['critical_report_sha256']==sha(BASE/'sdk-critical/report.json') and sdh_test['iterator_report_sha256']==sha(BASE/'sdk-ble-dispatch/report.json')
    assert sdh['sdk_report_sha256']==sha(BASE/'application-sdk/report.json') and sdh['selected_object_sha256']==sha(sdh_path.parent/'sdh.o') and sdh['configuration_object_sha256']==sha(sdh_path.parent/'configuration.o')
    for path,digest in sdh['inputs'].items():assert sha(ROOT/path)==digest,path
    assert sdh_evidence['application_sha256']==app_hash and sdh_evidence['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for row in sdh_evidence['functions']:
        gh=sdh_path.parent/('ghidra-'+row['symbol']+'-body.json');assert sha(gh)==row['ghidra_sha256'];a=int(row['entry'],16)
        assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['body_bytes']]
        if row.get('pseudocode_file'):assert sha(sdh_path.parent/row['pseudocode_file'])==row['pseudocode_sha256']
    assert sdh_test['source_state_cold_zero_bytes_compared']==board_test['sdh_state_initial_zero_bytes_compared']==3 and sdh_test['section_table_bytes_compared']==board_test['sdh_range_set_bytes_compared']==84 and sdh_test['typed_observer_record_bytes_pointer_normalized']==board_test['sdh_observer_bytes_pointer_normalized']==32
    atfifo_path=BASE/'sdk-atfifo/report.json';atfifo=json.loads(atfifo_path.read_text());atfifo_test=receipts['sdk-atfifo/verification.json'];atfifo_evidence=json.loads((atfifo_path.parent/'evidence.json').read_text())
    assert atfifo_test['application_sha256']==app_hash and atfifo_test['report_sha256']==sha(atfifo_path) and atfifo_test['selected_object_sha256']==atfifo['selected_object_sha256']==sha(atfifo_path.parent/'atfifo-atomic.o')
    assert atfifo_test['forced_exclusive_failures_per_implementation']>0 and atfifo['sdk_report_sha256']==sha(BASE/'application-sdk/report.json') and not atfifo['remaining_symbols']
    for path,digest in atfifo['inputs'].items():assert sha(ROOT/path)==digest,path
    assert atfifo_evidence['application_sha256']==app_hash and atfifo_evidence['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for row in atfifo_evidence['functions']:
        gh=atfifo_path.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256']
        if row['pseudocode_file']:assert sha(atfifo_path.parent/row['pseudocode_file'])==row['pseudocode_sha256']
        a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['body_bytes']]
    real_fifo=json.loads((BASE/'sdk-atfifo/fstorage-integration-verification.json').read_text());assert real_fifo['application_sha256']==app_hash and real_fifo['workflows']>0 and real_fifo['actions']>0 and real_fifo['svc_calls_per_implementation']>0
    for path,digest in real_fifo['provider_reports'].items():assert sha(BASE/path)==digest,path
    sdk_sd_path=BASE/'sdk-fstorage-sd/report.json';sdk_sd=json.loads(sdk_sd_path.read_text());sdk_sd_test=receipts['sdk-fstorage-sd/verification.json'];sdk_sd_evidence=json.loads((sdk_sd_path.parent/'evidence.json').read_text())
    assert sdk_sd_test['application_sha256']==app_hash and sdk_sd_test['report_sha256']==sha(sdk_sd_path) and sdk_sd_test['object_sha256']==sdk_sd['units'][0]['object_sha256']==sha(sdk_sd_path.parent/'fstorage-sd.o')
    assert sdk_sd_test['memory_report_sha256']==sha(BASE/'runtime/report.json') and sdk_sd['sdk_report_sha256']==sha(BASE/'application-sdk/report.json')
    assert sdk_sd_test['cold_zero_bytes_compared']==board_test['sd_fstorage_initial_zero_bytes_compared']==184 and sdk_sd_test['api_table_bytes_pointer_normalized']==board_test['sd_fstorage_api_bytes_pointer_normalized']==32
    assert sdk_sd_test['flash_info_bytes_compared']==board_test['sd_fstorage_flash_info_bytes_compared']==12 and sdk_sd_test['fifo_pointer_bytes_compared']==board_test['sd_fstorage_fifo_pointer_bytes_compared']==4 and sdk_sd_test['observer_record_bytes_pointer_normalized']==board_test['sd_fstorage_observer_bytes_pointer_normalized']==24
    assert sdk_sd_test['svc_calls_per_implementation']>0 and sdk_sd['configuration_source_sha256']==sha(ROOT/sdk_sd['configuration_source'])
    for path,digest in sdk_sd['inputs'].items():assert sha(ROOT/path)==digest,path
    rea_sd_path=sdk_sd_path.parent/sdk_sd_evidence['rea_queue_function']['file'];assert sha(rea_sd_path)==sdk_sd_evidence['rea_queue_function']['sha256']
    rea_sd=json.loads(rea_sd_path.read_text());assert rea_sd['evidence_id']==sdk_sd_evidence['rea_queue_function']['evidence_id'] and rea_sd['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8'
    assert rea_sd['raw_result']['value']['procedure']['body']==sdk_sd_evidence['rea_queue_function']['body'] and sdk_sd_evidence['rea_queue_function']['body']['total_bytes']==404 and sdk_sd_evidence['rea_queue_function']['body']['non_contiguous']
    assert sdk_sd_evidence['application_sha256']==app_hash and sdk_sd_evidence['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for row in sdk_sd_evidence['functions']:
        gh=sdk_sd_path.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256']
        if row['pseudocode_file']:assert sha(sdk_sd_path.parent/row['pseudocode_file'])==row['pseudocode_sha256']
        a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['native_body_bytes']]
    sdk_sd_facades=json.loads((BASE/'sdk-fstorage-sd/facade-integration-verification.json').read_text())
    assert sdk_sd_facades['application_sha256']==app_hash and sdk_sd_facades['report_sha256']==sha(sdk_sd_path) and sdk_sd_facades['object_sha256']==sdk_sd_test['object_sha256'] and sdk_sd_facades['actual_public_facades_executed'] and sdk_sd_facades['facade_report_sha256']==sha(BASE/'sdk-fstorage/report.json')
    sdk_fstorage_path=BASE/'sdk-fstorage/report.json';sdk_fstorage=json.loads(sdk_fstorage_path.read_text());sdk_fstorage_test=receipts['sdk-fstorage/verification.json'];sdk_fstorage_evidence=json.loads((sdk_fstorage_path.parent/'evidence.json').read_text())
    assert sdk_fstorage_test['application_sha256']==app_hash and sdk_fstorage_test['report_sha256']==sha(sdk_fstorage_path) and sdk_fstorage_test['object_sha256']==sdk_fstorage['units'][0]['object_sha256']==sha(sdk_fstorage_path.parent/'fstorage.o')
    sdk_fstorage_integration=json.loads((BASE/'native-internal-flash-operations/sdk-integration-verification.json').read_text())
    assert sdk_fstorage_integration['application_sha256']==app_hash and sdk_fstorage_integration['report_sha256']==sha(BASE/'native-internal-flash-operations/report.json') and sdk_fstorage_integration['actual_sdk_fstorage_facades_executed'] and sdk_fstorage_integration['sdk_report_sha256']==sha(sdk_fstorage_path)
    assert sdk_fstorage_integration['object_sha256']==json.loads((BASE/'native-internal-flash-operations/report.json').read_text())['units'][0]['object_sha256']
    assert sdk_fstorage['sdk_report_sha256']==sha(BASE/'application-sdk/report.json') and sdk_fstorage_test['instance_range_bytes_authenticated']==40
    for path,digest in sdk_fstorage['inputs'].items():assert sha(ROOT/path)==digest,path
    rea_write_path=sdk_fstorage_path.parent/sdk_fstorage_evidence['rea_write_function']['file'];assert sha(rea_write_path)==sdk_fstorage_evidence['rea_write_function']['sha256']
    rea_write=json.loads(rea_write_path.read_text());assert rea_write['evidence_id']==sdk_fstorage_evidence['rea_write_function']['evidence_id'] and rea_write['subject']['digest']['sha256']=='92c47a5cca2d71f9020e17693a0268c192677f00e3734c47e28f04d1f1b081e8' and rea_write['operation']=='analyze_function'
    assert sdk_fstorage_evidence['application_sha256']==app_hash and sdk_fstorage_evidence['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for row in sdk_fstorage_evidence['functions']:
        gh=sdk_fstorage_path.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256']
        if row['pseudocode_file']:assert sha(sdk_fstorage_path.parent/row['pseudocode_file'])==row['pseudocode_sha256']
        a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['body_bytes']]
    internal_ops_path=BASE/'native-internal-flash-operations/report.json';internal_ops=json.loads(internal_ops_path.read_text());internal_ops_test=receipts['native-internal-flash-operations/verification.json'];internal_ops_evidence=json.loads((internal_ops_path.parent/'evidence.json').read_text())
    assert internal_ops_test['application_sha256']==app_hash and internal_ops_test['report_sha256']==sha(internal_ops_path) and internal_ops_test['object_sha256']==internal_ops['units'][0]['object_sha256']==sha(internal_ops_path.parent/'native_internal_flash_operations.o')
    assert internal_ops_test['cold_zero_bytes_compared']==board_test['internal_flash_pending_initial_zero_bytes_compared']==1 and internal_ops['sdk_report_sha256']==sha(BASE/'application-sdk/report.json')
    for path,digest in internal_ops['inputs'].items():assert sha(ROOT/path)==digest,path
    assert internal_ops_evidence['application_sha256']==app_hash and internal_ops_evidence['ownership_ledger_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and internal_ops_evidence['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for row in internal_ops_evidence['functions']:
        gh=internal_ops_path.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256']
        if row['pseudocode_file']:assert sha(internal_ops_path.parent/row['pseudocode_file'])==row['pseudocode_sha256']
        a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['body_bytes']]
    internal_flash_path=BASE/'native-internal-flash/report.json';internal_flash=json.loads(internal_flash_path.read_text());internal_flash_test=receipts['native-internal-flash/verification.json'];internal_flash_evidence=json.loads((internal_flash_path.parent/'evidence.json').read_text())
    assert internal_flash_test['application_sha256']==app_hash and internal_flash_test['report_sha256']==sha(internal_flash_path) and internal_flash_test['object_sha256']==internal_flash['units'][0]['object_sha256']==sha(internal_flash_path.parent/'native_internal_flash.o')
    assert internal_flash_test['memory_report_sha256']==sha(BASE/'runtime/report.json') and internal_flash_test['registry_report_sha256']==sha(BASE/'i2c5/report.json') and internal_flash_test['registry_object_sha256']==sha(BASE/'i2c5/stock_registry.o')
    assert internal_flash_test['record_bytes_pointer_normalized']==board_test['internal_flash_record_bytes_pointer_normalized']==80 and internal_flash_test['fstorage_context_bytes_compared']==board_test['internal_flash_fstorage_bytes_pointer_normalized']==20 and internal_flash_test['name_bytes_compared']==board_test['internal_flash_name_bytes_compared']==13
    assert internal_flash['sdk_report_sha256']==sha(BASE/'application-sdk/report.json')
    for path,digest in internal_flash['inputs'].items():assert sha(ROOT/path)==digest,path
    assert internal_flash_evidence['application_sha256']==app_hash and internal_flash_evidence['ownership_ledger_sha256']==sha(ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv') and internal_flash_evidence['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    assert internal_flash_evidence['correlation_sha256']==sha(ROOT/'r1/docs/correlation/INTERNAL-FLASH-CORRELATION.md')
    for row in internal_flash_evidence['functions']:
        gh=internal_flash_path.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256']
        a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['body_bytes']]
    native_fal_path=BASE/'native-fal-device/report.json';native_fal=json.loads(native_fal_path.read_text());native_fal_test=receipts['native-fal-device/verification.json'];native_fal_evidence=json.loads((native_fal_path.parent/'evidence.json').read_text())
    assert native_fal_test['application_sha256']==app_hash and native_fal_test['report_sha256']==sha(native_fal_path) and native_fal_test['object_sha256']==native_fal['units'][0]['object_sha256']==sha(native_fal_path.parent/'native_fal_device.o')
    assert native_fal_test['memory_report_sha256']==sha(BASE/'runtime/report.json') and native_fal_test['registry_report_sha256']==sha(BASE/'i2c5/report.json') and native_fal_test['registry_object_sha256']==sha(BASE/'i2c5/stock_registry.o')
    assert native_fal_test['cold_zero_bytes_compared']==board_test['native_fal_initial_zero_bytes_compared']==44 and native_fal_test['device_record_bytes_pointer_normalized']==board_test['native_fal_record_bytes_pointer_normalized']==56
    assert native_fal['sdk_report_sha256']==sha(BASE/'application-sdk/report.json')
    for path,digest in native_fal['inputs'].items():assert sha(ROOT/path)==digest,path
    assert native_fal_evidence['application_sha256']==app_hash and native_fal_evidence['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for row in native_fal_evidence['functions']:
        gh=native_fal_path.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256']
        if row['pseudocode_file']:assert sha(native_fal_path.parent/row['pseudocode_file'])==row['pseudocode_sha256']
        a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['body_bytes']]
    fal_partition_path=BASE/'sdk-fal-partition/report.json';fal_partition=json.loads(fal_partition_path.read_text());fal_partition_test=receipts['sdk-fal-partition/verification.json'];fal_partition_evidence=json.loads((fal_partition_path.parent/'evidence.json').read_text())
    assert fal_partition_test['application_sha256']==app_hash and fal_partition_test['report_sha256']==sha(fal_partition_path) and fal_partition_test['object_sha256']==fal_partition['units'][0]['object_sha256']==sha(fal_partition_path.parent/'fal-partition.o')
    assert fal_partition_test['memory_report_sha256']==sha(BASE/'runtime/report.json') and fal_partition_test['cold_zero_bytes_compared']==board_test['fal_partition_initial_zero_bytes_compared']==37 and fal_partition_test['partition_record_bytes_compared']==board_test['fal_partition_record_bytes_compared']==448
    assert fal_partition_test['terminal_assertion_comparisons']>0 and fal_partition['public_report_sha256']==sha(BASE/'public-providers/report.json')
    for path,digest in fal_partition['inputs'].items():assert sha(ROOT/path)==digest,path
    assert fal_partition_evidence['application_sha256']==app_hash and fal_partition_evidence['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for name,digest in fal_partition_evidence['counterexamples'].items():assert sha(fal_partition_path.parent/name)==digest,name
    for row in fal_partition_evidence['functions']:
        gh=fal_partition_path.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'] and sha(fal_partition_path.parent/row['pseudocode_file'])==row['pseudocode_sha256']
        a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['body_bytes']]
    fal_device_path=BASE/'sdk-fal-device/report.json';fal_device=json.loads(fal_device_path.read_text());fal_device_test=receipts['sdk-fal-device/verification.json'];fal_device_evidence=json.loads((fal_device_path.parent/'evidence.json').read_text())
    assert fal_device_test['application_sha256']==app_hash and fal_device_test['report_sha256']==sha(fal_device_path) and fal_device_test['object_sha256']==fal_device['units'][0]['object_sha256']==sha(fal_device_path.parent/'fal-device.o')
    fal_device_core=json.loads((BASE/'sdk-fal-core/device-integration-verification.json').read_text())
    assert fal_device_core['application_sha256']==app_hash and fal_device_core['report_sha256']==sha(BASE/'sdk-fal-core/report.json') and fal_device_core['actual_fal_device_initializer_executed'] and fal_device_core['device_report_sha256']==sha(fal_device_path) and fal_device_core['strncmp_report_sha256']==sha(BASE/'runtime-strncmp/report.json')
    assert fal_device_core['object_sha256']==json.loads((BASE/'sdk-fal-core/report.json').read_text())['units'][0]['object_sha256'] and fal_device_core['shared_readiness_checks']==fal_device_core['comparisons']
    assert fal_device_test['terminal_assertion_comparisons']>0 and fal_device_test['cold_zero_bytes_compared']==board_test['fal_device_initial_zero_bytes_compared']==1
    assert fal_device_test['strncmp_report_sha256']==sha(BASE/'runtime-strncmp/report.json') and fal_device['public_report_sha256']==sha(BASE/'public-providers/report.json')
    for path,digest in fal_device['inputs'].items():assert sha(ROOT/path)==digest,path
    strncmp_report=json.loads((BASE/'runtime-strncmp/report.json').read_text())
    for path,digest in strncmp_report['inputs'].items():assert sha(ROOT/path)==digest,path
    assert strncmp_report['runtime_report_sha256']==sha(BASE/'runtime/report.json')
    assert fal_device_evidence['application_sha256']==app_hash and fal_device_evidence['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c')
    for row in fal_device_evidence['functions']:
        gh=fal_device_path.parent/row['ghidra_file'];assert sha(gh)==row['ghidra_sha256'] and sha(fal_device_path.parent/row['pseudocode_file'])==row['pseudocode_sha256']
        a=int(row['entry'],16);assert bytes(json.loads(gh.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[a-0x27000:a-0x27000+row['body_bytes']]
    fal_core_path=BASE/'sdk-fal-core/report.json';fal_core=json.loads(fal_core_path.read_text());fal_core_test=receipts['sdk-fal-core/verification.json'];fal_core_evidence=json.loads((fal_core_path.parent/'evidence.json').read_text())
    assert fal_core_test['application_sha256']==app_hash and fal_core_test['report_sha256']==sha(fal_core_path) and fal_core_test['object_sha256']==fal_core['units'][0]['object_sha256']==sha(fal_core_path.parent/'fal-core.o')
    assert fal_core_test['shared_readiness_checks']==fal_core_test['comparisons'] and fal_core_test['printf_calls_per_implementation']>0 and fal_core_test['cold_zero_bytes_compared']==board_test['fal_readiness_initial_zero_bytes_compared']==1
    assert fal_core['public_report_sha256']==sha(BASE/'public-providers/report.json')
    for path,digest in fal_core['inputs'].items():assert sha(ROOT/path)==digest,path
    assert fal_core_evidence['application_sha256']==app_hash and fal_core_evidence['ghidra_memory_sha256']==sha(fal_core_path.parent/'ghidra-body.json')
    assert fal_core_evidence['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and fal_core_evidence['pseudocode_sha256']==sha(fal_core_path.parent/'accumulated-pseudocode.c.txt')
    assert bytes(json.loads((fal_core_path.parent/'ghidra-body.json').read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x62f40-0x27000:0x62f7e-0x27000]
    assert 'sdk-fal-core/report.json' in board['input_reports'] and 'sdk-fal-readiness/report.json' not in board['input_reports']
    fal_ready_path=BASE/'sdk-fal-readiness/report.json';fal_ready=json.loads(fal_ready_path.read_text());fal_ready_test=json.loads((fal_ready_path.parent/'verification.json').read_text());fal_ready_evidence=json.loads((fal_ready_path.parent/'supplemental-contracts.json').read_text())
    assert fal_ready_test['application_sha256']==app_hash and fal_ready_test['report_sha256']==sha(fal_ready_path) and fal_ready_test['object_sha256']==fal_ready['units'][0]['object_sha256']==sha(fal_ready_path.parent/'fal-readiness.o')
    assert fal_ready_test['cold_zero_bytes_compared']==board_test['fal_readiness_initial_zero_bytes_compared']==1 and fal_ready_test['comparisons']==256 and fal_ready_test['compiled_partition_record_bytes_compared']==448
    assert fal_ready_test['public_report_sha256']==fal_ready['public_report_sha256']==sha(BASE/'public-providers/report.json') and fal_ready_test['partition_object_sha256']==sha(BASE/'public-providers/flashdb-2.0.0-fal_partition.o')
    assert fal_ready_test['native_partition_decode_sha256']==sha(fal_ready_path.parent/'native-partitions.json')
    for path,digest in fal_ready['inputs'].items():assert sha(ROOT/path)==digest,path
    fal_ready_ghidra=fal_ready_path.parent/'ghidra-body.json';assert fal_ready_evidence['application_sha256']==app_hash and fal_ready_evidence['ghidra_memory_sha256']==sha(fal_ready_ghidra)
    assert bytes(json.loads(fal_ready_ghidra.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x62fe8-0x27000:0x62fee-0x27000]
    kv_init_path=BASE/'native-kv-initialize/report.json';kv_init=json.loads(kv_init_path.read_text());kv_init_test=json.loads((kv_init_path.parent/'verification.json').read_text());kv_init_evidence=json.loads((kv_init_path.parent/'supplemental-contracts.json').read_text())
    assert kv_init_test['application_sha256']==app_hash and kv_init_test['report_sha256']==sha(kv_init_path) and kv_init_test['object_sha256']==kv_init['units'][0]['object_sha256']==sha(kv_init_path.parent/'native_kv_initialize.o')
    assert kv_init_test['initial_zero_bytes_compared']==board_test['kv_init_initial_zero_bytes_compared']==98 and kv_init_test['descriptor_bytes_compared']==board_test['kv_init_descriptor_bytes_compared']
    assert kv_init['sdk_report_sha256']==sha(BASE/'application-sdk/report.json')
    for path,digest in kv_init['inputs'].items():assert sha(ROOT/path)==digest,path
    kv_init_ghidra=kv_init_path.parent/'ghidra-body.json';assert kv_init_evidence['application_sha256']==app_hash and kv_init_evidence['ghidra_memory_sha256']==sha(kv_init_ghidra)
    assert bytes(json.loads(kv_init_ghidra.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x94e3c-0x27000:0x94f8e-0x27000]
    kv_put_path=BASE/'native-kv-store-put/report.json';kv_put=json.loads(kv_put_path.read_text());kv_put_test=json.loads((kv_put_path.parent/'verification.json').read_text());kv_put_evidence=json.loads((kv_put_path.parent/'supplemental-contracts.json').read_text())
    assert kv_put_test['application_sha256']==app_hash and kv_put_test['report_sha256']==sha(kv_put_path) and kv_put_test['object_sha256']==kv_put['units'][0]['object_sha256']==sha(kv_put_path.parent/'native_kv_store_put.o')
    assert kv_put_test['memory_report_sha256']==sha(BASE/'runtime/report.json') and board_test['kv_put_descriptor_bytes_compared']>0
    for path,digest in kv_put['inputs'].items():assert sha(ROOT/path)==digest,path
    assert kv_put['sdk_report_sha256']==sha(BASE/'application-sdk/report.json')
    assert kv_put_evidence['rea_query']['sha256']==sha(kv_put_path.parent/kv_put_evidence['rea_query']['report']) and not kv_put_evidence['rea_query']['analysis_success']
    kv_put_ghidra=kv_put_path.parent/'ghidra-body.json';assert kv_put_evidence['application_sha256']==app_hash and kv_put_evidence['ghidra_memory_sha256']==sha(kv_put_ghidra)
    assert bytes(json.loads(kv_put_ghidra.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x95304-0x27000:0x95428-0x27000]
    kv_get_path=BASE/'native-kv-store-get/report.json';kv_get=json.loads(kv_get_path.read_text());kv_get_test=receipts['native-kv-store-get/verification.json']
    assert kv_get_test['application_sha256']==app_hash and kv_get_test['report_sha256']==sha(kv_get_path) and kv_get_test['object_sha256']==kv_get['units'][0]['object_sha256']==sha(kv_get_path.parent/'native_kv_store_get.o')
    assert kv_get_test['memory_report_sha256']==sha(BASE/'runtime/report.json') and board_test['kv_get_descriptor_bytes_compared']>0
    for path,digest in kv_get['inputs'].items():assert sha(ROOT/path)==digest,path
    kv_get_evidence=json.loads((kv_get_path.parent/'evidence.json').read_text());kv_get_ghidra=kv_get_path.parent/'ghidra-body.json'
    assert kv_get_evidence['application_sha256']==app_hash and kv_get_evidence['ghidra_memory_sha256']==sha(kv_get_ghidra) and kv_get_evidence['native_body_bytes']==248
    assert bytes(json.loads(kv_get_ghidra.read_text())['data'])==(ROOT/'r1/blobs/official/r1-2.2.6.0009/application.bin').read_bytes()[0x95168-0x27000:0x95260-0x27000]
    assert kv_get_evidence['accumulated_pseudocode_sha256']==sha(ROOT/'r1/research/decompilation/application/decompiler-output.c') and kv_get_evidence['extracted_pseudocode_sha256']==sha(kv_get_path.parent/'accumulated-pseudocode.c.txt')
    kv_path=BASE/'native-kv-class/report.json';kv=json.loads(kv_path.read_text());kv_test=receipts['native-kv-class/verification.json']
    assert kv_test['report_sha256']==sha(kv_path) and kv_test['object_sha256']==kv['units'][0]['object_sha256']==sha(kv_path.parent/'native_kv_class.o')
    assert sha(BASE/'application-sdk/report.json')==kv['sdk_report_sha256'] and sha(BASE/'runtime/report.json')==kv_test['memory_report_sha256']
    for path,digest in kv['inputs'].items():assert sha(ROOT/path)==digest,path
    assert kv_test['port_callback_calls']>0
    kv_advertising=json.loads((BASE/'native-advertising-configuration/kv-integration-verification.json').read_text())
    assert kv_advertising['application_sha256']==app_hash and kv_advertising['report_sha256']==sha(advertising_configuration_path) and kv_advertising['object_sha256']==advertising_configuration_test['object_sha256'] and kv_advertising['actual_cached_kv_read_executed']
    for path,digest in kv_advertising['provider_reports'].items():assert sha(BASE/path)==digest,path
    assert kv_advertising['actual_product_config_start_callback_cases']==72
    kv_port_path=BASE/'native-kv-port/report.json';kv_port=json.loads(kv_port_path.read_text());kv_port_test=json.loads((kv_port_path.parent/'verification.json').read_text())
    assert kv_port_test['application_sha256']==app_hash and kv_port_test['report_sha256']==sha(kv_port_path) and kv_port_test['object_sha256']==kv_port['units'][0]['object_sha256']==sha(kv_port_path.parent/'native_kv_port.o')
    assert sha(BASE/'application-sdk/report.json')==kv_port['sdk_report_sha256']
    for path,digest in kv_port['inputs'].items():assert sha(ROOT/path)==digest,path
    assert kv_port_test['port_record_bytes_pointer_normalized']==board_test['kv_port_record_bytes_pointer_normalized']==36
    assert kv_port_test['initial_zero_bytes_compared']==board_test['kv_port_initial_zero_bytes_compared']==9 and kv_port_test['os_mutex_calls']>0
    kv_port_core=json.loads((BASE/'native-kv-class/port-integration-verification.json').read_text())
    assert kv_port_core['application_sha256']==app_hash and kv_port_core['report_sha256']==sha(kv_path) and kv_port_core['object_sha256']==kv_test['object_sha256'] and kv_port_core['port_report_sha256']==sha(kv_port_path) and kv_port_core['actual_port_callbacks_executed']
    assert kv_port_core['memory_report_sha256']==sha(BASE/'runtime/report.json')
    kv_port_advertising=json.loads((BASE/'native-advertising-configuration/port-integration-verification.json').read_text())
    assert kv_port_advertising['application_sha256']==app_hash and kv_port_advertising['report_sha256']==sha(advertising_configuration_path) and kv_port_advertising['object_sha256']==advertising_configuration_test['object_sha256'] and kv_port_advertising['actual_port_mutex_adapters_executed'] and kv_port_advertising['actual_cached_kv_read_executed'] and kv_port_advertising['os_mutex_calls']>0
    for path,digest in kv_port_advertising['provider_reports'].items():assert sha(BASE/path)==digest,path
    ownership=ROOT/'r1/docs/reference/FUNCTION-OWNERSHIP.csv' 
    output=[];counts=collections.Counter();families=collections.defaultdict(collections.Counter)
    for row in csv.DictReader(ownership.open()):
        if row['image']=='application' and row['entry']=='0x00030ac8':
            correction=irq_e['ownership_correction'];assert row==correction['original_row'] and set(correction['effective_fields'])=={'provider_family','source_disposition','upstream_symbol','confidence','evidence'};row={**row,**correction['effective_fields']}
        if row['image']=='application' and row['entry']=='0x00097ba4':
            correction=qce['attribution_correction'][row['entry']];assert row==correction['original_row'] and correction['original']=='prvInitialiseNewQueue' and correction['effective']=='xQueueGenericReset';row={**row,'upstream_symbol':correction['effective'],'evidence':row['evidence']+' Supplemental authenticated reset correction: rtos-queue-create/evidence.json.'}
        if row['image']=='application' and row['entry'] in twe['attribution_corrections']:
            correction=twe['attribution_corrections'][row['entry']];assert row==correction['original_row'];row={**row,'upstream_symbol':correction['effective_symbol'],'evidence':row['evidence']+' Supplemental native timeout/ordered-wait correction: rtos-task-wait/evidence.json.'}
        if row['image']=='application' and row['entry']=='0x000961b8':
            assert row==timer_ownership_correction['original_row'];row={**row,'upstream_symbol':timer_ownership_correction['effective_symbol'],'evidence':row['evidence']+' Supplemental authenticated restricted-wait correction: rtos-timer-runtime/evidence.json.'}
        if row['image']=='application' and row['entry'] in notification_ownership_mappings:
            correction=notification_ownership_mappings[row['entry']];assert row==correction['original_row'];row={**row,'upstream_symbol':correction['effective_symbol'],'evidence':row['evidence']+' Supplemental indexed/event/shared-body mapping: rtos-notification-wrappers/event-next-target.json and module evidence.'}
        if row['image']=='application' and row['entry']=='0x0008569c':
            assert row==timer_id_correction['original_row'];row={**row,'upstream_symbol':'pvTimerGetTimerID','evidence':row['evidence']+' Supplemental native timer callback/ID correction: rtos-timer-new/attribution-correction.json.'}
        contract=VERIFIED.get(row['entry']) if row['image']=='application' else None
        name=contract[0] if contract else row['upstream_symbol']
        matches=candidates.get(name,[])
        if contract and contract[1]=='native-boot-ctors/verification.json':matches=[m for m in matches if m['report']=='native-initcalls/report.json']
        if contract and name in ['r1_native_sscanf','r1_native_scanf_descriptor_init']:matches=[m for m in matches if m['report']=='native-sscanf-frontend/report.json']
        if contract and contract[1]=='native-pow-dispatch/source-verification.json':matches=[m for m in matches if m['report']=='native-pow-dispatch/report.json']
        if contract and contract[1]=='native-powf-dispatch/source-verification.json':matches=[m for m in matches if m['report']=='native-powf-dispatch/report.json']
        if contract and contract[1]=='native-tanh/source-verification.json':matches=[m for m in matches if m['report']=='native-tanh/report.json']
        if contract and contract[1]=='native-stacmd-receive/verification.json':matches=[m for m in matches if m['report']=='native-stacmd-receive/report.json']
        if contract and contract[1]=='native-stacmd-transmit/verification.json':matches=[m for m in matches if m['report']=='native-stacmd-transmit/report.json']
        if contract and contract[1]=='native-stacmd-frames/verification.json':matches=[m for m in matches if m['report']=='native-stacmd-frames/report.json']
        if contract and contract[1]=='native-stacmd-write-retry/verification.json':matches=[m for m in matches if m['report']=='native-stacmd-write-retry/report.json']
        if contract and contract[1]=='native-stacmd-delay/verification.json':matches=[m for m in matches if m['report']=='native-stacmd-delay/report.json']
        if contract and contract[1]=='native-stacmd-recovery/verification.json':matches=[m for m in matches if m['report']=='native-stacmd-recovery/report.json']
        if contract and contract[1]=='native-stacmd-operations/verification.json':matches=[m for m in matches if m['report']=='native-stacmd-operations/report.json']
        if contract and contract[1]=='native-yhm-initialize/verification.json':matches=[m for m in matches if m['report']=='native-yhm-initialize/report.json']
        if contract and contract[1]=='native-yhm-transport/verification.json':matches=[m for m in matches if m['report']=='native-yhm-transport/report.json']
        if contract and contract[1]=='native-yhm-frontend/verification.json':matches=[m for m in matches if m['report']=='native-yhm-frontend/report.json']
        if contract and contract[1]=='native-yhm-system-track/verification.json':matches=[m for m in matches if m['report']=='native-yhm-system-track/report.json']
        if contract and contract[1]=='native-yhm-status/verification.json':matches=[m for m in matches if m['report']=='native-yhm-status/report.json']
        if contract and contract[1]=='native-charger-state/verification.json':matches=[m for m in matches if m['report']=='native-charger-state/report.json']
        if contract and contract[1]=='native-battery-control/verification.json':matches=[m for m in matches if m['report']=='native-battery-control/report.json']
        if contract and contract[1]=='native-battery-statistics/verification.json':matches=[m for m in matches if m['report']=='native-battery-statistics/report.json']
        if contract and contract[1]=='native-battery-runtime/frame-tx-integration-verification.json':matches=[m for m in matches if m['report']=='native-tx/report.json']
        if contract and contract[1] in ('native-sqrt-core-abi/verification.json','native-log/verification.json','native-exp/verification.json','native-expm1/verification.json','native-atan/verification.json','native-tanf/verification.json','native-sinf/verification.json','native-cosf/verification.json','native-trig-reduce/verification.json','native-atan2f/verification.json','native-atanf/verification.json','native-float-logs/verification.json','native-expf-tanhf/verification.json','native-math-special/verification.json','native-math-round/verification.json','native-double-directed/verification.json','native-double-flags/verification.json','native-math-selection/verification.json','native-math-sqrt/verification.json','native-float-sqrt/verification.json','native-float-rounding/verification.json','native-polynomial/verification.json','native-float-bits/verification.json','native-formatter-stream/verification.json','native-rtt-write/verification.json','native-formatter-wrappers/verification.json','native-formatter-core/verification.json','native-formatter-product/verification.json','native-formatter-add/verification.json','native-formatter-unsigned/verification.json','native-formatter-decimal/verification.json','native-formatter-output/verification.json','native-protocol-device-info/verification.json','native-protocol-device-status/verification.json','native-protocol-event-handlers/verification.json','native-protocol-modules/verification.json','native-protocol-ingress/verification.json','native-protocol-receive/verification.json','native-protocol-port/verification.json','native-protocol-fragment/verification.json','native-protocol-send-registration/verification.json','native-protocol-send-hook/verification.json','native-protocol-connection-gates/verification.json'):matches=[m for m in matches if m['report']==contract[1].replace('verification.json','report.json')]
        if contract and contract[1]=='native-protocol-encoder/verification.json':matches=[m for m in matches if m['report']=='native-protocol-encoder/report.json']
        if contract and contract[1]=='native-protocol-response/verification.json':matches=[m for m in matches if m['report']=='native-protocol-response/report.json']
        if contract and contract[1]=='native-phone-operation/verification.json':matches=[m for m in matches if m['report']==('native-phone-operation/report.json' if name=='r1_phone_cmd_send_op1' else 'native-protocol-response-header/report.json')]
        if contract and contract[1]=='native-battery-protocol/verification.json':matches=[m for m in matches if m['report']=='native-battery-protocol/report.json']
        if contract and contract[1]=='native-battery-frame/verification.json':matches=[m for m in matches if m['report']=='native-battery-frame/report.json']
        if contract and contract[1] in ('native-battery-voltage/verification.json','native-battery-runtime/voltage-integration-verification.json'):matches=[m for m in matches if m['report']=='native-battery-voltage/report.json']
        if contract and contract[1]=='native-kv-device-fields/verification.json':matches=[m for m in matches if m['report']=='native-kv-device-fields/report.json']
        if contract and contract[1]=='native-battery-low/verification.json':matches=[m for m in matches if m['report']=='native-battery-low/report.json']
        if contract and contract[1]=='native-battery-diagnostic/verification.json':matches=[m for m in matches if m['report']=='native-battery-diagnostic/report.json']
        if contract and contract[1]=='native-battery-initial-curve/verification.json':matches=[m for m in matches if m['report']=='native-battery-initial-curve/report.json']
        if contract and contract[1]=='native-battery-recovery/verification.json':matches=[m for m in matches if m['report']=='native-battery-recovery/report.json']
        if contract and contract[1]=='native-battery-cadence/verification.json':matches=[m for m in matches if m['report']=='native-battery-cadence/report.json']
        if contract and contract[1]=='native-battery-configuration/verification.json':matches=[m for m in matches if m['report']=='native-battery-configuration/report.json']
        if contract and contract[1]=='native-battery-discharge/verification.json':matches=[m for m in matches if m['report']=='native-battery-discharge/report.json']
        if contract and contract[1]=='native-battery-filter/verification.json':matches=[m for m in matches if m['report']=='native-battery-filter/report.json']
        if contract and contract[1]=='native-battery-runtime/verification.json':matches=[m for m in matches if m['report']=='native-battery-runtime/report.json']
        if contract and contract[1] in ('native-status-record/verification.json','native-thread-init-logs/verification.json'):matches=[m for m in matches if m['report']==contract[1].replace('verification.json','report.json')]
        if contract and contract[1]=='rtos-timer-new/verification.json':matches=[m for m in matches if m['report']==('rtos-timer-id/report.json' if name=='pvTimerGetTimerID' else 'rtos-timer-new/report.json')]
        if contract and contract[1]=='rtos-timer-controls/verification.json':matches=[m for m in matches if m['report']==('rtos-timer-active/report.json' if name=='xTimerIsTimerActive' else 'rtos-timer-controls/report.json')]
        if contract and contract[1] in ('rtos-notification-wrappers/verification.json','rtos-notification-tasks/verification.json','rtos-event-groups/verification.json','rtos-unordered-event/verification.json'):matches=[m for m in matches if m['report']==contract[1].replace('verification.json','report.json')]
        if contract and contract[1] in ('rtos-synchronization/verification.json','rtos-mutex-kernel/verification.json','rtos-mutex-tasks/verification.json'):matches=[m for m in matches if m['report']==contract[1].replace('verification.json','report.json')]
        if contract and contract[1] in ('rtos-message-queue/verification.json','rtos-queue-receive-isr/verification.json'):matches=[m for m in matches if m['report']==contract[1].replace('verification.json','report.json')]
        if contract and contract[1].startswith(('rtos-timer-runtime/','rtos-timer-api/','rtos-timer-queue/','rtos-timer-task-wait/','rtos-timer-isr-queue/')):
            expected_report='rtos-task-count/report.json' if name=='uxTaskGetNumberOfTasks' else contract[1].replace('verification.json','report.json');matches=[m for m in matches if m['report']==expected_report]
        if contract and contract[1]=='native-stack-overflow/verification.json':matches=[m for m in matches if m['report']=='native-stack-overflow/report.json']
        if contract and contract[1]=='rtos-context-port/verification.json':matches=[m for m in matches if m['report']=='rtos-context-port/report.json']
        if contract and contract[1]=='rtos-port-start/verification.json':matches=[m for m in matches if m['report']=='rtos-port-start/report.json']
        if contract and contract[1]=='rtos-scheduler-start/verification.json':matches=[m for m in matches if m['report']=='rtos-scheduler-start/report.json']
        if contract and contract[1]=='rtos-sleep-kernel/verification.json':matches=[m for m in matches if m['report']=='rtos-sleep-kernel/report.json']
        if contract and contract[1]=='rtos-tickless-port/verification.json':matches=[m for m in matches if m['report']=='rtos-tickless-port/report.json']
        if contract and contract[1]=='rtos-task-termination/verification.json':matches=[m for m in matches if m['report']=='rtos-task-termination/report.json']
        if contract and contract[1]=='rtos-thread-new/verification.json':matches=[m for m in matches if m['report']=='rtos-thread-new/report.json']
        if contract and contract[1]=='native-task-construction/verification.json':matches=[m for m in matches if m['report']=='native-task-construction/report.json']
        if contract and contract[1]=='rtos-task-wait/verification.json':matches=[m for m in matches if m['report']=='rtos-task-wait/report.json']
        if contract and contract[1]=='rtos-queue-operations/verification.json':matches=[m for m in matches if m['report']=='rtos-queue-operations/report.json']
        if contract and contract[1]=='rtos-scheduler-tick/verification.json':matches=[m for m in matches if m['report']=='rtos-scheduler-tick/report.json']
        if contract and contract[1]=='rtos-scheduler-resume/verification.json':matches=[m for m in matches if m['report']=='rtos-scheduler-resume/report.json']
        if contract and contract[1]=='native-heap/verification.json':matches=[m for m in matches if m['report']=='native-heap/report.json']
        if contract and contract[1]=='rtos-queue-create/verification.json':matches=[m for m in matches if m['report']=='rtos-queue-create/report.json']
        if contract and contract[1]=='rtos-semaphore-new/verification.json':matches=[m for m in matches if m['report']=='rtos-semaphore-new/report.json']
        if contract and contract[1]=='native-stacmd-registration/verification.json':matches=[m for m in matches if m['report']==('software-twi/gpio-report.json' if name.startswith('r1_twi_gpio_') else 'native-stacmd-registration/report.json')]
        if contract and contract[1]=='native-hw-twi-registration/verification.json':matches=[m for m in matches if m['report']=='native-hw-twi-registration/report.json']
        if contract and contract[1]=='native-initcalls/verification.json':matches=[m for m in matches if m['report']=='native-initcalls/report.json']
        if contract and contract[1]=='board/rtc-startup-verification.json':matches=[m for m in matches if m['report']=='native-rtc-discovery/report.json']
        if contract and contract[1]=='native-rtc-error/verification.json':matches=[m for m in matches if m['report']=='native-rtc-error/report.json']
        if contract and contract[1]=='sdk-nrfx-rtc/irq-verification.json':matches=[m for m in matches if m['report']=='sdk-nrfx-rtc/report.json']
        if contract and contract[1]=='sdk-nrfx-rtc/verification.json':matches=[m for m in matches if m['report']=='sdk-nrfx-rtc/report.json']
        if contract and contract[1]=='native-rtc-lifecycle/verification.json':matches=[m for m in matches if m['report']=='native-rtc-lifecycle/report.json']
        if contract and contract[1]=='native-rtc-device/verification.json':matches=[m for m in matches if m['report']=='native-rtc-device/report.json']
        if contract and contract[1]=='native-clock-calendar/verification.json':matches=[m for m in matches if m['report']=='native-clock-calendar/report.json']
        if contract and contract[1]=='native-clock-port/verification.json':matches=[m for m in matches if m['report']=='native-clock-port/report.json']
        if contract and contract[1]=='native-clock-bootstrap/verification.json':matches=[m for m in matches if m['report']=='native-clock-bootstrap/report.json']
        if contract and contract[1]=='native-rtt-delay/verification.json':matches=[m for m in matches if m['report']=='native-rtt-delay/report.json']
        if contract and contract[1]=='native-log-calendar/verification.json':matches=[m for m in matches if m['report']=='native-log-calendar/report.json']
        if contract and contract[1]=='sdk-log-modules/verification.json':matches=[m for m in matches if m['report']=='sdk-log-modules/report.json']
        if contract and contract[1]=='sdk-fprintf/verification.json':matches=[m for m in matches if m['report']=='sdk-fprintf/report.json']
        if contract and contract[1]=='sdk-log-formatter/verification.json':matches=[m for m in matches if m['report']=='sdk-log-formatter/report.json']
        if contract and contract[1]=='sdk-log-serial/verification.json':matches=[m for m in matches if m['report']=='sdk-log-serial/report.json']
        if contract and contract[1]=='sdk-segger-rtt/verification.json':matches=[m for m in matches if m['report']=='sdk-segger-rtt/report.json']
        if contract and contract[1]=='sdk-rtt-backend/verification.json':matches=[m for m in matches if m['report']=='sdk-rtt-backend/report.json']
        if contract and contract[1]=='sdk-memobj/verification.json':matches=[m for m in matches if m['report']=='sdk-memobj/report.json']
        if contract and contract[1] in ('sdk-logger-frontend/panic-verification.json','sdk-logger-frontend/frontend-verification.json','sdk-logger-frontend/initialization-verification.json'):
            matches=[m for m in matches if m['report']=='sdk-logger-frontend/report.json']
        if contract and contract[1]=='sdk-power-management/verification.json':
            matches=[m for m in matches if m['report']=='sdk-power-management/report.json']
        if contract and contract[1] in ('sdk-nrfx-clock/verification.json','sdk-nrfx-clock/irq-verification.json'):
            matches=[m for m in matches if m['report']=='sdk-nrfx-clock/report.json']
        if contract and contract[1]=='sdk-clock/critical-integration-verification.json':
            matches=[m for m in matches if m['report']=='sdk-clock/report.json']
        if contract and contract[1]=='sdk-soc/verification.json':
            matches=[m for m in matches if m['report']=='sdk-soc/report.json']
        if contract and contract[1]=='sdk-sdh/irq-integration-verification.json':
            matches=[m for m in matches if m['report']=='sdk-sdh/report.json']
        if contract and contract[1]=='sdk-atfifo/verification.json':
            matches=[m for m in matches if m['report']=='sdk-atfifo/report.json']
        if contract and contract[1]=='sdk-fstorage-sd/verification.json':
            matches=[m for m in matches if m['report']=='sdk-fstorage-sd/report.json']
        if contract and contract[1]=='sdk-fstorage/verification.json':
            matches=[m for m in matches if m['report']=='sdk-fstorage/report.json']
        if contract and contract[1]=='native-internal-flash-operations/verification.json':
            matches=[m for m in matches if m['report']=='native-internal-flash-operations/report.json']
        if contract and contract[1]=='native-internal-flash/verification.json':
            matches=[m for m in matches if m['report']=='native-internal-flash/report.json']
        if contract and contract[1]=='native-fal-device/verification.json':
            matches=[m for m in matches if m['report']=='native-fal-device/report.json']
        if contract and contract[1]=='sdk-fal-partition/verification.json':
            matches=[m for m in matches if m['report']=='sdk-fal-partition/report.json']
        if contract and contract[1]=='sdk-fal-device/verification.json':
            matches=[m for m in matches if m['report']=='sdk-fal-device/report.json']
        if contract and contract[1]=='sdk-fal-core/verification.json':
            matches=[m for m in matches if m['report']=='sdk-fal-core/report.json']
        if contract and contract[1]=='native-kv-scans/verification.json':
            matches=[m for m in matches if m['report']=='native-kv-scans/report.json']
        if contract and contract[1]=='native-kv-store-get/verification.json':
            matches=[m for m in matches if m['report']=='native-kv-store-get/report.json']
        if contract and contract[1]=='native-kv-class/verification.json':
            matches=[m for m in matches if m['report']=='native-kv-class/report.json']
        if contract and contract[1]=='native-advertising-configuration/verification.json':
            matches=[m for m in matches if m['report']=='native-advertising-configuration/report.json']
        if contract and contract[1]=='sdk-advertising-init/verification.json':
            matches=[m for m in matches if m['report']=='sdk-advertising-init/report.json']
        if contract and contract[1]=='sdk-advertising/verification.json':
            matches=[m for m in matches if m['report']=='sdk-advertising/report.json']
        if contract and contract[1]=='native-gatt/verification.json':
            matches=[m for m in matches if m['report']=='native-gatt/report.json']
        if contract and contract[1]=='sdk-gatt/verification.json':
            matches=[m for m in matches if m['report']=='sdk-gatt/report.json']
        if contract and contract[1]=='sdk-qwr/verification.json':
            matches=[m for m in matches if m['report']=='sdk-qwr/report.json']
        if contract and contract[1].startswith('sdk-ble-dispatch/'):
            matches=[m for m in matches if m['report']=='sdk-ble-dispatch/report.json']
        if contract and contract[1]=='sdk-connection-events/verification.json':
            matches=[m for m in matches if m['report']=='sdk-connection-events/report.json']
        if contract and contract[1]=='sdk-connection-index/verification.json':
            matches=[m for m in matches if m['report']=='sdk-connection-index/report.json']
        if contract and contract[1]=='sdk-link-context/verification.json':
            matches=[m for m in matches if m['report']=='sdk-link-context/report.json']
        if contract and contract[1]=='native-bae8-send/verification.json':
            matches=[m for m in matches if m['report']=='native-bae8-send/report.json']
        if contract and contract[1]=='native-ble-send/verification.json':
            matches=[m for m in matches if m['report']=='native-ble-send/report.json']
        if contract and contract[1]=='native-output/verification.json':
            matches=[m for m in matches if m['report']=='native-output/report.json']
        if contract and contract[1] in ('watchdog-logging/verification.json','watchdog-logging/strerror-verification.json'):
            matches=[m for m in matches if m['report']=='watchdog-logging/report.json']
        if contract and contract[1]=='sdk-critical/verification.json':
            matches=[m for m in matches if m['report']=='sdk-critical/report.json']
        if contract and contract[1]=='integer-runtime/verification.json':
            matches=[m for m in matches if m['report']=='integer-runtime/report.json']
        if contract and contract[1]=='rtos-critical/verification.json':
            matches=[m for m in matches if m['report']=='rtos-critical/report.json']
        if contract and contract[1]=='rtos-ticks/verification.json':
            expected='rtos-critical/report.json' if name=='vPortValidateInterruptPriority' else 'rtos-ticks/report.json'
            matches=[m for m in matches if m['report']==expected]
        if contract and contract[1]=='native-watchdog/verification.json':
            matches=[m for m in matches if m['report']=='native-watchdog/report.json']
        if contract and contract[1]=='watchdog-startup/sdk-execution.json':
            matches=[m for m in matches if m['report']=='application-sdk/report.json']
        status='tested_contract_candidate' if contract and matches else 'compiled_symbol_hint' if matches else 'unresolved_source_route'
        if contract:
            assert matches and (BASE/contract[1]).is_file(),contract
        counts[status]+=1;families[row['provider_family']][status]+=1
        output.append(dict(image=row['image'],inventory_source=row['inventory_source'],entry=row['entry'],size=row['size'],
                           provider_family=row['provider_family'],source_symbol=row['upstream_symbol'],candidate_symbol=name,
                           status=status,candidate_sources=';'.join(sorted({m['source'] for m in matches})),
                           candidate_objects=';'.join(sorted({m['object'] for m in matches})),
                           candidate_reports=';'.join(sorted({m['report'] for m in matches})),
                           behavior_receipt=contract[1] if contract else '',instruction_identity_proven='false',
                           image_integration_proven='false'))
    with (BASE/'function-frontier.csv').open('w') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(output[0]));writer.writeheader();writer.writerows(output)
    summary=dict(schema=1,supplemental_native_contract_candidates={'0x84cc0':{'symbol':'r1_protocol_command_00084cc0','receipt':'native-protocol-event-handlers/verification.json','receipt_sha256':sha(event_leaf_dir/'verification.json'),'comparisons':65633,'locked_ownership_row':False,'attribution':'native-protocol-event-handlers/target-attribution.json','attribution_sha256':sha(event_leaf_dir/'target-attribution.json'),'graph_receipt':'native-battery-runtime/event-handlers-integration-verification.json','scope':'Registered24-byte special event target; actual event provider remains a fixture'},'0x65740':{'symbol':'r1_native_delayed_initialize','receipt':'native-delayed-initialize/verification.json','receipt_sha256':sha(BASE/'native-delayed-initialize/verification.json'),'comparisons':3072,'locked_ownership_row':False,'scope':'Instruction-backed supplemental initializer; factory providers remain fixtures'},'0x65ea8':{'symbol':'r1_native_delayed_worker','receipt':'native-delayed-worker/verification.json','receipt_sha256':sha(BASE/'native-delayed-worker/verification.json'),'comparisons':1512,'locked_ownership_row':False,'graph_receipt':'native-delayed-reschedule/graph-verification.json','scope':'Bounded queue worker and12 actual queue dispatch workflows; physical blocking remains gated'}},ownership_ledger_sha256=sha(ownership),ownership_attribution_corrections={'native-battery-runtime/frame-tx-attribution.json':sha(BASE/'native-battery-runtime/frame-tx-attribution.json'),'native-battery-control/evidence.json':sha(BASE/'native-battery-control/evidence.json'),'native-battery-runtime/evidence.json':sha(BASE/'native-battery-runtime/evidence.json'),'native-status-record/evidence.json':sha(BASE/'native-status-record/evidence.json'),'rtos-timer-new/attribution-correction.json':sha(BASE/'rtos-timer-new/attribution-correction.json'),'sdk-nrfx-clock/irq-evidence.json':sha(irq_ep),'rtos-queue-create/evidence.json':sha(qc.parent/'evidence.json'),'rtos-task-wait/evidence.json':sha(tw.parent/'evidence.json'),'rtos-timer-runtime/evidence.json':sha(BASE/'rtos-timer-runtime/evidence.json'),**{n+'/evidence.json':sha(BASE/n/'evidence.json') for n in ('rtos-notification-tasks','rtos-event-groups','rtos-unordered-event')}},input_reports=input_reports,ownership_entries=len(output),
                 counts=dict(counts),providers={name:dict(count) for name,count in sorted(families.items())},
                 exact_instruction_matches_proven=0,compiled_instruction_byte_spans=[{'entry':'0x00044a6c','bytes':10,'object':'native-formatter-stream/native_formatter_stream.o','section':'.text.r1_format_unbounded_putc','sha256':stream_receipt['unbounded_putc_section_sha256'],'relocations':False,'image_placement_proven':False},{'entry':'0x0002839a','bytes':4,'object':'native-float-bits/native_float_bits.o','section':'.text.r1_native_floating_environment_control','sha256':fp_bits_receipt['environment_section_sha256'],'relocations':False,'image_placement_proven':False}]+math_special_spans,image_integration_proven=False,
                 limitations=['Ownership ledger has 3326 entries from multiple inventories; the structural Ghidra corpus has 2972 functions. These are different scopes.',
                              'Name matches include local symbols and are routing hints, not ABI/body matches or source admission.',
                              'Tested contract candidates cover bounded inputs in cited receipts; they do not prove all input behavior or exact compiler output.',
                              'Compiled instruction-byte spans are section-local matches; original image placement and complete instruction identity remain separate gates.',
                              'This audit verifies recorded source/object hashes; report-specific header/configuration authentication remains owned by each build target.'])
    (BASE/'function-frontier-summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(f'Ownership entries accounted for: {len(output)}; statuses: {dict(counts)}')
    remaining=sorted(((count['unresolved_source_route'],name) for name,count in families.items()),reverse=True)
    print('Largest unresolved source routes:',remaining[:6])


if __name__=='__main__':main()
