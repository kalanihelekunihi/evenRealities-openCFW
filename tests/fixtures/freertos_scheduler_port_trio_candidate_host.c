#include <setjmp.h>
#include <stddef.h>

#include "../../research/candidates/freertos_scheduler_port_trio.h"

enum open_cfw_test_port_event
{
    OPEN_CFW_TEST_PORT_WRITE_ICSR = 1,
    OPEN_CFW_TEST_PORT_SET_MASK = 2,
    OPEN_CFW_TEST_PORT_READ_NESTING = 3,
    OPEN_CFW_TEST_PORT_WRITE_NESTING = 4,
    OPEN_CFW_TEST_PORT_DSB = 5,
    OPEN_CFW_TEST_PORT_ISB = 6,
    OPEN_CFW_TEST_PORT_CLEAR_MASK = 7,
    OPEN_CFW_TEST_PORT_ASSERT = 8
};

typedef struct open_cfw_test_port_event_record
{
    open_cfw_freertos_port_u32 code;
    open_cfw_freertos_port_u32 value;
} open_cfw_test_port_event_record;

static volatile open_cfw_freertos_port_u32 open_cfw_test_icsr;
static volatile open_cfw_freertos_port_u32 open_cfw_test_nesting;
static open_cfw_freertos_port_u32 open_cfw_test_set_result;
static open_cfw_freertos_port_u32 open_cfw_test_set_calls;
static open_cfw_freertos_port_u32 open_cfw_test_clear_calls;
static open_cfw_freertos_port_u32 open_cfw_test_clear_value;
static open_cfw_test_port_event_record open_cfw_test_events[16];
static size_t open_cfw_test_event_count_value;
static jmp_buf open_cfw_test_assert_jump;

static void open_cfw_test_log(
    open_cfw_freertos_port_u32 code,
    open_cfw_freertos_port_u32 value)
{
    if (open_cfw_test_event_count_value < 16U)
    {
        open_cfw_test_events[open_cfw_test_event_count_value].code = code;
        open_cfw_test_events[open_cfw_test_event_count_value].value = value;
        open_cfw_test_event_count_value++;
    }
}

static void open_cfw_test_write_icsr(open_cfw_freertos_port_u32 value)
{
    open_cfw_test_icsr = value;
    open_cfw_test_log(OPEN_CFW_TEST_PORT_WRITE_ICSR, value);
}

static open_cfw_freertos_port_u32 open_cfw_test_read_nesting(void)
{
    open_cfw_freertos_port_u32 value = open_cfw_test_nesting;
    open_cfw_test_log(OPEN_CFW_TEST_PORT_READ_NESTING, value);
    return value;
}

static void open_cfw_test_write_nesting(open_cfw_freertos_port_u32 value)
{
    open_cfw_test_nesting = value;
    open_cfw_test_log(OPEN_CFW_TEST_PORT_WRITE_NESTING, value);
}

static open_cfw_freertos_port_u32 open_cfw_test_set_mask(void)
{
    open_cfw_test_set_calls++;
    open_cfw_test_log(OPEN_CFW_TEST_PORT_SET_MASK, open_cfw_test_set_result);
    return open_cfw_test_set_result;
}

static void open_cfw_test_clear_mask(open_cfw_freertos_port_u32 value)
{
    open_cfw_test_clear_calls++;
    open_cfw_test_clear_value = value;
    open_cfw_test_log(OPEN_CFW_TEST_PORT_CLEAR_MASK, value);
}

static void open_cfw_test_dsb(void)
{
    open_cfw_test_log(OPEN_CFW_TEST_PORT_DSB, 0U);
}

static void open_cfw_test_isb(void)
{
    open_cfw_test_log(OPEN_CFW_TEST_PORT_ISB, 0U);
}

__attribute__((noreturn))
static void open_cfw_test_assert_failure(void)
{
    open_cfw_test_log(OPEN_CFW_TEST_PORT_ASSERT, 0U);
    longjmp(open_cfw_test_assert_jump, 1);
    __builtin_unreachable();
}

#define OPEN_CFW_FREERTOS_PORT_WRITE_ICSR(value) \
    open_cfw_test_write_icsr(value)
#define OPEN_CFW_FREERTOS_PORT_READ_CRITICAL_NESTING() \
    open_cfw_test_read_nesting()
#define OPEN_CFW_FREERTOS_PORT_WRITE_CRITICAL_NESTING(value) \
    open_cfw_test_write_nesting(value)
#define OPEN_CFW_FREERTOS_PORT_SET_INTERRUPT_MASK() open_cfw_test_set_mask()
#define OPEN_CFW_FREERTOS_PORT_CLEAR_INTERRUPT_MASK(mask) \
    open_cfw_test_clear_mask(mask)
#define OPEN_CFW_FREERTOS_PORT_DATA_BARRIER() open_cfw_test_dsb()
#define OPEN_CFW_FREERTOS_PORT_INSTRUCTION_BARRIER() open_cfw_test_isb()
#define OPEN_CFW_FREERTOS_PORT_ASSERT_FAILURE() \
    open_cfw_test_assert_failure()

#include "../../research/candidates/freertos_scheduler_port_trio.c"

void open_cfw_test_port_reset(
    open_cfw_freertos_port_u32 nesting,
    open_cfw_freertos_port_u32 set_result)
{
    size_t index;

    open_cfw_test_icsr = 0U;
    open_cfw_test_nesting = nesting;
    open_cfw_test_set_result = set_result;
    open_cfw_test_set_calls = 0U;
    open_cfw_test_clear_calls = 0U;
    open_cfw_test_clear_value = 0xFFFFFFFFU;
    open_cfw_test_event_count_value = 0U;
    for (index = 0U; index < 16U; index++)
    {
        open_cfw_test_events[index].code = 0U;
        open_cfw_test_events[index].value = 0U;
    }
}

void open_cfw_test_port_run_yield(void)
{
    open_cfw_freertos_port_yield();
}

void open_cfw_test_port_run_enter(void)
{
    open_cfw_freertos_port_enter_critical();
}

int open_cfw_test_port_run_exit(void)
{
    if (setjmp(open_cfw_test_assert_jump) == 0)
    {
        open_cfw_freertos_port_exit_critical();
        return 0;
    }
    return 1;
}

open_cfw_freertos_port_u32 open_cfw_test_port_icsr(void)
{
    return open_cfw_test_icsr;
}

open_cfw_freertos_port_u32 open_cfw_test_port_nesting(void)
{
    return open_cfw_test_nesting;
}

open_cfw_freertos_port_u32 open_cfw_test_port_set_calls(void)
{
    return open_cfw_test_set_calls;
}

open_cfw_freertos_port_u32 open_cfw_test_port_clear_calls(void)
{
    return open_cfw_test_clear_calls;
}

open_cfw_freertos_port_u32 open_cfw_test_port_clear_value(void)
{
    return open_cfw_test_clear_value;
}

size_t open_cfw_test_port_event_count(void)
{
    return open_cfw_test_event_count_value;
}

open_cfw_freertos_port_u32 open_cfw_test_port_event_code(size_t index)
{
    return open_cfw_test_events[index].code;
}

open_cfw_freertos_port_u32 open_cfw_test_port_event_value(size_t index)
{
    return open_cfw_test_events[index].value;
}
