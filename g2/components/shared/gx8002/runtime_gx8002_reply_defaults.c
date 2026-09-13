/* SPDX-License-Identifier: MIT */
/* Candidate typed storage. Existing reply helpers must adopt MSG_PACK-compatible
 * declarations before this definition is admitted into their linked program. */
#include <stddef.h>
#include <uart_message_v2.h>
MSG_PACK open_cfw_gx8002_app_reply_state
    __attribute__((section(".data.reply_packet"))) = {
        .msg_header = {.magic = MSG_SLAVE_MAGIC},
        .body_addr = 0, .port = 0, .len = 0, .body_vef = 0
    };
_Static_assert(sizeof(MESSAGE_HEADER) == 14, "wire header");
_Static_assert(sizeof(MSG_PACK) == 32, "packet storage");
_Static_assert(offsetof(MSG_PACK, body_addr) == 16, "payload");
_Static_assert(offsetof(MSG_PACK, len) == 24, "payload length");
