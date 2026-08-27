struct open_cfw_test_transfer_call {
    unsigned int argument_0;
    unsigned int argument_1;
    int argument_2;
    unsigned int argument_3;
    unsigned int result_present;
    unsigned int schedule_present;
};

static unsigned int open_cfw_test_critical_context;
static unsigned int open_cfw_test_schedule_required;
static int open_cfw_test_result;
static unsigned int open_cfw_test_critical_calls;
static unsigned int open_cfw_test_normal_calls;
static unsigned int open_cfw_test_pendsv_calls;
static struct open_cfw_test_transfer_call open_cfw_test_calls[2];

static unsigned int open_cfw_test_critical_context_get(void)
{
    return open_cfw_test_critical_context;
}

static void open_cfw_test_record(
    unsigned int index,
    unsigned int argument_0,
    unsigned int argument_1,
    int argument_2,
    unsigned int argument_3,
    int *result,
    unsigned int *schedule_required
)
{
    open_cfw_test_calls[index].argument_0 = argument_0;
    open_cfw_test_calls[index].argument_1 = argument_1;
    open_cfw_test_calls[index].argument_2 = argument_2;
    open_cfw_test_calls[index].argument_3 = argument_3;
    open_cfw_test_calls[index].result_present = result != (int *)0;
    open_cfw_test_calls[index].schedule_present =
        schedule_required != (unsigned int *)0;
    if (result != (int *)0) {
        *result = open_cfw_test_result;
    }
    if (schedule_required != (unsigned int *)0) {
        *schedule_required = open_cfw_test_schedule_required;
    }
}

static void open_cfw_test_critical_transfer(
    unsigned int argument_0, unsigned int argument_1, int argument_2,
    unsigned int argument_3, int *result, unsigned int *schedule_required
)
{
    open_cfw_test_record(open_cfw_test_critical_calls++, argument_0, argument_1,
        argument_2, argument_3, result, schedule_required);
}

static void open_cfw_test_normal_transfer(
    unsigned int argument_0, unsigned int argument_1, int argument_2,
    unsigned int argument_3, int *result
)
{
    open_cfw_test_record(open_cfw_test_normal_calls++, argument_0, argument_1,
        argument_2, argument_3, result, (unsigned int *)0);
}

static void open_cfw_test_pendsv_set(void) { open_cfw_test_pendsv_calls += 1U; }

#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() open_cfw_test_critical_context_get()
#define OPEN_CFW_BOOTLOADER_RUNTIME_TRANSFER_CRITICAL_418FE8(...) open_cfw_test_critical_transfer(__VA_ARGS__)
#define OPEN_CFW_BOOTLOADER_RUNTIME_TRANSFER_NORMAL_418E70(...) open_cfw_test_normal_transfer(__VA_ARGS__)
#define OPEN_CFW_BOOTLOADER_PENDSV_SET() open_cfw_test_pendsv_set()
#include "../../components/bootloader/core_overlay/runtime_transfer_41623a.c"

void open_cfw_test_transfer_reset(unsigned int critical, int result, unsigned int schedule)
{
    unsigned int index;
    open_cfw_test_critical_context = critical;
    open_cfw_test_result = result;
    open_cfw_test_schedule_required = schedule;
    open_cfw_test_critical_calls = 0U;
    open_cfw_test_normal_calls = 0U;
    open_cfw_test_pendsv_calls = 0U;
    for (index = 0U; index < 2U; index += 1U) {
        open_cfw_test_calls[index] = (struct open_cfw_test_transfer_call){0};
    }
}

unsigned int open_cfw_test_transfer_critical_calls_get(void) { return open_cfw_test_critical_calls; }
unsigned int open_cfw_test_transfer_normal_calls_get(void) { return open_cfw_test_normal_calls; }
unsigned int open_cfw_test_transfer_pendsv_calls_get(void) { return open_cfw_test_pendsv_calls; }
struct open_cfw_test_transfer_call open_cfw_test_transfer_call_get(unsigned int index) { return open_cfw_test_calls[index]; }
