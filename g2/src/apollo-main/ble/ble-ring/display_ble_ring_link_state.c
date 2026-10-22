/* Native _ringLinkStateName 0x49f828 and _SetRingLinkState 0x49f870. */
#include <stdint.h>
extern volatile uint8_t audio_ble_ring_link_state; /* RAM 0x20074f85 */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.master";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_central.c";
static const char function[]="_SetRingLinkState";
static const char no_reason[]="";
/* Stock 0x49F828 (_ringLinkStateName) */
const char *audio_ble_ring_link_state_name(uint8_t state) {
    switch(state) {
    case 0u:return "IDLE";
    case 1u:return "OPENING";
    case 2u:return "CONNECTED";
    case 3u:return "LOCAL_DISCONNECTING";
    case 4u:return "SWITCH_DISCONNECTING";
    case 5u:return "CANCELLING";
    case 6u:return "UNPAIRING";
    default:return "?";
    }
}
/* Stock 0x49F870 (_SetRingLinkState) */
void audio_ble_set_ring_link_state(uint8_t next,const char *reason) {
    uint8_t previous=audio_ble_ring_link_state;
    if(next==previous) {
        if(audio_log_level()&2u)
            audio_log_extended(4u,module,source,function,0x9cu,
                "[RingLink] stay %s reason=\"%s\"",
                audio_ble_ring_link_state_name(next),reason?reason:no_reason);
        if((audio_log_level()&1u)||(audio_log_level()&4u))
            (void)compressed_log_output(0x10800000u,
                "[ble.master][RingLink] stay %s reason=\"%s\"",
                "[ble.master][RingLink] stay %s reason=\"%s\"",
                audio_ble_ring_link_state_name(next),reason?reason:no_reason);
    } else {
        if(audio_log_level()&2u)
            audio_log_extended(3u,module,source,function,0xa2u,
                "[RingLink] %s -> %s reason=\"%s\"",
                audio_ble_ring_link_state_name(previous),
                audio_ble_ring_link_state_name(next),reason?reason:no_reason);
        if((audio_log_level()&1u)||(audio_log_level()&4u))
            (void)compressed_log_output(0x0cc00000u,
                "[ble.master][RingLink] %s -> %s reason=\"%s\"",
                "[ble.master][RingLink] %s -> %s reason=\"%s\"",
                audio_ble_ring_link_state_name(previous),
                audio_ble_ring_link_state_name(next),reason?reason:no_reason);
        audio_ble_ring_link_state=next;
    }
}
