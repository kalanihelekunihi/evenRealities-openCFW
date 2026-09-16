/* SPDX-License-Identifier: MIT */
#include <stddef.h>
#include "uart_message_v2.h"
#include "lvp_queue.h"
/* Stock dispatch scans sixteen 28-byte entries. Queue backing-buffer
 * initialization remains a separate recovery dependency. */
UART_MSG_REGIST s_uart_msg_regist_array[16];
LVP_QUEUE s_uart_recv_pack_queue;
_Static_assert(sizeof(UART_MSG_REGIST)==28,"registration stride");
_Static_assert(offsetof(UART_MSG_REGIST,msg_id)==4,"command offset");
_Static_assert(offsetof(UART_MSG_REGIST,msg_pack_callback)==20,"callback offset");
_Static_assert(offsetof(UART_MSG_REGIST,priv)==24,"private data offset");
_Static_assert(sizeof(LVP_QUEUE)==20,"queue descriptor size");
