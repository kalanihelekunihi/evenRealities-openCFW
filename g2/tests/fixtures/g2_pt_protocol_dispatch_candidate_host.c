/* SPDX-License-Identifier: MIT */

#include "../../research/candidates/g2_pt_protocol_dispatch_candidate.c"

unsigned int open_cfw_test_pt_command_count(void)
{
    return open_cfw_pt_candidate_command_count();
}

int open_cfw_test_pt_command_at(
    unsigned int index,
    open_cfw_pt_u8 *command
)
{
    return open_cfw_pt_candidate_command_at(index, command);
}

int open_cfw_test_pt_command_policy(unsigned int command)
{
    return (int)open_cfw_pt_candidate_command_policy(
        (open_cfw_pt_u8)command
    );
}

int open_cfw_test_pt_dispatch(
    const open_cfw_pt_u8 *request,
    unsigned int request_length,
    open_cfw_pt_u8 *response,
    unsigned int response_capacity,
    unsigned int *response_length
)
{
    return (int)open_cfw_pt_candidate_dispatch(
        request,
        request_length,
        response,
        response_capacity,
        response_length
    );
}
