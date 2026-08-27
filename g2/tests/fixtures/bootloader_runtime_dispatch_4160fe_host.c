static unsigned int open_cfw_test_critical;
static unsigned int open_cfw_test_critical_calls;
static unsigned int open_cfw_test_path_a_calls;
static unsigned int open_cfw_test_path_b_calls;
static unsigned int open_cfw_test_path_a_result;
static unsigned int open_cfw_test_path_b_result;
static int open_cfw_test_path_b_status;
static unsigned int open_cfw_test_arguments[7];

static unsigned int open_cfw_test_critical_context(void)
{
    open_cfw_test_critical_calls += 1U;
    return open_cfw_test_critical;
}

static unsigned int open_cfw_test_path_a(
    unsigned int a0, unsigned int a1, unsigned int a2, unsigned int a3,
    unsigned int a4, unsigned int a5, unsigned int a6
)
{
    unsigned int values[7] = {a0, a1, a2, a3, a4, a5, a6};
    unsigned int index;
    open_cfw_test_path_a_calls += 1U;
    for (index = 0U; index < 7U; index += 1U) {
        open_cfw_test_arguments[index] = values[index];
    }
    return open_cfw_test_path_a_result;
}

static int open_cfw_test_path_b(
    unsigned int a0, unsigned int a1, unsigned short a2, unsigned int a3,
    unsigned int a4, unsigned int *result
)
{
    open_cfw_test_path_b_calls += 1U;
    open_cfw_test_arguments[0] = a0;
    open_cfw_test_arguments[1] = a1;
    open_cfw_test_arguments[2] = a2;
    open_cfw_test_arguments[3] = a3;
    open_cfw_test_arguments[4] = a4;
    open_cfw_test_arguments[5] = (result != (unsigned int *)0);
    *result = open_cfw_test_path_b_result;
    return open_cfw_test_path_b_status;
}

#define OPEN_CFW_BOOTLOADER_CRITICAL_CONTEXT() open_cfw_test_critical_context()
#define OPEN_CFW_BOOTLOADER_RUNTIME_4160FE_PATH_A(...) open_cfw_test_path_a(__VA_ARGS__)
#define OPEN_CFW_BOOTLOADER_RUNTIME_4160FE_PATH_B(...) open_cfw_test_path_b(__VA_ARGS__)
#include "../../components/bootloader/core_overlay/runtime_dispatch_4160fe.c"

void open_cfw_test_runtime_dispatch_set(
    unsigned int critical,
    unsigned int path_a_result,
    int path_b_status,
    unsigned int path_b_result
)
{
    unsigned int index;
    open_cfw_test_critical = critical;
    open_cfw_test_path_a_result = path_a_result;
    open_cfw_test_path_b_status = path_b_status;
    open_cfw_test_path_b_result = path_b_result;
    open_cfw_test_critical_calls = 0U;
    open_cfw_test_path_a_calls = 0U;
    open_cfw_test_path_b_calls = 0U;
    for (index = 0U; index < 7U; index += 1U) {
        open_cfw_test_arguments[index] = 0U;
    }
}

unsigned int open_cfw_test_runtime_dispatch_critical_calls(void) { return open_cfw_test_critical_calls; }
unsigned int open_cfw_test_runtime_dispatch_path_a_calls(void) { return open_cfw_test_path_a_calls; }
unsigned int open_cfw_test_runtime_dispatch_path_b_calls(void) { return open_cfw_test_path_b_calls; }
unsigned int open_cfw_test_runtime_dispatch_argument(unsigned int index)
{
    return index < 7U ? open_cfw_test_arguments[index] : 0U;
}

unsigned int open_cfw_test_runtime_dispatch_options_size(void)
{
    return (unsigned int)sizeof(struct open_cfw_bootloader_runtime_4160fe_options);
}
