/* Stock R1 application 0x4e66c: service setup and two transport credit pools.
 * The aligned configuration preserves its escaping caller-SP-minus-16 slot. */
#include <stdint.h>
extern unsigned char r1_native_bae8_service[];
extern void *volatile r1_ble_link_semaphores[2];
extern uint32_t r1_bae8_service_configuration(void *,const void *);
extern void r1_bae8_event_route(const void *);
extern void *osSemaphoreNew(uint32_t,uint32_t,const void *);
extern void r1_adc_error(uint32_t);
extern uint32_t r1_structured_log_mode_get(void);
extern uint32_t r1_structured_log_format(uint32_t,const char *,const char *,...);
extern void nrf_log_frontend_std_0(uint32_t,const char *);
static const char ring[]="[RING]Failed to create eus tx semaphore";
static const char sdk[]="Failed to create eus tx semaphore";
void r1_bae8_transport_provider_configuration(void)
{
    _Alignas(8) void (*configuration)(const void *)=r1_bae8_event_route;
    uint32_t status=r1_bae8_service_configuration(r1_native_bae8_service,&configuration);
    if (status) r1_adc_error(status);
    r1_ble_link_semaphores[0]=osSemaphoreNew(4,4,0);
    void *second=osSemaphoreNew(4,4,0);
    r1_ble_link_semaphores[1]=second;
    if (!r1_ble_link_semaphores[0] || !second) {
        if ((r1_structured_log_mode_get()&1u)||
            (r1_structured_log_mode_get()&4u))
            r1_structured_log_format(0x04000000,ring,ring);
        if (r1_structured_log_mode_get()&2u)
            nrf_log_frontend_std_0(0x001c0001,sdk);
        r1_adc_error(4);
    }
}
