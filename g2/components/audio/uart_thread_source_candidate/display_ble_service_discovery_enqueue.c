/* Product APP_StartServiceDiscovery 0x5354c2, currently referenced by
 * audio_ble_comm_disconnect_delayed. Native diagnostics and message effects. */
#include <stdint.h>
extern void audio_event_loop_remove_delayed(void (*callback)(void));
extern uint8_t *audio_ble_pair_record(uint8_t connection);
extern void audio_ble_pair_record_clear_a(uint8_t *record,uint8_t flag);
extern void audio_ble_pair_record_clear_b(uint8_t *record,uint8_t flag);
extern uint8_t *WsfMsgAlloc(uint16_t length);
extern void WsfMsgSend(uint8_t handler,void *message);
extern uint8_t audio_ble_discovery_handler_id_20074f8a; /* live App handler */
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,...);
void audio_ble_comm_disconnect_delayed(uint8_t connection);
__attribute__((used,noinline)) static void service_discovery_body(uint8_t connection,uint32_t inherited_r4)
{
    static const char module[]="ble.disc";
    static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\ble\\app_ble_discovery.c";
    static const char function[]="APP_StartServiceDiscovery";
    static const char format[]="connId = %d, pMsg = 0x%x handlerId = 0x%x";
    static const char compact[]="[ble.disc]connId = %d, pMsg = 0x%x handlerId = 0x%x";
    static const char reset[]="[Service Discovery] Reset discovery status in APP_StartServiceDiscovery";
    static const char reset_compact[]="[ble.disc][Service Discovery] Reset discovery status in APP_StartServiceDiscovery";
    audio_event_loop_remove_delayed((void (*)(void))audio_ble_comm_disconnect_delayed);
    if (audio_log_flags()&2u)
        audio_log_extended(4u,module,source,function,0xd9u,format,connection,inherited_r4,audio_ble_discovery_handler_id_20074f8a);
    uint32_t flags=audio_log_flags();
    if ((flags&1u)||((flags=audio_log_flags())&4u))
        (void)compressed_log_output(0x10c00000u,compact,compact,connection,inherited_r4,audio_ble_discovery_handler_id_20074f8a);
    uint8_t *record=audio_ble_pair_record(connection);
    if (record) {
        audio_ble_pair_record_clear_a(record,0u);
        audio_ble_pair_record_clear_b(record,0u);
        if (audio_log_flags()&2u)
            audio_log_extended(4u,module,source,function,0xe1u,reset);
        flags=audio_log_flags();
        if ((flags&1u)||((flags=audio_log_flags())&4u))
            (void)compressed_log_output(0x10000000u,reset_compact);
    }
    uint8_t *message=WsfMsgAlloc(0x0cu);
    if (!message) return;
    message[2u]=0xa5u;
    message[0u]=connection;
    message[1u]=0u;
    WsfMsgSend(audio_ble_discovery_handler_id_20074f8a,message);
}

/* The stock entry forwards its incoming callee-saved R4 in the first log.
 * Capture it before the C compiler's prologue changes the register. */
__attribute__((naked)) void audio_ble_comm_disconnect_delayed(uint8_t connection __attribute__((unused)))
{
    __asm volatile("push {r4, lr}\nmov r1, r4\nbl service_discovery_body\npop {r4, pc}");
}
