/* Stock R1 application 0x5d5e0: BLE receive dispatch and notification reports.
 * Output-slot and provider frames are private to their C ABI contract;
 * see the replay receipt for the remaining native/C frame difference. */
#include <stdint.h>
extern unsigned char r1_native_bae8_service[];
extern uint32_t r1_advertising_configuration_byte_get(void);
extern uint32_t r1_bae8_bc_rx_enqueue(uint32_t,uint32_t,const void *,uint32_t);
extern uint32_t r1_factory_thread_message_encode(uint32_t,uint32_t,const void *,uint32_t);
extern uint32_t r1_eus_rx_reassembly(uint32_t,uint32_t,const void *,uint32_t);
extern void r1_glasses_connection_role_assign(uint32_t);
extern int32_t r1_native_delayed_cancel(void (*)(uint32_t),uint32_t);
extern uint32_t r1_native_bae8_context_get(void *,uint32_t,void *volatile *);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_1(uint32_t,const char *,uint32_t);
extern void nrf_log_frontend_std_2(uint32_t,const char *,uint32_t,uint32_t);
static uint32_t half(const volatile uint8_t *p){return *(const volatile uint16_t *)p;}
static const void *pointer(const volatile uint8_t *p){return *(const void *volatile const *)p;}
void r1_bae8_rx_timeout_noop(uint32_t argument){(void)argument;}
void r1_bae8_event_route(const void *event)
{
    const volatile uint8_t *e=event;
    uint32_t type=e[0];
    const char *ring,*sdk;
    uint32_t result;
    if (type==2) {
        uint32_t factory=r1_advertising_configuration_byte_get();
        uint32_t length=half(e+20);
        uint32_t connection=half(e+8);
        const void *data=pointer(e+16);
        result=factory==85 ? r1_factory_thread_message_encode(connection,1,data,length)
                           : r1_bae8_bc_rx_enqueue(connection,1,data,length);
        if (!result) return;
        ring="[RING]bc rx state = %d";sdk="bc rx state = %d";
    } else if (type==3) {
        (void)r1_native_delayed_cancel(r1_bae8_rx_timeout_noop,0);
        uint32_t length=half(e+20);
        uint32_t connection=half(e+8);
        const void *data=pointer(e+16);
        result=r1_eus_rx_reassembly(connection,2,data,length);
        if (!result) return;
        ring="[RING]eus rx state = %d";sdk="eus rx state = %d";
    } else if (type>=6 && type<=9) {
        uint32_t eus=type>=8;
        if (!eus) r1_glasses_connection_role_assign(half(e+8));
        void *volatile client;
        uint32_t connection=half(e+8);
        void *storage=*(void *volatile *)(r1_native_bae8_service+40);
        uint32_t status=r1_native_bae8_context_get(storage,connection,&client);
        if (status) {
            ring="[RING]Link context for 0x%02X connection handle could not be fetched.";
            sdk="Link context for 0x%02X connection handle could not be fetched.";
            if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
                r1_structured_log_format(0x04400000,ring,ring,half(e+8));
            if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_1(0x001c0001,sdk,half(e+8));
            return;
        }
        ring=eus ? "[RING]conn_handle = %d, p_client->is_eus_notification_enabled = %d"
                 : "[RING]conn_handle = %d, p_client->is_glasses_notification_enabled = %d";
        sdk=eus ? "conn_handle = %d, p_client->is_eus_notification_enabled = %d"
                : "conn_handle = %d, p_client->is_glasses_notification_enabled = %d";
        if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u)) {
            uint32_t enabled=((volatile uint8_t *)client)[eus];
            r1_structured_log_format(0x0c800000,ring,ring,half(e+8),enabled);
        }
        if (r1_structured_log_mode_get()&2u) {
            uint32_t connection=half(e+8);
            uint32_t enabled=((volatile uint8_t *)client)[eus];
            nrf_log_frontend_std_2(0x001c0003,sdk,connection,enabled);
        }
        return;
    } else return;
    if ((r1_structured_log_mode_get()&1u)||(r1_structured_log_mode_get()&4u))
        r1_structured_log_format(0x04400000,ring,ring,result);
    if (r1_structured_log_mode_get()&2u) nrf_log_frontend_std_1(0x001c0001,sdk,result);
}
