/* Apollo uLED driver identify 0x4c9d9c..0x4c9f31, official two-entry ROM section. */
#include <stdint.h>
extern const uint8_t display_driver_uled_option_type1[]; /* native 0x70afe4 */
extern const uint8_t display_driver_uled_option_type0[]; /* native 0x70b024 */
extern void * volatile display_driver_uled_instance; /* SRAM 0x20074530 */
extern uint32_t audio_delay(uint32_t); /* selected 0x449376 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const uint8_t *const options[2]={display_driver_uled_option_type1,display_driver_uled_option_type0};
static const char module[]="driver.uled";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\drv_mspi_uled.c";
static const char function[]="uled_driver_identify";
static const char no_match[]=" Error - Failed to find uled_driver_opt.\r\n";
static const char no_match_compact[]="[driver.uled] Error - Failed to find uled_driver_opt.\r\n";
static const char found[]="find uled_driver_opt type %d index %d \r\n";
static const char found_compact[]="[driver.uled]find uled_driver_opt type %d index %d \r\n";
uint32_t display_driver_uled_config_mode_4c9d9c(uint32_t requested) {
    uint8_t type=(uint8_t)requested;
    for(uint32_t i=0;i<2u;++i) {
        const uint8_t *option=options[i];
        if(option!=0 && option[0x3cu]==type) {
            display_driver_uled_instance=(void *)option;
            if((audio_log_flags()&2u)!=0u)
                audio_log_extended(3u,module,path,function,0x76u,found,type,i);
            if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
                (void)compressed_log_output(0x0c800000u,found_compact,found_compact,type,i);
            return 0u;
        }
    }
    (void)audio_delay(1u);
    if((audio_log_flags()&2u)!=0u)
        audio_log_extended(1u,module,path,function,0x7cu,no_match);
    if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
        (void)compressed_log_output(0x04000000u,no_match_compact,no_match_compact);
    return UINT32_MAX;
}
