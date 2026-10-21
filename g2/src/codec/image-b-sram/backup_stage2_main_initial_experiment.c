/* Stock image-B 0x1000a8ec..0x1000aa56, LvpSystemInit.
 * Native call/branch order is corroborated by pinned NationalChip
 * lvp/common/lvp_system_init.c. The twelve LDO trim values are the named
 * voltage enumeration from that SDK and equal native table 0x1001330c.
 * Hardware children remain typed source/link obligations.
 */
#include <stdint.h>

extern void gx8002_image_b_cache_initialize_100051a4(void);
extern void gx8002_image_b_dma_initialize_10004d14(void);
extern void gx8002_image_b_console_initialize_10004808(uint32_t port,
                                                        uint32_t baud);
extern uint32_t gx8002_image_b_platform_status_10003fb8(void);
extern void gx8002_image_b_platform_retention_10004ffc(void);
extern void gx8002_image_b_gpio_initialize_1000482c(void);
extern void gx8002_image_b_spi_master_registry_initialize_10008204(void);
extern void gx8002_image_b_board_devices_initialize_100085ac(void);
extern uint32_t gx8002_image_b_pmu_initialize_1000a744(void);
extern uint32_t gx8002_image_b_flash_probe_10007fac(uint32_t bus,
    uint32_t chip_select, uint32_t speed, uint32_t mode);
extern uint32_t gx8002_image_b_flash_info_10008018(uint32_t flash,
                                                     uint32_t selector);
extern const char *gx8002_image_b_flash_type_1000800c(uint32_t flash);
extern uint32_t gx8002_image_b_clock_frequency_10003cf0(uint32_t module);
extern uint32_t gx8002_image_b_analog_ldo_digital_control_10008134(void);
extern int32_t gx8002_image_b_platform_read_10003edc(uint32_t selector,
                                                       void *result);
extern void gx8002_image_b_rtc_initialize_100081ec(void);
extern void gx8002_image_b_rtc_tick_initialize_10008978(void);
extern void gx8002_image_b_rtc_tick_configure_1000881c(void);
extern void gx8002_image_b_rtc_write_control_10008810(uint32_t value);
extern void gx8002_image_b_rtc_start_tick_10008800(void);
extern int gx8002_image_b_heap_log_10009934(const char *, ...);

static const uint32_t gx8002_image_b_ldo_millivolts_1001330c[12] = {
    950u, 924u, 897u, 871u, 845u, 819u,
    792u, 766u, 740u, 714u, 687u, 661u
};

void gx8002_image_b_main_initial_1000a8ec(void)
{
    gx8002_image_b_cache_initialize_100051a4();
    gx8002_image_b_dma_initialize_10004d14();
    gx8002_image_b_console_initialize_10004808(1u, 115200u);

    if (gx8002_image_b_platform_status_10003fb8() < 2u) {
        (void)gx8002_image_b_heap_log_10009934(
            "[LVP]Low-Power Voice Preprocess\n");
        (void)gx8002_image_b_heap_log_10009934(
            "[LVP]Copyright (C) 2001-2020 NationalChip Co., Ltd\n");
        (void)gx8002_image_b_heap_log_10009934(
            "[LVP]ALL RIGHTS RESERVED!\n");
        (void)gx8002_image_b_heap_log_10009934(
            "[LVP]Board Model: [%s]\n", "grus_gx8002b_dev_1v");
        (void)gx8002_image_b_heap_log_10009934(
            "[LVP]MCU Version: [%s]\n", "");
        (void)gx8002_image_b_heap_log_10009934(
            "[LVP]Release Ver: [0x%x]\n", UINT32_C(0x42555858));
        (void)gx8002_image_b_heap_log_10009934(
            "[LVP]Build Date : [%s]\n", "2026-03-26, 17:07:19");

        uint32_t flash = gx8002_image_b_flash_probe_10007fac(
            0u, 0u, UINT32_C(6144000), 2048u);
        uint32_t flash_id = gx8002_image_b_flash_info_10008018(flash, 2u);
        if (flash_id == UINT32_C(0x00854012) ||
            flash_id == UINT32_C(0x00856013)) {
            (void)gx8002_image_b_heap_log_10009934(
                "[LVP]Flash vendor:[%s]\n", "PUYA");
        } else if (flash_id == UINT32_C(0x001c3812) ||
                   flash_id == UINT32_C(0x001c3813)) {
            (void)gx8002_image_b_heap_log_10009934(
                "[LVP]Flash vendor:[%s]\n", "ESMT");
        } else if (flash_id == UINT32_C(0x005e3414)) {
            (void)gx8002_image_b_heap_log_10009934(
                "[LVP]Flash vendor:[%s]\n", "ZBIT");
        }
        (void)gx8002_image_b_heap_log_10009934(
            "[LVP]Flash type:  [%s]\n",
            gx8002_image_b_flash_type_1000800c(flash));
        (void)gx8002_image_b_heap_log_10009934(
            "[LVP]Flash ID:    [%#x]\n", flash_id);
        (void)gx8002_image_b_heap_log_10009934(
            "[LVP]Flash size:  [%d Byte]\n",
            gx8002_image_b_flash_info_10008018(flash, 3u));
        (void)gx8002_image_b_heap_log_10009934(
            "[LVP]CPU   Freq:  [%d Hz][fix]\n",
            gx8002_image_b_clock_frequency_10003cf0(10u));
        (void)gx8002_image_b_heap_log_10009934(
            "[LVP]SRAM  Freq:  [%d Hz]\n",
            gx8002_image_b_clock_frequency_10003cf0(6u));
        (void)gx8002_image_b_heap_log_10009934(
            "[LVP]NPU   Freq:  [%d Hz]\n",
            gx8002_image_b_clock_frequency_10003cf0(12u));
        (void)gx8002_image_b_heap_log_10009934(
            "[LVP]FLASH Freq:  [%d Hz]\n",
            gx8002_image_b_clock_frequency_10003cf0(13u));
        if (gx8002_image_b_analog_ldo_digital_control_10008134() == 2u) {
            (void)gx8002_image_b_heap_log_10009934(
                "[LVP]enable bypass core Ldo\n");
        } else {
            uint8_t trim_byte;
            (void)gx8002_image_b_platform_read_10003edc(8u, &trim_byte);
            uint32_t trim = (uint32_t)trim_byte & 15u;
            int32_t millivolts = trim < 12u ?
                (int32_t)gx8002_image_b_ldo_millivolts_1001330c[trim] : -1;
            (void)gx8002_image_b_heap_log_10009934(
                "[LVP]Ldo   Trim:  [%d mV]\n", millivolts);
        }

        gx8002_image_b_rtc_initialize_100081ec();
        gx8002_image_b_rtc_tick_initialize_10008978();
        gx8002_image_b_rtc_tick_configure_1000881c();
        gx8002_image_b_rtc_write_control_10008810(0u);
        gx8002_image_b_rtc_start_tick_10008800();
    }

    gx8002_image_b_platform_retention_10004ffc();
    gx8002_image_b_gpio_initialize_1000482c();
    gx8002_image_b_spi_master_registry_initialize_10008204();
    gx8002_image_b_board_devices_initialize_100085ac();
    (void)gx8002_image_b_pmu_initialize_1000a744();
}
