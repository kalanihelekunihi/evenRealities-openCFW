#include <stdint.h>

/* Native 0x318c1c..0x318d7e: drain the received-packet queue (native
 * 0x325350). Packets of unused connections are released and counted
 * (0x805ab5, under the critical section). For encrypted connections (+109)
 * the optional MIC hook at 0x8051dc may reject the packet (terminate with
 * 0x48); otherwise the two supervision timers (+496/+476) are restarted.
 * Data PDUs (LLID 1/2) go to native 0x325324 unless the connection is
 * stopping (+403, terminate 0x48); control PDUs (LLID 3) go to the hook at
 * 0x80280c; other PDUs go to the registered handler (*0x805cd8 +0x14) when
 * present. Afterwards collect and clear every connection's pending flag
 * (+377) under the critical section and report the set ones to the
 * notifier at 0x805b14. */
extern uintptr_t opencfw_em9305_child_325350(uintptr_t);
extern uint32_t opencfw_em9305_short_header_decode_32dedc(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_wsf_timer_start_ms(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_receive_packet_release_3253bc(uintptr_t);
extern uint32_t opencfw_em9305_wsf_critical_enter(void);
extern uint32_t opencfw_em9305_wsf_critical_exit(void);
extern uint32_t opencfw_em9305_receive_terminate_325c08(uintptr_t,uint32_t);
extern uint32_t opencfw_em9305_child_325324(uintptr_t,uintptr_t);

typedef uint32_t (*opencfw_em9305_rx_hook_t)(uintptr_t, uintptr_t);

static void opencfw_em9305_rx_release_318c1c(uintptr_t packet)
{
    (void)opencfw_em9305_receive_packet_release_3253bc(packet);
    (void)opencfw_em9305_wsf_critical_enter();
    volatile uint8_t *released = (volatile uint8_t *)(uintptr_t)0x805ab5u;
    *released = (uint8_t)(*released + 1u);
    (void)opencfw_em9305_wsf_critical_exit();
}

void opencfw_em9305_callback_318c1c(void)
{
    uint16_t handle = 0u;
    uint8_t header[8] __attribute__((aligned(4)));
    uint8_t pending[4];
    for (;;) {
        uintptr_t packet = opencfw_em9305_child_325350((uintptr_t)&handle);
        if (packet == 0u) break;
        uint32_t index = handle;
        uintptr_t base = *(volatile uint32_t *)(uintptr_t)0x805c70u;
        uintptr_t connection = index * 912u + base;
        if (*(volatile uint8_t *)connection == 0u) {
            opencfw_em9305_rx_release_318c1c(packet);
            continue;
        }
        (void)opencfw_em9305_short_header_decode_32dedc((uintptr_t)header, packet);
        uint32_t terminate = 0u;
        if (*(volatile uint8_t *)(connection + 109u) != 0u) {
            uintptr_t hook = *(volatile uint32_t *)(uintptr_t)0x8051dcu;
            if (hook != 0u && ((opencfw_em9305_rx_hook_t)hook)(connection + 84u, packet) == 0u) {
                terminate = 1u;
            } else {
                uintptr_t entry = index * 912u + base;
                (void)opencfw_em9305_wsf_timer_start_ms(entry + 496u, *(volatile uint32_t *)(entry + 492u));
                (void)opencfw_em9305_wsf_timer_start_ms(entry + 476u, *(volatile uint32_t *)(entry + 472u));
            }
        }
        if (terminate == 0u) {
            uint32_t llid = header[0];
            if (llid - 1u < 2u) {
                if (*(volatile uint8_t *)(index * 912u + base + 403u) == 0u) {
                    (void)opencfw_em9305_child_325324(connection, packet);
                    continue;
                }
            } else if (llid == 3u) {
                uintptr_t control = *(volatile uint32_t *)(uintptr_t)0x80280cu;
                if (control != 0u) ((opencfw_em9305_rx_hook_t)control)(connection, packet);
                opencfw_em9305_rx_release_318c1c(packet);
                continue;
            } else {
                uintptr_t registry = *(volatile uint32_t *)(uintptr_t)0x805cd8u;
                uintptr_t handler = registry != 0u ? *(volatile uint32_t *)(registry + 0x14u) : 0u;
                if (handler != 0u) {
                    ((opencfw_em9305_rx_hook_t)handler)(handle, packet);
                    continue;
                }
                opencfw_em9305_rx_release_318c1c(packet);
                continue;
            }
        }
        opencfw_em9305_rx_release_318c1c(packet);
        (void)opencfw_em9305_receive_terminate_325c08(connection, 0x48u);
    }
    uintptr_t config = *(volatile uint32_t *)(uintptr_t)0x805cacu;
    uint32_t count = *(volatile uint8_t *)(config + 34u);
    (void)opencfw_em9305_wsf_critical_enter();
    uintptr_t base = *(volatile uint32_t *)(uintptr_t)0x805c70u;
    for (uint32_t index = count; index != 0u;) {
        --index;
        volatile uint8_t *flag = (volatile uint8_t *)(base + index * 912u + 377u);
        uint32_t value = *flag;
        *flag = 0u;
        pending[index] = (uint8_t)value;
    }
    (void)opencfw_em9305_wsf_critical_exit();
    config = *(volatile uint32_t *)(uintptr_t)0x805cacu;
    uintptr_t notify = *(volatile uint32_t *)(uintptr_t)0x805b14u;
    uint32_t index = *(volatile uint8_t *)(config + 34u);
    do {
        --index;
        uint32_t value = pending[index];
        if (value != 0u && notify != 0u) {
            ((opencfw_em9305_rx_hook_t)notify)((uint16_t)index, value);
            notify = *(volatile uint32_t *)(uintptr_t)0x805b14u;
        }
    } while (index != 0u);
}
