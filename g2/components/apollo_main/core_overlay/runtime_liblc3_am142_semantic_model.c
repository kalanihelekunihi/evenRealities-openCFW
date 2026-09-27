/*
 * SPDX-License-Identifier: MIT
 *
 * Semantic reference models for AM142 retained helper clusters. This file is
 * host-testable evidence for the next source pull-through steps; it is not yet
 * routed into the firmware overlay.
 */

#include <stdint.h>

typedef struct {
    uint32_t context_0x1c;
} open_cfw_am142_0x59aa84_inputs;

typedef struct {
    uint32_t r0;
    uint32_t call_target;
    uint32_t call_r0;
    uint32_t cleared_byte_offset;
    uint32_t cleared_byte_value;
} open_cfw_am142_0x59aa84_outputs;

open_cfw_am142_0x59aa84_outputs
open_cfw_am142_0x59aa84_semantic_model(
    open_cfw_am142_0x59aa84_inputs in)
{
    open_cfw_am142_0x59aa84_outputs out;

    out.call_target = 0x005999a6U;
    out.call_r0 = in.context_0x1c;
    out.r0 = 0U;
    out.cleared_byte_offset = in.context_0x1c + 0x2cU;
    out.cleared_byte_value = 0U;
    return out;
}

typedef struct {
    uint32_t context_0x1c;
    uint32_t stacked_r4;
} open_cfw_am142_0x59af42_inputs;

typedef struct {
    uint32_t r0;
    uint32_t r4;
    uint32_t call_target;
    uint32_t call_r0;
    uint32_t cleared_byte_offset;
    uint32_t cleared_byte_value;
    uint32_t return_restored_r4_from_stack;
} open_cfw_am142_0x59af42_outputs;

open_cfw_am142_0x59af42_outputs
open_cfw_am142_0x59af42_semantic_model(
    open_cfw_am142_0x59af42_inputs in)
{
    open_cfw_am142_0x59af42_outputs out;

    out.call_target = 0x005999a6U;
    out.call_r0 = 0U;
    out.r0 = 0U;
    out.r4 = in.stacked_r4;
    out.cleared_byte_offset = in.context_0x1c + 0x2cU;
    out.cleared_byte_value = 0U;
    out.return_restored_r4_from_stack = 1U;
    return out;
}

typedef struct {
    uint32_t object;
    uint32_t context_0x1c;
    uint32_t context_flag_0x2c;
    uint32_t slot_0x18_current;
    uint32_t arg_field_0x00;
    uint32_t arg_field_0x04;
    uint32_t arg_field_0x08;
    uint32_t arg_field_0x0c;
    uint32_t first_call_return;
    uint32_t second_call_return;
    uint32_t stacked_r4;
    uint32_t stacked_r5;
    uint32_t stacked_r6;
} open_cfw_am142_0x59af54_inputs;

typedef struct {
    uint32_t r0;
    uint32_t r4;
    uint32_t r5;
    uint32_t r6;
    uint32_t first_call_performed;
    uint32_t first_call_target;
    uint32_t first_call_r0;
    uint32_t first_call_r1;
    uint32_t first_call_r2;
    uint32_t second_call_performed;
    uint32_t second_call_target;
    uint32_t second_call_r0;
    uint32_t second_call_r1;
    uint32_t second_call_r2;
    uint32_t slot_store_performed;
    uint32_t slot_store_value;
    uint32_t return_restored_registers_from_stack;
} open_cfw_am142_0x59af54_outputs;

open_cfw_am142_0x59af54_outputs
open_cfw_am142_0x59af54_semantic_model(
    open_cfw_am142_0x59af54_inputs in)
{
    open_cfw_am142_0x59af54_outputs out;

    out.r4 = in.stacked_r4;
    out.r5 = in.stacked_r5;
    out.r6 = in.stacked_r6;
    out.first_call_performed = in.context_flag_0x2c == 0U ? 1U : 0U;
    out.first_call_target = 0x00599978U;
    out.first_call_r0 = in.context_0x1c;
    out.first_call_r1 = in.arg_field_0x00;
    out.first_call_r2 = in.arg_field_0x04;
    out.second_call_performed = 0U;
    out.second_call_target = 0x005998E8U;
    out.second_call_r0 = in.context_0x1c;
    out.second_call_r1 = in.arg_field_0x08;
    out.second_call_r2 = in.arg_field_0x0c;
    out.slot_store_performed = 0U;
    out.slot_store_value = 0U;
    if (out.first_call_performed != 0U && in.first_call_return != 0U) {
        out.r0 = in.first_call_return;
        if (in.slot_0x18_current == 0U) {
            out.slot_store_performed = 1U;
            out.slot_store_value = in.first_call_return;
        }
    } else {
        out.second_call_performed = 1U;
        out.r0 = in.second_call_return;
        if (in.second_call_return != 0U && in.slot_0x18_current == 0U) {
            out.slot_store_performed = 1U;
            out.slot_store_value = in.second_call_return;
        }
    }
    out.return_restored_registers_from_stack = 1U;
    (void)in.object;
    return out;
}

typedef struct {
    uint32_t object;
    uint32_t context_0x1c;
    uint32_t context_flag_0x2c;
    uint32_t slot_0x18_current;
    uint32_t arg_field_0x00;
    uint32_t arg_field_0x04;
    uint32_t arg_field_0x08;
    uint32_t arg_field_0x0c;
    uint32_t arg_field_0x10;
    uint32_t arg_field_0x14;
    uint32_t arg_field_0x18;
    uint32_t arg_field_0x1c;
    uint32_t first_call_return;
    uint32_t second_call_return;
    uint32_t stacked_r4;
    uint32_t stacked_r5;
    uint32_t stacked_r6;
} open_cfw_am142_0x59afa0_inputs;

typedef struct {
    uint32_t r0;
    uint32_t r4;
    uint32_t r5;
    uint32_t r6;
    uint32_t first_call_performed;
    uint32_t first_call_target;
    uint32_t first_call_r0;
    uint32_t first_call_r1;
    uint32_t first_call_r2;
    uint32_t second_call_performed;
    uint32_t second_call_target;
    uint32_t second_call_r0;
    uint32_t second_call_r1;
    uint32_t fallback_call_count;
    uint32_t fallback_call_target;
    uint32_t fallback0_r1;
    uint32_t fallback0_r2;
    uint32_t fallback0_r3;
    uint32_t fallback1_r1;
    uint32_t fallback1_r2;
    uint32_t fallback1_r3;
    uint32_t fallback2_r1;
    uint32_t fallback2_r2;
    uint32_t fallback2_r3;
    uint32_t slot_store_performed;
    uint32_t slot_store_value;
    uint32_t return_restored_registers_from_stack;
} open_cfw_am142_0x59afa0_outputs;

open_cfw_am142_0x59afa0_outputs
open_cfw_am142_0x59afa0_semantic_model(
    open_cfw_am142_0x59afa0_inputs in)
{
    open_cfw_am142_0x59afa0_outputs out;

    out.r4 = in.stacked_r4;
    out.r5 = in.stacked_r5;
    out.r6 = in.stacked_r6;
    out.first_call_performed = in.context_flag_0x2c == 0U ? 1U : 0U;
    out.first_call_target = 0x00599978U;
    out.first_call_r0 = in.context_0x1c;
    out.first_call_r1 = in.arg_field_0x00;
    out.first_call_r2 = in.arg_field_0x04;
    out.second_call_performed = 0U;
    out.second_call_target = 0x0059987EU;
    out.second_call_r0 = in.context_0x1c;
    out.second_call_r1 = 3U;
    out.fallback_call_count = 0U;
    out.fallback_call_target = 0x005998AAU;
    out.fallback0_r1 = in.arg_field_0x08;
    out.fallback0_r2 = in.arg_field_0x0c;
    out.fallback0_r3 = 0U;
    out.fallback1_r1 = in.arg_field_0x10;
    out.fallback1_r2 = in.arg_field_0x14;
    out.fallback1_r3 = 0U;
    out.fallback2_r1 = in.arg_field_0x18;
    out.fallback2_r2 = in.arg_field_0x1c;
    out.fallback2_r3 = 1U;
    out.slot_store_performed = 0U;
    out.slot_store_value = 0U;
    if (out.first_call_performed != 0U && in.first_call_return != 0U) {
        out.r0 = in.first_call_return;
        if (in.slot_0x18_current == 0U) {
            out.slot_store_performed = 1U;
            out.slot_store_value = in.first_call_return;
        }
    } else {
        out.second_call_performed = 1U;
        if (in.second_call_return != 0U) {
            out.r0 = in.second_call_return;
            if (in.slot_0x18_current == 0U) {
                out.slot_store_performed = 1U;
                out.slot_store_value = in.second_call_return;
            }
        } else {
            out.r0 = in.second_call_return;
            out.fallback_call_count = 3U;
        }
    }
    out.return_restored_registers_from_stack = 1U;
    (void)in.object;
    return out;
}

typedef struct {
    uint32_t object_field_0x00;
    uint32_t object_field_0x0c;
    uint32_t arg_r1;
    uint32_t helper_return;
    uint32_t stacked_r4;
} open_cfw_am142_0x59aec8_inputs;

typedef struct {
    uint32_t r0;
    uint32_t r4;
    uint32_t helper_call_performed;
    uint32_t helper_call_target;
    uint32_t helper_call_r0;
    uint32_t helper_call_r1;
    uint32_t initial_range_rejected;
    uint32_t arg_threshold_rejected;
    uint32_t helper_range_rejected;
    uint32_t return_restored_r4_from_stack;
} open_cfw_am142_0x59aec8_outputs;

open_cfw_am142_0x59aec8_outputs
open_cfw_am142_0x59aec8_semantic_model(
    open_cfw_am142_0x59aec8_inputs in)
{
    open_cfw_am142_0x59aec8_outputs out;

    out.r4 = in.stacked_r4;
    out.helper_call_performed = 0U;
    out.helper_call_target = 0x004EC774U;
    out.helper_call_r0 = 0x07D00000U;
    out.helper_call_r1 = in.arg_r1 << 16U;
    out.initial_range_rejected = (
        in.object_field_0x00 < 1U || in.object_field_0x0c < 1U) ? 1U : 0U;
    out.arg_threshold_rejected = 0U;
    out.helper_range_rejected = 0U;
    out.return_restored_r4_from_stack = 1U;
    if (out.initial_range_rejected != 0U) {
        out.r0 = 0x24U;
        return out;
    }
    out.arg_threshold_rejected = in.arg_r1 >= 0x8000U ? 1U : 0U;
    if (out.arg_threshold_rejected != 0U) {
        out.r0 = 0xA4U;
        return out;
    }
    out.helper_call_performed = 1U;
    out.helper_range_rejected = (
        in.helper_return < in.object_field_0x00 ||
        in.helper_return >= in.object_field_0x0c) ? 1U : 0U;
    out.r0 = out.helper_range_rejected != 0U ? 0xA4U : 0U;
    return out;
}

typedef struct {
    uint32_t object;
    uint32_t object_word_0x00;
    uint32_t field_0x6c;
    uint32_t field_0x74;
    uint32_t stacked_r0;
    uint32_t stacked_r4;
    uint32_t stacked_r5;
} open_cfw_am142_0x59af1e_inputs;

typedef struct {
    uint32_t r0;
    uint32_t r4;
    uint32_t r5;
    uint32_t cleanup_performed;
    uint32_t first_call_target;
    uint32_t first_call_r0;
    uint32_t first_call_r1;
    uint32_t first_clear_offset;
    uint32_t first_clear_value;
    uint32_t second_call_target;
    uint32_t second_call_r0;
    uint32_t second_call_r1;
    uint32_t second_clear_offset;
    uint32_t second_clear_value;
    uint32_t return_restored_registers_from_stack;
} open_cfw_am142_0x59af1e_outputs;

open_cfw_am142_0x59af1e_outputs
open_cfw_am142_0x59af1e_semantic_model(
    open_cfw_am142_0x59af1e_inputs in)
{
    open_cfw_am142_0x59af1e_outputs out;
    uint32_t present = in.object != 0U;

    out.r0 = in.stacked_r0;
    out.r4 = in.stacked_r4;
    out.r5 = in.stacked_r5;
    out.cleanup_performed = present;
    out.first_call_target = 0x004f1276U;
    out.first_call_r0 = in.object_word_0x00;
    out.first_call_r1 = in.field_0x6c;
    out.first_clear_offset = in.object + 0x6cU;
    out.first_clear_value = 0U;
    out.second_call_target = 0x004f1276U;
    out.second_call_r0 = in.object_word_0x00;
    out.second_call_r1 = in.field_0x74;
    out.second_clear_offset = in.object + 0x74U;
    out.second_clear_value = 0U;
    out.return_restored_registers_from_stack = 1U;
    return out;
}

typedef struct {
    uint32_t object;
    uint32_t arg_r1;
    uint32_t arg_r2;
    uint32_t runtime_call_return;
    uint32_t stacked_r0;
    uint32_t stacked_r4;
    uint32_t stacked_r5;
    uint32_t stacked_r6;
    uint32_t stacked_r7;
} open_cfw_am142_0x59b00e_inputs;

typedef struct {
    uint32_t r0;
    uint32_t r4;
    uint32_t r5;
    uint32_t r6;
    uint32_t r7;
    uint32_t runtime_call_target;
    uint32_t runtime_call_r0;
    uint32_t runtime_call_r1;
    uint32_t runtime_call_r2;
    uint32_t runtime_call_return;
    uint32_t store_arg_r1_offset;
    uint32_t store_arg_r1_value;
    uint32_t store_arg_r2_offset;
    uint32_t store_arg_r2_value;
    uint32_t literal0_offset;
    uint32_t literal0_value;
    uint32_t literal1_offset;
    uint32_t literal1_value;
    uint32_t literal2_offset;
    uint32_t literal2_value;
    uint32_t return_restored_registers_from_stack;
} open_cfw_am142_0x59b00e_outputs;

open_cfw_am142_0x59b00e_outputs
open_cfw_am142_0x59b00e_semantic_model(
    open_cfw_am142_0x59b00e_inputs in)
{
    open_cfw_am142_0x59b00e_outputs out;

    out.r0 = in.stacked_r0;
    out.r4 = in.stacked_r4;
    out.r5 = in.stacked_r5;
    out.r6 = in.stacked_r6;
    out.r7 = in.stacked_r7;
    out.runtime_call_target = 0x00404104U;
    out.runtime_call_r0 = in.object;
    out.runtime_call_r1 = 0x20U;
    out.runtime_call_r2 = 0U;
    out.runtime_call_return = in.runtime_call_return;
    out.store_arg_r1_offset = in.object + 0x14U;
    out.store_arg_r1_value = in.arg_r1;
    out.store_arg_r2_offset = in.object + 0x18U;
    out.store_arg_r2_value = in.arg_r2;
    out.literal0_offset = in.object;
    out.literal0_value = 0x005d2f23U;
    out.literal1_offset = in.object + 4U;
    out.literal1_value = 0x005d2f35U;
    out.literal2_offset = in.object + 0x0cU;
    out.literal2_value = 0x005d2f81U;
    out.return_restored_registers_from_stack = 1U;
    return out;
}

typedef struct {
    uint32_t object;
    uint32_t arg_r2;
    uint32_t object_field_0x04;
    uint32_t dispatch_table_0x224;
    uint32_t callback_0x20;
    uint32_t callback_return;
    uint32_t stacked_r1;
    uint32_t stacked_r2;
    uint32_t stacked_r4;
} open_cfw_am142_0x59b272_inputs;

typedef struct {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r4;
    uint32_t table_load_base;
    uint32_t table_load_offset;
    uint32_t callback_load_base;
    uint32_t callback_load_offset;
    uint32_t stack_arg0_value;
    uint32_t callback_call_target;
    uint32_t callback_call_r0;
    uint32_t callback_call_r2;
    uint32_t callback_call_r3;
    uint32_t return_restored_registers_from_stack;
} open_cfw_am142_0x59b272_outputs;

open_cfw_am142_0x59b272_outputs
open_cfw_am142_0x59b272_semantic_model(
    open_cfw_am142_0x59b272_inputs in)
{
    open_cfw_am142_0x59b272_outputs out;

    out.r0 = in.callback_return;
    out.r1 = in.stacked_r1;
    out.r2 = in.stacked_r2;
    out.r3 = in.arg_r2;
    out.r4 = in.stacked_r4;
    out.table_load_base = in.object_field_0x04;
    out.table_load_offset = 0x224U;
    out.callback_load_base = in.dispatch_table_0x224;
    out.callback_load_offset = 0x20U;
    out.stack_arg0_value = 0U;
    out.callback_call_target = in.callback_0x20;
    out.callback_call_r0 = in.object_field_0x04;
    out.callback_call_r2 = 0U;
    out.callback_call_r3 = in.arg_r2;
    out.return_restored_registers_from_stack = 1U;
    (void)in.object;
    return out;
}

typedef struct {
    uint32_t object;
    uint32_t nested_0x218;
    uint32_t nested_field_0x180;
    uint32_t nested_field_0x184;
    uint32_t nested_field_0x188;
    uint32_t call_return;
    uint32_t saved_r3;
    uint32_t saved_r4;
    uint32_t saved_r5;
    uint32_t saved_r6;
    uint32_t saved_r7;
} open_cfw_am142_0x59b2aa_inputs;

typedef struct {
    uint32_t r0;
    uint32_t r4;
    uint32_t r5;
    uint32_t r6;
    uint32_t r7;
    uint32_t helper_call_target;
    uint32_t helper_call_r0;
    uint32_t helper_call_r1;
    uint32_t store_arg_r1_value;
    uint32_t store_arg_r2_value;
    uint32_t store_arg_r3_value;
    uint32_t return_restored_registers_from_stack;
} open_cfw_am142_0x59b2aa_outputs;

open_cfw_am142_0x59b2aa_outputs
open_cfw_am142_0x59b2aa_semantic_model(
    open_cfw_am142_0x59b2aa_inputs in)
{
    open_cfw_am142_0x59b2aa_outputs out;

    out.r0 = in.saved_r3;
    out.r4 = in.saved_r4;
    out.r5 = in.saved_r5;
    out.r6 = in.saved_r6;
    out.r7 = in.saved_r7;
    out.helper_call_target = 0x004EC774U;
    out.helper_call_r0 = in.nested_field_0x180;
    out.helper_call_r1 = 0x03E80000U;
    out.store_arg_r1_value = in.call_return;
    out.store_arg_r2_value = in.nested_field_0x184 << 16U;
    out.store_arg_r3_value = in.nested_field_0x188 << 16U;
    out.return_restored_registers_from_stack = 1U;
    (void)in.object;
    (void)in.nested_0x218;
    return out;
}

typedef struct {
    uint32_t object;
    uint32_t arg_r1;
    uint32_t arg_r2;
    uint32_t object_field_0x230;
    uint32_t object_field_0x238;
    uint32_t table_0x240;
    uint32_t table_word_index;
    uint32_t table_word_index_plus_1;
    uint32_t stacked_r1;
    uint32_t stacked_r4;
    uint32_t stacked_r5;
    uint32_t stacked_r6;
    uint32_t stacked_r7;
} open_cfw_am142_0x59b33e_inputs;

typedef struct {
    uint32_t r0;
    uint32_t r1;
    uint32_t r4;
    uint32_t r5;
    uint32_t r6;
    uint32_t r7;
    uint32_t init_call_target;
    uint32_t init_call_r0;
    uint32_t init_call_r1;
    uint32_t init_call_r2;
    uint32_t computed_index;
    uint32_t bounds_rejected;
    uint32_t store_arg_r2_0x04;
    uint32_t store_arg_r2_0x08;
    uint32_t store_arg_r2_0x0c;
    uint32_t return_restored_registers_from_stack;
} open_cfw_am142_0x59b33e_outputs;

open_cfw_am142_0x59b33e_outputs
open_cfw_am142_0x59b33e_semantic_model(
    open_cfw_am142_0x59b33e_inputs in)
{
    open_cfw_am142_0x59b33e_outputs out;

    out.r1 = in.stacked_r1;
    out.r4 = in.stacked_r4;
    out.r5 = in.stacked_r5;
    out.r6 = in.stacked_r6;
    out.r7 = in.stacked_r7;
    out.init_call_target = 0x00404104U;
    out.init_call_r0 = in.arg_r2;
    out.init_call_r1 = 0x10U;
    out.init_call_r2 = 0U;
    out.computed_index = in.object_field_0x238 + in.arg_r1;
    out.bounds_rejected =
        out.computed_index >= in.object_field_0x230 ? 1U : 0U;
    out.store_arg_r2_0x04 = 0U;
    out.store_arg_r2_0x08 = 0U;
    out.store_arg_r2_0x0c = 0U;
    if (out.bounds_rejected != 0U) {
        out.r0 = 1U;
        out.return_restored_registers_from_stack = 1U;
        (void)in.object;
        (void)in.table_0x240;
        (void)in.table_word_index;
        (void)in.table_word_index_plus_1;
        return out;
    }
    out.store_arg_r2_0x0c = in.table_word_index;
    out.store_arg_r2_0x04 = in.table_word_index;
    out.store_arg_r2_0x08 = in.table_word_index_plus_1;
    out.r0 = 0U;
    out.return_restored_registers_from_stack = 1U;
    (void)in.object;
    (void)in.table_0x240;
    return out;
}

typedef struct {
    uint32_t object;
    uint32_t arg_r1;
    uint32_t arg_r2;
    uint32_t object_field_0x04;
    uint32_t object_field_0x214;
    uint32_t callback_0x250;
    uint32_t callback_context_0x34;
    uint32_t helper_return;
    uint32_t callback_return;
    uint32_t stack_word0;
    uint32_t stack_word1;
    uint32_t stacked_r1;
    uint32_t stacked_r2;
    uint32_t stacked_r3;
    uint32_t stacked_r4;
    uint32_t stacked_r5;
    uint32_t stacked_r6;
    uint32_t stacked_r7;
} open_cfw_am142_0x59b382_inputs;

typedef struct {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t r3;
    uint32_t r4;
    uint32_t r5;
    uint32_t r6;
    uint32_t r7;
    uint32_t init_call_target;
    uint32_t init_call_r0;
    uint32_t init_call_r1;
    uint32_t init_call_r2;
    uint32_t helper_call_performed;
    uint32_t helper_call_target;
    uint32_t helper_call_r0;
    uint32_t helper_call_r1;
    uint32_t callback_call_performed;
    uint32_t callback_call_target;
    uint32_t callback_call_r0;
    uint32_t callback_call_r1;
    uint32_t callback_call_r2_is_stack_pair;
    uint32_t callback_call_r3_is_stack_word1;
    uint32_t store_arg_r2_0x04;
    uint32_t store_arg_r2_0x08;
    uint32_t store_arg_r2_0x0c;
    uint32_t return_restored_registers_from_stack;
} open_cfw_am142_0x59b382_outputs;

open_cfw_am142_0x59b382_outputs
open_cfw_am142_0x59b382_semantic_model(
    open_cfw_am142_0x59b382_inputs in)
{
    open_cfw_am142_0x59b382_outputs out;

    out.r1 = in.stacked_r1;
    out.r2 = in.stacked_r2;
    out.r3 = in.stacked_r3;
    out.r4 = in.stacked_r4;
    out.r5 = in.stacked_r5;
    out.r6 = in.stacked_r6;
    out.r7 = in.stacked_r7;
    out.init_call_target = 0x00404104U;
    out.init_call_r0 = in.arg_r2;
    out.init_call_r1 = 0x10U;
    out.init_call_r2 = 0U;
    out.helper_call_performed = in.callback_context_0x34 == 0U ? 1U : 0U;
    out.helper_call_target = 0x0059A1B6U;
    out.helper_call_r0 = in.object_field_0x214;
    out.helper_call_r1 = in.arg_r1;
    out.callback_call_performed = 0U;
    out.callback_call_target = in.callback_0x250;
    out.callback_call_r0 = in.object_field_0x04;
    out.callback_call_r1 = in.arg_r1;
    out.callback_call_r2_is_stack_pair = 1U;
    out.callback_call_r3_is_stack_word1 = 1U;
    out.store_arg_r2_0x04 = 0U;
    out.store_arg_r2_0x08 = 0U;
    out.store_arg_r2_0x0c = 0U;
    if (out.helper_call_performed != 0U) {
        if ((int32_t)in.helper_return < 0) {
            out.r0 = 0x12U;
            out.return_restored_registers_from_stack = 1U;
            (void)in.object;
            return out;
        }
        out.callback_call_r1 = in.helper_return;
    }
    out.callback_call_performed = 1U;
    out.r0 = in.callback_return;
    if (in.callback_return == 0U) {
        out.store_arg_r2_0x04 = in.stack_word0;
        out.store_arg_r2_0x08 = in.stack_word0 + in.stack_word1;
        out.store_arg_r2_0x0c = in.stack_word0;
    }
    out.return_restored_registers_from_stack = 1U;
    (void)in.object;
    return out;
}

typedef struct {
    uint32_t object;
    uint32_t arg_r1;
    uint32_t arg_r1_field_0x04;
    uint32_t arg_r1_field_0x08;
    uint32_t object_field_0x04;
    uint32_t callback_0x254;
    uint32_t callback_return;
    uint32_t stacked_r0;
} open_cfw_am142_0x59b3de_inputs;

typedef struct {
    uint32_t r0;
    uint32_t callback_call_target;
    uint32_t callback_call_r0;
    uint32_t callback_call_r1;
    uint32_t callback_call_r2;
    uint32_t callback_call_return;
    uint32_t callback_load_offset;
    uint32_t return_restored_from_stack;
} open_cfw_am142_0x59b3de_outputs;

open_cfw_am142_0x59b3de_outputs
open_cfw_am142_0x59b3de_semantic_model(
    open_cfw_am142_0x59b3de_inputs in)
{
    open_cfw_am142_0x59b3de_outputs out;

    out.r0 = in.stacked_r0;
    out.callback_call_target = in.callback_0x254;
    out.callback_call_r0 = in.object_field_0x04;
    out.callback_call_r1 = in.arg_r1 + 4U;
    out.callback_call_r2 = in.arg_r1_field_0x08 - in.arg_r1_field_0x04;
    out.callback_call_return = in.callback_return;
    out.callback_load_offset = 0x254U;
    out.return_restored_from_stack = 1U;
    (void)in.object;
    return out;
}

typedef struct {
    uint32_t object_field_0x04;
    uint32_t arg_r1_field_0x04;
    uint32_t arg_r1_field_0x08;
    uint32_t nested_0x80;
    uint32_t callback_context_0x34;
    uint32_t callback_receiver_0x04;
    uint32_t callback_slot_0x04;
    uint32_t callback_return;
    uint32_t stacked_r0;
    uint32_t stacked_r1;
    uint32_t stacked_r2;
} open_cfw_am142_0x59b454_inputs;

typedef struct {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t stack_word0;
    uint32_t stack_word1;
    uint32_t callback_performed;
    uint32_t callback_call_target;
    uint32_t callback_call_r0;
    uint32_t callback_call_r1_is_stack_pair;
    uint32_t callback_call_return;
    uint32_t return_restored_registers_from_stack;
} open_cfw_am142_0x59b454_outputs;

open_cfw_am142_0x59b454_outputs
open_cfw_am142_0x59b454_semantic_model(
    open_cfw_am142_0x59b454_inputs in)
{
    open_cfw_am142_0x59b454_outputs out;

    out.r0 = in.stacked_r0;
    out.r1 = in.stacked_r1;
    out.r2 = in.stacked_r2;
    out.stack_word0 = in.arg_r1_field_0x04;
    out.stack_word1 = in.arg_r1_field_0x08 - in.arg_r1_field_0x04;
    out.callback_performed = in.callback_context_0x34 != 0U ? 1U : 0U;
    out.callback_call_target = in.callback_slot_0x04;
    out.callback_call_r0 = in.callback_receiver_0x04;
    out.callback_call_r1_is_stack_pair = 1U;
    out.callback_call_return = in.callback_return;
    out.return_restored_registers_from_stack = 1U;
    (void)in.object_field_0x04;
    (void)in.nested_0x80;
    return out;
}

typedef struct {
    uint32_t r0;
    uint32_t stacked_r0;
} open_cfw_am142_0x59c052_inputs;

typedef struct {
    uint32_t r0;
    uint32_t call_target;
    uint32_t call_r0;
    uint32_t call_offset;
    uint32_t return_restored_from_stack;
} open_cfw_am142_0x59c052_outputs;

open_cfw_am142_0x59c052_outputs
open_cfw_am142_0x59c052_semantic_model(
    open_cfw_am142_0x59c052_inputs in)
{
    open_cfw_am142_0x59c052_outputs out;

    out.call_target = 0x0059a32eU;
    out.call_offset = 0x2d5cU;
    out.call_r0 = in.r0 + out.call_offset;
    out.r0 = in.stacked_r0;
    out.return_restored_from_stack = 1U;
    return out;
}

typedef struct {
    uint32_t object;
    uint32_t nested_0x1c;
    uint32_t nested_call_arg_0x0c;
    uint32_t stacked_r0;
} open_cfw_am142_0x59b52c_inputs;

typedef struct {
    uint32_t r0;
    uint32_t zero_store_offset;
    uint32_t zero_store_value;
    uint32_t call_target;
    uint32_t call_r0;
    uint32_t return_restored_from_stack;
} open_cfw_am142_0x59b52c_outputs;

open_cfw_am142_0x59b52c_outputs
open_cfw_am142_0x59b52c_semantic_model(
    open_cfw_am142_0x59b52c_inputs in)
{
    open_cfw_am142_0x59b52c_outputs out;

    out.r0 = in.stacked_r0;
    out.zero_store_offset = in.object + 0x10U;
    out.zero_store_value = 0U;
    out.call_target = 0x004ecbc8U;
    (void)in.nested_0x1c;
    out.call_r0 = in.nested_call_arg_0x0c;
    out.return_restored_from_stack = 1U;
    return out;
}

typedef struct {
    uint32_t object;
    uint32_t nested_0x1c;
    uint32_t nested_field_0x0c;
    uint32_t first_call_return;
    uint32_t second_call_return;
    uint32_t stacked_r4;
} open_cfw_am142_0x59b53c_inputs;

typedef struct {
    uint32_t r0;
    uint32_t r4;
    uint32_t first_call_target;
    uint32_t first_call_r0;
    uint32_t first_call_return;
    uint32_t second_call_target;
    uint32_t second_call_r0;
    uint32_t return_restored_r4_from_stack;
} open_cfw_am142_0x59b53c_outputs;

open_cfw_am142_0x59b53c_outputs
open_cfw_am142_0x59b53c_semantic_model(
    open_cfw_am142_0x59b53c_inputs in)
{
    open_cfw_am142_0x59b53c_outputs out;

    out.r0 = in.second_call_return;
    out.r4 = in.stacked_r4;
    out.first_call_target = 0x005999A6U;
    out.first_call_r0 = in.nested_0x1c;
    out.first_call_return = in.first_call_return;
    out.second_call_target = 0x004ECE9AU;
    out.second_call_r0 = in.nested_field_0x0c;
    out.return_restored_r4_from_stack = 1U;
    (void)in.object;
    return out;
}

typedef struct {
    uint32_t object;
    uint32_t call_return;
    uint32_t stacked_r4;
} open_cfw_am142_0x59b654_inputs;

typedef struct {
    uint32_t r0;
    uint32_t r4;
    uint32_t call_target;
    uint32_t call_r0;
    uint32_t call_r1;
    uint32_t call_r2;
    uint32_t call_return;
    uint32_t return_restored_r4_from_stack;
} open_cfw_am142_0x59b654_outputs;

open_cfw_am142_0x59b654_outputs
open_cfw_am142_0x59b654_semantic_model(
    open_cfw_am142_0x59b654_inputs in)
{
    open_cfw_am142_0x59b654_outputs out;

    out.r0 = in.call_return;
    out.r4 = in.stacked_r4;
    out.call_target = 0x00404104U;
    out.call_r0 = in.object;
    out.call_r1 = 0x14U;
    out.call_r2 = 0U;
    out.call_return = in.call_return;
    out.return_restored_r4_from_stack = 1U;
    return out;
}

typedef struct {
    uint32_t object;
    uint32_t object_word_0x00;
    uint32_t r1;
    uint32_t stacked_r1;
} open_cfw_am142_0x59cb44_inputs;

typedef struct {
    uint32_t r0;
    uint32_t r1;
    uint32_t failure_call_performed;
    uint32_t failure_call_target;
    uint32_t failure_call_r0;
    uint32_t failure_call_r1;
    uint32_t size_store_offset;
    uint32_t size_store_value;
    uint32_t word_count_store_offset;
    uint32_t word_count_store_value;
    uint32_t flag_store_offset_0;
    uint32_t flag_store_offset_1;
    uint32_t flag_store_value;
} open_cfw_am142_0x59cb44_outputs;

open_cfw_am142_0x59cb44_outputs
open_cfw_am142_0x59cb44_semantic_model(
    open_cfw_am142_0x59cb44_inputs in)
{
    open_cfw_am142_0x59cb44_outputs out;
    uint32_t accepted = in.r1 < 0x61U;

    out.r1 = in.stacked_r1;
    out.failure_call_performed = accepted ? 0U : 1U;
    out.failure_call_target = 0x0059aa2aU;
    out.failure_call_r0 = in.object_word_0x00;
    out.failure_call_r1 = 0x12U;
    out.size_store_offset = in.object + 8U;
    out.size_store_value = accepted ? in.r1 : 0U;
    out.word_count_store_offset = in.object + 0x0cU;
    out.word_count_store_value = accepted ? ((in.r1 + 7U) >> 3) : 0U;
    out.flag_store_offset_0 = in.object + 4U;
    out.flag_store_offset_1 = in.object + 5U;
    out.flag_store_value = accepted ? 1U : 0U;
    out.r0 = accepted ? in.r1 : 0U;
    return out;
}

typedef struct {
    uint32_t object;
    uint32_t arg_r1;
    uint32_t arg_r2;
    uint32_t object_field_0x0c;
    uint32_t setup_call_return;
    uint32_t byte_call_return;
    uint32_t stacked_r4;
    uint32_t stacked_r5;
    uint32_t stacked_r6;
} open_cfw_am142_0x59cb6c_inputs;

typedef struct {
    uint32_t r0;
    uint32_t r4;
    uint32_t r5;
    uint32_t r6;
    uint32_t setup_call_target;
    uint32_t setup_call_r0;
    uint32_t setup_call_r1;
    uint32_t byte_loop_performed;
    uint32_t byte_loop_count;
    uint32_t byte_call_target;
    uint32_t byte_call_r0;
    uint32_t first_byte_store_offset;
    uint32_t last_byte_store_offset;
    uint32_t byte_store_value;
    uint32_t return_restored_registers_from_stack;
} open_cfw_am142_0x59cb6c_outputs;

open_cfw_am142_0x59cb6c_outputs
open_cfw_am142_0x59cb6c_semantic_model(
    open_cfw_am142_0x59cb6c_inputs in)
{
    open_cfw_am142_0x59cb6c_outputs out;

    out.r0 = in.byte_call_return;
    out.r4 = in.stacked_r4;
    out.r5 = in.stacked_r5;
    out.r6 = in.stacked_r6;
    out.setup_call_target = 0x0059CB44U;
    out.setup_call_r0 = in.object;
    out.setup_call_r1 = in.arg_r2;
    out.byte_loop_performed = in.setup_call_return != 0U ? 1U : 0U;
    out.byte_loop_count = out.byte_loop_performed != 0U ?
        in.object_field_0x0c : 0U;
    out.byte_call_target = 0x0059EDB8U;
    out.byte_call_r0 = in.arg_r1;
    out.first_byte_store_offset = in.object + 0x10U;
    out.last_byte_store_offset = out.byte_loop_count == 0U ?
        out.first_byte_store_offset :
        in.object + 0x10U + out.byte_loop_count - 1U;
    out.byte_store_value = in.byte_call_return & 0xffU;
    out.return_restored_registers_from_stack = 1U;
    return out;
}

typedef struct {
    uint32_t object;
    uint32_t arg_r1;
    uint32_t object_field_0x0c;
    uint32_t setup_call_return;
    uint32_t tail_byte_before_mask;
    uint32_t stacked_r0;
    uint32_t stacked_r4;
    uint32_t stacked_r5;
} open_cfw_am142_0x59cb98_inputs;

typedef struct {
    uint32_t r0;
    uint32_t r4;
    uint32_t r5;
    uint32_t setup_call_target;
    uint32_t setup_call_r0;
    uint32_t setup_call_r1;
    uint32_t fill_performed;
    uint32_t fill_count;
    uint32_t fill_first_offset;
    uint32_t fill_last_offset;
    uint32_t fill_value;
    uint32_t tail_mask;
    uint32_t tail_store_offset;
    uint32_t tail_store_value;
    uint32_t return_restored_registers_from_stack;
} open_cfw_am142_0x59cb98_outputs;

open_cfw_am142_0x59cb98_outputs
open_cfw_am142_0x59cb98_semantic_model(
    open_cfw_am142_0x59cb98_inputs in)
{
    open_cfw_am142_0x59cb98_outputs out;
    uint32_t shift = ((0U - in.arg_r1) & 7U);
    uint32_t mask = (1U << shift) - 1U;

    out.r0 = in.stacked_r0;
    out.r4 = in.stacked_r4;
    out.r5 = in.stacked_r5;
    out.setup_call_target = 0x0059CB44U;
    out.setup_call_r0 = in.object;
    out.setup_call_r1 = in.arg_r1;
    out.fill_performed = in.setup_call_return != 0U ? 1U : 0U;
    out.fill_count = out.fill_performed != 0U ? in.object_field_0x0c : 0U;
    out.fill_first_offset = in.object + 0x10U;
    out.fill_last_offset = out.fill_count == 0U ?
        out.fill_first_offset : in.object + 0x10U + out.fill_count - 1U;
    out.fill_value = 0xffU;
    out.tail_mask = mask;
    out.tail_store_offset = in.object + in.object_field_0x0c + 0x0fU;
    out.tail_store_value = in.tail_byte_before_mask & (~mask & 0xffU);
    out.return_restored_registers_from_stack = 1U;
    return out;
}

typedef struct {
    uint32_t object;
    uint32_t arg_r1;
    uint32_t call_return;
    uint32_t stacked_r4;
    uint32_t stacked_r5;
    uint32_t stacked_r6;
} open_cfw_am142_0x59cb1e_inputs;

typedef struct {
    uint32_t r0;
    uint32_t r4;
    uint32_t r5;
    uint32_t r6;
    uint32_t call_target;
    uint32_t call_r0;
    uint32_t call_r1;
    uint32_t call_r2;
    uint32_t call_return;
    uint32_t store_offset;
    uint32_t store_value;
    uint32_t return_restored_registers_from_stack;
} open_cfw_am142_0x59cb1e_outputs;

open_cfw_am142_0x59cb1e_outputs
open_cfw_am142_0x59cb1e_semantic_model(
    open_cfw_am142_0x59cb1e_inputs in)
{
    open_cfw_am142_0x59cb1e_outputs out;

    out.r0 = in.call_return;
    out.r4 = in.stacked_r4;
    out.r5 = in.stacked_r5;
    out.r6 = in.stacked_r6;
    out.call_target = 0x00404104U;
    out.call_r0 = in.object;
    out.call_r1 = 0x1cU;
    out.call_r2 = 0U;
    out.call_return = in.call_return;
    out.store_offset = in.object;
    out.store_value = in.arg_r1;
    out.return_restored_registers_from_stack = 1U;
    return out;
}

typedef struct {
    uint32_t base;
    uint32_t arg_r1;
    uint32_t arg_r2;
    uint32_t saved_low_0x2dd0;
    uint32_t saved_high_0x2dd4;
    uint32_t predicate_return;
    uint32_t field_0x2dd8;
    uint32_t field_0x2ddc;
    uint32_t callback;
    uint32_t helper_result_low;
    uint32_t helper_result_high;
} open_cfw_am142_0x59c530_inputs;

typedef struct {
    uint32_t r0;
    uint32_t saved_low;
    uint32_t saved_high;
    uint32_t predicate_call_target;
    uint32_t predicate_call_r0;
    uint32_t fallback_call_performed;
    uint32_t fallback_call_target;
    uint32_t fallback_call_r0;
    uint32_t fallback_call_r1;
    uint32_t fallback_call_r2;
    uint32_t helper_call_target;
    uint32_t helper_call_r0;
    uint32_t helper_call_r1;
    uint32_t helper_call_r3;
    uint32_t callback_call_target;
    uint32_t callback_call_r0;
    uint32_t callback_call_r1_is_saved_pair;
    uint32_t restored_low_0x2dd0;
    uint32_t restored_high_0x2dd4;
    uint32_t stored_arg_r1_0x2db8;
    uint32_t stored_arg_r2_0x2dbc;
} open_cfw_am142_0x59c530_outputs;

open_cfw_am142_0x59c530_outputs
open_cfw_am142_0x59c530_semantic_model(
    open_cfw_am142_0x59c530_inputs in)
{
    open_cfw_am142_0x59c530_outputs out;

    out.r0 = 0U;
    out.saved_low = in.saved_low_0x2dd0;
    out.saved_high = in.saved_high_0x2dd4;
    out.predicate_call_target = 0x0059b70aU;
    out.predicate_call_r0 = in.base + 8U;
    out.fallback_call_performed = in.predicate_return == 0U ? 1U : 0U;
    out.fallback_call_target = 0x0059c774U;
    out.fallback_call_r0 = in.base;
    out.fallback_call_r1 = in.field_0x2dd8;
    out.fallback_call_r2 = in.field_0x2ddc;
    out.helper_call_target = 0x0059c060U;
    out.helper_call_r0 = in.base;
    out.helper_call_r1 = in.base + 8U;
    out.helper_call_r3 = in.arg_r1;
    out.callback_call_target = in.callback;
    out.callback_call_r0 = in.callback;
    out.callback_call_r1_is_saved_pair = 1U;
    out.restored_low_0x2dd0 = in.helper_result_low;
    out.restored_high_0x2dd4 = in.helper_result_high;
    out.stored_arg_r1_0x2db8 = in.arg_r1;
    out.stored_arg_r2_0x2dbc = in.arg_r2;
    return out;
}

typedef struct {
    int32_t r0;
    int32_t r1;
    float s2;
    float s3;
    float s4;
    float s16;
    uint32_t delta_words[3];
    float coefficients[3];
} open_cfw_am142_0x59a312_inputs;

typedef struct {
    int32_t r0;
    int32_t r2;
    int32_t r4;
    float s4;
    float s5;
    float s6;
    float s7;
    float s16;
    uint32_t stack_zero_words[3];
    int branch_to_0x0059a45c;
} open_cfw_am142_0x59a312_outputs;

open_cfw_am142_0x59a312_outputs
open_cfw_am142_0x59a312_semantic_model(
    open_cfw_am142_0x59a312_inputs in)
{
    open_cfw_am142_0x59a312_outputs out;
    int32_t r0 = in.r0;
    int32_t r1 = in.r1;
    float s4;
    float s5;
    float s6;
    float s7;
    float s16 = in.s16;

    out.r4 = r1 - r0;
    s16 -= in.s4 * in.s2;

    out.stack_zero_words[0] = 0;
    r1 = (int32_t)in.delta_words[0];
    s4 = in.s3 - in.s4;
    r0 -= r1;
    s5 = (float)r1;
    s16 -= s5 * in.coefficients[0];

    out.stack_zero_words[1] = 0;
    r1 = (int32_t)in.delta_words[1];
    s5 = s4 - s5;
    r0 -= r1;
    s6 = (float)r1;
    s16 -= s6 * in.coefficients[1];

    out.stack_zero_words[2] = 0;
    r1 = (int32_t)in.delta_words[2];
    s6 = s5 - s6;
    s7 = (float)r1;
    s16 -= s7 * in.coefficients[2];

    out.r2 = r0 - r1;
    s6 -= (float)((int32_t)(r1 * r1));

    out.r0 = r0;
    out.s4 = s4;
    out.s5 = s5;
    out.s6 = s6;
    out.s7 = s7;
    out.s16 = s16;
    out.branch_to_0x0059a45c = out.r2 >= 10;
    return out;
}

typedef struct {
    uint32_t r1;
    uint32_t r3;
    uint32_t ip;
    uint32_t sl;
} open_cfw_am142_0x59c060_inputs;

typedef struct {
    uint32_t r2;
    uint32_t r3;
    uint32_t ip;
    uint32_t lr;
    int branch_to_0x0059c086;
} open_cfw_am142_0x59c060_outputs;

open_cfw_am142_0x59c060_outputs
open_cfw_am142_0x59c060_semantic_model(
    open_cfw_am142_0x59c060_inputs in)
{
    open_cfw_am142_0x59c060_outputs out;

    out.lr = in.sl - in.ip;
    out.ip = in.r1 - in.ip;
    out.r2 = in.sl - in.r3;
    out.r2 *= out.ip;
    out.r2 += out.lr * in.r3;
    out.r3 = out.lr + (out.lr << 1);
    out.r3 <<= 4;
    out.branch_to_0x0059c086 = 1;
    return out;
}

typedef struct {
    uint32_t r1;
    int32_t r4;
} open_cfw_am142_0x59ba4a_inputs;

typedef struct {
    uint32_t r0;
    int branch_to_0x0059b8b2;
} open_cfw_am142_0x59ba4a_outputs;

open_cfw_am142_0x59ba4a_outputs
open_cfw_am142_0x59ba4a_semantic_model(
    open_cfw_am142_0x59ba4a_inputs in)
{
    open_cfw_am142_0x59ba4a_outputs out;

    out.r0 = in.r1 + 0x400U;
    out.branch_to_0x0059b8b2 = in.r4 <= 1;
    return out;
}

typedef struct {
    int32_t stack_word_0x10c;
    float stack_float_0x4c;
    float s6;
    float s7;
    float s8;
    float s16;
} open_cfw_am142_0x59a3d2_inputs;

typedef struct {
    int32_t lr;
    int32_t r2;
    float s9;
    float s10;
    float s11;
    float s12;
    int branch_to_0x0059a420;
} open_cfw_am142_0x59a3d2_outputs;

open_cfw_am142_0x59a3d2_outputs
open_cfw_am142_0x59a3d2_semantic_model(
    open_cfw_am142_0x59a3d2_inputs in)
{
    open_cfw_am142_0x59a3d2_outputs out;

    out.r2 = 1;
    out.lr = (int32_t)((uint32_t)in.stack_word_0x10c << 1);
    out.s9 = in.s16 + in.stack_float_0x4c;
    out.s10 = (float)out.lr + in.s6;
    out.s10 += 1.0f;
    out.s9 *= out.s9;
    out.s11 = out.s9 * in.s8;
    out.s12 = out.s10 * in.s7;
    out.branch_to_0x0059a420 = out.s12 >= out.s11;
    return out;
}

typedef struct {
    uint32_t sl;
} open_cfw_am142_0x4ec718_inputs;

typedef struct {
    uint32_t r0;
    uint32_t call_target;
} open_cfw_am142_0x4ec718_outputs;

open_cfw_am142_0x4ec718_outputs
open_cfw_am142_0x4ec718_semantic_model(
    open_cfw_am142_0x4ec718_inputs in)
{
    open_cfw_am142_0x4ec718_outputs out;

    out.r0 = in.sl;
    out.call_target = 0x0044104cU;
    return out;
}

typedef struct {
    uint32_t r0;
} open_cfw_am142_0x4ec774_inputs;

typedef struct {
    uint32_t r0;
    uint32_t r1;
    uint32_t r2;
    uint32_t sb;
    uint32_t call_target;
} open_cfw_am142_0x4ec774_outputs;

open_cfw_am142_0x4ec774_outputs
open_cfw_am142_0x4ec774_semantic_model(
    open_cfw_am142_0x4ec774_inputs in)
{
    open_cfw_am142_0x4ec774_outputs out;

    out.sb = in.r0;
    out.r2 = 3;
    out.r1 = 0;
    out.r0 = out.sb;
    out.call_target = 0x0043f09aU;
    return out;
}
