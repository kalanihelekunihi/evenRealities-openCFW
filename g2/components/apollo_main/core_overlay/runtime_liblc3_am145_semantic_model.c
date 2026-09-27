/*
 * SPDX-License-Identifier: MIT
 *
 * Semantic reference models for AM145 bounded local-return chunks. These
 * models are host-testable source pull-through evidence; they are not yet
 * routed into the firmware overlay.
 */

#include <stdint.h>

typedef struct {
    uint32_t context;
    uint32_t owner;
    uint32_t callback;
    uint32_t callback_return;
} open_cfw_am145_0x5a6e34_inputs;

typedef struct {
    uint32_t r0;
    uint32_t call_target;
    uint32_t call_r0;
    int callback_performed;
} open_cfw_am145_0x5a6e34_outputs;

open_cfw_am145_0x5a6e34_outputs
open_cfw_am145_0x5a6e34_semantic_model(
    open_cfw_am145_0x5a6e34_inputs in)
{
    open_cfw_am145_0x5a6e34_outputs out;

    out.callback_performed = in.callback != 0U;
    out.call_target = out.callback_performed ? in.callback : 0U;
    out.call_r0 = out.callback_performed ? in.context : 0U;
    out.r0 = out.callback_performed ? in.callback_return : 0x96U;
    return out;
}

typedef struct {
    uint32_t context;
    uint32_t source;
    uint32_t parser_callback;
    uint32_t parser_return;
    uint32_t parsed_length;
    uint32_t copy_return;
    uint32_t first_record_count_word;
} open_cfw_am145_0x5a6e4a_inputs;

typedef struct {
    uint32_t r0;
    uint32_t parser_call_target;
    uint32_t parser_call_r0;
    uint32_t parser_call_r2;
    uint32_t copy_call_target;
    uint32_t copy_call_r0;
    uint32_t copy_call_r1;
    uint32_t copy_call_r2_is_context_buffer;
    uint32_t stored_length;
    uint32_t clamped_record_count;
    uint32_t records_scan_entered;
} open_cfw_am145_0x5a6e4a_outputs;

open_cfw_am145_0x5a6e4a_outputs
open_cfw_am145_0x5a6e4a_semantic_model(
    open_cfw_am145_0x5a6e4a_inputs in)
{
    open_cfw_am145_0x5a6e4a_outputs out;

    out.r0 = 0U;
    out.parser_call_target = in.parser_callback;
    out.parser_call_r0 = in.context;
    out.parser_call_r2 = in.source;
    out.copy_call_target = 0x004f09b2U;
    out.copy_call_r0 = in.source;
    out.copy_call_r1 = in.parsed_length;
    out.copy_call_r2_is_context_buffer = 1U;
    out.stored_length = 0U;
    out.clamped_record_count = 0U;
    out.records_scan_entered = 0U;

    if (in.parser_return != 0U) {
        out.r0 = in.parser_return;
        return out;
    }
    if (in.parsed_length < 4U) {
        out.r0 = 0x8eU;
        return out;
    }
    if (in.copy_return != 0U) {
        out.r0 = in.copy_return;
        return out;
    }

    out.stored_length = in.parsed_length;
    out.clamped_record_count = in.first_record_count_word & 0xffffU;
    if (out.clamped_record_count >= 0x21U) {
        out.clamped_record_count = 0x20U;
    }
    out.records_scan_entered = 1U;
    return out;
}

typedef struct {
    uint32_t record_flags;
    uint32_t record_cursor_offset;
    uint32_t record_end_offset;
    uint32_t declared_subrecord_count;
    uint32_t current_bit;
} open_cfw_am145_0x5a6f5c_inputs;

typedef struct {
    uint32_t r0;
    uint32_t enough_header_bytes;
    uint32_t extension_flag_matches;
    uint32_t effective_subrecord_count;
    uint32_t feature_mask;
    uint32_t nested_scan_entered;
} open_cfw_am145_0x5a6f5c_outputs;

open_cfw_am145_0x5a6f5c_outputs
open_cfw_am145_0x5a6f5c_semantic_model(
    open_cfw_am145_0x5a6f5c_inputs in)
{
    open_cfw_am145_0x5a6f5c_outputs out;
    uint32_t available = 0U;

    out.r0 = 0U;
    out.enough_header_bytes = 0U;
    out.extension_flag_matches = (in.record_flags & 3U) == 1U ? 1U : 0U;
    out.effective_subrecord_count = 0U;
    out.feature_mask = 0U;
    out.nested_scan_entered = 0U;

    if (!out.extension_flag_matches) {
        return out;
    }
    if (in.record_end_offset >= in.record_cursor_offset + 8U) {
        out.enough_header_bytes = 1U;
    } else {
        return out;
    }
    if (in.record_end_offset > in.record_cursor_offset + 8U) {
        available = in.record_end_offset - (in.record_cursor_offset + 8U);
    }
    out.effective_subrecord_count = in.declared_subrecord_count & 0xffffU;
    if (available < out.effective_subrecord_count * 6U) {
        out.effective_subrecord_count = available / 6U;
    }
    out.feature_mask = in.current_bit;
    out.nested_scan_entered = out.effective_subrecord_count != 0U ? 1U : 0U;
    return out;
}

typedef struct {
    uint32_t remaining_sorted_words;
    uint32_t previous_word;
    uint32_t current_word;
    uint32_t record_payload_length;
    uint32_t record_end_offset;
    uint32_t record_cursor_offset;
    uint32_t record_flags;
    uint32_t current_bit;
} open_cfw_am145_0x5a6eb6_inputs;

typedef struct {
    uint32_t r0;
    uint32_t sorted_scan_continues;
    uint32_t current_bit_mask;
    uint32_t record_payload_accepted;
    uint32_t clamped_record_end_offset;
    uint32_t enters_nested_extension_path;
    uint32_t final_status_store_ready;
} open_cfw_am145_0x5a6eb6_outputs;

open_cfw_am145_0x5a6eb6_outputs
open_cfw_am145_0x5a6eb6_semantic_model(
    open_cfw_am145_0x5a6eb6_inputs in)
{
    open_cfw_am145_0x5a6eb6_outputs out;
    uint32_t payload_end = in.record_cursor_offset + in.record_payload_length;

    out.r0 = 0U;
    out.sorted_scan_continues =
        in.remaining_sorted_words != 0U
        && in.previous_word < in.current_word ? 1U : 0U;
    out.current_bit_mask = out.sorted_scan_continues ? 0U : in.current_bit;
    out.record_payload_accepted = in.record_payload_length >= 0x0fU ? 1U : 0U;
    out.clamped_record_end_offset =
        in.record_end_offset < payload_end ? in.record_end_offset : payload_end;
    out.enters_nested_extension_path =
        out.record_payload_accepted
        && ((in.record_flags >> 8U) == 0U)
        && ((in.record_flags & 3U) == 1U) ? 1U : 0U;
    out.final_status_store_ready =
        out.sorted_scan_continues ? 0U : 1U;
    return out;
}

typedef struct {
    uint32_t stack_result;
} open_cfw_am145_0x5a6c52_inputs;

typedef struct {
    uint32_t r0;
    uint32_t call_target;
    uint32_t call_r2_is_stack_scratch;
} open_cfw_am145_0x5a6c52_outputs;

open_cfw_am145_0x5a6c52_outputs
open_cfw_am145_0x5a6c52_semantic_model(
    open_cfw_am145_0x5a6c52_inputs in)
{
    open_cfw_am145_0x5a6c52_outputs out;

    out.call_target = 0x005a812eU;
    out.call_r2_is_stack_scratch = 1U;
    out.r0 = in.stack_result;
    return out;
}

typedef struct {
    uint32_t context;
    uint32_t callback;
    uint32_t callback_return;
} open_cfw_am145_callback_tail_inputs;

typedef struct {
    uint32_t r0;
    uint32_t call_target;
    uint32_t call_r0;
    uint32_t callback_table_offset;
} open_cfw_am145_callback_tail_outputs;

open_cfw_am145_callback_tail_outputs
open_cfw_am145_0x5a6c94_semantic_model(
    open_cfw_am145_callback_tail_inputs in)
{
    open_cfw_am145_callback_tail_outputs out;

    out.callback_table_offset = 0x08U;
    out.call_target = in.callback;
    out.call_r0 = in.context;
    out.r0 = in.callback_return;
    return out;
}

open_cfw_am145_callback_tail_outputs
open_cfw_am145_0x5a6ca2_semantic_model(
    open_cfw_am145_callback_tail_inputs in)
{
    open_cfw_am145_callback_tail_outputs out;

    out.callback_table_offset = 0x0cU;
    out.call_target = in.callback;
    out.call_r0 = in.context;
    out.r0 = in.callback_return;
    return out;
}

typedef struct {
    uint32_t stream_base;
    uint32_t stream_limit;
    uint32_t first_word;
    uint32_t second_word;
} open_cfw_am145_0x5a6cb0_inputs;

typedef struct {
    uint32_t r0;
    uint32_t first_tag;
    uint32_t second_tag;
    uint32_t selected_tag;
    uint32_t bytes_consumed;
    uint32_t short_buffer_error;
    uint32_t falls_into_parser_body;
} open_cfw_am145_0x5a6cb0_outputs;

open_cfw_am145_0x5a6cb0_outputs
open_cfw_am145_0x5a6cb0_semantic_model(
    open_cfw_am145_0x5a6cb0_inputs in)
{
    open_cfw_am145_0x5a6cb0_outputs out;

    out.r0 = 0U;
    out.first_tag = 0U;
    out.second_tag = 0U;
    out.selected_tag = 0U;
    out.bytes_consumed = 0U;
    out.short_buffer_error = 0U;
    out.falls_into_parser_body = 0U;

    if (in.stream_base == 0U || in.stream_limit < in.stream_base + 4U) {
        out.r0 = 8U;
        out.short_buffer_error = 1U;
        return out;
    }

    out.first_tag = in.first_word & 0xffffU;
    out.bytes_consumed = 2U;
    if (out.first_tag != 0U) {
        out.selected_tag = out.first_tag;
        out.falls_into_parser_body = 1U;
        return out;
    }

    out.second_tag = in.second_word & 0xffffU;
    out.bytes_consumed = 4U;
    out.selected_tag = out.second_tag;
    if (out.second_tag == 0U) {
        out.r0 = 8U;
    } else {
        out.falls_into_parser_body = 1U;
    }
    return out;
}

typedef struct {
    uint32_t tag_count;
    uint32_t stream_cursor;
    uint32_t stream_end;
    uint32_t record_offset;
    uint32_t record_limit;
    uint32_t list_node_present;
    uint32_t node_tag_matches;
    uint32_t formatter_success;
    uint32_t callback_target;
    uint32_t attach_success;
} open_cfw_am145_0x5a6d10_inputs;

typedef struct {
    uint32_t r0;
    uint32_t normalized_tag_count;
    uint32_t enough_record_bytes;
    uint32_t record_offset_accepted;
    uint32_t format_call_target;
    uint32_t status_call_target;
    uint32_t callback_target;
    uint32_t callback_performed;
    uint32_t attach_call_target;
    uint32_t attach_performed;
} open_cfw_am145_0x5a6d10_outputs;

open_cfw_am145_0x5a6d10_outputs
open_cfw_am145_0x5a6d10_semantic_model(
    open_cfw_am145_0x5a6d10_inputs in)
{
    open_cfw_am145_0x5a6d10_outputs out;

    out.r0 = 0U;
    out.normalized_tag_count = in.tag_count & 0xffffU;
    out.enough_record_bytes =
        in.stream_end >= in.stream_cursor + 8U ? 1U : 0U;
    out.record_offset_accepted = 0U;
    out.format_call_target = 0x004ecf90U;
    out.status_call_target = 0x0052f79cU;
    out.callback_target = 0U;
    out.callback_performed = 0U;
    out.attach_call_target = 0x004eee7aU;
    out.attach_performed = 0U;

    if (out.normalized_tag_count == 0U || !out.enough_record_bytes) {
        return out;
    }
    if (in.record_limit >= 2U
        && in.record_offset != 0U
        && in.record_offset <= in.record_limit - 2U) {
        out.record_offset_accepted = 1U;
    } else {
        return out;
    }
    if (in.list_node_present != 0U && in.node_tag_matches != 0U) {
        if (in.formatter_success != 0U) {
            out.callback_target = in.callback_target;
            out.callback_performed = in.callback_target != 0U ? 1U : 0U;
        }
        out.attach_performed = in.attach_success != 0U ? 1U : 0U;
    }
    return out;
}

typedef struct {
    uint32_t nested_offset_0x64_value;
    uint32_t context_offset_0x14_value;
} open_cfw_am145_0x5a6c7c_inputs;

typedef struct {
    uint32_t r0;
    uint32_t call_target;
    uint32_t call_r0;
    uint32_t call_r1;
    uint32_t clears_context_offset_0x10;
    uint32_t clears_context_offset_0x14;
} open_cfw_am145_0x5a6c7c_outputs;

open_cfw_am145_0x5a6c7c_outputs
open_cfw_am145_0x5a6c7c_semantic_model(
    open_cfw_am145_0x5a6c7c_inputs in)
{
    open_cfw_am145_0x5a6c7c_outputs out;

    out.call_target = 0x004f1276U;
    out.call_r0 = in.nested_offset_0x64_value;
    out.call_r1 = in.context_offset_0x14_value;
    out.clears_context_offset_0x10 = 1U;
    out.clears_context_offset_0x14 = 1U;
    out.r0 = 0U;
    return out;
}

typedef struct {
    uint32_t nested_offset_0x64_value;
    uint32_t nested_offset_0x10_value;
    uint32_t callback;
    uint32_t callback_return;
} open_cfw_am145_0x5a6c5e_inputs;

typedef struct {
    uint32_t r0;
    uint32_t call_target;
    uint32_t call_r0;
    uint32_t call_r1_is_context;
    uint32_t call_r2;
    uint32_t call_r3_literal;
    uint32_t stack_arg0;
    uint32_t stack_arg1_is_nested;
} open_cfw_am145_0x5a6c5e_outputs;

open_cfw_am145_0x5a6c5e_outputs
open_cfw_am145_0x5a6c5e_semantic_model(
    open_cfw_am145_0x5a6c5e_inputs in)
{
    open_cfw_am145_0x5a6c5e_outputs out;

    out.call_target = in.callback;
    out.call_r0 = in.nested_offset_0x64_value;
    out.call_r1_is_context = 1U;
    out.call_r2 = in.nested_offset_0x10_value;
    out.call_r3_literal = 0x005dec33U;
    out.stack_arg0 = 0U;
    out.stack_arg1_is_nested = 1U;
    out.r0 = in.callback_return;
    return out;
}

typedef struct {
    uint32_t context;
    uint32_t source_offset_0x10;
    uint32_t entry_count;
    uint32_t parser_arg_r2;
    uint32_t parser_return;
} open_cfw_am145_0x5a67d2_inputs;

typedef struct {
    uint32_t r0;
    uint32_t parser_call_target;
    uint32_t parser_call_r0;
    uint32_t parser_call_r1;
    uint32_t parser_call_r2;
    uint32_t output_table_offset;
    uint32_t source_start_offset;
    uint32_t source_stride;
    uint32_t decoded_word_count;
    uint32_t appends_zero_terminator;
} open_cfw_am145_0x5a67d2_outputs;

open_cfw_am145_0x5a67d2_outputs
open_cfw_am145_0x5a67d2_semantic_model(
    open_cfw_am145_0x5a67d2_inputs in)
{
    open_cfw_am145_0x5a67d2_outputs out;

    out.parser_call_target = 0x005a6290U;
    out.parser_call_r0 = in.context;
    out.parser_call_r1 = in.entry_count + 1U;
    out.parser_call_r2 = in.parser_arg_r2;
    out.output_table_offset = 0x20U;
    out.source_start_offset = in.source_offset_0x10 + 0x0aU;
    out.source_stride = 8U;
    out.decoded_word_count = in.parser_return == 0U ? in.entry_count : 0U;
    out.appends_zero_terminator = in.parser_return == 0U ? 1U : 0U;
    out.r0 = 0U;
    return out;
}

typedef struct {
    uint32_t context;
    uint32_t source_offset_0x10;
    uint32_t entry_count;
    uint32_t parser_arg_r2;
    uint32_t parser_return;
} open_cfw_am145_0x5a6822_inputs;

typedef struct {
    uint32_t r0;
    uint32_t parser_call_target;
    uint32_t parser_call_r0;
    uint32_t parser_call_r1;
    uint32_t parser_call_r2;
    uint32_t output_table_offset;
    uint32_t source_start_offset;
    uint32_t decoded_record_prefix_entered;
} open_cfw_am145_0x5a6822_outputs;

open_cfw_am145_0x5a6822_outputs
open_cfw_am145_0x5a6822_semantic_model(
    open_cfw_am145_0x5a6822_inputs in)
{
    open_cfw_am145_0x5a6822_outputs out;

    out.parser_call_target = 0x005a6290U;
    out.parser_call_r0 = in.context;
    out.parser_call_r1 = in.entry_count + 1U;
    out.parser_call_r2 = in.parser_arg_r2;
    out.output_table_offset = 0x20U;
    out.source_start_offset = in.source_offset_0x10 + 0x0aU;
    out.decoded_record_prefix_entered = in.parser_return == 0U ? 1U : 0U;
    out.r0 = 0U;
    return out;
}

typedef struct {
    uint32_t stream_limit;
    uint32_t table_limit;
    uint32_t sequence_limit;
    uint32_t previous_sequence;
    uint32_t next_sequence;
    uint32_t first_table_offset;
    uint32_t second_table_offset;
    uint32_t first_nested_count;
    uint32_t second_nested_count;
} open_cfw_am145_0x5a63c8_inputs;

typedef struct {
    uint32_t r0;
    uint32_t error_call_target;
    uint32_t error_call_r1;
    uint32_t error_call_count;
    uint32_t sequence_monotonic;
    uint32_t first_table_accepted;
    uint32_t second_table_accepted;
    uint32_t first_nested_table_fits;
    uint32_t second_nested_table_fits;
} open_cfw_am145_0x5a63c8_outputs;

open_cfw_am145_0x5a63c8_outputs
open_cfw_am145_0x5a63c8_semantic_model(
    open_cfw_am145_0x5a63c8_inputs in)
{
    open_cfw_am145_0x5a63c8_outputs out;

    out.r0 = 0U;
    out.error_call_target = 0x004ecfa4U;
    out.error_call_r1 = 8U;
    out.error_call_count = 0U;
    out.sequence_monotonic =
        in.next_sequence > in.previous_sequence
        && in.next_sequence < in.sequence_limit ? 1U : 0U;
    out.first_table_accepted =
        in.first_table_offset != 0U
        && in.first_table_offset < in.stream_limit ? 1U : 0U;
    out.second_table_accepted =
        in.second_table_offset != 0U
        && in.second_table_offset < in.stream_limit ? 1U : 0U;
    out.first_nested_table_fits = 0U;
    out.second_nested_table_fits = 0U;

    if (!out.sequence_monotonic) {
        out.error_call_count++;
    }
    if (!out.first_table_accepted && in.first_table_offset != 0U) {
        out.error_call_count++;
    }
    if (!out.second_table_accepted && in.second_table_offset != 0U) {
        out.error_call_count++;
    }
    if (out.first_table_accepted
        && in.table_limit >= in.first_table_offset + 4U
        && (in.table_limit - (in.first_table_offset + 4U)) / 4U
            >= in.first_nested_count) {
        out.first_nested_table_fits = 1U;
    } else if (out.first_table_accepted) {
        out.error_call_count++;
    }
    if (out.second_table_accepted
        && in.table_limit >= in.second_table_offset + 4U
        && (in.table_limit - (in.second_table_offset + 4U)) / 5U
            >= in.second_nested_count) {
        out.second_nested_table_fits = 1U;
    } else if (out.second_table_accepted) {
        out.error_call_count++;
    }
    return out;
}

typedef struct {
    uint32_t table_base;
    uint32_t count_word;
    uint32_t low_index;
    uint32_t high_index;
} open_cfw_am145_0x5a65b0_inputs;

typedef struct {
    uint32_t r0;
    uint32_t decoded_entry_count;
    uint32_t search_active;
    uint32_t midpoint_index;
    uint32_t midpoint_record_offset;
    uint32_t next_compare_prefix_entered;
} open_cfw_am145_0x5a65b0_outputs;

open_cfw_am145_0x5a65b0_outputs
open_cfw_am145_0x5a65b0_semantic_model(
    open_cfw_am145_0x5a65b0_inputs in)
{
    open_cfw_am145_0x5a65b0_outputs out;
    uint32_t high = in.high_index != 0U ? in.high_index : in.count_word;

    out.r0 = 0U;
    out.decoded_entry_count = in.count_word;
    out.search_active = in.low_index < high ? 1U : 0U;
    out.midpoint_index = out.search_active
        ? ((in.low_index + high) >> 1U)
        : in.low_index;
    out.midpoint_record_offset =
        in.table_base + 4U + (out.midpoint_index << 2U);
    out.next_compare_prefix_entered = out.search_active;
    return out;
}

typedef struct {
    uint32_t parser_status;
    uint32_t tag;
    uint32_t special_tag_matched;
    uint32_t recursive_return;
} open_cfw_am145_0x5a340c_inputs;

typedef struct {
    uint32_t r0;
    uint32_t clears_status_slots;
    uint32_t parser_call_target;
    uint32_t parser_status;
    uint32_t special_tag_path_entered;
    uint32_t recursive_call_target;
    uint32_t accepted_tag;
    uint32_t unsupported_tag_error;
    uint32_t writes_type_slot;
    uint32_t type_slot_value;
} open_cfw_am145_0x5a340c_outputs;

open_cfw_am145_0x5a340c_outputs
open_cfw_am145_0x5a340c_semantic_model(
    open_cfw_am145_0x5a340c_inputs in)
{
    open_cfw_am145_0x5a340c_outputs out;
    uint32_t known_tag;

    out.r0 = 0U;
    out.clears_status_slots = 1U;
    out.parser_call_target = 0x005a6d10U;
    out.parser_status = in.parser_status;
    out.special_tag_path_entered = 0U;
    out.recursive_call_target = 0U;
    out.accepted_tag = 0U;
    out.unsupported_tag_error = 0U;
    out.writes_type_slot = 0U;
    out.type_slot_value = 0U;

    if (in.parser_status != 0U) {
        out.r0 = in.parser_status;
        return out;
    }

    if (in.special_tag_matched != 0U) {
        out.special_tag_path_entered = 1U;
        out.recursive_call_target = 0x005a2e00U;
        if (in.recursive_return != 0U) {
            out.r0 = in.recursive_return;
            return out;
        }
    }

    known_tag = (
        in.tag == 0x00010000U ||
        in.tag == 0x00010004U ||
        in.tag == 0x00020000U
    ) ? 1U : 0U;
    if (known_tag == 0U) {
        out.r0 = 2U;
        out.unsupported_tag_error = 1U;
        return out;
    }

    out.accepted_tag = 1U;
    out.writes_type_slot = 1U;
    out.type_slot_value = 0x00010004U;
    return out;
}

typedef struct {
    uint32_t precheck_return;
    uint32_t decoded_count;
    uint32_t available_word_count;
    uint32_t allocate_status;
    uint32_t table_pointer;
    uint32_t element_decode_return;
} open_cfw_am145_0x5a34ca_inputs;

typedef struct {
    uint32_t r0;
    uint32_t precheck_call_target;
    uint32_t count_zero_error;
    uint32_t count_capacity_error;
    uint32_t allocate_call_target;
    uint32_t allocate_call_r1;
    uint32_t allocation_stored_at_offset_0x90;
    uint32_t element_decode_call_target;
    uint32_t elements_written;
    uint32_t close_call_target;
} open_cfw_am145_0x5a34ca_outputs;

open_cfw_am145_0x5a34ca_outputs
open_cfw_am145_0x5a34ca_semantic_model(
    open_cfw_am145_0x5a34ca_inputs in)
{
    open_cfw_am145_0x5a34ca_outputs out;

    out.r0 = 0U;
    out.precheck_call_target = 0x005a6d10U;
    out.count_zero_error = 0U;
    out.count_capacity_error = 0U;
    out.allocate_call_target = 0x004edcf2U;
    out.allocate_call_r1 = 4U;
    out.allocation_stored_at_offset_0x90 = 0U;
    out.element_decode_call_target = 0x005a2e00U;
    out.elements_written = 0U;
    out.close_call_target = 0x005a2eaeU;

    if (in.precheck_return != 0U) {
        out.r0 = in.precheck_return;
        return out;
    }
    if (in.decoded_count == 0U) {
        out.r0 = 8U;
        out.count_zero_error = 1U;
        return out;
    }
    if (in.available_word_count < in.decoded_count) {
        out.r0 = 0x0aU;
        out.count_capacity_error = 1U;
        return out;
    }

    out.allocation_stored_at_offset_0x90 = in.table_pointer;
    if (in.allocate_status != 0U) {
        out.r0 = in.allocate_status;
        return out;
    }
    if (in.element_decode_return != 0U) {
        out.r0 = in.element_decode_return;
        return out;
    }

    out.elements_written = in.decoded_count;
    return out;
}

typedef struct {
    uint32_t cached_vtable_present;
    uint32_t vtable_lookup_result;
    uint32_t parser_delegate_return;
    int32_t signed_index;
    uint32_t decoded_count;
    uint32_t table_lookup_return;
    uint32_t callback58_return;
} open_cfw_am145_0x5a35a4_inputs;

typedef struct {
    uint32_t r0;
    uint32_t vtable_lookup_performed;
    uint32_t vtable_lookup_call_target;
    uint32_t cached_vtable_stored;
    uint32_t parser_delegate_call_target;
    uint32_t normalized_index;
    uint32_t negative_index;
    uint32_t bounds_error;
    uint32_t table_lookup_call_target;
    uint32_t callback58_performed;
    uint32_t callback58_is_indirect_boundary;
} open_cfw_am145_0x5a35a4_outputs;

open_cfw_am145_0x5a35a4_outputs
open_cfw_am145_0x5a35a4_semantic_model(
    open_cfw_am145_0x5a35a4_inputs in)
{
    open_cfw_am145_0x5a35a4_outputs out;
    uint32_t magnitude;

    out.r0 = 0U;
    out.vtable_lookup_performed = 0U;
    out.vtable_lookup_call_target = 0x004ebe6eU;
    out.cached_vtable_stored = 0U;
    out.parser_delegate_call_target = 0x005a338cU;
    out.normalized_index = 0U;
    out.negative_index = in.signed_index < 0 ? 1U : 0U;
    out.bounds_error = 0U;
    out.table_lookup_call_target = 0x005a2c00U;
    out.callback58_performed = 0U;
    out.callback58_is_indirect_boundary = 0U;

    if (in.cached_vtable_present == 0U) {
        out.vtable_lookup_performed = 1U;
        if (in.vtable_lookup_result == 0U) {
            out.r0 = 0x0bU;
            return out;
        }
        out.cached_vtable_stored = 1U;
    }

    if (in.parser_delegate_return != 0U) {
        out.r0 = in.parser_delegate_return;
        return out;
    }

    magnitude = out.negative_index != 0U
        ? (uint32_t)(-in.signed_index)
        : (uint32_t)in.signed_index;
    magnitude &= 0xffffU;
    if (out.negative_index != 0U) {
        magnitude -= 1U;
    }
    out.normalized_index = magnitude;

    if (magnitude >= in.decoded_count) {
        if (out.negative_index == 0U) {
            out.r0 = 6U;
            out.bounds_error = 1U;
            return out;
        }
    }

    if (in.table_lookup_return != 0U) {
        out.r0 = in.table_lookup_return;
        return out;
    }

    out.callback58_performed = 1U;
    out.callback58_is_indirect_boundary = 1U;
    out.r0 = in.callback58_return;
    return out;
}

typedef struct {
    uint32_t parser_return;
    uint32_t parsed_length;
    uint32_t scalar_status;
    uint32_t tag_word;
    uint32_t field_size;
    uint32_t entry_count;
    uint32_t payload_length;
} open_cfw_am145_0x5a36ac_inputs;

typedef struct {
    uint32_t r0;
    uint32_t parser_call_target;
    uint32_t parser_call_r2_is_source;
    uint32_t parsed_length_ok;
    uint32_t scalar_reads_attempted;
    uint32_t parse_failed_zeroes_fields;
    uint32_t tag_ok;
    uint32_t field_size_ok;
    uint32_t count_ok;
    uint32_t payload_length_ok;
    uint32_t structure_accepted;
} open_cfw_am145_0x5a36ac_outputs;

open_cfw_am145_0x5a36ac_outputs
open_cfw_am145_0x5a36ac_semantic_model(
    open_cfw_am145_0x5a36ac_inputs in)
{
    open_cfw_am145_0x5a36ac_outputs out;
    uint32_t count16;
    uint32_t payload16;

    out.r0 = 0U;
    out.parser_call_target = 0x005a338cU;
    out.parser_call_r2_is_source = 1U;
    out.parsed_length_ok = in.parsed_length >= 0x14U ? 1U : 0U;
    out.scalar_reads_attempted = 0U;
    out.parse_failed_zeroes_fields = 0U;
    out.tag_ok = 0U;
    out.field_size_ok = 0U;
    out.count_ok = 0U;
    out.payload_length_ok = 0U;
    out.structure_accepted = 0U;

    if (in.parser_return != 0U || out.parsed_length_ok == 0U) {
        out.parse_failed_zeroes_fields = 1U;
        return out;
    }

    out.scalar_reads_attempted = 6U;
    if (in.scalar_status != 0U) {
        out.parse_failed_zeroes_fields = 1U;
        return out;
    }

    count16 = in.entry_count & 0xffffU;
    payload16 = in.payload_length & 0xffffU;
    out.tag_ok = in.tag_word == 0x00010000U ? 1U : 0U;
    out.field_size_ok = (in.field_size & 0xffffU) == 0x14U ? 1U : 0U;
    out.count_ok = (count16 != 0U && count16 < 0x3fffU) ? 1U : 0U;
    out.payload_length_ok =
        payload16 == ((count16 << 2U) + 4U) ? 1U : 0U;
    out.structure_accepted = (
        out.tag_ok != 0U &&
        out.field_size_ok != 0U &&
        out.count_ok != 0U &&
        out.payload_length_ok != 0U
    ) ? 1U : 0U;
    return out;
}

typedef struct {
    uint32_t prior_dirty_bit;
    uint32_t required_span;
    uint32_t available_span;
    uint32_t row_count;
    uint32_t column_count;
    uint32_t row_stride;
    uint32_t first_alloc_status;
    uint32_t second_alloc_status;
    uint32_t row_copy_status;
    uint32_t compare_iterations_before_match;
} open_cfw_am145_0x5a3798_inputs;

typedef struct {
    uint32_t r0;
    uint32_t dirty_bit_set;
    uint32_t allocation_attempts;
    uint32_t first_alloc_call_target;
    uint32_t second_alloc_call_target;
    uint32_t allocations_failed;
    uint32_t row_copy_call_target;
    uint32_t row_copy_attempts;
    uint32_t compare_call_target;
    uint32_t compare_attempts;
    uint32_t dimension_incremented;
    uint32_t cleanup_calls;
} open_cfw_am145_0x5a3798_outputs;

open_cfw_am145_0x5a3798_outputs
open_cfw_am145_0x5a3798_semantic_model(
    open_cfw_am145_0x5a3798_inputs in)
{
    open_cfw_am145_0x5a3798_outputs out;
    uint32_t rows;
    uint32_t columns;

    out.r0 = 0U;
    out.dirty_bit_set = in.prior_dirty_bit != 0U ? 1U : 0U;
    out.allocation_attempts = 0U;
    out.first_alloc_call_target = 0x004ed9d0U;
    out.second_alloc_call_target = 0x004ed9d0U;
    out.allocations_failed = 0U;
    out.row_copy_call_target = 0x004ed1beU;
    out.row_copy_attempts = 0U;
    out.compare_call_target = 0x004ed1beU;
    out.compare_attempts = 0U;
    out.dimension_incremented = 0U;
    out.cleanup_calls = 0U;

    if (in.required_span > in.available_span) {
        out.dirty_bit_set = 1U;
    }
    if (out.dirty_bit_set == 0U) {
        return out;
    }

    out.allocation_attempts = 2U;
    if (in.first_alloc_status != 0U || in.second_alloc_status != 0U) {
        out.allocations_failed = 1U;
        out.cleanup_calls = 2U;
        return out;
    }

    rows = in.row_count & 0xffffU;
    columns = in.column_count & 0xffffU;
    out.row_copy_attempts = rows;
    if (in.row_copy_status != 0U) {
        out.cleanup_calls = 2U;
        return out;
    }

    out.compare_attempts = in.compare_iterations_before_match;
    if (out.compare_attempts > columns) {
        out.compare_attempts = columns;
    }
    if (out.compare_attempts == columns) {
        out.dimension_incremented = 1U;
    }
    out.cleanup_calls = 2U;
    (void)in.row_stride;
    return out;
}

typedef struct {
    uint32_t bound_word;
    uint32_t mode_gate;
    uint32_t mode0_primary_return;
    uint32_t mode0_secondary_return;
    uint32_t fallback_chain_present;
    uint32_t context_magic_matches;
    uint32_t mode1_primary_return;
    uint32_t mode1_secondary_return;
} open_cfw_am145_0x5a3ab0_inputs;

typedef struct {
    uint32_t r0;
    uint32_t setup_callback_count;
    uint32_t bound_error;
    uint32_t mode0_entered;
    uint32_t mode0_primary_call_target;
    uint32_t mode0_secondary_call_target;
    uint32_t status_0xfa_cleared;
    uint32_t mode1_entered;
    uint32_t mode1_primary_call_target;
    uint32_t mode1_secondary_call_target;
    uint32_t flag_0x124_set;
    uint32_t exits_prefix;
} open_cfw_am145_0x5a3ab0_outputs;

open_cfw_am145_0x5a3ab0_outputs
open_cfw_am145_0x5a3ab0_semantic_model(
    open_cfw_am145_0x5a3ab0_inputs in)
{
    open_cfw_am145_0x5a3ab0_outputs out;
    uint32_t result;

    out.r0 = 0U;
    out.setup_callback_count = 0U;
    out.bound_error = 0U;
    out.mode0_entered = 0U;
    out.mode0_primary_call_target = 0U;
    out.mode0_secondary_call_target = 0U;
    out.status_0xfa_cleared = 0U;
    out.mode1_entered = 0U;
    out.mode1_primary_call_target = 0U;
    out.mode1_secondary_call_target = 0U;
    out.flag_0x124_set = 0U;
    out.exits_prefix = 0U;

    if (((in.bound_word & 0xffffU) - 0x10U) >= 0x3ff1U) {
        out.r0 = 8U;
        out.bound_error = 1U;
        out.exits_prefix = 1U;
        return out;
    }

    out.setup_callback_count = 4U;
    if (in.mode_gate != 0U) {
        return out;
    }

    out.mode0_entered = 1U;
    out.mode0_primary_call_target = 0x0000001cU;
    out.mode0_secondary_call_target = 0x0000005cU;
    result = in.mode0_primary_return;
    if (result == 0U) {
        result = in.mode0_secondary_return;
        if ((result & 0xffU) == 0x8eU) {
            result = 0x93U;
            if (in.fallback_chain_present != 0U) {
                out.status_0xfa_cleared = 1U;
                result = 0U;
            }
        }
    } else if ((result & 0xffU) == 0x8eU) {
        if (in.context_magic_matches != 0U) {
            result = 0U;
        } else {
            result = 0x8fU;
            if (in.fallback_chain_present != 0U) {
                out.status_0xfa_cleared = 1U;
                result = 0U;
            }
        }
    }
    if (result != 0U) {
        out.r0 = result;
        out.exits_prefix = 1U;
        return out;
    }

    out.mode1_entered = 1U;
    out.mode1_primary_call_target = 0x0000001cU;
    out.mode1_secondary_call_target = 0x0000005cU;
    result = in.mode1_primary_return;
    if (result == 0U) {
        result = in.mode1_secondary_return;
        if (result == 0U) {
            out.flag_0x124_set = 1U;
        }
    }
    out.r0 = result;
    return out;
}

typedef struct {
    uint32_t incoming_status;
    uint32_t callback28_return;
    uint32_t optional_callback60_present;
    uint32_t optional_callback60_return;
    uint32_t parse_gate_174_is_unset;
    uint32_t flag_1b4_bit8_set;
    uint32_t mode9_gate;
    uint32_t mode7_gate;
    uint32_t parser_status;
} open_cfw_am145_0x5a3bcc_inputs;

typedef struct {
    uint32_t r0;
    uint32_t enters_prefix;
    uint32_t callback28_performed;
    uint32_t status_0x174_forced_unset;
    uint32_t optional_callback60_performed;
    uint32_t fixed_callback_count;
    uint32_t slot_0x10_loaded_from_0x108;
    uint32_t slot_0x14_cleared;
    uint32_t slot_0x18_cleared;
    uint32_t parser_call_count;
    uint32_t first_parser_id;
    uint32_t second_parser_id;
    uint32_t third_parser_id;
    uint32_t exits_prefix;
} open_cfw_am145_0x5a3bcc_outputs;

open_cfw_am145_0x5a3bcc_outputs
open_cfw_am145_0x5a3bcc_semantic_model(
    open_cfw_am145_0x5a3bcc_inputs in)
{
    open_cfw_am145_0x5a3bcc_outputs out;

    out.r0 = in.incoming_status;
    out.enters_prefix = (in.incoming_status & 0xffU) == 0x8eU ? 1U : 0U;
    out.callback28_performed = 0U;
    out.status_0x174_forced_unset = 0U;
    out.optional_callback60_performed = 0U;
    out.fixed_callback_count = 0U;
    out.slot_0x10_loaded_from_0x108 = 0U;
    out.slot_0x14_cleared = 0U;
    out.slot_0x18_cleared = 0U;
    out.parser_call_count = 0U;
    out.first_parser_id = 0U;
    out.second_parser_id = 0U;
    out.third_parser_id = 0U;
    out.exits_prefix = out.enters_prefix == 0U ? 1U : 0U;

    if (out.enters_prefix == 0U) {
        return out;
    }

    out.callback28_performed = 1U;
    if (in.callback28_return != 0U) {
        out.status_0x174_forced_unset = 1U;
    }
    if (in.optional_callback60_present != 0U) {
        out.optional_callback60_performed = 1U;
        out.r0 = in.optional_callback60_return;
    }
    out.fixed_callback_count = 3U;
    out.slot_0x10_loaded_from_0x108 = 1U;
    out.slot_0x14_cleared = 1U;
    out.slot_0x18_cleared = 1U;

    if (in.parse_gate_174_is_unset != 0U || in.flag_1b4_bit8_set == 0U) {
        out.parser_call_count = 1U;
        out.first_parser_id = 0x15U;
    } else {
        if (in.mode9_gate == 0U) {
            out.parser_call_count++;
            out.first_parser_id = 0x10U;
            if (in.parser_status != 0U) {
                out.r0 = in.parser_status;
                out.exits_prefix = 1U;
                return out;
            }
        }
        out.parser_call_count++;
        if (out.first_parser_id == 0U) {
            out.first_parser_id = 1U;
        } else {
            out.second_parser_id = 1U;
        }
        if (in.parser_status != 0U) {
            out.r0 = in.parser_status;
            out.exits_prefix = 1U;
            return out;
        }
        if (in.mode7_gate == 0U) {
            out.parser_call_count++;
            if (out.second_parser_id == 0U) {
                out.second_parser_id = 0x11U;
            } else {
                out.third_parser_id = 0x11U;
            }
        }
        if (out.third_parser_id == 0U) {
            out.third_parser_id = 2U;
        }
    }

    out.r0 = in.parser_status;
    return out;
}

typedef struct {
    uint32_t incoming_status;
    uint32_t slot_0x14_present;
    uint32_t mode9_gate;
    uint32_t slot_0x18_present;
    uint32_t mode7_gate;
    uint32_t parser_status;
    uint32_t base_flags;
    uint32_t mode_byte_0x2f8;
    uint32_t mode8_gate;
    uint32_t type_word_0x1dc;
    uint32_t pointer_0x1e8_present;
    uint32_t flag_0x124_set;
    uint32_t pointer_0x310_present;
    uint32_t dirty_bit_set;
    uint32_t feature_probe_allows_0x100;
} open_cfw_am145_0x5a3cc6_inputs;

typedef struct {
    uint32_t r0;
    uint32_t enters_prefix;
    uint32_t parser_call_count;
    uint32_t first_parser_id;
    uint32_t second_parser_id;
    uint32_t third_parser_id;
    uint32_t exits_prefix;
    uint32_t composed_flags;
    uint32_t feature_probe_count;
    uint32_t flags_stored;
} open_cfw_am145_0x5a3cc6_outputs;

open_cfw_am145_0x5a3cc6_outputs
open_cfw_am145_0x5a3cc6_semantic_model(
    open_cfw_am145_0x5a3cc6_inputs in)
{
    open_cfw_am145_0x5a3cc6_outputs out;
    uint32_t flags;

    out.r0 = in.incoming_status;
    out.enters_prefix = in.incoming_status == 0U ? 1U : 0U;
    out.parser_call_count = 0U;
    out.first_parser_id = 0U;
    out.second_parser_id = 0U;
    out.third_parser_id = 0U;
    out.exits_prefix = out.enters_prefix == 0U ? 1U : 0U;
    out.composed_flags = in.base_flags;
    out.feature_probe_count = 0U;
    out.flags_stored = 0U;

    if (out.enters_prefix == 0U) {
        return out;
    }

    if (in.slot_0x14_present == 0U && in.mode9_gate == 0U) {
        out.parser_call_count++;
        out.first_parser_id = 0x10U;
        if (in.parser_status != 0U) {
            out.r0 = in.parser_status;
            out.exits_prefix = 1U;
            return out;
        }
    }
    if (in.slot_0x14_present == 0U) {
        out.parser_call_count++;
        if (out.first_parser_id == 0U) {
            out.first_parser_id = 1U;
        } else {
            out.second_parser_id = 1U;
        }
        if (in.parser_status != 0U) {
            out.r0 = in.parser_status;
            out.exits_prefix = 1U;
            return out;
        }
    }
    out.parser_call_count++;
    if (out.first_parser_id == 0U) {
        out.first_parser_id = 0x16U;
    } else if (out.second_parser_id == 0U) {
        out.second_parser_id = 0x16U;
    } else {
        out.third_parser_id = 0x16U;
    }
    if (in.parser_status != 0U) {
        out.r0 = in.parser_status;
        out.exits_prefix = 1U;
        return out;
    }
    if (in.slot_0x18_present == 0U && in.mode7_gate == 0U) {
        out.parser_call_count++;
    }
    if (in.slot_0x18_present == 0U) {
        out.parser_call_count++;
    }

    flags = in.base_flags | 0x18U;
    if (in.mode_byte_0x2f8 == 2U || in.mode_byte_0x2f8 == 3U) {
        flags |= 0x4000U;
    }
    if (in.mode8_gate == 1U) {
        flags |= 0x1U;
    }
    if (in.mode8_gate == 0U && in.type_word_0x1dc != 0x30000U) {
        flags |= 0x200U;
    }
    if (in.pointer_0x1e8_present != 0U) {
        flags |= 0x4U;
    }
    if (in.flag_0x124_set != 0U) {
        flags |= 0x20U;
    }
    if (in.pointer_0x310_present != 0U) {
        flags |= 0x40U;
    }
    if (in.dirty_bit_set != 0U) {
        out.feature_probe_count = 3U;
        if (in.feature_probe_allows_0x100 != 0U) {
            flags |= 0x100U;
        }
    }
    out.composed_flags = flags;
    out.flags_stored = 1U;
    out.r0 = 0U;
    return out;
}

typedef struct {
    uint32_t initial_flags;
    uint32_t existing_output_flags;
    uint32_t use_alt_source;
    uint32_t byte_0x1b4;
    uint32_t byte_0xcc;
    uint32_t table_count;
} open_cfw_am145_0x5a3e24_inputs;

typedef struct {
    uint32_t r0;
    uint32_t source_byte_offset;
    uint32_t low_bit_from_source;
    uint32_t high_bit_from_source;
    uint32_t merged_flags;
    uint32_t output_flags_stored;
    uint32_t post_merge_call_target;
    uint32_t table_loop_entered;
    uint32_t table_iterations_planned;
} open_cfw_am145_0x5a3e24_outputs;

open_cfw_am145_0x5a3e24_outputs
open_cfw_am145_0x5a3e24_semantic_model(
    open_cfw_am145_0x5a3e24_inputs in)
{
    open_cfw_am145_0x5a3e24_outputs out;
    uint32_t source = in.use_alt_source != 0U ? in.byte_0xcc : in.byte_0x1b4;
    uint32_t flags = in.initial_flags;

    out.source_byte_offset = in.use_alt_source != 0U ? 0xccU : 0x1b4U;
    out.low_bit_from_source = source & 1U;
    out.high_bit_from_source = in.use_alt_source != 0U
        ? ((source >> 1U) & 1U)
        : ((source >> 5U) & 1U);
    if (in.use_alt_source != 0U) {
        if (out.low_bit_from_source != 0U) {
            flags |= 0x2U;
        }
        if (out.high_bit_from_source != 0U) {
            flags |= 0x1U;
        }
    } else {
        if (out.low_bit_from_source != 0U) {
            flags |= 0x1U;
        }
        if (out.high_bit_from_source != 0U) {
            flags |= 0x2U;
        }
    }
    out.merged_flags = flags | in.existing_output_flags;
    out.output_flags_stored = 1U;
    out.post_merge_call_target = 0x005a6cb2U;
    out.table_loop_entered = in.table_count != 0U ? 1U : 0U;
    out.table_iterations_planned = in.table_count;
    out.r0 = 0U;
    return out;
}

typedef struct {
    uint32_t loop_condition_nonzero;
    uint32_t loop_index;
    uint32_t loop_limit;
    uint32_t allocator_status;
    uint32_t allocation_result;
    uint32_t pointer_0x1c_present;
    uint32_t existing_status_flags;
    uint32_t bit0_already_set;
    uint32_t copy_geometry;
    int32_t geom_c4;
    int32_t geom_c6;
    int32_t geom_c8;
    int32_t geom_ca;
    uint32_t half_b2;
    uint32_t half_dc;
    uint32_t half_de;
    uint32_t half_e0;
} open_cfw_am145_0x5a3fe8_inputs;

typedef struct {
    uint32_t r0;
    uint32_t loop_continues;
    uint32_t allocator_call_target;
    uint32_t allocator_arg_element_size;
    uint32_t allocation_status_error;
    uint32_t allocation_result_stored;
    uint32_t status_flags;
    uint32_t pointer_0x1c_stored;
    uint32_t geometry_copied;
    int32_t copied_c4;
    int32_t copied_c6;
    int32_t copied_c8;
    int32_t copied_ca;
    uint32_t copied_b2;
    uint32_t copied_dc;
    uint32_t copied_de;
    uint32_t derived_4a;
} open_cfw_am145_0x5a3fe8_outputs;

open_cfw_am145_0x5a3fe8_outputs
open_cfw_am145_0x5a3fe8_semantic_model(
    open_cfw_am145_0x5a3fe8_inputs in)
{
    open_cfw_am145_0x5a3fe8_outputs out;
    uint32_t flags = in.existing_status_flags;

    out.r0 = 0U;
    out.loop_continues =
        in.loop_condition_nonzero != 0U && in.loop_index + 1U < in.loop_limit
            ? 1U
            : 0U;
    out.allocator_call_target = 0x004ed1d4U;
    out.allocator_arg_element_size = 4U;
    out.allocation_status_error = in.allocator_status != 0U ? 1U : 0U;
    out.allocation_result_stored = 0U;
    out.pointer_0x1c_stored = 0U;
    out.geometry_copied = 0U;
    out.copied_c4 = 0;
    out.copied_c6 = 0;
    out.copied_c8 = 0;
    out.copied_ca = 0;
    out.copied_b2 = 0U;
    out.copied_dc = 0U;
    out.copied_de = 0U;
    out.derived_4a = 0U;

    if (out.loop_continues != 0U) {
        out.status_flags = flags;
        return out;
    }
    if (in.allocator_status != 0U) {
        out.r0 = in.allocator_status;
        out.status_flags = flags;
        return out;
    }

    if (in.pointer_0x1c_present != 0U) {
        out.allocation_result_stored = in.allocation_result;
        flags |= 0x2U;
        out.pointer_0x1c_stored = 1U;
    }
    if (((flags | in.bit0_already_set) & 0x3U) == 0U) {
        flags |= 0x1U;
    }

    if ((flags & 0x1U) != 0U && in.copy_geometry != 0U) {
        out.geometry_copied = 1U;
        out.copied_c4 = in.geom_c4;
        out.copied_c6 = in.geom_c6;
        out.copied_c8 = in.geom_c8;
        out.copied_ca = in.geom_ca;
        out.copied_b2 = in.half_b2 & 0xffffU;
        out.copied_dc = in.half_dc & 0xffffU;
        out.copied_de = in.half_de & 0xffffU;
        out.derived_4a = (in.half_e0 + out.copied_dc - out.copied_de)
            & 0xffffU;
    }

    out.status_flags = flags;
    return out;
}

typedef struct {
    uint32_t use_alternate_geometry;
    uint32_t existing_46;
    uint32_t existing_48;
    uint32_t base_1be;
    int32_t alt_1c0;
    int32_t alt_1c2;
} open_cfw_am145_0x5a40ca_inputs;

typedef struct {
    uint32_t r0;
    uint32_t writes_46;
    uint32_t writes_48;
    uint32_t copied_46;
    uint32_t copied_48;
    uint32_t derived_4a;
} open_cfw_am145_0x5a40ca_outputs;

open_cfw_am145_0x5a40ca_outputs
open_cfw_am145_0x5a40ca_semantic_model(
    open_cfw_am145_0x5a40ca_inputs in)
{
    open_cfw_am145_0x5a40ca_outputs out;
    uint32_t value46 = in.existing_46 & 0xffffU;
    uint32_t value48 = in.existing_48 & 0xffffU;

    out.r0 = 0U;
    out.writes_46 = 0U;
    out.writes_48 = 0U;

    if (in.use_alternate_geometry != 0U) {
        value46 = (uint32_t)in.alt_1c0 & 0xffffU;
        value48 = (uint32_t)(-in.alt_1c2) & 0xffffU;
        out.writes_46 = 1U;
        out.writes_48 = 1U;
    }

    out.copied_46 = value46;
    out.copied_48 = value48;
    out.derived_4a = (in.base_1be + value46 - value48) & 0xffffU;
    return out;
}

typedef struct {
    uint32_t current_max_index;
    uint32_t cursor_index;
    uint32_t pair_count;
    uint32_t base_offset;
    uint32_t accumulated_offset;
    uint32_t high_cursor;
    uint32_t delta;
    uint32_t first_pair;
    uint32_t second_pair;
} open_cfw_am145_0x5a490c_inputs;

typedef struct {
    uint32_t r0;
    uint32_t normalized_cursor;
    uint32_t next_max_index;
    uint32_t scan_base_offset;
    uint32_t accumulated_offset;
    uint32_t high_cursor;
    uint32_t scanned_pairs;
    uint32_t selected_index;
    uint32_t selected_value;
    uint32_t branch_to_record_match;
    uint32_t branch_to_outer_loop;
} open_cfw_am145_0x5a490c_outputs;

open_cfw_am145_0x5a490c_outputs
open_cfw_am145_0x5a490c_semantic_model(
    open_cfw_am145_0x5a490c_inputs in)
{
    open_cfw_am145_0x5a490c_outputs out;
    uint32_t cursor = in.cursor_index;
    uint32_t max_index = in.current_max_index;
    uint32_t pair_values[2];
    uint32_t scan_index;

    if (max_index < cursor) {
        max_index = cursor;
        cursor = 0U;
    } else {
        cursor = max_index - cursor;
    }

    out.r0 = 0U;
    out.normalized_cursor = cursor;
    out.next_max_index = max_index;
    out.scan_base_offset = in.base_offset + (cursor << 1);
    out.accumulated_offset = in.accumulated_offset + out.scan_base_offset;
    out.high_cursor = (in.high_cursor >> 8) << 8;
    out.scanned_pairs = 0U;
    out.selected_index = 0U;
    out.selected_value = 0U;
    out.branch_to_record_match = 0U;
    out.branch_to_outer_loop = 0U;

    pair_values[0] = in.first_pair & 0xffffU;
    pair_values[1] = in.second_pair & 0xffffU;
    for (scan_index = 0U;
         scan_index < in.pair_count && scan_index < 2U;
         ++scan_index) {
        uint32_t value = pair_values[scan_index];
        out.scanned_pairs = scan_index + 1U;
        out.high_cursor = (out.high_cursor + 1U) & 0xffffffffU;
        if (value != 0U && ((value + in.delta) & 0xffffU) != 0U) {
            out.selected_index = out.high_cursor;
            out.selected_value = value;
            out.branch_to_record_match = 1U;
            return out;
        }
    }

    if (in.pair_count != 0U && out.high_cursor != 0U) {
        out.high_cursor = (out.high_cursor - 1U) & 0xffffffffU;
    }
    if (out.high_cursor < 0x100U) {
        out.high_cursor = (out.high_cursor + 1U) & 0xffffffffU;
    } else {
        out.high_cursor = ((out.high_cursor >> 8) << 8) + 0x100U;
    }
    out.branch_to_outer_loop = 1U;
    return out;
}

typedef struct {
    uint32_t entry_count;
    uint32_t first_marker_seen;
    uint32_t second_marker_seen;
    uint32_t context_flag_value;
    uint32_t predicate0_return;
    uint32_t predicate1_return;
    uint32_t predicate2_return;
} open_cfw_am145_0x5a3980_inputs;

typedef struct {
    uint32_t r0;
    uint32_t marker_scan_performed;
    uint32_t first_marker_found;
    uint32_t second_marker_found;
    uint32_t predicate_call_target;
    uint32_t predicate_calls_performed;
    uint32_t gate_enabled;
} open_cfw_am145_0x5a3980_outputs;

open_cfw_am145_0x5a3980_outputs
open_cfw_am145_0x5a3980_semantic_model(
    open_cfw_am145_0x5a3980_inputs in)
{
    open_cfw_am145_0x5a3980_outputs out;

    out.r0 = 0U;
    out.marker_scan_performed = in.entry_count != 0U ? 1U : 0U;
    out.first_marker_found = in.first_marker_seen != 0U ? 1U : 0U;
    out.second_marker_found = in.second_marker_seen != 0U ? 1U : 0U;
    out.predicate_call_target = 0x005a7178U;
    out.predicate_calls_performed = 0U;
    out.gate_enabled = 0U;

    if (in.context_flag_value != 0U) {
        out.gate_enabled = 1U;
        return out;
    }
    out.predicate_calls_performed = 1U;
    if (in.predicate0_return != 0U) {
        out.gate_enabled = 1U;
        return out;
    }
    out.predicate_calls_performed = 2U;
    if (in.predicate1_return != 0U) {
        out.gate_enabled = 1U;
        return out;
    }
    out.predicate_calls_performed = 3U;
    if (in.predicate2_return != 0U) {
        out.gate_enabled = 1U;
    }
    return out;
}

typedef struct {
    uint32_t parser_callback_return;
    uint32_t marker_gate_enabled;
    uint32_t optional_callback;
    uint32_t optional_callback_return;
    uint32_t fallback_callback;
    uint32_t fallback_callback_return;
} open_cfw_am145_0x5a3a10_inputs;

typedef struct {
    uint32_t r0;
    uint32_t parser_success_flag;
    uint32_t optional_callback_performed;
    uint32_t optional_success_flag;
    uint32_t fallback_callback_performed;
    uint32_t fallback_return;
} open_cfw_am145_0x5a3a10_outputs;

open_cfw_am145_0x5a3a10_outputs
open_cfw_am145_0x5a3a10_semantic_model(
    open_cfw_am145_0x5a3a10_inputs in)
{
    open_cfw_am145_0x5a3a10_outputs out;

    out.r0 = 0U;
    out.parser_success_flag = in.parser_callback_return == 0U ? 1U : 0U;
    out.optional_callback_performed = 0U;
    out.optional_success_flag = 0U;
    out.fallback_callback_performed = 0U;
    out.fallback_return = 0U;

    if (in.marker_gate_enabled == 0U && in.optional_callback != 0U) {
        out.optional_callback_performed = 1U;
        out.optional_success_flag =
            in.optional_callback_return == 0U ? 1U : 0U;
    }
    if (out.optional_success_flag == 0U || out.parser_success_flag != 0U) {
        out.fallback_callback_performed = in.fallback_callback != 0U ? 1U : 0U;
        out.fallback_return = out.fallback_callback_performed
            ? in.fallback_callback_return
            : 0U;
        out.r0 = out.fallback_return;
    }
    return out;
}

typedef struct {
    uint32_t r0;
} open_cfw_am145_zero_return_outputs;

open_cfw_am145_zero_return_outputs
open_cfw_am145_0x5a6596_semantic_model(void)
{
    open_cfw_am145_zero_return_outputs out;

    out.r0 = 0U;
    return out;
}

typedef struct {
    uint32_t r0;
    uint32_t writes_status_word;
    uint32_t status_word_value;
} open_cfw_am145_0x5a659a_outputs;

open_cfw_am145_0x5a659a_outputs
open_cfw_am145_0x5a659a_semantic_model(void)
{
    open_cfw_am145_0x5a659a_outputs out;

    out.r0 = 0U;
    out.writes_status_word = 1U;
    out.status_word_value = 0U;
    return out;
}

typedef struct {
    uint32_t r0;
    uint32_t writes_status_word;
    uint32_t status_word_value;
    uint32_t writes_status_code;
    uint32_t status_code_value;
} open_cfw_am145_0x5a65a2_outputs;

open_cfw_am145_0x5a65a2_outputs
open_cfw_am145_0x5a65a2_semantic_model(void)
{
    open_cfw_am145_0x5a65a2_outputs out;

    out.r0 = 0U;
    out.writes_status_word = 1U;
    out.status_word_value = 0xffffffffU;
    out.writes_status_code = 1U;
    out.status_code_value = 0x0eU;
    return out;
}

typedef struct {
    uint32_t selector;
    uint32_t parser_return_pointer;
    uint32_t range_base;
    uint32_t range_count;
    int32_t result_bias;
    uint32_t table_span;
    uint32_t selected_value;
} open_cfw_am145_0x5a4802_inputs;

typedef struct {
    uint32_t r0;
    uint32_t parser_call_target;
    uint32_t parser_call_r1;
    uint32_t selector_delta;
    uint32_t range_check_passed;
    uint32_t table_lookup_performed;
} open_cfw_am145_0x5a4802_outputs;

open_cfw_am145_0x5a4802_outputs
open_cfw_am145_0x5a4802_semantic_model(
    open_cfw_am145_0x5a4802_inputs in)
{
    open_cfw_am145_0x5a4802_outputs out;
    uint32_t selector = in.selector & 0xffU;
    uint32_t delta = selector - in.range_base;
    uint32_t range_ok = (
        in.parser_return_pointer != 0U
        && selector >= in.range_base
        && delta < in.range_count
        && in.table_span != 0U
    );

    out.parser_call_target = 0x005a47b0U;
    out.parser_call_r1 = in.selector;
    out.selector_delta = delta;
    out.range_check_passed = range_ok;
    out.table_lookup_performed = range_ok && in.selected_value != 0U;
    out.r0 = out.table_lookup_performed
        ? (uint32_t)((int32_t)(in.selected_value & 0xffffU) + in.result_bias)
        : 0U;
    out.r0 &= 0xffffU;
    return out;
}

typedef struct {
    uint32_t current_selector;
    uint32_t parser_context;
    uint32_t parser_return_pointer;
    uint32_t record_field0;
    uint32_t record_field1;
    int32_t record_signed_field2;
} open_cfw_am145_0x5a487a_inputs;

typedef struct {
    uint32_t r0;
    uint32_t parser_call_target;
    uint32_t parser_call_r0;
    uint32_t parser_call_r1;
    uint32_t decoded_field0;
    uint32_t decoded_field1;
    int32_t decoded_signed_field2;
    uint32_t decoded_prefix_entered;
} open_cfw_am145_0x5a487a_outputs;

open_cfw_am145_0x5a487a_outputs
open_cfw_am145_0x5a487a_semantic_model(
    open_cfw_am145_0x5a487a_inputs in)
{
    open_cfw_am145_0x5a487a_outputs out;
    uint32_t selector = in.current_selector + 1U;

    if (selector == 0U) {
        selector = 0x100U;
    }

    out.r0 = 0U;
    out.parser_call_target = 0x005a47b0U;
    out.parser_call_r0 = in.parser_context;
    out.parser_call_r1 = selector;
    out.decoded_field0 = 0U;
    out.decoded_field1 = 0U;
    out.decoded_signed_field2 = 0;
    out.decoded_prefix_entered = 0U;

    if (selector >= 0x10000U || in.parser_return_pointer == 0U) {
        return out;
    }

    out.decoded_field0 = in.record_field0 & 0xffffU;
    out.decoded_field1 = in.record_field1 & 0xffffU;
    out.decoded_signed_field2 = (int16_t)(in.record_signed_field2 & 0xffff);
    out.decoded_prefix_entered = 1U;
    return out;
}

typedef struct {
    uint32_t current_index;
    uint32_t minimum_index;
    uint32_t maximum_index;
    int32_t result_bias;
    uint32_t table_base;
    uint32_t stream_limit;
    uint32_t decoder_limit;
    uint32_t candidate_word;
    int32_t prior_entry_return;
} open_cfw_am145_0x5a4a66_inputs;

typedef struct {
    uint32_t r0;
    uint32_t next_index;
    uint32_t result_value;
    uint32_t prior_entry_call_target;
    uint32_t prior_entry_call_r1;
    uint32_t prior_entry_performed;
    uint32_t table_lookup_performed;
    uint32_t computed_range_performed;
} open_cfw_am145_0x5a4a66_outputs;

open_cfw_am145_0x5a4a66_outputs
open_cfw_am145_0x5a4a66_semantic_model(
    open_cfw_am145_0x5a4a66_inputs in)
{
    open_cfw_am145_0x5a4a66_outputs out;
    uint32_t next = in.current_index + 1U;

    out.r0 = 0U;
    out.next_index = 0xffffffffU;
    out.result_value = 0U;
    out.prior_entry_call_target = 0x005a49bcU;
    out.prior_entry_call_r1 = 0U;
    out.prior_entry_performed = 0U;
    out.table_lookup_performed = 0U;
    out.computed_range_performed = 0U;

    if (in.current_index >= 0xffffU) {
        return out;
    }
    if (next < in.minimum_index) {
        next = in.minimum_index;
    }
    if (in.maximum_index < next) {
        out.prior_entry_call_r1 = in.current_index + 1U;
        out.prior_entry_performed = 1U;
        if (in.prior_entry_return >= 0) {
            out.next_index = in.minimum_index;
        }
        return out;
    }
    if (in.table_base != 0U) {
        uint32_t candidate_address =
            in.table_base + ((next - in.minimum_index) << 1);

        if (in.stream_limit >= candidate_address
            && in.candidate_word != 0U) {
            uint32_t result =
                (uint32_t)((int32_t)(in.candidate_word & 0xffffU)
                           + in.result_bias) & 0xffffU;

            if (result != 0U) {
                out.next_index = next;
                out.result_value = result;
                out.table_lookup_performed = 1U;
                return out;
            }
        }
    } else {
        uint32_t result = (uint32_t)((int32_t)next + in.result_bias) & 0xffffU;

        if (result < in.decoder_limit || in.result_bias == 0) {
            out.next_index = next;
            out.result_value = result;
            out.computed_range_performed = 1U;
            return out;
        }
    }

    out.prior_entry_call_r1 = in.current_index + 1U;
    out.prior_entry_performed = 1U;
    if (in.prior_entry_return >= 0) {
        out.next_index = in.minimum_index;
    }
    return out;
}

typedef struct {
    uint32_t record_offset;
    uint32_t stream_limit;
    uint32_t mode;
    uint32_t declared_payload_length;
    uint32_t count_word;
    uint32_t split_word_a;
    uint32_t split_word_b;
    uint32_t split_log2;
} open_cfw_am145_0x5a4b36_inputs;

typedef struct {
    uint32_t r0;
    uint32_t error_call_target;
    uint32_t error_call_r1;
    uint32_t error_call_count;
    uint32_t effective_payload_length;
    uint32_t entry_count;
    uint32_t table0_offset;
    uint32_t table1_offset;
    uint32_t table2_offset;
    uint32_t table3_offset;
    uint32_t loop_prefix_entered;
} open_cfw_am145_0x5a4b36_outputs;

open_cfw_am145_0x5a4b36_outputs
open_cfw_am145_0x5a4b36_semantic_model(
    open_cfw_am145_0x5a4b36_inputs in)
{
    open_cfw_am145_0x5a4b36_outputs out;
    uint32_t available = 0U;
    uint32_t count = (in.count_word & 0xffffU) >> 1U;

    out.r0 = 0U;
    out.error_call_target = 0x004ecfa4U;
    out.error_call_r1 = 8U;
    out.error_call_count = 0U;
    out.effective_payload_length = in.declared_payload_length & 0xffffU;
    out.entry_count = count;
    out.table0_offset = 0U;
    out.table1_offset = 0U;
    out.table2_offset = 0U;
    out.table3_offset = 0U;
    out.loop_prefix_entered = 0U;

    if (in.stream_limit < in.record_offset + 4U) {
        out.error_call_count++;
    }
    if (in.stream_limit >= in.record_offset) {
        available = in.stream_limit - in.record_offset;
    }
    if (out.effective_payload_length > available && in.mode != 0U) {
        out.effective_payload_length = available;
    }
    if (out.effective_payload_length < 0x10U) {
        out.error_call_count++;
    }
    if (in.mode >= 2U && (in.count_word & 1U) != 0U) {
        out.error_call_count++;
    }
    if (out.effective_payload_length < (count << 3U) + 0x10U) {
        out.error_call_count++;
    }
    if (in.mode >= 2U) {
        uint32_t split_a = (in.split_word_a & 0xffffU) >> 1U;
        uint32_t split_b = (in.split_word_b & 0xffffU) >> 1U;
        uint32_t expected = 1UL << (in.split_log2 & 31U);

        if (((in.split_word_a | in.split_word_b) & 1U) != 0U
            || count < split_a
            || (split_a << 1U) < count
            || split_a + split_b != count
            || split_a != expected) {
            out.error_call_count++;
        }
    }
    out.table0_offset = in.record_offset + 0x0eU;
    out.table1_offset = in.record_offset + 0x10U + (count << 1U);
    out.table2_offset = out.table1_offset + (count << 1U);
    out.table3_offset = out.table2_offset + (count << 1U);
    out.loop_prefix_entered = 1U;
    return out;
}

typedef struct {
    uint32_t context;
    uint32_t callback_owner;
    uint32_t callback_arg;
    uint32_t parser_arg_r3;
    uint32_t parser_return_pointer;
    uint32_t first_offset;
    uint32_t second_offset;
    uint32_t first_path_accepts;
    uint32_t callback_target;
    uint32_t callback_return;
    uint32_t fallback_return;
} open_cfw_am145_0x5a66cc_inputs;

typedef struct {
    uint32_t r0;
    uint32_t pair_parser_call_target;
    uint32_t first_parser_call_target;
    uint32_t fallback_parser_call_target;
    uint32_t selected_offset;
    uint32_t callback_target;
    uint32_t callback_performed;
    uint32_t fallback_performed;
} open_cfw_am145_0x5a66cc_outputs;

open_cfw_am145_0x5a66cc_outputs
open_cfw_am145_0x5a66cc_semantic_model(
    open_cfw_am145_0x5a66cc_inputs in)
{
    open_cfw_am145_0x5a66cc_outputs out;

    out.pair_parser_call_target = 0x005a6672U;
    out.first_parser_call_target = 0x005a65b0U;
    out.fallback_parser_call_target = 0x005a660eU;
    out.callback_target = 0U;
    out.callback_performed = 0U;
    out.fallback_performed = 0U;
    out.selected_offset = 0U;
    out.r0 = 0U;

    if (in.parser_return_pointer == 0U) {
        return out;
    }
    if (in.first_offset != 0U && in.first_path_accepts != 0U) {
        out.selected_offset = in.first_offset;
        out.callback_target = in.callback_target;
        out.callback_performed = in.callback_target != 0U;
        out.r0 = out.callback_performed ? in.callback_return : 0U;
        return out;
    }
    if (in.second_offset != 0U) {
        out.selected_offset = in.second_offset;
        out.fallback_performed = 1U;
        out.r0 = in.fallback_return;
    }
    return out;
}

typedef struct {
    uint32_t context;
    uint32_t callback_arg;
    uint32_t parser_arg_r2;
    uint32_t parser_return_pointer;
    uint32_t first_offset;
    uint32_t second_offset;
    uint32_t first_path_accepts;
    uint32_t fallback_accepts;
} open_cfw_am145_0x5a674a_inputs;

typedef struct {
    int32_t r0;
    uint32_t pair_parser_call_target;
    uint32_t first_parser_call_target;
    uint32_t fallback_parser_call_target;
    uint32_t selected_offset;
    uint32_t first_path_checked;
    uint32_t fallback_checked;
} open_cfw_am145_0x5a674a_outputs;

open_cfw_am145_0x5a674a_outputs
open_cfw_am145_0x5a674a_semantic_model(
    open_cfw_am145_0x5a674a_inputs in)
{
    open_cfw_am145_0x5a674a_outputs out;

    out.pair_parser_call_target = 0x005a6672U;
    out.first_parser_call_target = 0x005a65b0U;
    out.fallback_parser_call_target = 0x005a660eU;
    out.selected_offset = 0U;
    out.first_path_checked = 0U;
    out.fallback_checked = 0U;
    out.r0 = -1;

    if (in.parser_return_pointer == 0U) {
        return out;
    }
    if (in.first_offset != 0U) {
        out.first_path_checked = 1U;
        out.selected_offset = in.first_offset;
        if (in.first_path_accepts != 0U) {
            out.r0 = 1;
            return out;
        }
    }
    if (in.second_offset != 0U) {
        out.fallback_checked = 1U;
        out.selected_offset = in.second_offset;
        if (in.fallback_accepts != 0U) {
            out.r0 = 0;
        }
    }
    return out;
}
