/* SPDX-License-Identifier: MIT
 * These original call targets are the same 0x08009170 formatter wrapper.
 * A naked long tail branch preserves the ARM variadic word stream and its
 * return while avoiding Thumb-1 short-branch relocation range limits.
 * UART/formatter effects remain in g2_log_printf and its imported lowers.
 */
#include <stdint.h>

#define CASE_LOG_ALIAS(name) \
    __attribute__((naked)) uint32_t name(const char *format, ...) { \
        __asm__ volatile("push {r3}\n" \
                         "ldr r3, =g2_log_printf\n" \
                         "mov ip, r3\n" \
                         "pop {r3}\n" \
                         "bx ip\n"); \
    }

CASE_LOG_ALIAS(case_legacy_logger)
CASE_LOG_ALIAS(case_binary_3d_logger)
CASE_LOG_ALIAS(case_binary_3e_logger)
CASE_LOG_ALIAS(case_binary_3f_logger)
CASE_LOG_ALIAS(case_binary_3f_program_log)
CASE_LOG_ALIAS(case_binary_56_logger)
CASE_LOG_ALIAS(case_binary_56_exit_log)
CASE_LOG_ALIAS(case_binary_5e_logger)
CASE_LOG_ALIAS(case_binary_5e_failure_log)
CASE_LOG_ALIAS(case_binary_logger)
