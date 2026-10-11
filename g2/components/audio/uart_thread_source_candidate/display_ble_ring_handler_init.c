/* Native APP_BleRingHandlerInit 0x4c4810 and four service handles. */
#include <stdint.h>
struct audio_ble_ring_handler_state {
    uint8_t active;
    uint8_t handler;
    uint16_t reserved;
    uint16_t *service_handles;
    uint16_t initialized;
};
extern struct audio_ble_ring_handler_state audio_ble_ring_handler_state; /* RAM 0x20074074 */
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="ble.ring";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\profiles\\ring\\profile_ring.c";
static const char function[]="APP_BleRingHandlerInit";
static const char short_text[]="[ble.ring]APP_BleRingHandlerInit";
void audio_ble_ring_handler_init(uint8_t handler,uint8_t *storage) {
    if(audio_log_level()&2u)
        audio_log_extended(4u,module,source,function,0x98u,function);
    if((audio_log_level()&1u)||(audio_log_level()&4u))
        (void)compressed_log_output(0x10000000u,short_text,short_text);
    audio_ble_ring_handler_state.handler=handler;
    audio_ble_ring_handler_state.active=0u;
    audio_ble_ring_handler_state.initialized=1u;
    audio_ble_ring_handler_state.service_handles=(uint16_t *)(void *)storage;
    uint16_t *handles=audio_ble_ring_handler_state.service_handles;
    handles[0]=0x10u;handles[1]=0x12u;handles[2]=0x13u;
}
