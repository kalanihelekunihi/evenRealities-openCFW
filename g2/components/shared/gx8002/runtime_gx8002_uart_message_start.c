/* SPDX-License-Identifier: MIT */
/* Recovered two-port UART-message v2 send scheduler, pinned upstream lineage. */
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
extern struct message_handle open_cfw_gx8002_uart_message_contexts[2];
extern int gx_uart_stop_async_send(unsigned);
extern int gx_uart_start_async_send(unsigned,int (*)(int,int,void *),void *);
extern int open_cfw_gx8002_uart_message_send_callback(int,int,void *);
extern int open_cfw_gx8002_power_lock(int);
struct message_handle *open_cfw_gx8002_uart_message_get(unsigned port)
{
    if(port==0)return &open_cfw_gx8002_uart_message_contexts[0];
    if(port==1)return &open_cfw_gx8002_uart_message_contexts[1];
    return NULL;
}
int open_cfw_gx8002_uart_message_start(unsigned port)
{
    struct message_handle *handle=open_cfw_gx8002_uart_message_get(port);
    if(!handle)return -1;
    if(LvpQueueIsEmpty(&handle->send_queue)) {
        handle->sending=0;
        gx_uart_stop_async_send(port);
        return -1;
    }
    handle->sending=1;
    LvpQueueGet(&handle->send_queue,(unsigned char *)&handle->send_packet);
    handle->send_state=0;
    open_cfw_gx8002_power_lock(handle->pmu_lock);
    gx_uart_start_async_send(handle->port,open_cfw_gx8002_uart_message_send_callback,NULL);
    return 0;
}
