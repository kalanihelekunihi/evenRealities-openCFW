#ifndef OPEN_CFW_SYSTEM_MONITOR_HOST_H
#define OPEN_CFW_SYSTEM_MONITOR_HOST_H

#define OPEN_CFW_SYSTEM_MONITOR_LOG_FLAGS() \
    open_cfw_test_system_monitor_log_flags()
#define OPEN_CFW_SYSTEM_MONITOR_LOG_RECORD \
    open_cfw_test_system_monitor_log_record
#define OPEN_CFW_SYSTEM_MONITOR_TRACE_RECORD \
    open_cfw_test_system_monitor_trace_record
#define OPEN_CFW_SYSTEM_MONITOR_DISPLAY_RUNNING() \
    open_cfw_test_system_monitor_display_running()
#define OPEN_CFW_SYSTEM_MONITOR_FOREGROUND_RUNNING() \
    open_cfw_test_system_monitor_foreground_running()
#define OPEN_CFW_SYSTEM_MONITOR_BACKGROUND_RUNNING() \
    open_cfw_test_system_monitor_background_running()
#define OPEN_CFW_SYSTEM_MONITOR_POST_DISPLAY_COMMAND(a, b, c) \
    open_cfw_test_system_monitor_post_display_command((a), (b), (c))
#define OPEN_CFW_SYSTEM_MONITOR_DELAY(ticks) \
    open_cfw_test_system_monitor_delay((ticks))
#define OPEN_CFW_SYSTEM_MONITOR_LENS_SIDE() \
    open_cfw_test_system_monitor_lens_side()
#define OPEN_CFW_SYSTEM_MONITOR_SEND_SCHEDULER_IDLE() \
    open_cfw_test_system_monitor_send_scheduler_idle()
#define OPEN_CFW_SYSTEM_MONITOR_RESET_DASHBOARD() \
    open_cfw_test_system_monitor_reset_dashboard()
#define OPEN_CFW_SYSTEM_MONITOR_RESET_APP_STATE(reason) \
    open_cfw_test_system_monitor_reset_app_state((reason))
#define OPEN_CFW_SYSTEM_MONITOR_RESET_ONBOARDING_COLORS() \
    open_cfw_test_system_monitor_reset_onboarding_colors()
#define OPEN_CFW_SYSTEM_MONITOR_RESET_TERMINAL_STATE() \
    open_cfw_test_system_monitor_reset_terminal_state()
#define OPEN_CFW_SYSTEM_MONITOR_PUBLISH_LENS_STATUS() \
    open_cfw_test_system_monitor_publish_lens_status()

unsigned int open_cfw_test_system_monitor_log_flags(void);
void open_cfw_test_system_monitor_log_record(unsigned int, const void *, const void *, const void *, unsigned int, const void *, ...);
void open_cfw_test_system_monitor_trace_record(unsigned int, const void *, const void *, ...);
unsigned int open_cfw_test_system_monitor_display_running(void);
unsigned int open_cfw_test_system_monitor_foreground_running(void);
unsigned int open_cfw_test_system_monitor_background_running(void);
unsigned int open_cfw_test_system_monitor_post_display_command(unsigned int, unsigned int, unsigned int);
void open_cfw_test_system_monitor_delay(unsigned int);
unsigned int open_cfw_test_system_monitor_lens_side(void);
unsigned int open_cfw_test_system_monitor_send_scheduler_idle(void);
void open_cfw_test_system_monitor_reset_dashboard(void);
void open_cfw_test_system_monitor_reset_app_state(unsigned int);
void open_cfw_test_system_monitor_reset_onboarding_colors(void);
void open_cfw_test_system_monitor_reset_terminal_state(void);
void open_cfw_test_system_monitor_publish_lens_status(void);

#endif
