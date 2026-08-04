unsigned int open_cfw_test_policy_count;
unsigned int open_cfw_test_policy_ready;
unsigned int open_cfw_test_policy_operation;
unsigned int open_cfw_test_policy_result;
unsigned int open_cfw_test_log_flags_value;
unsigned int open_cfw_test_log_count;
unsigned int open_cfw_test_log_level[2];
unsigned int open_cfw_test_log_line[2];
unsigned long open_cfw_test_log_tag[2];
unsigned long open_cfw_test_log_format[2];
unsigned int open_cfw_test_trace_count;
unsigned int open_cfw_test_trace_mask[2];
unsigned long open_cfw_test_trace_schema[2];

unsigned int open_cfw_test_policy(
    unsigned int ready,
    unsigned int operation
)
{
    ++open_cfw_test_policy_count;
    open_cfw_test_policy_ready = ready;
    open_cfw_test_policy_operation = operation;
    return open_cfw_test_policy_result;
}

unsigned int open_cfw_test_log_flags(void)
{
    return open_cfw_test_log_flags_value;
}

void open_cfw_test_log_record(
    unsigned int level,
    const void *module,
    const void *file,
    const void *tag,
    unsigned int line,
    const void *format,
    ...
)
{
    unsigned int index = open_cfw_test_log_count++;

    (void)module;
    (void)file;
    open_cfw_test_log_level[index] = level;
    open_cfw_test_log_line[index] = line;
    open_cfw_test_log_tag[index] = (unsigned long)tag;
    open_cfw_test_log_format[index] = (unsigned long)format;
}

void open_cfw_test_trace_record(
    unsigned int mask,
    const void *schema,
    const void *format,
    ...
)
{
    unsigned int index = open_cfw_test_trace_count++;

    (void)format;
    open_cfw_test_trace_mask[index] = mask;
    open_cfw_test_trace_schema[index] = (unsigned long)schema;
}

#define OPEN_CFW_UI_STARTUP_POLICY(ready, operation) \
    open_cfw_test_policy(ready, operation)
#define OPEN_CFW_UI_STARTUP_LOG_FLAGS open_cfw_test_log_flags
#define OPEN_CFW_UI_STARTUP_LOG_RECORD open_cfw_test_log_record
#define OPEN_CFW_UI_STARTUP_TRACE_RECORD open_cfw_test_trace_record

#include "../../components/apollo_main/core_overlay/ui_startup_app.c"
