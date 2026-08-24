#include "at_tp_host.h"

#include <stdarg.h>
#include <stdio.h>
#include <string.h>

volatile uint8_t open_cfw_test_at_tp_debug_flag;
char open_cfw_test_at_tp_output_log[2048];
unsigned int open_cfw_test_at_tp_output_count;
unsigned int open_cfw_test_at_tp_stop_count;
unsigned int open_cfw_test_at_tp_read_diff_count;
unsigned int open_cfw_test_at_tp_prepare_count;
unsigned int open_cfw_test_at_tp_save_count;
unsigned int open_cfw_test_at_tp_write_count;
unsigned int open_cfw_test_at_tp_read_count;
unsigned int open_cfw_test_at_tp_delay_count;
uint32_t open_cfw_test_at_tp_delay_ticks;
uint16_t open_cfw_test_at_tp_diff[5];
uint16_t open_cfw_test_at_tp_baseline;
uint16_t open_cfw_test_at_tp_written;
uint16_t open_cfw_test_at_tp_readback;
int open_cfw_test_at_tp_write_status;
int open_cfw_test_at_tp_read_status;

void open_cfw_test_at_tp_reset(void)
{
    open_cfw_test_at_tp_debug_flag = 0u;
    open_cfw_test_at_tp_output_log[0] = '\0';
    open_cfw_test_at_tp_output_count = 0u;
    open_cfw_test_at_tp_stop_count = 0u;
    open_cfw_test_at_tp_read_diff_count = 0u;
    open_cfw_test_at_tp_prepare_count = 0u;
    open_cfw_test_at_tp_save_count = 0u;
    open_cfw_test_at_tp_write_count = 0u;
    open_cfw_test_at_tp_read_count = 0u;
    open_cfw_test_at_tp_delay_count = 0u;
    open_cfw_test_at_tp_delay_ticks = 0u;
    memset(open_cfw_test_at_tp_diff, 0, sizeof(open_cfw_test_at_tp_diff));
    open_cfw_test_at_tp_baseline = 0u;
    open_cfw_test_at_tp_written = 0u;
    open_cfw_test_at_tp_readback = 0u;
    open_cfw_test_at_tp_write_status = 0;
    open_cfw_test_at_tp_read_status = 0;
}

void open_cfw_test_at_tp_output(const char *format, ...)
{
    size_t used = strlen(open_cfw_test_at_tp_output_log);
    va_list arguments;
    va_start(arguments, format);
    (void)vsnprintf(
        open_cfw_test_at_tp_output_log + used,
        sizeof(open_cfw_test_at_tp_output_log) - used,
        format,
        arguments
    );
    va_end(arguments);
    ++open_cfw_test_at_tp_output_count;
}

void open_cfw_test_at_tp_stop(void) { ++open_cfw_test_at_tp_stop_count; }
void open_cfw_test_at_tp_read_diff(uint16_t values[5])
{
    memcpy(values, open_cfw_test_at_tp_diff, sizeof(open_cfw_test_at_tp_diff));
    ++open_cfw_test_at_tp_read_diff_count;
}
uint16_t open_cfw_test_at_tp_read_baseline(void) { return open_cfw_test_at_tp_baseline; }
void open_cfw_test_at_tp_prepare(uint32_t *state)
{
    *state = 0x12345678u;
    ++open_cfw_test_at_tp_prepare_count;
}
void open_cfw_test_at_tp_save(void) { ++open_cfw_test_at_tp_save_count; }
int open_cfw_test_at_tp_write(const uint16_t *configuration)
{
    open_cfw_test_at_tp_written = *configuration;
    ++open_cfw_test_at_tp_write_count;
    return open_cfw_test_at_tp_write_status;
}
int open_cfw_test_at_tp_read(uint16_t *configuration)
{
    *configuration = open_cfw_test_at_tp_readback;
    ++open_cfw_test_at_tp_read_count;
    return open_cfw_test_at_tp_read_status;
}
int open_cfw_test_at_tp_delay(uint32_t ticks)
{
    open_cfw_test_at_tp_delay_ticks = ticks;
    ++open_cfw_test_at_tp_delay_count;
    return 0;
}
