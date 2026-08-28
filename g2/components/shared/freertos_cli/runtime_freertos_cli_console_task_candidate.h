/*
 * SPDX-License-Identifier: MIT
 *
 * Production-excluded clean-room candidate for the G2 FreeRTOS+CLI console
 * task at 0x00541600.
 */

#ifndef OPEN_CFW_RUNTIME_FREERTOS_CLI_CONSOLE_TASK_CANDIDATE_H
#define OPEN_CFW_RUNTIME_FREERTOS_CLI_CONSOLE_TASK_CANDIDATE_H

typedef __UINT8_TYPE__ open_cfw_freertos_cli_console_u8;
typedef __UINT32_TYPE__ open_cfw_freertos_cli_console_u32;
typedef __INT32_TYPE__ open_cfw_freertos_cli_console_s32;

enum {
    OPEN_CFW_FREERTOS_CLI_CONSOLE_BUFFER_BYTES = 128U,
    OPEN_CFW_FREERTOS_CLI_CONSOLE_PAYLOAD_BYTES = 127U,
    OPEN_CFW_FREERTOS_CLI_CONSOLE_REGISTER_GROUPS = 22U,
    OPEN_CFW_FREERTOS_CLI_CONSOLE_RECEIVE_FOREVER = -1
};

struct open_cfw_freertos_cli_console_state {
    open_cfw_freertos_cli_console_u8 *input;
    open_cfw_freertos_cli_console_u8 *output;
    open_cfw_freertos_cli_console_u32 length;
};

/* Fixed SRAM objects selected by the stock literal table at 0x00541770. */
extern void *volatile open_cfw_retained_freertos_cli_console_receive_handle;
extern open_cfw_freertos_cli_console_u8
    open_cfw_retained_freertos_cli_console_output[128];
extern open_cfw_freertos_cli_console_u8
    open_cfw_retained_freertos_cli_console_input[128];

/*
 * Exact retained call ABI used at 0x005416A0.  The candidate accepts a byte
 * only when the returned count is exactly one.  Stock ignored this return and
 * could consume stack residue after an error or spurious wake.
 */
extern open_cfw_freertos_cli_console_u32
open_cfw_retained_freertos_cli_console_receive(
    void *handle,
    void *destination,
    open_cfw_freertos_cli_console_u32 length,
    open_cfw_freertos_cli_console_s32 timeout
);

/* Stock display helpers at 0x005415C2 and 0x005415D8. */
extern void open_cfw_retained_freertos_cli_console_display_string(
    const char *text
);
extern void open_cfw_retained_freertos_cli_console_display_byte(
    open_cfw_freertos_cli_console_u8 value
);

/* FreeRTOS_CLIProcessCommand at 0x005847FE. */
extern open_cfw_freertos_cli_console_s32
open_cfw_retained_freertos_cli_process_command(
    const char *input,
    char *output,
    open_cfw_freertos_cli_console_u32 output_length
);

/* The 22 registration-only setup functions called at 0x00541604..0x0054165B. */
extern void open_cfw_retained_freertos_cli_register_group_57e626(void);
extern void open_cfw_retained_freertos_cli_register_group_57e810(void);
extern void open_cfw_retained_freertos_cli_register_group_57ff40(void);
extern void open_cfw_retained_freertos_cli_register_group_580392(void);
extern void open_cfw_retained_freertos_cli_register_group_5807c0(void);
extern void open_cfw_retained_freertos_cli_register_group_580c04(void);
extern void open_cfw_retained_freertos_cli_register_group_580fec(void);
extern void open_cfw_retained_freertos_cli_register_group_5810d8(void);
extern void open_cfw_retained_freertos_cli_register_group_581136(void);
extern void open_cfw_retained_freertos_cli_register_group_581644(void);
extern void open_cfw_retained_freertos_cli_register_group_58183a(void);
extern void open_cfw_retained_freertos_cli_register_group_581960(void);
extern void open_cfw_retained_freertos_cli_register_group_581d60(void);
extern void open_cfw_retained_freertos_cli_register_group_5827d0(void);
extern void open_cfw_retained_freertos_cli_register_group_5836b8(void);
extern void open_cfw_retained_freertos_cli_register_group_583cec(void);
extern void open_cfw_retained_freertos_cli_register_group_583f74(void);
extern void open_cfw_retained_freertos_cli_register_group_5840f4(void);
extern void open_cfw_retained_freertos_cli_register_group_5841ee(void);
extern void open_cfw_retained_freertos_cli_register_group_584320(void);
extern void open_cfw_retained_freertos_cli_register_group_584430(void);
extern void open_cfw_retained_freertos_cli_register_group_584702(void);

void open_cfw_freertos_cli_console_state_initialize(
    struct open_cfw_freertos_cli_console_state *state,
    open_cfw_freertos_cli_console_u8 *input,
    open_cfw_freertos_cli_console_u8 *output
);

void open_cfw_freertos_cli_console_register_groups_candidate(void);

void open_cfw_freertos_cli_console_consume_byte_candidate(
    struct open_cfw_freertos_cli_console_state *state,
    open_cfw_freertos_cli_console_u8 value
);

/* One bounded receive/consume iteration, exposed for host differential tests. */
open_cfw_freertos_cli_console_u32
open_cfw_freertos_cli_console_poll_once_candidate(
    struct open_cfw_freertos_cli_console_state *state
);

/* CMSIS/FreeRTOS thread-entry ABI selected by the stored pointer 0x00541601. */
void open_cfw_freertos_cli_console_task_candidate(void *argument);

#endif
