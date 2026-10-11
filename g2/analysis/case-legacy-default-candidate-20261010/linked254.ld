ENTRY(case_legacy_known_dispatch)
case_legacy_gpio_bit4 = 0x0010f001;
case_legacy_gpio_bit0 = 0x0010f101;
case_legacy_logger = 0x0010f201;
case_legacy_fill8 = 0x0010f301;
case_legacy_hex_log = 0x0010f401;
case_legacy_value_a = 0x0010f501;
case_legacy_value_b = 0x0010f601;
case_legacy_value_c = 0x0010f701;
case_legacy_set_sn = 0x0010f801;
case_legacy_aa_first = 0x0010f901;
case_legacy_aa_second = 0x0010fa01;
case_legacy_ab_child = 0x0010fb01;
case_legacy_b0_child = 0x0010fc01;
case_legacy_pmic_set = 0x0010fd01;
case_legacy_watchdog_set = 0x0010fe01;
SECTIONS { . = 0x00100000; .text : { *(.text*) *(.rodata*) } /DISCARD/ : { *(.ARM.exidx*) *(.ARM.extab*) *(.comment*) } }
