/* Native Cordio profileAnccProcMsg 0x4bf780. The ANCC action list and
 * callback pointer are live product RAM; their producer remains separate. */
#include <stdint.h>
extern uint8_t DmConnRole(uint8_t);
extern void audio_ble_ancc_value_update_4befce(const void *);
extern void audio_ble_ancc_conn_open_4bea04(uint8_t,uint32_t);
extern void audio_ble_ancc_conn_close_4bea14(void);
extern uint32_t audio_ble_ancc_action_pop_4bea36(void);
extern void audio_ble_ancc_get_notification_attribute_4beae8(uint32_t,uint32_t);
extern uint32_t audio_ble_ancc_no_connection_active_4bea24(void);
extern void audio_ble_ancc_get_next_delayed_4bea7a(void);
extern void audio_event_loop_push_delayed(void (*)(void),uint32_t,uint32_t);
extern uint32_t audio_event_loop_remove_delayed(void (*)(void));
extern uint8_t *audio_ble_ancc_service_context; /* RAM pointer cell 0x200748a0 */
extern uint8_t audio_ble_ancc_state[]; /* RAM 0x200695c8 */
static uint32_t rd32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|
    ((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
/* Stock 0x4BF780 (profileAnccProcMsg) */
void audio_ble_ancc_message(uint8_t handler,void *message){
    (void)handler;
    if(message==0)return;
    uint8_t *m=(uint8_t *)message;
    uint8_t event=m[2u];
    if(event==5u||event==13u||event==14u){audio_ble_ancc_value_update_4befce(m);return;}
    if(event==9u||event==10u)return;
    if(event==0x27u){
        if(DmConnRole(m[0u])==1u)
            audio_ble_ancc_conn_open_4bea04(m[0u],(uint32_t)(uintptr_t)audio_ble_ancc_service_context);
        return;
    }
    if(event==0x28u){
        if(DmConnRole(m[0u])==1u)audio_ble_ancc_conn_close_4bea14();
        return;
    }
    if(event!=0xa2u)return;
    if(audio_ble_ancc_action_pop_4bea36()!=0u){
        uint16_t index=(uint16_t)((uint32_t)audio_ble_ancc_state[8u]|
                                  ((uint32_t)audio_ble_ancc_state[9u]<<8));
        audio_ble_ancc_get_notification_attribute_4beae8(
            rd32(audio_ble_ancc_state+4u),
            rd32(audio_ble_ancc_state+0x20u+(uint32_t)index*12u));
        if(audio_ble_ancc_no_connection_active_4bea24()==0u)
            audio_event_loop_push_delayed(audio_ble_ancc_get_next_delayed_4bea7a,0xa2u,200u);
    }else (void)audio_event_loop_remove_delayed(audio_ble_ancc_get_next_delayed_4bea7a);
}
