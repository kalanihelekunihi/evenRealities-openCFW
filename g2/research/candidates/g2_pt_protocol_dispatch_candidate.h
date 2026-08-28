/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room, unrouted product-test command policy surface for the G2.
 */

#ifndef OPEN_CFW_G2_PT_PROTOCOL_DISPATCH_CANDIDATE_H
#define OPEN_CFW_G2_PT_PROTOCOL_DISPATCH_CANDIDATE_H

typedef unsigned char open_cfw_pt_u8;

enum open_cfw_pt_command_policy {
    OPEN_CFW_PT_COMMAND_UNKNOWN = 0,
    OPEN_CFW_PT_COMMAND_KNOWN_WITHHELD = 1
};

enum open_cfw_pt_dispatch_result {
    OPEN_CFW_PT_DISPATCH_FRAME_READY_UNSUPPORTED = 1,
    OPEN_CFW_PT_DISPATCH_INVALID_ARGUMENT = -1,
    OPEN_CFW_PT_DISPATCH_OUTPUT_TOO_SMALL = -2
};

/* The authenticated G2 2.2.6.10 dispatcher contains exactly 66 command IDs. */
unsigned int open_cfw_pt_candidate_command_count(void);

/* Returns zero if index is outside the authenticated command-ID surface. */
int open_cfw_pt_candidate_command_at(
    unsigned int index,
    open_cfw_pt_u8 *command
);

/* No product-test hardware operation is admitted by this candidate. */
enum open_cfw_pt_command_policy open_cfw_pt_candidate_command_policy(
    open_cfw_pt_u8 command
);

/*
 * Build the evidenced unsupported-command frame:
 *   5a a5 ff 05 <command> 01 03 01 02 <additive checksum>
 *
 * Known and unknown commands intentionally take the same fail-closed path.
 */
enum open_cfw_pt_dispatch_result open_cfw_pt_candidate_dispatch(
    const open_cfw_pt_u8 *request,
    unsigned int request_length,
    open_cfw_pt_u8 *response,
    unsigned int response_capacity,
    unsigned int *response_length
);

#endif
