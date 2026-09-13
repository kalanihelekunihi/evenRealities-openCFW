/* SPDX-License-Identifier: MIT
 * Common command response. Pending decoded qualification.
 */
#include <stdint.h>
#include <stddef.h>
#include <uart_message_v2.h>
extern MSG_PACK open_cfw_gx8002_app_reply_state;
extern uint16_t open_cfw_gx8002_app_reply_value;
extern int open_cfw_gx8002_app_enqueue(MSG_PACK *);
int open_cfw_gx8002_app_reply(uint32_t kind,uint32_t command,uint32_t value)
{
    open_cfw_gx8002_app_reply_value=(uint16_t)value;
    command|=kind==1?0x300:0x200;
    open_cfw_gx8002_app_reply_state.msg_header.flags=1; __asm__ volatile ("" ::: "memory");
    open_cfw_gx8002_app_reply_state.body_addr=(unsigned char *)&open_cfw_gx8002_app_reply_value; __asm__ volatile ("" ::: "memory");
    open_cfw_gx8002_app_reply_state.msg_header.cmd=(uint16_t)command; __asm__ volatile ("" ::: "memory");
    open_cfw_gx8002_app_reply_state.len=2; __asm__ volatile ("" ::: "memory");
    open_cfw_gx8002_app_enqueue(&open_cfw_gx8002_app_reply_state);
    return 0;
}
