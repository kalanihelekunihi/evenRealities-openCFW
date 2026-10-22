/* Native OTA/EUS/ESS/EFS/NUS profile event bodies 0x4bdc0c..0x4be76c.
 * Their four-byte product state cells are shared with authenticated inits. */
#include <stdint.h>
extern uint8_t audio_ble_ota_handler_state[4];
extern uint8_t audio_ble_eus_handler_state[4];
extern uint8_t audio_ble_ess_handler_state[4];
extern uint8_t audio_ble_efs_handler_state[4];
extern uint8_t audio_ble_nus_handler_state[4];
extern uint8_t audio_dm_conn_role(uint8_t);
extern void audio_ble_ota_update(void *); /* 0x4bdb90 */
extern void audio_ble_eus_update(void *); /* 0x4bde4c */
extern void audio_ble_ess_update(void *); /* 0x4be228 */
extern void audio_ble_efs_update(void *); /* 0x4be3a4 */
extern void audio_ble_nus_update(void *); /* 0x4be6f0 */
extern void audio_ble_ota_disconnect(void); /* 0x448784 */
extern void audio_ble_ota_reset_event(uint32_t,uint32_t); /* 0x4d3534 */
extern void audio_ble_ota_connection_changed(uint8_t); /* 0x4bb04a */
extern void audio_event_loop_push_delayed(void (*)(void),uint32_t,uint32_t);
extern void audio_ble_ota_delayed_callback(void); /* native function 0x4bdb38 */
extern void audio_ble_profile_write_event(uint8_t,uint16_t,uint16_t,uint32_t); /* 0x533ed8 */

static uint16_t half(const uint8_t *p,unsigned n) {
    return (uint16_t)p[n]|(uint16_t)((uint16_t)p[n+1u]<<8);
}
static uint32_t word(const uint8_t *p,unsigned n) {
    return (uint32_t)p[n]|((uint32_t)p[n+1u]<<8)|
           ((uint32_t)p[n+2u]<<16)|((uint32_t)p[n+3u]<<24);
}
static void profile_event(uint8_t *state,const uint8_t *message,uint8_t write_event,
                          uint16_t attribute,void (*update)(void *)) {
    uint8_t event=message[2];
    if(event==0x12u)state[3]=(message[3]==0u);
    else if(event==0x14u)update((void *)message);
    else if(event!=0x27u) {
        if(event==0x28u) {
            if(audio_dm_conn_role((uint8_t)half(message,0u))==1u)state[0]=0u;
        } else if(event==write_event) {
            state[3]=0u;
            audio_ble_profile_write_event((uint8_t)half(message,0u),attribute,
                                          half(message,8u),word(message,4u));
        }
    }
}
/* Stock 0x004BDC0C (evenOtaProcMsg) */
void audio_ble_ota_message_body(void *raw) {
    const uint8_t *m=(const uint8_t *)raw;
    uint8_t event=m[2];
    if(event==0xa0u)audio_ble_ota_reset_event(0u,0u);
    else if(event==0xa1u) {
        audio_ble_ota_connection_changed(audio_ble_ota_handler_state[0]);
        audio_event_loop_push_delayed(audio_ble_ota_delayed_callback,0u,200u);
    } else if(event==0x28u) {
        if(audio_dm_conn_role((uint8_t)half(m,0u))==1u) {
            audio_ble_ota_handler_state[0]=0u;
            audio_ble_ota_disconnect();
        }
    } else profile_event(audio_ble_ota_handler_state,m,0xa7u,0x824u,audio_ble_ota_update);
}
/* Stock 0x4BDED6 (eusProcMsg) */
void audio_ble_eus_message_body(void *raw) {
    profile_event(audio_ble_eus_handler_state,(const uint8_t *)raw,0xa8u,0x844u,audio_ble_eus_update);
}
/* Stock 0x4BE24E (essProcMsg) */
void audio_ble_ess_message_body(void *raw) {
    profile_event(audio_ble_ess_handler_state,(const uint8_t *)raw,0xa9u,0x864u,audio_ble_ess_update);
}
/* Stock 0x4BE420 (efsProcMsg) */
void audio_ble_efs_message_body(void *raw) {
    profile_event(audio_ble_efs_handler_state,(const uint8_t *)raw,0xaau,0x884u,audio_ble_efs_update);
}
/* Stock 0x4BE76C (nusProcMsg) */
void audio_ble_nus_message_body(void *raw) {
    profile_event(audio_ble_nus_handler_state,(const uint8_t *)raw,0xabu,0x8a4u,audio_ble_nus_update);
}
