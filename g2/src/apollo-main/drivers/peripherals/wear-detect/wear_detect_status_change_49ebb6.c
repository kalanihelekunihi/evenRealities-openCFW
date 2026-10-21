/* Native WearDetect_HandleStatusChange 0x49ebb6..0x49ed04. */
#include <stdint.h>
extern uint32_t audio_wear_detect_get_enable_49ead8(void);
extern void audio_ble_master_emit_ring_event(uint8_t);
extern uint32_t audio_wear_child_46b0ec(void);
extern void audio_wear_child_502bf0(uint32_t);
extern void audio_wear_child_474100(void);
extern void audio_wear_child_47432c(void);
extern void audio_wear_child_46805a(uint32_t);
extern void audio_wear_child_47e320(uint32_t);
extern uint8_t audio_uart_device_role_get(void);
extern void audio_uart_display_housekeep(void);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="wear.detect";
static const char path[]="D:\\01_workspace\\s200_ap510b_iar_git\\app\\ux\\ux_wear_detect\\ux_wear_detect.c";
static const char function[]="WearDetect_HandleStatusChange";
static const char wear[]="WEAR!!!";
static const char wear_short[]="[wear.detect]WEAR!!!";
static const char unwear[]="UNWEAR!!!";
static const char unwear_short[]="[wear.detect]UNWEAR!!!";
static const char invalid[]="wear detect state is invalid, state=%d";
static const char invalid_short[]="[wear.detect]wear detect state is invalid, state=%d";
uint32_t audio_wear_detect_handle_status_change_49ebb6(uint32_t requested) {
    uint32_t state=(uint8_t)requested;
    if(state==2u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,0x63u,wear);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0c000000u,wear_short,wear_short);
        audio_ble_master_emit_ring_event(2u);
        if(audio_wear_child_46b0ec()==1u) {
            if(audio_wear_detect_get_enable_49ead8()==1u)
                audio_wear_child_502bf0(3u);
            audio_wear_child_474100();
        }
        if(audio_uart_device_role_get()==1u)
            audio_wear_child_46805a(0u);
        if(audio_wear_detect_get_enable_49ead8()==1u)
            audio_wear_child_47e320(1u);
    } else if(state==1u) {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(3u,module,path,function,0x76u,unwear);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x0c000000u,unwear_short,unwear_short);
        if(audio_wear_detect_get_enable_49ead8()==1u) {
            audio_wear_child_47432c();
            audio_wear_child_47e320(0u);
        } else if(audio_wear_child_46b0ec()==1u)
            audio_wear_child_474100();
    } else {
        if((audio_log_flags()&2u)!=0u)
            audio_log_extended(2u,module,path,function,0x7fu,invalid,state);
        if((audio_log_flags()&1u)!=0u||(audio_log_flags()&4u)!=0u)
            (void)compressed_log_output(0x08400000u,invalid_short,invalid_short,state);
    }
    audio_uart_display_housekeep();
    return 0u;
}
