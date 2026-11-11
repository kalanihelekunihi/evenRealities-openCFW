#include <stdint.h>

/* Native 0x323028..0x3230de: report the LL connection-complete event (code
 * 5) with status, role, peer address type and addresses (peer a4/a5, local
 * RPA s0/s1, peer RPA a6/a7) and, for a known record, its connection
 * parameters (+0x20, +0x24, +43). After a successful completion (status 0)
 * with feature bit 6 of 0x805a95 set, LL event 33 follows with byte s3.
 * Returns the last event result, or 33 when no follow-up is sent. */
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern uintptr_t opencfw_em9305_radio_address_write_3045e8(uintptr_t,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_ll_event_callback_30e79c(uintptr_t);

struct ll_connection_event {
    uint16_t handle;
    uint8_t code;
    uint8_t status;
    uint8_t status_again;
    uint8_t reserved;
    uint16_t handle_again;
    uint8_t role;
    uint8_t peer_type;
    uint8_t peer_address[6];
    uint32_t interval;
    uint16_t latency;
    uint8_t accuracy;
    uint8_t local_rpa[6];
    uint8_t peer_rpa[6];
    uint8_t clock_accuracy;
    uint16_t timeout;
} __attribute__((aligned(4)));

struct ll_event_33 {
    uint16_t handle;
    uint16_t code;
    uint16_t handle_again;
    uint8_t value;
};

uint32_t opencfw_em9305_mode_event_323028(uint32_t handle, uint32_t role, uintptr_t record,
                                          uint32_t peer_type, uint32_t peer_low, uint32_t peer_high,
                                          uint32_t peer_rpa_low, uint32_t peer_rpa_high,
                                          uint32_t local_rpa_low, uint32_t local_rpa_high,
                                          uint32_t status, uint32_t follow_up,
                                          uint32_t clock_accuracy, uint32_t timeout)
{
    struct ll_connection_event event;
    event.role = (uint8_t)role;
    event.handle_again = (uint16_t)handle;
    event.handle = (uint16_t)handle;
    event.peer_type = (uint8_t)peer_type;
    event.code = 5u;
    event.status_again = (uint8_t)status;
    event.status = (uint8_t)status;
    (void)opencfw_em9305_memset(event.peer_address, 0u, 25u);
    event.timeout = (uint16_t)timeout;
    event.clock_accuracy = (uint8_t)clock_accuracy;
    if (record != 0u) {
        event.interval = *(volatile uint32_t *)(record + 0x20u);
        event.latency = *(volatile uint16_t *)(record + 0x24u);
        event.accuracy = *(volatile uint8_t *)(record + 43u);
    }
    (void)opencfw_em9305_radio_address_write_3045e8((uintptr_t)event.peer_address, peer_low, peer_high);
    (void)opencfw_em9305_radio_address_write_3045e8((uintptr_t)event.peer_rpa, peer_rpa_low, peer_rpa_high);
    (void)opencfw_em9305_radio_address_write_3045e8((uintptr_t)event.local_rpa, local_rpa_low, local_rpa_high);
    uint32_t result = opencfw_em9305_ll_event_callback_30e79c((uintptr_t)&event);
    if (status != 0u) return result;
    if ((*(volatile uint8_t *)(uintptr_t)0x805a95u & 0x40u) == 0u) return 33u;
    struct ll_event_33 follow;
    follow.code = 33u;
    follow.handle_again = (uint16_t)handle;
    follow.handle = (uint16_t)handle;
    follow.value = (uint8_t)follow_up;
    return opencfw_em9305_ll_event_callback_30e79c((uintptr_t)&follow);
}
