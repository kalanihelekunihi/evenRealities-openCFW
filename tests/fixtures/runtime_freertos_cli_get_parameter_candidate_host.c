#include <stddef.h>
#include <stdint.h>

#include "../../components/shared/freertos_cli/runtime_freertos_cli_get_parameter_candidate.h"

extern const char *FreeRTOS_CLIGetParameter(
    const char *pc_command,
    uint32_t wanted_parameter,
    int32_t *parameter_length
);

extern const char *open_cfw_freertos_cli_get_parameter(
    const char *pc_command,
    uint32_t wanted_parameter,
    int32_t *parameter_length
);

static int32_t open_cfw_test_offset(
    const char *input,
    const char *result
)
{
    if (result == (const char *)0) {
        return -1;
    }
    return (int32_t)(result - input);
}

int32_t open_cfw_test_freertos_cli_get_parameter_candidate(
    const char *input,
    uint32_t wanted_parameter,
    int32_t *parameter_length
)
{
    return open_cfw_test_offset(
        input,
        open_cfw_freertos_cli_get_parameter_candidate(
            input,
            wanted_parameter,
            parameter_length
        )
    );
}

int32_t open_cfw_test_freertos_cli_get_parameter_production(
    const char *input,
    uint32_t wanted_parameter,
    int32_t *parameter_length
)
{
    return open_cfw_test_offset(
        input,
        open_cfw_freertos_cli_get_parameter(
            input,
            wanted_parameter,
            parameter_length
        )
    );
}

int32_t open_cfw_test_freertos_cli_get_parameter_upstream(
    const char *input,
    uint32_t wanted_parameter,
    int32_t *parameter_length
)
{
    return open_cfw_test_offset(
        input,
        FreeRTOS_CLIGetParameter(
            input,
            wanted_parameter,
            parameter_length
        )
    );
}
