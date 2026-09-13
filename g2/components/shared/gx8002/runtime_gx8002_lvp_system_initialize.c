/* SPDX-License-Identifier: MIT */
/* Recovered LvpSystemInit; lvp_system_init.c at upstream commit
 * 8bf9ee5cb6eeb226011e61c15fa4981b83b93bd5. Diagnostics are named separately
 * so each required data range can be reconstructed and accounted for. */
#include <stdint.h>
extern void gx_cache_init(void), gx_dma_init(void);
extern int gx_console_init(unsigned, unsigned);
extern unsigned gx_pmu_get_wakeup_source(void);
extern void *gx_spi_flash_probe(unsigned,unsigned,unsigned,unsigned);
extern unsigned gx_spi_flash_getinfo(void *,unsigned);
extern const char *gx_spi_flash_gettype(void *);
extern int gx_clock_get_module_frequence(unsigned), gx_analog_get_ldo_dig_ctrl(void);
extern int gx_pmu_ctrl_get(unsigned,void *);
extern void LvpPrintCtcKwsList(void), gx_gpio_init(void), BoardInit(void);
extern void gx_rtc_init(void), gx_rtc_set_tick(unsigned), gx_rtc_start_tick(void);
extern void gx_timer_init(void), gx_irq_init(void), device_list_init(void), spi_master_v3_probe(void);
extern int open_cfw_gx8002_power_initialize(void);
extern int printf(const char *,...);
extern const char sys_title[], sys_copyright[], sys_rights[], sys_board[], sys_board_format[];
extern const char sys_version[], sys_version_format[], sys_release_format[], sys_date[], sys_date_format[];
extern const char sys_puya[], sys_esmt[], sys_zbit[], sys_vendor_format[], sys_type_format[], sys_id_format[], sys_size_format[];
extern const char sys_cpu_format[], sys_sram_format[], sys_npu_format[], sys_flash_format[], sys_bypass[], sys_trim_format[];
extern const int16_t sys_trim_millivolts[12];
void open_cfw_gx8002_lvp_system_initialize(void)
{
    gx_cache_init();
    gx_dma_init();
    gx_console_init(1,115200);
    if (gx_pmu_get_wakeup_source()<2) {
        printf(sys_title); printf(sys_copyright); printf(sys_rights);
        printf(sys_board_format,sys_board); printf(sys_version_format,sys_version);
        printf(sys_release_format,UINT32_C(0x42555858)); printf(sys_date_format,sys_date);
        void *flash=gx_spi_flash_probe(0,0,6144000,2048);
        unsigned id=gx_spi_flash_getinfo(flash,2);
        if(id==0x854012 || id==0x856013) printf(sys_vendor_format,sys_puya);
        if(id==0x1c3812 || id==0x1c3813) printf(sys_vendor_format,sys_esmt);
        if(id==0x5e3414) printf(sys_vendor_format,sys_zbit);
        printf(sys_type_format,gx_spi_flash_gettype(flash));
        printf(sys_id_format,id); printf(sys_size_format,gx_spi_flash_getinfo(flash,3));
        printf(sys_cpu_format,gx_clock_get_module_frequence(10));
        printf(sys_sram_format,gx_clock_get_module_frequence(6));
        printf(sys_npu_format,gx_clock_get_module_frequence(12));
        printf(sys_flash_format,gx_clock_get_module_frequence(13));
        if(gx_analog_get_ldo_dig_ctrl()==2) printf(sys_bypass);
        else {
            uint32_t config;
            gx_pmu_ctrl_get(8,&config);
            unsigned trim=config&15;
            printf(sys_trim_format,trim<12 ? sys_trim_millivolts[trim] : -1);
        }
        LvpPrintCtcKwsList(); gx_gpio_init(); BoardInit();
        gx_rtc_init(); gx_rtc_set_tick(0); gx_rtc_start_tick();
    }
    gx_timer_init(); gx_irq_init(); device_list_init(); spi_master_v3_probe();
    open_cfw_gx8002_power_initialize();
}
