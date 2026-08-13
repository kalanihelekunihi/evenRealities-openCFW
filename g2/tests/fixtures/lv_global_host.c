#include <stdarg.h>

unsigned int open_cfw_test_lv_global_list_calls;
void *open_cfw_test_lv_global_list_pointers[2];
unsigned int open_cfw_test_lv_global_list_sizes[2];
unsigned int open_cfw_test_lv_global_finalize_calls;
unsigned int open_cfw_test_lv_global_finalize_cookie;
unsigned int open_cfw_test_lv_global_log_calls;
unsigned int open_cfw_test_lv_global_log_level;
const void *open_cfw_test_lv_global_log_file;
unsigned int open_cfw_test_lv_global_log_line;
const void *open_cfw_test_lv_global_log_function;
const void *open_cfw_test_lv_global_log_arguments[4];
unsigned int open_cfw_test_lv_global_fatal_calls;

void open_cfw_test_lv_global_list_initialize(
    void *list,
    unsigned int node_size
)
{
    unsigned int index = open_cfw_test_lv_global_list_calls++;

    if (index < 2U) {
        open_cfw_test_lv_global_list_pointers[index] = list;
        open_cfw_test_lv_global_list_sizes[index] = node_size;
    }
}

void open_cfw_test_lv_global_finalize(unsigned int cookie)
{
    open_cfw_test_lv_global_finalize_calls += 1U;
    open_cfw_test_lv_global_finalize_cookie = cookie;
}

void open_cfw_test_lv_global_log(
    unsigned int level,
    const void *file,
    unsigned int line,
    const void *function,
    ...
)
{
    va_list arguments;
    unsigned int index;

    open_cfw_test_lv_global_log_calls += 1U;
    open_cfw_test_lv_global_log_level = level;
    open_cfw_test_lv_global_log_file = file;
    open_cfw_test_lv_global_log_line = line;
    open_cfw_test_lv_global_log_function = function;
    va_start(arguments, function);
    for (index = 0U; index < 4U; index += 1U) {
        open_cfw_test_lv_global_log_arguments[index] =
            va_arg(arguments, const void *);
    }
    va_end(arguments);
}

void open_cfw_test_lv_global_fatal(void)
{
    open_cfw_test_lv_global_fatal_calls += 1U;
}

#define OPEN_CFW_LV_GLOBAL_LIST_INITIALIZE(list, node_size) \
    open_cfw_test_lv_global_list_initialize((list), (node_size))
#define OPEN_CFW_LV_GLOBAL_FINALIZE(cookie) \
    open_cfw_test_lv_global_finalize(cookie)
#define OPEN_CFW_LV_GLOBAL_LOG open_cfw_test_lv_global_log
#define OPEN_CFW_LV_GLOBAL_FATAL() open_cfw_test_lv_global_fatal()

#include "../../components/apollo_main/core_overlay/lv_memory.c"
#include "../../components/apollo_main/core_overlay/lv_global.c"
