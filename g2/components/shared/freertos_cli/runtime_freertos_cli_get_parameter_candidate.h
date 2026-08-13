/* SPDX-License-Identifier: MIT */
#ifndef OPEN_CFW_RUNTIME_FREERTOS_CLI_GET_PARAMETER_CANDIDATE_H
#define OPEN_CFW_RUNTIME_FREERTOS_CLI_GET_PARAMETER_CANDIDATE_H

/*
 * Isolated 32-bit ABI for the production-excluded FreeRTOS+CLI parameter
 * accessor candidate.  These types match the authenticated G2 ABI without
 * importing the rest of the FreeRTOS application configuration.
 */
typedef __UINT32_TYPE__ open_cfw_freertos_cli_ubase_type;
typedef __INT32_TYPE__ open_cfw_freertos_cli_base_type;

_Static_assert(
    sizeof(open_cfw_freertos_cli_ubase_type) == 4U,
    "G2 UBaseType_t must remain 32-bit"
);
_Static_assert(
    sizeof(open_cfw_freertos_cli_base_type) == 4U,
    "G2 BaseType_t must remain 32-bit"
);

/*
 * Return the start of the requested space-delimited parameter and write its
 * byte length.  Parameter numbering starts at one; zero and missing
 * parameters return null after first writing a zero length.
 *
 * The input contract is intentionally identical to upstream: pc_command must
 * be NUL terminated.  This leaf performs no independent bounds check.
 */
const char *open_cfw_freertos_cli_get_parameter_candidate(
    const char *pc_command,
    open_cfw_freertos_cli_ubase_type wanted_parameter,
    open_cfw_freertos_cli_base_type *parameter_length
);

#endif
