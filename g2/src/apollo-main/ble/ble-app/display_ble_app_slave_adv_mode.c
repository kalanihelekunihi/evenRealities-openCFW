/* Pinned Cordio app_slave_leg.c appSlaveAdvMode, native Main 0x4b2bde.
 * Callback bodies and live appSlaveCb are separate genuine interfaces. */
#include <stdint.h>
extern uint8_t audio_ble_subsystem_link_state_200719c8[];
extern volatile uint8_t audio_ble_trace_level_cell; /* native 0x2007502f */
extern void appSlaveLegAdvStop(void *event);
extern void appSlaveLegAdvRestart(void *event);
extern int32_t audio_ble_hci_vendor_compare_44b610(const void *,const void *,uint32_t);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern void audio_ble_wsf_trace(const char *,const char *,...);

static uint32_t get32(const uint8_t *p) {
    return (uint32_t)p[0]|((uint32_t)p[1]<<8u)|
           ((uint32_t)p[2]<<16u)|((uint32_t)p[3]<<24u);
}
static void set32(uint8_t *p,uint32_t v) {
    p[0]=(uint8_t)v;p[1]=(uint8_t)(v>>8u);
    p[2]=(uint8_t)(v>>16u);p[3]=(uint8_t)(v>>24u);
}
static void invalid_mode_log(uint8_t level) {
    static const char module[]="APP";
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\app_slave_leg.c";
    static const char name[]="appSlaveAdvMode";
    static const char message[]="Invalid DM advertising mode; mode configured as extended";
    if (audio_log_flags()&2u)
        audio_log_extended(level,module,source,name,0x142u,message);
}

int appSlaveAdvMode(void)
{
    static const char warn[]="WARN",error[]="ERR",info[]="INFO",hci[]="HCI",app[]="APP";
    static const char message[]="Invalid DM advertising mode; mode configured as extended";
    uint8_t *const state=audio_ble_subsystem_link_state_200719c8;
    uint32_t stop=get32(state+0x78u);
    if (!stop) {
        set32(state+0x78u,(uint32_t)(uintptr_t)appSlaveLegAdvStop);
        set32(state+0x7cu,(uint32_t)(uintptr_t)appSlaveLegAdvRestart);
        return 1;
    }
    if (stop==(uint32_t)(uintptr_t)appSlaveLegAdvStop) return 1;
    if (!audio_ble_trace_level_cell ||
        audio_ble_hci_vendor_compare_44b610(warn,error,3u)!=0) {
        if (!audio_ble_trace_level_cell ||
            audio_ble_hci_vendor_compare_44b610(warn,warn,4u)!=0) {
            if (!audio_ble_trace_level_cell ||
                audio_ble_hci_vendor_compare_44b610(warn,info,4u)!=0) {
                if (!audio_ble_trace_level_cell) {
                    if (!audio_ble_trace_level_cell ||
                        audio_ble_hci_vendor_compare_44b610(app,hci,3u)!=0)
                        audio_ble_wsf_trace(warn,message);
                } else invalid_mode_log(4u);
            } else invalid_mode_log(3u);
        } else invalid_mode_log(2u);
    } else invalid_mode_log(1u);
    return 0;
}
