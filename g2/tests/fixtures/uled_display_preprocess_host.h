#ifndef OPEN_CFW_ULED_DISPLAY_PREPROCESS_HOST_H
#define OPEN_CFW_ULED_DISPLAY_PREPROCESS_HOST_H

#include <stdint.h>

void open_cfw_test_uled_assert(const char *expression);
int open_cfw_test_uled_gpu_start(const void *, const void *, uint32_t);
void open_cfw_test_uled_destination_configure(uint32_t, uint32_t);
void open_cfw_test_uled_destination_mode(uint32_t);
void open_cfw_test_uled_destination_enable(uint32_t, uint32_t);
void open_cfw_test_uled_source_configure(
    const void *, uint32_t, uint32_t, uint32_t, uint32_t, uint32_t
);
void open_cfw_test_uled_offset_configure(uint32_t, uint32_t);
void open_cfw_test_uled_commit(uint32_t);
void open_cfw_test_uled_diagnostic(uint32_t);

#define OPEN_CFW_ULED_ASSERT(condition, expression) \
    do { \
        if (!(condition)) { \
            open_cfw_test_uled_assert(expression); \
            return; \
        } \
    } while (0)
#define OPEN_CFW_ULED_GPU_START(destination, region, flags) \
    open_cfw_test_uled_gpu_start((destination), (region), (flags))
#define OPEN_CFW_ULED_GPU_DESTINATION_CONFIGURE(channel, enabled) \
    open_cfw_test_uled_destination_configure((channel), (enabled))
#define OPEN_CFW_ULED_GPU_DESTINATION_MODE(channel) \
    open_cfw_test_uled_destination_mode(channel)
#define OPEN_CFW_ULED_GPU_DESTINATION_ENABLE(channel, enabled) \
    open_cfw_test_uled_destination_enable((channel), (enabled))
#define OPEN_CFW_ULED_GPU_SOURCE_CONFIGURE(source, width, height, format, stride, flags) \
    open_cfw_test_uled_source_configure( \
        (source), (width), (height), (format), (stride), (flags) \
    )
#define OPEN_CFW_ULED_GPU_OFFSET_CONFIGURE(x, y) \
    open_cfw_test_uled_offset_configure((x), (y))
#define OPEN_CFW_ULED_GPU_COMMIT(enabled) open_cfw_test_uled_commit(enabled)
#define OPEN_CFW_ULED_DIAGNOSTIC(result) open_cfw_test_uled_diagnostic(result)

extern int open_cfw_test_uled_start_result;
extern uint32_t open_cfw_test_uled_assert_count;
extern uint32_t open_cfw_test_uled_diagnostic_count;
extern uint32_t open_cfw_test_uled_call_count;
extern uint32_t open_cfw_test_uled_descriptor[7];
extern uint32_t open_cfw_test_uled_region[4];
extern uintptr_t open_cfw_test_uled_source;
extern uint32_t open_cfw_test_uled_source_args[5];
extern uint32_t open_cfw_test_uled_offset[2];
extern uint32_t open_cfw_test_uled_sequence[6];
extern char open_cfw_test_uled_assert_expression[80];

void open_cfw_test_uled_reset(void);

#endif
