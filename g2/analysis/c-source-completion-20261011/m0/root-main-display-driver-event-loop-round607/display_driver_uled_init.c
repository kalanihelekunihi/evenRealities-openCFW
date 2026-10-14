/* Apollo uLED startup wrapper 0x4c9f32..0x4c9fb3. Candidate. */
#include <stdint.h>
extern uint8_t *audio_ble_hci_radio_mode_state_50938e(uint32_t); /* selected 0x50938e */
extern uint32_t display_driver_uled_config_mode_4c9d9c(uint32_t); /* lower body pending */
extern void * volatile display_driver_uled_instance; /* SRAM 0x20074530 */
extern void display_driver_uled_row_callback_4ca2ac(void); /* callback body pending */
extern uint8_t display_driver_uled_work_buffer[]; /* native SRAM 0x203795a0, size gated */
void *display_driver_uled_context=(void *)(uintptr_t)0x20094400u; /* decoded SRAM cell 0x200007b8 */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="driver.uled";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\driver\\uled\\drv_mspi_uled.c";
static const char function[]="uled_mspi_init";
static const char text[]="Error - Failed to find uled driver.\r\n";
static const char compact[]="[driver.uled]Error - Failed to find uled driver.\r\n";
uint32_t display_driver_init_4c9f32(void) {
    uint8_t mode=*audio_ble_hci_radio_mode_state_50938e(1u);
    (void)display_driver_uled_config_mode_4c9d9c(mode==6u);
    uint8_t *driver=(uint8_t *)display_driver_uled_instance;
    if(driver==0) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(1u,module,path,function,0x90u,text);
        if((audio_log_flags()&1u)!=0u || (audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x04000000u,compact,compact);
        return UINT32_MAX;
    }
    uint32_t (*initialize)(void (*)(void),void *,void *)=
        *(uint32_t (**)(void (*)(void),void *,void *))(void *)(driver+8u);
    return initialize(display_driver_uled_row_callback_4ca2ac,
                      display_driver_uled_context,display_driver_uled_work_buffer);
}
