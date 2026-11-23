#include <stdint.h>
#include "em9305_ram.h"

/* Native 0x316f70..0x317110: reassemble ISO SDUs from a received BIS/CIS
 * payload (data + 2, length bytes) into the context's SDU buffer (+0, write
 * offset +4, sequence +8, time stamp +16, state +7, flush flag +6). Each
 * segment header (native 0x31bd18: start/continuation +0, complete +1,
 * length +2, time offset +4; start segments carry 3 header bytes) either
 * starts a new SDU (buffer from native 0x32543c, counted at ((uintptr_t)&em9305_ram_805a6c + 0x71u)),
 * continues the current one, or drops it. A completed SDU gets a 20-byte
 * ISO header (native 0x31b9ac: handle, 0x102, SDU length, time stamp,
 * sequence, status 1 when longer than max) and is queued for the handler
 * (ll_event_enqueue); a start segment longer than max is reported with
 * status 2. Returns the number of SDUs queued. */
extern uint32_t opencfw_em9305_wsf_event_release(uintptr_t);
extern uint32_t opencfw_em9305_dispatch_child_31bd18(uintptr_t,uintptr_t);
extern uintptr_t opencfw_em9305_dispatch_child_32543c(void);
extern uint32_t opencfw_em9305_wsf_critical_enter(void);
extern uint32_t opencfw_em9305_wsf_critical_exit(void);
extern void *opencfw_em9305_memcpy(void *destination, const void *source, uint32_t bytes);
extern void *opencfw_em9305_memset(void *,uint32_t,uint32_t);
extern uint32_t opencfw_em9305_dispatch_child_31b9ac(uintptr_t,uintptr_t);
extern uint32_t opencfw_em9305_ll_event_enqueue(uintptr_t,uint32_t,uintptr_t);

struct iso_segment {
    uint8_t start;
    uint8_t complete;
    uint8_t length;
    uint8_t reserved;
    uint32_t time_offset;
};

struct iso_sdu_header {
    uint16_t handle;
    uint16_t kind;
    uint16_t sdu_length;
    uint16_t reserved;
    uint32_t time_stamp;
    uint16_t sequence;
    uint16_t length;
    uint8_t status;
    uint8_t reserved2[7];
};

struct iso_frame {
    struct iso_segment segment;
    struct iso_sdu_header header;
} __attribute__((aligned(4)));

#define ISO_U8(a) (*(volatile uint8_t *)(a))
#define ISO_U16(a) (*(volatile uint16_t *)(a))
#define ISO_U32(a) (*(volatile uint32_t *)(a))

static void iso_report(uintptr_t queue, uint32_t handle, uintptr_t sdu, struct iso_frame *frame)
{
    (void)opencfw_em9305_dispatch_child_31b9ac(sdu, (uintptr_t)&frame->header);
    (void)opencfw_em9305_ll_event_enqueue(queue, (uint8_t)handle, sdu);
}

uint32_t opencfw_em9305_dispatch_child_316f70(uintptr_t context, uintptr_t queue, uint32_t handle,
                                              uintptr_t data, uint32_t length, uint32_t now, uint32_t max)
{
    struct iso_frame frame;
    uint32_t queued = 0u;
    if (ISO_U8(context + 6u) != 0u) {
        uintptr_t pending = ISO_U32(context);
        ISO_U8(context + 6u) = 0u;
        if (pending != 0u) {
            (void)opencfw_em9305_wsf_event_release(pending);
            ISO_U32(context) = 0u;
            return 0u;
        }
    }
    frame.segment.time_offset = 0u;
    *(uint32_t *)(void *)&frame.segment = 0u;
    if (length == 0u) return 0u;
    uintptr_t cursor = data + 2u;
    do {
        uint32_t used = opencfw_em9305_dispatch_child_31bd18((uintptr_t)&frame.segment, cursor);
        uint32_t start = frame.segment.start;
        if (start == 0u) frame.segment.length = (uint8_t)(frame.segment.length - 3u);
        uint32_t state = ISO_U8(context + 7u);
        cursor += used;
        uintptr_t sdu;
        uintptr_t target;
        uint32_t size;
        if (state == 1u) {
            sdu = ISO_U32(context);
            if (start != 1u) {
                (void)opencfw_em9305_wsf_event_release(sdu);
                ISO_U32(context) = 0u;
                ISO_U8(context + 7u) = 0u;
                uint32_t skip = frame.segment.length;
                cursor += skip;
                length -= skip + used;
                continue;
            }
            target = sdu + ISO_U16(context + 4u);
            size = frame.segment.length;
        } else if (state != 0u) {
            uintptr_t pending = ISO_U32(context);
            if (pending != 0u) {
                (void)opencfw_em9305_wsf_event_release(pending);
                ISO_U32(context) = 0u;
            }
            uint32_t skip = frame.segment.length;
            cursor += skip;
            length -= skip + used;
            continue;
        } else {
            sdu = opencfw_em9305_dispatch_child_32543c();
            ISO_U32(context) = (uint32_t)sdu;
            if (sdu == 0u) continue;
            (void)opencfw_em9305_wsf_critical_enter();
            volatile uint8_t *buffers = &em9305_ram_805a6c.u8_805add;
            *buffers = (uint8_t)(*buffers - 1u);
            (void)opencfw_em9305_wsf_critical_exit();
            sdu = ISO_U32(context);
            ISO_U16(context + 4u) = 12u;
            if (frame.segment.start != 0u) {
                (void)opencfw_em9305_wsf_event_release(sdu);
                uint32_t skip = frame.segment.length;
                ISO_U32(context) = 0u;
                cursor += skip;
                length -= skip + used;
                continue;
            }
            size = frame.segment.length;
            uint32_t offset = frame.segment.time_offset;
            ISO_U32(context + 16u) = offset;
            if (max < size) {
                (void)opencfw_em9305_memset(&frame.header.sdu_length, 0u, 0x14u);
                uint32_t sequence = ISO_U16(context + 8u);
                frame.header.kind = 258u;
                frame.header.sequence = (uint16_t)sequence;
                ISO_U16(context + 8u) = (uint16_t)(sequence + 1u);
                frame.header.status = 2u;
                frame.header.handle = (uint16_t)handle;
                frame.header.time_stamp = now - offset;
                iso_report(queue, handle, sdu, &frame);
                ISO_U8(context + 7u) = 0u;
                ISO_U32(context) = 0u;
                return (uint8_t)(queued + 1u);
            }
            target = sdu + 12u;
        }
        (void)opencfw_em9305_memcpy((void *)target, (const void *)cursor, size);
        uint32_t copied = frame.segment.length;
        uint32_t total = ISO_U16(context + 4u) + copied;
        ISO_U16(context + 4u) = (uint16_t)total;
        if (frame.segment.complete == 0u) {
            ISO_U8(context + 7u) = 1u;
            return (uint8_t)queued;
        }
        (void)opencfw_em9305_memset(&frame.header.sdu_length, 0u, 0x14u);
        uint32_t sequence = ISO_U16(context + 8u);
        frame.header.kind = 258u;
        uint32_t stamp = ISO_U32(context + 16u);
        frame.header.sdu_length = (uint16_t)(total - 12u);
        frame.header.length = (uint16_t)(total - 12u);
        frame.header.status = max < (uint16_t)(total - 12u);
        ISO_U16(context + 8u) = (uint16_t)(sequence + 1u);
        frame.header.sequence = (uint16_t)sequence;
        frame.header.time_stamp = now - stamp;
        frame.header.handle = (uint16_t)handle;
        iso_report(queue, handle, ISO_U32(context), &frame);
        cursor += copied;
        ++queued;
        length -= frame.segment.length + used;
        ISO_U32(context) = 0u;
        ISO_U8(context + 7u) = 0u;
    } while ((length & 0xffu) != 0u);
    return (uint8_t)queued;
}
