/*
 * SPDX-License-Identifier: MIT
 *
 * Bounded eight-byte status-packet reporters matched to stock entries
 * 0x0047CE90, 0x0047CED6, and 0x0047CF28.
 */

typedef __UINTPTR_TYPE__ open_cfw_status_packets_uintptr;

typedef int (*open_cfw_status_packets_send_function)(
    unsigned int,
    const void *,
    unsigned int,
    unsigned int
);

#ifndef OPEN_CFW_STATUS_PACKETS_LENS_SIDE
#define OPEN_CFW_STATUS_PACKETS_LENS_SIDE() open_cfw_lens_side()
#endif
#ifndef OPEN_CFW_STATUS_PACKETS_STATE
#define OPEN_CFW_STATUS_PACKETS_STATE \
    (*(volatile unsigned char *)0x20075043U)
#endif
#ifndef OPEN_CFW_STATUS_PACKETS_SEND
#define OPEN_CFW_STATUS_PACKETS_SEND(command, payload, size, option) \
    (((open_cfw_status_packets_send_function) \
        (open_cfw_status_packets_uintptr)0x004651E1U)( \
            (command), \
            (payload), \
            (size), \
            (option) \
        ))
#endif

unsigned int open_cfw_lens_side(void);

static __attribute__((always_inline)) inline void
open_cfw_status_packets_prepare(unsigned char payload[8])
{
    payload[4] = (unsigned char)OPEN_CFW_STATUS_PACKETS_LENS_SIDE();
    payload[5] = (
        OPEN_CFW_STATUS_PACKETS_LENS_SIDE() == 1U
        ? 2U
        : 1U
    );
}

__attribute__((used, noinline))
unsigned int open_cfw_status_packet_template3(void)
{
    unsigned char payload[8] = {3U, 0U, 1U, 0U, 0U, 0U, 0U, 0U};

    open_cfw_status_packets_prepare(payload);
    payload[6] = (OPEN_CFW_STATUS_PACKETS_STATE >> 2U) & 1U;
    (void)OPEN_CFW_STATUS_PACKETS_SEND(0x103U, payload, 8U, 0U);
    return 0x00010003U;
}

__attribute__((used, noinline))
unsigned int open_cfw_status_packet_template6(void)
{
    unsigned char payload[8] = {6U, 0U, 1U, 0U, 0U, 0U, 0U, 0U};

    open_cfw_status_packets_prepare(payload);
    payload[6] = (
        ((OPEN_CFW_STATUS_PACKETS_STATE >> 4U) & 1U) != 0U
        ? 3U
        : 2U
    );
    (void)OPEN_CFW_STATUS_PACKETS_SEND(0x103U, payload, 8U, 0U);
    return 0x00010006U;
}

__attribute__((used, noinline))
unsigned int open_cfw_status_packet_template5(void)
{
    unsigned char payload[8] = {5U, 0U, 1U, 0U, 0U, 0U, 0U, 0U};

    open_cfw_status_packets_prepare(payload);
    (void)OPEN_CFW_STATUS_PACKETS_SEND(0x103U, payload, 8U, 0U);
    return 0x00010005U;
}

#undef OPEN_CFW_STATUS_PACKETS_SEND
#undef OPEN_CFW_STATUS_PACKETS_STATE
#undef OPEN_CFW_STATUS_PACKETS_LENS_SIDE
