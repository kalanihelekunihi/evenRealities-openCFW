/* SPDX-License-Identifier: MIT
 * Exact stock-address lower aliases used in experimental command routing.
 * The only selected caller, case_dispatch_received_frame, invokes both
 * command handlers as void and discards R0. These naked long tail branches call
 * the selected source provider without fabricating a return value; residual
 * R0 remains an unadmitted direct-entry equivalence question.
 */
#include <stdint.h>
#define TAIL_ALIAS(name,target) \
 __attribute__((naked)) uint32_t name(void) { \
  __asm__ volatile("push {r3}\n" \
                   "ldr r3, =" #target "\n" \
                   "mov ip, r3\n" \
                   "pop {r3}\n" \
                   "bx ip\n"); \
 }

TAIL_ALIAS(case_binary_14_send,case_send)
TAIL_ALIAS(case_binary_local_send,case_send)
TAIL_ALIAS(case_binary_send51,case_send)
TAIL_ALIAS(case_binary_send5f,case_send)
TAIL_ALIAS(case_binary_3e_ack,case_ack)
TAIL_ALIAS(case_binary_3f_ack,case_ack)
TAIL_ALIAS(case_binary_56_ack,case_ack)
TAIL_ALIAS(case_binary_local_ack,case_ack)
TAIL_ALIAS(case_binary_5e_hex,log_hex_buffer)
TAIL_ALIAS(case_legacy_gpio_bit0,case_control_a)
