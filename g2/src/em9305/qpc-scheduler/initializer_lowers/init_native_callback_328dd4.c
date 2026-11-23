#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x328dd4..0x329034: isochronous-group event-end callback (owner).
 * Steps the stream queues of every stream (+56[i]) that has pending
 * traffic in em9305_ram_80542c.u8_805434, then (unless the group is idle) advances the
 * 64-bit event counter (+32), the anchor (+8 += interval +16), applies a
 * pending channel-map update at its instant (+276, +280/+284) and pending
 * terminate/encryption requests (+273 -> 32909c 2/3), and reinserts the
 * schedule node; a refused insert restarts the whole pass. Afterwards it
 * flushes or counts the received-event bookkeeping of each stream (+108,
 * +112, 31aeb4 per sub-event), mirrors the counters into the peer group
 * (+180), refills the transmit queues (32d598/317124/317680, dropping
 * events when no buffer is free and counting them in ((uintptr_t)&em9305_ram_805a6c + 0x70u)) and
 * reports the event (32324c) when ((uintptr_t)&em9305_ram_805a6c + 0x43u) is set. */
#define U8(a) (*(volatile uint8_t *)(uintptr_t)(a))
#define U16(a) (*(volatile uint16_t *)(uintptr_t)(a))
#define U32(a) (*(volatile uint32_t *)(uintptr_t)(a))

extern void opencfw_em9305_child_3177e8(uintptr_t context, uint32_t budget, uint32_t max);
extern void opencfw_em9305_radio_stream_queue_step_317980(uintptr_t stream, uint32_t budget);
extern void opencfw_em9305_child_3235bc(uintptr_t object);
extern void opencfw_em9305_child_317304(uintptr_t record);
extern uint32_t opencfw_em9305_wsf_queue_empty(uintptr_t queue);
extern uint32_t opencfw_em9305_dispatch_child_3257f4(uintptr_t context);
extern uint32_t opencfw_em9305_dispatch_child_32520c(uintptr_t object, uint32_t first,
                                                     uint32_t second);
extern uint32_t opencfw_em9305_child_32909c(uintptr_t, uint32_t);
extern uint32_t opencfw_em9305_associated_schedule_insert_312da4(uintptr_t, uintptr_t);
extern uintptr_t opencfw_em9305_child_31aeb4(uint32_t handle, uint32_t mode, uint32_t range,
                                             uint32_t value);
extern uint32_t opencfw_em9305_ll_received_event_active(uintptr_t message);
extern uintptr_t opencfw_em9305_child_32d598(void);
extern uintptr_t opencfw_em9305_memset(uintptr_t dst, uint32_t value, uint32_t size);
extern uint32_t opencfw_em9305_child_317124(uintptr_t queue, uintptr_t out, uint32_t budget);
extern uint32_t opencfw_em9305_ll_stream_process_317680(uintptr_t, uintptr_t, uintptr_t);
extern uint32_t opencfw_em9305_wsf_event_release(uintptr_t event);
extern uintptr_t opencfw_em9305_wsf_event_remove(uintptr_t queue, uintptr_t handler_out);
extern uint32_t opencfw_em9305_wsf_critical_enter(void);
extern uint32_t opencfw_em9305_wsf_critical_exit(void);
extern uint32_t opencfw_em9305_dispatch_child_32324c(uint32_t handle, uint32_t value);

#define STREAM(link, i) U32((link) + 56u + 4u * (i))

uint32_t opencfw_em9305_callback_328dd4(uintptr_t owner)
{
    uintptr_t link = U32(owner + 36u);
    uintptr_t flags = link + 272u;
    uintptr_t requests = link + 273u;

    for (;;) {
        for (uint32_t i = 0u; i < U8(link + 52u); i++) {
            if (U8((uintptr_t)&em9305_ram_80542c.u8_805434[0] + i) == 0u)
                continue;
            uintptr_t stream = STREAM(link, i);
            U8(stream + 32u) = 1u;
            uint32_t mode = U8(link + 26u);
            uint32_t budget = U8((uintptr_t)&em9305_ram_80542c.u8_805434[0] + i);
            if (mode == 0u)
                opencfw_em9305_radio_stream_queue_step_317980(stream, budget);
            else
                opencfw_em9305_child_3177e8(stream, budget, U8((uintptr_t)&em9305_ram_80542c.u8_805438[0] + i));
        }
        opencfw_em9305_child_3235bc(link);
        opencfw_em9305_child_317304(link);
        if (U8(link + 1u) != 1u &&
            ((U8(flags) & 2u) == 0u || opencfw_em9305_wsf_queue_empty(link + 184u) != 0u))
            return opencfw_em9305_child_32909c(link, 4u);

        uint32_t interval = U32(link + 16u);
        U32(owner + 20u) = interval;
        uint32_t low = U32(link + 32u), high = U32(link + 36u);
        U32(link + 32u) = low + 1u;
        U32(link + 36u) = high + (low == 0xffffffffu);
        U32(owner + 8u) = U32(owner + 8u) + interval;
        (void)opencfw_em9305_dispatch_child_3257f4(link);

        uint32_t pending = U8(flags);
        if ((pending & 1u) != 0u) {
            if ((uint16_t)(U16(link + 32u) + 1u) == U16(link + 276u)) {
                uint32_t second = U32(link + 284u), first = U32(link + 280u);
                U8(flags) = (uint8_t)(pending & ~1u);
                (void)opencfw_em9305_dispatch_child_32520c(link, first, second);
                uintptr_t peer = U32(link + 180u);
                if (peer != 0u) {
                    U8(peer + 176u) = 1u;
                    U32(peer + 228u) = U32(link + 284u);
                    U32(peer + 224u) = U32(link + 280u);
                }
            }
            pending = U8(flags);
        }
        if (pending == 0u) {
            uint32_t request = U8(requests);
            if ((request & 1u) != 0u) {
                U8(requests) = (uint8_t)(request & ~1u);
                (void)opencfw_em9305_child_32909c(link, 2u);
            } else if ((request & 2u) != 0u) {
                U8(requests) = (uint8_t)(request & ~2u);
                (void)opencfw_em9305_child_32909c(link, 3u);
            }
        }
        if (opencfw_em9305_associated_schedule_insert_312da4(owner, 0u) != 0u)
            break;
    }

    for (uint32_t i = 0u; i < U8(link + 52u); i++) {
        uintptr_t stream = STREAM(link, i);
        if (U8(stream + 108u) == 0u)
            continue;
        if (U8(stream + 109u) != 0u) {
            U32(stream + 112u) = 0u;
            U16(stream + 108u) = 0u;
            continue;
        }
        if (U8(link + 30u) != 0u) {
            uint32_t received = U32(stream + 112u);
            U32(stream + 112u) = received + 1u;
            uintptr_t event = opencfw_em9305_child_31aeb4(U16(stream + 2u), U8(stream + 116u),
                                                          U16(link + 6u), received);
            if (event == 0u)
                goto mirror;
            (void)opencfw_em9305_ll_received_event_active(event);
            continue;
        }
        for (uint32_t j = 0u, count = U8(link + 24u); j < count; j++) {
            uint32_t base = U32(link + 32u) * count;
            uintptr_t event = opencfw_em9305_child_31aeb4(U16(stream + 2u), U8(stream + 116u),
                                                          U16(link + 6u), base + j);
            if (event == 0u)
                goto mirror;
            (void)opencfw_em9305_ll_received_event_active(event);
            count = U8(link + 24u);
        }
    }

mirror:;
    uintptr_t peer = U32(link + 180u);
    if (peer != 0u) {
        U32(peer + 180u) = U32(owner + 8u);
        uint32_t count = U8(link + 24u);
        uint64_t counter = ((uint64_t)U32(link + 36u) << 32) | U32(link + 32u);
        uint64_t total = counter * count;
        U32(peer + 236u) = (uint32_t)total;
        U32(peer + 240u) = (uint32_t)(total >> 32);
    }

    if (U8(link + 30u) == 1u) {
        uint8_t message[24] __attribute__((aligned(4)));
        uintptr_t out = (uintptr_t)message;
        for (uint32_t i = 0u; i < U8(link + 52u); i++) {
            uintptr_t stream = STREAM(link, i);
            uintptr_t queue = stream + 20u;
            for (uint32_t j = 0u; j < U8(link + 24u); j++) {
                if (U8(stream + 28u) == 0u)
                    continue;
                uintptr_t buffer = opencfw_em9305_child_32d598();
                if (buffer == 0u) {
                    uintptr_t dropped;
                    while ((dropped = opencfw_em9305_wsf_event_remove(queue, out)) != 0u) {
                        (void)opencfw_em9305_wsf_event_release(dropped);
                        (void)opencfw_em9305_wsf_critical_enter();
                        U8(((uintptr_t)&em9305_ram_805a6c + 0x70u)) = (uint8_t)(U8(((uintptr_t)&em9305_ram_805a6c + 0x70u)) + 1u);
                        (void)opencfw_em9305_wsf_critical_exit();
                    }
                    continue;
                }
                (void)opencfw_em9305_memset(out, 0u, 0x18u);
                uint32_t limit = U16(U32(stream + 4u) + 4u);
                *(volatile uint16_t *)out = U16(stream + 2u);
                uint32_t length = opencfw_em9305_child_317124(queue, buffer, limit);
                *(volatile uint16_t *)(out + 14u) = (uint16_t)length;
                if (length == 0u)
                    (void)opencfw_em9305_wsf_event_release(buffer);
                else
                    (void)opencfw_em9305_ll_stream_process_317680(stream, out, buffer);
            }
        }
    }

    if (U8(((uintptr_t)&em9305_ram_805a6c + 0x43u)) == 0u)
        return 0u;
    return opencfw_em9305_dispatch_child_32324c(U8(link + 2u), U32(link + 32u));
}
