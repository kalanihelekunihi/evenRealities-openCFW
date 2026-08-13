/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Host substitutions for the wall-clock seconds and validity helper.
 */

unsigned int open_cfw_test_wall_time_mode;
unsigned int open_cfw_test_wall_time_seconds;
unsigned int open_cfw_test_wall_time_mode_calls;
unsigned int open_cfw_test_wall_time_seconds_calls;
unsigned int open_cfw_test_wall_time_trace[4];
unsigned int open_cfw_test_wall_time_trace_count;

static void open_cfw_test_wall_time_record(unsigned int event)
{
    open_cfw_test_wall_time_trace[
        open_cfw_test_wall_time_trace_count
    ] = event;
    open_cfw_test_wall_time_trace_count += 1U;
}

static unsigned int open_cfw_test_wall_time_mode_query(void)
{
    open_cfw_test_wall_time_mode_calls += 1U;
    open_cfw_test_wall_time_record(1U);
    return open_cfw_test_wall_time_mode;
}

static unsigned int open_cfw_test_wall_time_seconds_query(void)
{
    open_cfw_test_wall_time_seconds_calls += 1U;
    open_cfw_test_wall_time_record(2U);
    return open_cfw_test_wall_time_seconds;
}

#define OPEN_CFW_WALL_TIME_MODE() \
    open_cfw_test_wall_time_mode_query()
#define OPEN_CFW_WALL_TIME_SECONDS() \
    open_cfw_test_wall_time_seconds_query()

#include "../../components/apollo_main/core_overlay/wall_time.c"
