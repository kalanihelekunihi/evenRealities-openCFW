/* SPDX-License-Identifier: MIT
 * Image-A XIP 0x102078a4..0x10207a05. The call/branch order and constants
 * come from native C-SKY disassembly. System sequence is corroborated by
 * pinned NationalChip lvp/common/lvp_system_init.c. Strings and LDO trim
 * table are exact decoded stock literals; all unowned children remain real
 * imported functions, not synthesized success returns.
 */
#include <stdint.h>

extern void gx8002_xip_cache_initialize_10203c40(void);
extern void gx8002_xip_dma_initialize_10203bc0(void);
extern uint32_t gx8002_xip_console_initialize_102037e0(uint32_t, uint32_t);
extern uint32_t gx8002_resident_pmu_wakeup_source_24940(void);
extern uint32_t gx8002_xip_tws_publish_10206c24(const char *, ...);
extern int32_t gx8002_resident_flash_probe_2475c(uint32_t, uint32_t,
                                                    uint32_t, uint32_t);
extern int32_t gx8002_resident_flash_dispatch_getinfo_247e0(
    const volatile uint8_t *, uint32_t);
extern uintptr_t gx8002_resident_flash_type_api_247d4(const void *);
extern uint32_t gx8002_resident_clock_frequency_25210(uint32_t);
extern uint32_t gx8002_resident_analog_ldo_digital_state_24710(void);
extern uint32_t gx8002_resident_platform_read_24810(uint32_t, void *);
extern void gx8002_xip_print_max_kws_list_10208880(void);
extern void gx8002_xip_gpio_initialize_102060d0(void);
extern void gx8002_xip_board_pin_initialize_102068a0(void);
extern void gx8002_xip_rtc_initialize_102066bc(void);
extern void gx8002_xip_rtc_set_tick_102066b0(uint32_t);
extern void gx8002_xip_rtc_start_tick_102066a0(void);
extern void gx8002_resident_timer_initialize_257e8(void);
extern void gx8002_resident_irq_restore_enabled_254e4(void);
extern void gx8002_xip_device_list_initialize_102060e8(void);
extern void gx8002_xip_spi_master_probe_10206480(void);
extern uint32_t gx8002_xip_power_initialize_10207680(void);

static const uint16_t gx8002_lvp_ldo_trim_mv[12] = {
    950, 924, 897, 871, 845, 819, 792, 766, 740, 714, 687, 661
};

void gx8002_xip_lvp_system_initialize_102078a4(void)
{
    gx8002_xip_cache_initialize_10203c40();
    gx8002_xip_dma_initialize_10203bc0();
    (void)gx8002_xip_console_initialize_102037e0(1u, 115200u);
    if (gx8002_resident_pmu_wakeup_source_24940() < 2u) {
        (void)gx8002_xip_tws_publish_10206c24("[LVP]Low-Power Voice Preprocess\n");
        (void)gx8002_xip_tws_publish_10206c24("[LVP]Copyright (C) 2001-2020 NationalChip Co., Ltd\n");
        (void)gx8002_xip_tws_publish_10206c24("[LVP]ALL RIGHTS RESERVED!\n");
        (void)gx8002_xip_tws_publish_10206c24("[LVP]Board Model: [%s]\n", "grus_gx8002b_dev_1v");
        (void)gx8002_xip_tws_publish_10206c24("[LVP]MCU Version: [%s]\n", "");
        (void)gx8002_xip_tws_publish_10206c24("[LVP]Release Ver: [0x%x]\n", UINT32_C(0x42555858));
        (void)gx8002_xip_tws_publish_10206c24("[LVP]Build Date : [%s]\n", "2026-03-26, 17:07:25");

        const volatile uint8_t *flash = (const volatile uint8_t *)(uintptr_t)
            (uint32_t)gx8002_resident_flash_probe_2475c(0u, 0u,
                                                          0x5dc000u, 0x800u);
        uint32_t flash_id = (uint32_t)gx8002_resident_flash_dispatch_getinfo_247e0(
            flash, 2u);
        if (flash_id == 0x00854012u || flash_id == 0x00856013u)
            (void)gx8002_xip_tws_publish_10206c24("[LVP]Flash vendor:[%s]\n", "PUYA");
        if (flash_id == 0x001c3812u || flash_id == 0x001c3813u)
            (void)gx8002_xip_tws_publish_10206c24("[LVP]Flash vendor:[%s]\n", "ESMT");
        else if (flash_id == 0x005e3414u)
            (void)gx8002_xip_tws_publish_10206c24("[LVP]Flash vendor:[%s]\n", "ZBIT");
        const char *type = (const char *)gx8002_resident_flash_type_api_247d4(flash);
        (void)gx8002_xip_tws_publish_10206c24("[LVP]Flash type:  [%s]\n", type);
        (void)gx8002_xip_tws_publish_10206c24("[LVP]Flash ID:    [%#x]\n", flash_id);
        (void)gx8002_xip_tws_publish_10206c24("[LVP]Flash size:  [%d Byte]\n",
            gx8002_resident_flash_dispatch_getinfo_247e0(flash, 3u));
        (void)gx8002_xip_tws_publish_10206c24("[LVP]CPU   Freq:  [%d Hz][fix]\n",
            gx8002_resident_clock_frequency_25210(10u));
        (void)gx8002_xip_tws_publish_10206c24("[LVP]SRAM  Freq:  [%d Hz]\n",
            gx8002_resident_clock_frequency_25210(6u));
        (void)gx8002_xip_tws_publish_10206c24("[LVP]NPU   Freq:  [%d Hz]\n",
            gx8002_resident_clock_frequency_25210(12u));
        (void)gx8002_xip_tws_publish_10206c24("[LVP]FLASH Freq:  [%d Hz]\n",
            gx8002_resident_clock_frequency_25210(13u));
        if (gx8002_resident_analog_ldo_digital_state_24710() == 2u) {
            (void)gx8002_xip_tws_publish_10206c24("[LVP]enable bypass core Ldo\n");
        } else {
            uint8_t readback[4];
            (void)gx8002_resident_platform_read_24810(8u, readback);
            uint32_t selector = readback[0] & 0xfu;
            int32_t millivolts = selector < 12u ? gx8002_lvp_ldo_trim_mv[selector] : -1;
            (void)gx8002_xip_tws_publish_10206c24("[LVP]Ldo   Trim:  [%d mV]\n",
                                                        millivolts);
        }
        gx8002_xip_print_max_kws_list_10208880();
        gx8002_xip_gpio_initialize_102060d0();
        gx8002_xip_board_pin_initialize_102068a0();
        gx8002_xip_rtc_initialize_102066bc();
        gx8002_xip_rtc_set_tick_102066b0(0u);
        gx8002_xip_rtc_start_tick_102066a0();
    }
    gx8002_resident_timer_initialize_257e8();
    gx8002_resident_irq_restore_enabled_254e4();
    gx8002_xip_device_list_initialize_102060e8();
    gx8002_xip_spi_master_probe_10206480();
    (void)gx8002_xip_power_initialize_10207680();
}
