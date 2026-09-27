/*
 * SPDX-License-Identifier: MIT
 *
 * Semantic reference model for the ranked AM115 bounded local-return chunk at
 * 0x00546e02. This file is host-testable evidence for source pull-through; it
 * is not yet routed into the firmware overlay.
 */

#include <stdint.h>

typedef struct {
    uint32_t r0;
    uint32_t stack_adjust_bytes;
    uint32_t restored_r4;
    uint32_t returned_via_pop_pc;
    uint32_t bounded_return_prefix_bytes;
    uint32_t post_return_boundary_bytes;
} open_cfw_am115_0x5455c6_outputs;

open_cfw_am115_0x5455c6_outputs
open_cfw_am115_0x5455c6_semantic_model(void)
{
    open_cfw_am115_0x5455c6_outputs out;

    out.r0 = 0U;
    out.stack_adjust_bytes = 0x18U;
    out.restored_r4 = 1U;
    out.returned_via_pop_pc = 1U;
    out.bounded_return_prefix_bytes = 6U;
    out.post_return_boundary_bytes = 24U;
    return out;
}

typedef struct {
    uint32_t gate_word;
} open_cfw_am115_0x546e02_inputs;

typedef struct {
    uint32_t r0;
    uint32_t r1;
    uint32_t call_r0;
    uint32_t call_r1;
    uint32_t call_target;
    int branch_to_call;
    int call_performed;
} open_cfw_am115_0x546e02_outputs;

open_cfw_am115_0x546e02_outputs
open_cfw_am115_0x546e02_semantic_model(
    open_cfw_am115_0x546e02_inputs in)
{
    open_cfw_am115_0x546e02_outputs out;

    out.branch_to_call = in.gate_word == 1U;
    out.call_performed = out.branch_to_call;
    out.call_target = out.call_performed ? 0x0043b40eU : 0U;
    out.call_r0 = out.call_performed ? 0x0078e144U : 0U;
    out.call_r1 = out.call_performed ? 0x200031b4U : 0U;
    out.r1 = out.call_r1;
    out.r0 = 0U;
    return out;
}

typedef struct {
    uint32_t r0;
    uint32_t r1;
} open_cfw_am115_0x545ec4_inputs;

typedef struct {
    uint32_t call_target;
    uint32_t call_r0;
    uint32_t call_r1;
    uint32_t return_register_passthrough;
} open_cfw_am115_0x545ec4_outputs;

open_cfw_am115_0x545ec4_outputs
open_cfw_am115_0x545ec4_semantic_model(
    open_cfw_am115_0x545ec4_inputs in)
{
    open_cfw_am115_0x545ec4_outputs out;

    out.call_target = 0x00486876U;
    out.call_r0 = in.r0;
    out.call_r1 = in.r1 & 0xFFFFU;
    out.return_register_passthrough = 1;
    return out;
}
