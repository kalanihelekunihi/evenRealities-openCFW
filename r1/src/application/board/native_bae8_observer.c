/* R1 application 0x52b20: service-specific BLE dispatch and credit handling. */
#include <stdint.h>
#include "nrf_sdh_ble.h"

extern void *r1_ble_link_semaphore(uint32_t connection);
extern void r1_ble_flush_drain(void *semaphore);
extern void r1_ble_flush_bounded(void *semaphore,uint32_t count);
extern void *volatile r1_ble_link_semaphores[2];
/* These product handlers remain explicit dependencies until reconstructed. */
extern void r1_bae8_connection_event_plan_build(void *service,
                                              ble_evt_t const *event);
extern void r1_bae8_write_event_plan_build(void *service,
                                         ble_evt_t const *event);

void r1_bae8_raw_observer(ble_evt_t const *event,void *service)
{
    if (!service || !event) return;
    const volatile uint8_t *bytes=(const volatile uint8_t *)event;
    uint16_t id=*(const volatile uint16_t *)bytes;
    if (id==16) {
        r1_bae8_connection_event_plan_build(service,event);
        return;
    }
    if (id==80) {
        r1_bae8_write_event_plan_build(service,event);
        return;
    }
    if (id==17) {
        void *semaphore=r1_ble_link_semaphore(
            *(const volatile uint16_t *)(bytes+4));
        if (semaphore) {
            r1_ble_flush_drain(semaphore);
            return;
        }
        r1_ble_flush_drain(r1_ble_link_semaphores[0]);
        r1_ble_flush_drain(r1_ble_link_semaphores[1]);
        return;
    }
    if (id==87) {
        uint16_t connection=*(const volatile uint16_t *)(bytes+4);
        /* Stock consumes only the low byte, before calling the selector. */
        uint32_t count=bytes[6];
        void *semaphore=r1_ble_link_semaphore(connection);
        if (semaphore) {
            r1_ble_flush_bounded(semaphore,count);
            return;
        }
        r1_ble_flush_bounded(r1_ble_link_semaphores[0],count);
        r1_ble_flush_bounded(r1_ble_link_semaphores[1],count);
    }
}
