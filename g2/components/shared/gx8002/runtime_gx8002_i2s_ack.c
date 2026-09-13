/* SPDX-License-Identifier: MIT
 * Common command response. Pending decoded qualification.
 */
#include <stdint.h>
#include <stddef.h>
#include <uart_message_v2.h>
extern MSG_PACK open_cfw_gx8002_app_reply_state;
extern const uint8_t open_cfw_gx8002_persistent_ack_value;
extern int open_cfw_gx8002_app_enqueue(MSG_PACK *);
/* The upstream queue retains the payload address. Use the shared immutable
 * response byte rather than the stock helper's expired stack local. */
void open_cfw_gx8002_i2s_ack(void)
{
    open_cfw_gx8002_app_reply_state.body_addr=(void *)&open_cfw_gx8002_persistent_ack_value;
    open_cfw_gx8002_app_reply_state.msg_header.cmd=271;
    open_cfw_gx8002_app_reply_state.msg_header.flags=1;
    open_cfw_gx8002_app_reply_state.len=1;
    open_cfw_gx8002_app_enqueue(&open_cfw_gx8002_app_reply_state);
}
