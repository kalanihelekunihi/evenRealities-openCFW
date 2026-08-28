/*
 * SPDX-License-Identifier: MIT
 *
 * Native host seam for the production seven-leaf G2 CLI console task.
 * The candidate fixture remains the single implementation of the retained
 * ABI recorder; these aliases bind its bounded host controls to production
 * symbols without compiling any candidate source into the test library.
 */

#define open_cfw_freertos_cli_console_consume_byte_candidate \
    open_cfw_freertos_cli_console_consume_byte
#define open_cfw_freertos_cli_console_poll_once_candidate \
    open_cfw_freertos_cli_console_poll_once
#define open_cfw_freertos_cli_console_register_groups_candidate \
    open_cfw_freertos_cli_console_register_groups

#include "runtime_freertos_cli_console_task_candidate_host.c"
