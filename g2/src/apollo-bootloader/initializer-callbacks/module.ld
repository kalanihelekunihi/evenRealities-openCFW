ENTRY(opencfw_boot_init_callback_platform_sequence)
opencfw_bl_descriptor_register = 0x430281;
opencfw_bl_adc_context_initialize = 0x42e8d1;
opencfw_bl_adc_configure = 0x42ec0d;
opencfw_bl_adc_profile_transfer = 0x42f021;
opencfw_bl_adc_context_configure = 0x42eb75;
opencfw_bl_adc_apply_profile = 0x42ea69;
opencfw_bl_adc_configure_channel = 0x42eaf7;
opencfw_bl_adc_activate = 0x42ed61;
opencfw_bl_adc_enable = 0x42ebab;
opencfw_bl_adc_command = 0x42eff5;
opencfw_bl_adc_enumerate = 0x42ee71;
opencfw_bl_adc_disable = 0x42ebe3;
opencfw_bl_adc_normalize = 0x42eda1;
opencfw_bl_adc_reset = 0x42ea33;
opencfw_bl_generic_log = 0x415faf;
opencfw_bl_register_mode = 0x41f531;
opencfw_bl_post_context_register = 0x422ad5;
opencfw_bl_post_configure = 0x422ba9;
opencfw_bl_post_validate = 0x42308f;
opencfw_bl_post_activate = 0x422dc7;
opencfw_bl_post_enable = 0x41f513;
opencfw_bl_post_precommit = 0x41f4f5;
opencfw_bl_post_finish = 0x4236cf;
opencfw_bl_post_record_initialized = 0x41f8bb;
opencfw_bl_context_claim = 0x42c4c7;
opencfw_bl_config_transaction = 0x42c989;
opencfw_bl_instance_configure = 0x42cc35;
opencfw_bl_context_enable = 0x42c539;
opencfw_bl_config_retry = 0x43048f;
opencfw_bl_context_interrupt_enable = 0x42c63b;
opencfw_bl_context_nvic_enable = 0x430471;
opencfw_bl_semaphore_create = 0x416763;
opencfw_bl_service_guard = 0x41a685;
opencfw_bl_service_enable = 0x417439;
opencfw_bl_service_configure = 0x417511;
opencfw_bl_service_commit = 0x4175b5;
opencfw_bl_service_mode = 0x4173cb;
opencfw_bl_service_wake = 0x41a69b;
opencfw_bl_service_sleep = 0x41a6a3;
opencfw_bl_invalid_pin_configure = 0x4174a7;
opencfw_bl_mutex_create = 0x416611;
opencfw_bl_logger_output = 0x4176cf;
SECTIONS {
  . = 0x10000;
  .text : { *(.text*) *(.rodata*) }
  /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) }
}
