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

extern struct message_handle *open_cfw_gx8002_uart_message_get(unsigned);
extern int gx_uart_async_send_buffer_stop(unsigned);
extern int gx_uart_async_recv_buffer_stop(unsigned);
extern int gx_uart_init(unsigned,unsigned);
extern int gx_uart_start_async_recv(unsigned,int (*)(int,int,void *),void *);
extern int open_cfw_gx8002_uart_message_recv_callback(int,int,void *);
int open_cfw_gx8002_uart_message_suspend(void *private_data)
{
    (void)private_data;
    int port=0;
    #pragma GCC unroll 1
    while(port<2) {
        struct message_handle *handle=open_cfw_gx8002_uart_message_get((unsigned char)port);
        ++port;
        if(!handle)continue;
        gx_uart_async_send_buffer_stop(handle->port);
        gx_uart_async_recv_buffer_stop(handle->port);
    }
    return 0;
}
int open_cfw_gx8002_uart_message_resume(void *private_data)
{
    (void)private_data;
    int port=0;
    #pragma GCC unroll 1
    while(port<2) {
        struct message_handle *handle=open_cfw_gx8002_uart_message_get((unsigned char)port);
        ++port;
        if(!handle || handle->initialized!=1)continue;
        gx_uart_async_send_buffer_stop(handle->port);
        gx_uart_async_recv_buffer_stop(handle->port);
        if(gx_uart_init(handle->port,handle->baudrate))return -1;
        gx_uart_start_async_recv(handle->port,open_cfw_gx8002_uart_message_recv_callback,NULL);
    }
    return 0;
}
