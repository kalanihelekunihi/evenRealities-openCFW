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
struct body_progress { unsigned sent[2], needed[2]; };
extern struct body_progress open_cfw_gx8002_uart_body_progress;
extern int gx_uart_write(unsigned,const void *,unsigned);
extern unsigned open_cfw_gx8002_uart_body_done(int,void *);
extern int gx_uart_async_send_buffer(unsigned,const void *,unsigned,unsigned (*)(int,void *),void *);
int open_cfw_gx8002_uart_message_body(int port,MSG_PACK *pack,unsigned *available)
{
    unsigned *sent=&open_cfw_gx8002_uart_body_progress.sent[port];
    unsigned *needed=&open_cfw_gx8002_uart_body_progress.needed[port];
    if(*sent==0)*needed=pack->len;
    if(*sent==*needed) {
        *sent=0;
        struct message_handle *handle=open_cfw_gx8002_uart_message_get((unsigned char)port);
        if(!handle)return -1;
        handle->send_state=handle->send_packet.msg_header.flags ? 2 : 3;
        gx_uart_start_async_send(port,open_cfw_gx8002_uart_message_send_callback,NULL);
        return 1;
    }
    if(!pack || !available || !*available) {
        gx_uart_start_async_send(port,open_cfw_gx8002_uart_message_send_callback,NULL);
        return -1;
    }
    unsigned length=*needed-*sent;
    if(*available<length)length=*available;
    gx_uart_write(port,(void *)((unsigned long)pack->body_addr+*sent),length);
    unsigned current=*sent+length;
    unsigned target=*needed;
    if(current==target)current=0;
    *sent=current;
    *available-=length;
    if(current==0)return 1;
    if((((unsigned long)pack->body_addr+current)&15)==0 || (current>=16 && target-current>32)) {
        length=(target-current)&~15u;
        gx_uart_stop_async_send(port);
        gx_uart_async_send_buffer(port,(void *)((unsigned long)pack->body_addr+*sent),length,open_cfw_gx8002_uart_body_done,NULL);
        *sent+=length;
        *available=0;
        return 0;
    }
    return current==0;
}
