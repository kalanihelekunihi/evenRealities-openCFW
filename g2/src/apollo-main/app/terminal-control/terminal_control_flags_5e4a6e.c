/* Stock Terminal content-update trigger handler 0x5e4a6e. */
#include <stdint.h>

extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);
extern void audio_terminal_output_start_5e4920(void);
extern void audio_terminal_set_output_5e49b0(uint32_t, uint32_t, uint32_t);

static const char module[] = "terminal.ui";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\app\\gui\\terminal\\terminal_ui.c";
static const char function[] = "terminal_ui_consume_content_update_trigger";
static const char start_message[] =
    "consume trigger output_start: trigger=0x%lx";
static const char short_start_message[] =
    "[terminal.ui]consume trigger output_start: trigger=0x%lx";
static const char end_message[] = "recv tool_end trigger";
static const char short_end_message[] = "[terminal.ui]recv tool_end trigger";

void audio_terminal_control_flags_5e4a6e(uint32_t trigger,
                                           uint32_t payload) {
    if (trigger == 0u)
        return;
    uint32_t output = trigger & 1u;
    uint32_t tool_end = (trigger >> 1) & 1u;
    uint32_t output_start = (trigger >> 2) & 1u;
    uint32_t output_update = (trigger >> 3) & 1u;

    if (output_start != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module, path, function, 0xe7u,
                               start_message, trigger);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x10400000u, short_start_message,
                                        short_start_message, trigger);
        audio_terminal_output_start_5e4920();
    }
    if (output_update != 0u)
        audio_terminal_set_output_5e49b0(output, 1u, payload);
    if (output != 0u && output_start == 0u && output_update == 0u)
        audio_terminal_set_output_5e49b0(1u, 0u, payload);
    if (tool_end != 0u) {
        if (audio_log_flags() & 2u)
            audio_log_extended(4u, module, path, function, 0xf4u, end_message);
        if ((audio_log_flags() & 1u) || (audio_log_flags() & 4u))
            (void)compressed_log_output(0x10000000u, short_end_message,
                                        short_end_message);
    }
}
