/* Authenticated two-node Case nanopb descriptor graph, stock root 0x77793c.
 * Regenerate with extract_main_case_descriptor_77793c_20261017.py. */
#include "pb.h"

static const uint32_t case_fields_0[5] = {0x10001204u, 0x10011208u, 0x2001380du, 0x00050004u, 0x00000000u};
static const uint32_t case_fields_1[6] = {0x10001204u, 0x10011208u, 0x1002120cu, 0x10031210u, 0x10041214u, 0x00000000u};
static const pb_msgdesc_t *const case_no_submessages[1] = {0};
static const pb_msgdesc_t case_nested_descriptor = {
    case_fields_1, case_no_submessages, 0, 0, 5u, 0u, 5u
};
static const pb_msgdesc_t *const case_root_submessages[2] = {
    &case_nested_descriptor, 0
};
const pb_msgdesc_t audio_uart_case_descriptor_77793c = {
    case_fields_0, case_root_submessages, 0, 0, 3u, 0u, 3u
};
