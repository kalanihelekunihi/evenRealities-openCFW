/* SPDX-License-Identifier: MIT */
/* Recovered two-port UART-message v2 receive completion callback, pinned upstream lineage. */
#include <stddef.h>
#include "uart_message_v2.h"
#include "lvp_queue.h"
struct message_handle {
    unsigned magic, verification, port;
    int initialized;
    unsigned baudrate;
    unsigned char send_sequence, recv_sequence;
    unsigned sending;
    MSG_PACK receive_packet, send_packet;
    unsigned char send_storage[8 * sizeof(MSG_PACK)];
    LVP_QUEUE send_queue;
    int receive_state, send_state, pmu_lock;
};
_Static_assert(sizeof(struct message_handle)==380,"context ABI");
_Static_assert(offsetof(struct message_handle,send_queue)==348,"queue ABI");
_Static_assert(offsetof(struct message_handle,send_packet)==60,"packet ABI");
_Static_assert(offsetof(struct message_handle,pmu_lock)==376,"lock ABI");
extern struct message_handle *open_cfw_gx8002_uart_message_get(unsigned);
extern int open_cfw_gx8002_uart_receive_body(unsigned,MSG_PACK *,unsigned char **,unsigned *);
unsigned open_cfw_gx8002_uart_receive_body_done(int port,void *private_data)
{
    (void)private_data;
    struct message_handle *handle=open_cfw_gx8002_uart_message_get((unsigned char)port);
    if(!handle)return (unsigned)-1;
    open_cfw_gx8002_uart_receive_body(port,&handle->receive_packet,NULL,NULL);
    return 0;
}
