/* SPDX-License-Identifier: MIT */
/* Recovered UART receive dispatcher; target dependencies remain unqualified. */
#include <stdint.h>
#include <stddef.h>
#include <uart_message_v2.h>
#include <lvp_queue.h>
#ifndef OPEN_CFW_GX8002_UART_HOST_TEST
_Static_assert(sizeof(MSG_PACK) == 32, "packet ABI");
_Static_assert(sizeof(UART_MSG_REGIST) == 28, "registration ABI");
_Static_assert(offsetof(MSG_PACK, body_addr) == 16, "packet body pointer");
_Static_assert(offsetof(MSG_PACK, len) == 24, "packet payload length");
#endif
extern LVP_QUEUE open_cfw_gx8002_uart_receive_queue;
extern UART_MSG_REGIST open_cfw_gx8002_uart_registrations[16];
extern uint32_t open_cfw_gx8002_crc32(uint32_t, const unsigned char *, unsigned int);
extern int open_cfw_gx8002_printf(const char *, ...);

int open_cfw_gx8002_uart_async_tick(void)
{
    MSG_PACK packet;
    if (!LvpQueueGet(&open_cfw_gx8002_uart_receive_queue, (unsigned char *)&packet))
        return -1;
    if (packet.msg_header.flags == 1 &&
        open_cfw_gx8002_crc32(0, packet.body_addr, packet.len) != packet.body_vef) {
        (void)open_cfw_gx8002_printf("Crc Error %d\n", packet.len);
        return -1;
    }
    for (unsigned int i = 0; i < 16; ++i) {
        UART_MSG_REGIST *entry = &open_cfw_gx8002_uart_registrations[i];
        if (entry->msg_id == packet.msg_header.cmd && entry->port == packet.port)
            return entry->msg_pack_callback(&packet, entry->priv);
    }
    return -1;
}
