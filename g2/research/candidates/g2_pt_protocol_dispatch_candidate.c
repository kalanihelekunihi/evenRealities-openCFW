/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room, unrouted product-test command policy surface for the G2.
 *
 * Evidence is limited to the authenticated 2.2.6.10 dispatcher at
 * 0x0056F4A0, its 66 command comparisons, and its unsupported response plus
 * prefix/checksum helpers. Command handlers and hardware providers are
 * deliberately absent until their policy can be justified independently.
 */

#include "g2_pt_protocol_dispatch_candidate.h"

#define OPEN_CFW_PT_COMMAND_COUNT 66U
#define OPEN_CFW_PT_UNSUPPORTED_FRAME_LENGTH 10U

static const open_cfw_pt_u8 open_cfw_pt_commands[OPEN_CFW_PT_COMMAND_COUNT] = {
    0x01U, 0x05U, 0x06U, 0x07U, 0x08U, 0x0BU, 0x11U, 0x13U,
    0x17U, 0x18U, 0x19U, 0x1AU, 0x1BU, 0x1CU, 0x20U, 0x22U,
    0x24U, 0x25U, 0x26U, 0x29U, 0x2AU, 0x2DU, 0x2EU, 0x30U,
    0x31U, 0x35U, 0x38U, 0x39U, 0x3AU, 0x3DU, 0x3EU, 0x42U,
    0x43U, 0x44U, 0x45U, 0x46U, 0x47U, 0x48U, 0x49U, 0x52U,
    0x53U, 0x54U, 0x55U, 0x57U, 0x58U, 0x59U, 0x5AU, 0x5BU,
    0x60U, 0x61U, 0x62U, 0x63U, 0x64U, 0x65U, 0x66U, 0x67U,
    0x69U, 0x6AU, 0x6BU, 0x6CU, 0x6DU, 0x6EU, 0x74U, 0x75U,
    0x77U, 0xF3U
};

__attribute__((used, noinline))
unsigned int open_cfw_pt_candidate_command_count(void)
{
    return OPEN_CFW_PT_COMMAND_COUNT;
}

__attribute__((used, noinline))
int open_cfw_pt_candidate_command_at(
    unsigned int index,
    open_cfw_pt_u8 *command
)
{
    if (command == (open_cfw_pt_u8 *)0 || index >= OPEN_CFW_PT_COMMAND_COUNT) {
        return 0;
    }
    *command = open_cfw_pt_commands[index];
    return 1;
}

__attribute__((used, noinline))
enum open_cfw_pt_command_policy open_cfw_pt_candidate_command_policy(
    open_cfw_pt_u8 command
)
{
    unsigned int index;

    for (index = 0U; index < OPEN_CFW_PT_COMMAND_COUNT; ++index) {
        if (open_cfw_pt_commands[index] == command) {
            return OPEN_CFW_PT_COMMAND_KNOWN_WITHHELD;
        }
    }
    return OPEN_CFW_PT_COMMAND_UNKNOWN;
}

__attribute__((used, noinline))
enum open_cfw_pt_dispatch_result open_cfw_pt_candidate_dispatch(
    const open_cfw_pt_u8 *request,
    unsigned int request_length,
    open_cfw_pt_u8 *response,
    unsigned int response_capacity,
    unsigned int *response_length
)
{
    unsigned int index;
    open_cfw_pt_u8 checksum;

    if (response_length != (unsigned int *)0) {
        *response_length = 0U;
    }
    if (request == (const open_cfw_pt_u8 *)0 || request_length == 0U ||
        response == (open_cfw_pt_u8 *)0 ||
        response_length == (unsigned int *)0) {
        return OPEN_CFW_PT_DISPATCH_INVALID_ARGUMENT;
    }
    if (response_capacity < OPEN_CFW_PT_UNSUPPORTED_FRAME_LENGTH) {
        return OPEN_CFW_PT_DISPATCH_OUTPUT_TOO_SMALL;
    }

    response[0] = 0x5AU;
    response[1] = 0xA5U;
    response[2] = 0xFFU;
    response[3] = 0x05U;
    response[4] = request[0];
    response[5] = 0x01U;
    response[6] = 0x03U;
    response[7] = 0x01U;
    response[8] = 0x02U;

    checksum = 0U;
    for (index = 0U; index < 9U; ++index) {
        checksum = (open_cfw_pt_u8)(checksum + response[index]);
    }
    response[9] = checksum;
    *response_length = OPEN_CFW_PT_UNSUPPORTED_FRAME_LENGTH;
    return OPEN_CFW_PT_DISPATCH_FRAME_READY_UNSUPPORTED;
}
