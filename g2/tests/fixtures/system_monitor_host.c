#include <stdint.h>

unsigned int open_cfw_test_system_monitor_flags;
unsigned int open_cfw_test_system_monitor_display_polls;
unsigned int open_cfw_test_system_monitor_display_true_polls;
unsigned int open_cfw_test_system_monitor_foreground;
unsigned int open_cfw_test_system_monitor_background;
unsigned int open_cfw_test_system_monitor_lens;
unsigned int open_cfw_test_system_monitor_command_calls;
unsigned int open_cfw_test_system_monitor_command_a;
unsigned int open_cfw_test_system_monitor_command_b;
unsigned int open_cfw_test_system_monitor_command_c;
unsigned int open_cfw_test_system_monitor_delay_calls;
unsigned int open_cfw_test_system_monitor_delay_ticks;
unsigned int open_cfw_test_system_monitor_idle_calls;
unsigned int open_cfw_test_system_monitor_dashboard_calls;
unsigned int open_cfw_test_system_monitor_app_state_calls;
unsigned int open_cfw_test_system_monitor_app_state_reason;
unsigned int open_cfw_test_system_monitor_onboarding_calls;
unsigned int open_cfw_test_system_monitor_terminal_calls;
unsigned int open_cfw_test_system_monitor_lens_status_calls;
unsigned int open_cfw_test_system_monitor_log_calls;
unsigned int open_cfw_test_system_monitor_trace_calls;

void open_cfw_test_system_monitor_reset(
    unsigned int display_true_polls,
    unsigned int foreground,
    unsigned int background,
    unsigned int lens
)
{
    open_cfw_test_system_monitor_flags = 0U;
    open_cfw_test_system_monitor_display_polls = 0U;
    open_cfw_test_system_monitor_display_true_polls = display_true_polls;
    open_cfw_test_system_monitor_foreground = foreground;
    open_cfw_test_system_monitor_background = background;
    open_cfw_test_system_monitor_lens = lens;
    open_cfw_test_system_monitor_command_calls = 0U;
    open_cfw_test_system_monitor_command_a = 0xFFFFFFFFU;
    open_cfw_test_system_monitor_command_b = 0xFFFFFFFFU;
    open_cfw_test_system_monitor_command_c = 0xFFFFFFFFU;
    open_cfw_test_system_monitor_delay_calls = 0U;
    open_cfw_test_system_monitor_delay_ticks = 0U;
    open_cfw_test_system_monitor_idle_calls = 0U;
    open_cfw_test_system_monitor_dashboard_calls = 0U;
    open_cfw_test_system_monitor_app_state_calls = 0U;
    open_cfw_test_system_monitor_app_state_reason = 0xFFFFFFFFU;
    open_cfw_test_system_monitor_onboarding_calls = 0U;
    open_cfw_test_system_monitor_terminal_calls = 0U;
    open_cfw_test_system_monitor_lens_status_calls = 0U;
    open_cfw_test_system_monitor_log_calls = 0U;
    open_cfw_test_system_monitor_trace_calls = 0U;
}

unsigned int open_cfw_test_system_monitor_log_flags(void)
{
    return open_cfw_test_system_monitor_flags;
}

void open_cfw_test_system_monitor_log_record(
    unsigned int level, const void *module, const void *file,
    const void *function, unsigned int line, const void *format, ...)
{
    (void)level; (void)module; (void)file; (void)function; (void)line; (void)format;
    ++open_cfw_test_system_monitor_log_calls;
}

void open_cfw_test_system_monitor_trace_record(
    unsigned int mask, const void *schema, const void *format, ...)
{
    (void)mask; (void)schema; (void)format;
    ++open_cfw_test_system_monitor_trace_calls;
}

unsigned int open_cfw_test_system_monitor_display_running(void)
{
    unsigned int result =
        open_cfw_test_system_monitor_display_polls <
        open_cfw_test_system_monitor_display_true_polls;
    ++open_cfw_test_system_monitor_display_polls;
    return result;
}

unsigned int open_cfw_test_system_monitor_foreground_running(void)
{
    return open_cfw_test_system_monitor_foreground;
}

unsigned int open_cfw_test_system_monitor_background_running(void)
{
    return open_cfw_test_system_monitor_background;
}

unsigned int open_cfw_test_system_monitor_post_display_command(
    unsigned int a, unsigned int b, unsigned int c)
{
    ++open_cfw_test_system_monitor_command_calls;
    open_cfw_test_system_monitor_command_a = a;
    open_cfw_test_system_monitor_command_b = b;
    open_cfw_test_system_monitor_command_c = c;
    return 0U;
}

void open_cfw_test_system_monitor_delay(unsigned int ticks)
{
    ++open_cfw_test_system_monitor_delay_calls;
    open_cfw_test_system_monitor_delay_ticks = ticks;
}

unsigned int open_cfw_test_system_monitor_lens_side(void)
{
    return open_cfw_test_system_monitor_lens;
}

unsigned int open_cfw_test_system_monitor_send_scheduler_idle(void)
{
    ++open_cfw_test_system_monitor_idle_calls;
    return 0U;
}

void open_cfw_test_system_monitor_reset_dashboard(void) { ++open_cfw_test_system_monitor_dashboard_calls; }
void open_cfw_test_system_monitor_reset_app_state(unsigned int reason) { ++open_cfw_test_system_monitor_app_state_calls; open_cfw_test_system_monitor_app_state_reason = reason; }
void open_cfw_test_system_monitor_reset_onboarding_colors(void) { ++open_cfw_test_system_monitor_onboarding_calls; }
void open_cfw_test_system_monitor_reset_terminal_state(void) { ++open_cfw_test_system_monitor_terminal_calls; }
void open_cfw_test_system_monitor_publish_lens_status(void) { ++open_cfw_test_system_monitor_lens_status_calls; }
