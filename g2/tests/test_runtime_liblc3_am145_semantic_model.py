import ctypes
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT /
    "components/apollo_main/core_overlay/runtime_liblc3_am145_semantic_model.c"
)


class Inputs5a6e34(ctypes.Structure):
    _fields_ = [
        ("context", ctypes.c_uint32),
        ("owner", ctypes.c_uint32),
        ("callback", ctypes.c_uint32),
        ("callback_return", ctypes.c_uint32),
    ]


class Outputs5a6e34(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("call_target", ctypes.c_uint32),
        ("call_r0", ctypes.c_uint32),
        ("callback_performed", ctypes.c_int),
    ]


class Inputs5a6e4a(ctypes.Structure):
    _fields_ = [
        ("context", ctypes.c_uint32),
        ("source", ctypes.c_uint32),
        ("parser_callback", ctypes.c_uint32),
        ("parser_return", ctypes.c_uint32),
        ("parsed_length", ctypes.c_uint32),
        ("copy_return", ctypes.c_uint32),
        ("first_record_count_word", ctypes.c_uint32),
    ]


class Outputs5a6e4a(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("parser_call_target", ctypes.c_uint32),
        ("parser_call_r0", ctypes.c_uint32),
        ("parser_call_r2", ctypes.c_uint32),
        ("copy_call_target", ctypes.c_uint32),
        ("copy_call_r0", ctypes.c_uint32),
        ("copy_call_r1", ctypes.c_uint32),
        ("copy_call_r2_is_context_buffer", ctypes.c_uint32),
        ("stored_length", ctypes.c_uint32),
        ("clamped_record_count", ctypes.c_uint32),
        ("records_scan_entered", ctypes.c_uint32),
    ]


class Inputs5a6f5c(ctypes.Structure):
    _fields_ = [
        ("record_flags", ctypes.c_uint32),
        ("record_cursor_offset", ctypes.c_uint32),
        ("record_end_offset", ctypes.c_uint32),
        ("declared_subrecord_count", ctypes.c_uint32),
        ("current_bit", ctypes.c_uint32),
    ]


class Outputs5a6f5c(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("enough_header_bytes", ctypes.c_uint32),
        ("extension_flag_matches", ctypes.c_uint32),
        ("effective_subrecord_count", ctypes.c_uint32),
        ("feature_mask", ctypes.c_uint32),
        ("nested_scan_entered", ctypes.c_uint32),
    ]


class Inputs5a6eb6(ctypes.Structure):
    _fields_ = [
        ("remaining_sorted_words", ctypes.c_uint32),
        ("previous_word", ctypes.c_uint32),
        ("current_word", ctypes.c_uint32),
        ("record_payload_length", ctypes.c_uint32),
        ("record_end_offset", ctypes.c_uint32),
        ("record_cursor_offset", ctypes.c_uint32),
        ("record_flags", ctypes.c_uint32),
        ("current_bit", ctypes.c_uint32),
    ]


class Outputs5a6eb6(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("sorted_scan_continues", ctypes.c_uint32),
        ("current_bit_mask", ctypes.c_uint32),
        ("record_payload_accepted", ctypes.c_uint32),
        ("clamped_record_end_offset", ctypes.c_uint32),
        ("enters_nested_extension_path", ctypes.c_uint32),
        ("final_status_store_ready", ctypes.c_uint32),
    ]


class Inputs5a6c52(ctypes.Structure):
    _fields_ = [
        ("stack_result", ctypes.c_uint32),
    ]


class Outputs5a6c52(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("call_target", ctypes.c_uint32),
        ("call_r2_is_stack_scratch", ctypes.c_uint32),
    ]


class CallbackTailInputs(ctypes.Structure):
    _fields_ = [
        ("context", ctypes.c_uint32),
        ("callback", ctypes.c_uint32),
        ("callback_return", ctypes.c_uint32),
    ]


class CallbackTailOutputs(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("call_target", ctypes.c_uint32),
        ("call_r0", ctypes.c_uint32),
        ("callback_table_offset", ctypes.c_uint32),
    ]


class Inputs5a6cb0(ctypes.Structure):
    _fields_ = [
        ("stream_base", ctypes.c_uint32),
        ("stream_limit", ctypes.c_uint32),
        ("first_word", ctypes.c_uint32),
        ("second_word", ctypes.c_uint32),
    ]


class Outputs5a6cb0(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("first_tag", ctypes.c_uint32),
        ("second_tag", ctypes.c_uint32),
        ("selected_tag", ctypes.c_uint32),
        ("bytes_consumed", ctypes.c_uint32),
        ("short_buffer_error", ctypes.c_uint32),
        ("falls_into_parser_body", ctypes.c_uint32),
    ]


class Inputs5a6d10(ctypes.Structure):
    _fields_ = [
        ("tag_count", ctypes.c_uint32),
        ("stream_cursor", ctypes.c_uint32),
        ("stream_end", ctypes.c_uint32),
        ("record_offset", ctypes.c_uint32),
        ("record_limit", ctypes.c_uint32),
        ("list_node_present", ctypes.c_uint32),
        ("node_tag_matches", ctypes.c_uint32),
        ("formatter_success", ctypes.c_uint32),
        ("callback_target", ctypes.c_uint32),
        ("attach_success", ctypes.c_uint32),
    ]


class Outputs5a6d10(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("normalized_tag_count", ctypes.c_uint32),
        ("enough_record_bytes", ctypes.c_uint32),
        ("record_offset_accepted", ctypes.c_uint32),
        ("format_call_target", ctypes.c_uint32),
        ("status_call_target", ctypes.c_uint32),
        ("callback_target", ctypes.c_uint32),
        ("callback_performed", ctypes.c_uint32),
        ("attach_call_target", ctypes.c_uint32),
        ("attach_performed", ctypes.c_uint32),
    ]


class Inputs5a6c7c(ctypes.Structure):
    _fields_ = [
        ("nested_offset_0x64_value", ctypes.c_uint32),
        ("context_offset_0x14_value", ctypes.c_uint32),
    ]


class Outputs5a6c7c(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("call_target", ctypes.c_uint32),
        ("call_r0", ctypes.c_uint32),
        ("call_r1", ctypes.c_uint32),
        ("clears_context_offset_0x10", ctypes.c_uint32),
        ("clears_context_offset_0x14", ctypes.c_uint32),
    ]


class Inputs5a6c5e(ctypes.Structure):
    _fields_ = [
        ("nested_offset_0x64_value", ctypes.c_uint32),
        ("nested_offset_0x10_value", ctypes.c_uint32),
        ("callback", ctypes.c_uint32),
        ("callback_return", ctypes.c_uint32),
    ]


class Outputs5a6c5e(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("call_target", ctypes.c_uint32),
        ("call_r0", ctypes.c_uint32),
        ("call_r1_is_context", ctypes.c_uint32),
        ("call_r2", ctypes.c_uint32),
        ("call_r3_literal", ctypes.c_uint32),
        ("stack_arg0", ctypes.c_uint32),
        ("stack_arg1_is_nested", ctypes.c_uint32),
    ]


class Inputs5a67d2(ctypes.Structure):
    _fields_ = [
        ("context", ctypes.c_uint32),
        ("source_offset_0x10", ctypes.c_uint32),
        ("entry_count", ctypes.c_uint32),
        ("parser_arg_r2", ctypes.c_uint32),
        ("parser_return", ctypes.c_uint32),
    ]


class Outputs5a67d2(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("parser_call_target", ctypes.c_uint32),
        ("parser_call_r0", ctypes.c_uint32),
        ("parser_call_r1", ctypes.c_uint32),
        ("parser_call_r2", ctypes.c_uint32),
        ("output_table_offset", ctypes.c_uint32),
        ("source_start_offset", ctypes.c_uint32),
        ("source_stride", ctypes.c_uint32),
        ("decoded_word_count", ctypes.c_uint32),
        ("appends_zero_terminator", ctypes.c_uint32),
    ]


class Inputs5a6822(ctypes.Structure):
    _fields_ = [
        ("context", ctypes.c_uint32),
        ("source_offset_0x10", ctypes.c_uint32),
        ("entry_count", ctypes.c_uint32),
        ("parser_arg_r2", ctypes.c_uint32),
        ("parser_return", ctypes.c_uint32),
    ]


class Outputs5a6822(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("parser_call_target", ctypes.c_uint32),
        ("parser_call_r0", ctypes.c_uint32),
        ("parser_call_r1", ctypes.c_uint32),
        ("parser_call_r2", ctypes.c_uint32),
        ("output_table_offset", ctypes.c_uint32),
        ("source_start_offset", ctypes.c_uint32),
        ("decoded_record_prefix_entered", ctypes.c_uint32),
    ]


class Inputs5a63c8(ctypes.Structure):
    _fields_ = [
        ("stream_limit", ctypes.c_uint32),
        ("table_limit", ctypes.c_uint32),
        ("sequence_limit", ctypes.c_uint32),
        ("previous_sequence", ctypes.c_uint32),
        ("next_sequence", ctypes.c_uint32),
        ("first_table_offset", ctypes.c_uint32),
        ("second_table_offset", ctypes.c_uint32),
        ("first_nested_count", ctypes.c_uint32),
        ("second_nested_count", ctypes.c_uint32),
    ]


class Outputs5a63c8(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("error_call_target", ctypes.c_uint32),
        ("error_call_r1", ctypes.c_uint32),
        ("error_call_count", ctypes.c_uint32),
        ("sequence_monotonic", ctypes.c_uint32),
        ("first_table_accepted", ctypes.c_uint32),
        ("second_table_accepted", ctypes.c_uint32),
        ("first_nested_table_fits", ctypes.c_uint32),
        ("second_nested_table_fits", ctypes.c_uint32),
    ]


class Inputs5a340c(ctypes.Structure):
    _fields_ = [
        ("parser_status", ctypes.c_uint32),
        ("tag", ctypes.c_uint32),
        ("special_tag_matched", ctypes.c_uint32),
        ("recursive_return", ctypes.c_uint32),
    ]


class Outputs5a340c(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("clears_status_slots", ctypes.c_uint32),
        ("parser_call_target", ctypes.c_uint32),
        ("parser_status", ctypes.c_uint32),
        ("special_tag_path_entered", ctypes.c_uint32),
        ("recursive_call_target", ctypes.c_uint32),
        ("accepted_tag", ctypes.c_uint32),
        ("unsupported_tag_error", ctypes.c_uint32),
        ("writes_type_slot", ctypes.c_uint32),
        ("type_slot_value", ctypes.c_uint32),
    ]


class Inputs5a34ca(ctypes.Structure):
    _fields_ = [
        ("precheck_return", ctypes.c_uint32),
        ("decoded_count", ctypes.c_uint32),
        ("available_word_count", ctypes.c_uint32),
        ("allocate_status", ctypes.c_uint32),
        ("table_pointer", ctypes.c_uint32),
        ("element_decode_return", ctypes.c_uint32),
    ]


class Outputs5a34ca(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("precheck_call_target", ctypes.c_uint32),
        ("count_zero_error", ctypes.c_uint32),
        ("count_capacity_error", ctypes.c_uint32),
        ("allocate_call_target", ctypes.c_uint32),
        ("allocate_call_r1", ctypes.c_uint32),
        ("allocation_stored_at_offset_0x90", ctypes.c_uint32),
        ("element_decode_call_target", ctypes.c_uint32),
        ("elements_written", ctypes.c_uint32),
        ("close_call_target", ctypes.c_uint32),
    ]


class Inputs5a35a4(ctypes.Structure):
    _fields_ = [
        ("cached_vtable_present", ctypes.c_uint32),
        ("vtable_lookup_result", ctypes.c_uint32),
        ("parser_delegate_return", ctypes.c_uint32),
        ("signed_index", ctypes.c_int32),
        ("decoded_count", ctypes.c_uint32),
        ("table_lookup_return", ctypes.c_uint32),
        ("callback58_return", ctypes.c_uint32),
    ]


class Outputs5a35a4(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("vtable_lookup_performed", ctypes.c_uint32),
        ("vtable_lookup_call_target", ctypes.c_uint32),
        ("cached_vtable_stored", ctypes.c_uint32),
        ("parser_delegate_call_target", ctypes.c_uint32),
        ("normalized_index", ctypes.c_uint32),
        ("negative_index", ctypes.c_uint32),
        ("bounds_error", ctypes.c_uint32),
        ("table_lookup_call_target", ctypes.c_uint32),
        ("callback58_performed", ctypes.c_uint32),
        ("callback58_is_indirect_boundary", ctypes.c_uint32),
    ]


class Inputs5a36ac(ctypes.Structure):
    _fields_ = [
        ("parser_return", ctypes.c_uint32),
        ("parsed_length", ctypes.c_uint32),
        ("scalar_status", ctypes.c_uint32),
        ("tag_word", ctypes.c_uint32),
        ("field_size", ctypes.c_uint32),
        ("entry_count", ctypes.c_uint32),
        ("payload_length", ctypes.c_uint32),
    ]


class Outputs5a36ac(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("parser_call_target", ctypes.c_uint32),
        ("parser_call_r2_is_source", ctypes.c_uint32),
        ("parsed_length_ok", ctypes.c_uint32),
        ("scalar_reads_attempted", ctypes.c_uint32),
        ("parse_failed_zeroes_fields", ctypes.c_uint32),
        ("tag_ok", ctypes.c_uint32),
        ("field_size_ok", ctypes.c_uint32),
        ("count_ok", ctypes.c_uint32),
        ("payload_length_ok", ctypes.c_uint32),
        ("structure_accepted", ctypes.c_uint32),
    ]


class Inputs5a3798(ctypes.Structure):
    _fields_ = [
        ("prior_dirty_bit", ctypes.c_uint32),
        ("required_span", ctypes.c_uint32),
        ("available_span", ctypes.c_uint32),
        ("row_count", ctypes.c_uint32),
        ("column_count", ctypes.c_uint32),
        ("row_stride", ctypes.c_uint32),
        ("first_alloc_status", ctypes.c_uint32),
        ("second_alloc_status", ctypes.c_uint32),
        ("row_copy_status", ctypes.c_uint32),
        ("compare_iterations_before_match", ctypes.c_uint32),
    ]


class Outputs5a3798(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("dirty_bit_set", ctypes.c_uint32),
        ("allocation_attempts", ctypes.c_uint32),
        ("first_alloc_call_target", ctypes.c_uint32),
        ("second_alloc_call_target", ctypes.c_uint32),
        ("allocations_failed", ctypes.c_uint32),
        ("row_copy_call_target", ctypes.c_uint32),
        ("row_copy_attempts", ctypes.c_uint32),
        ("compare_call_target", ctypes.c_uint32),
        ("compare_attempts", ctypes.c_uint32),
        ("dimension_incremented", ctypes.c_uint32),
        ("cleanup_calls", ctypes.c_uint32),
    ]


class Inputs5a3ab0(ctypes.Structure):
    _fields_ = [
        ("bound_word", ctypes.c_uint32),
        ("mode_gate", ctypes.c_uint32),
        ("mode0_primary_return", ctypes.c_uint32),
        ("mode0_secondary_return", ctypes.c_uint32),
        ("fallback_chain_present", ctypes.c_uint32),
        ("context_magic_matches", ctypes.c_uint32),
        ("mode1_primary_return", ctypes.c_uint32),
        ("mode1_secondary_return", ctypes.c_uint32),
    ]


class Outputs5a3ab0(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("setup_callback_count", ctypes.c_uint32),
        ("bound_error", ctypes.c_uint32),
        ("mode0_entered", ctypes.c_uint32),
        ("mode0_primary_call_target", ctypes.c_uint32),
        ("mode0_secondary_call_target", ctypes.c_uint32),
        ("status_0xfa_cleared", ctypes.c_uint32),
        ("mode1_entered", ctypes.c_uint32),
        ("mode1_primary_call_target", ctypes.c_uint32),
        ("mode1_secondary_call_target", ctypes.c_uint32),
        ("flag_0x124_set", ctypes.c_uint32),
        ("exits_prefix", ctypes.c_uint32),
    ]


class Inputs5a3bcc(ctypes.Structure):
    _fields_ = [
        ("incoming_status", ctypes.c_uint32),
        ("callback28_return", ctypes.c_uint32),
        ("optional_callback60_present", ctypes.c_uint32),
        ("optional_callback60_return", ctypes.c_uint32),
        ("parse_gate_174_is_unset", ctypes.c_uint32),
        ("flag_1b4_bit8_set", ctypes.c_uint32),
        ("mode9_gate", ctypes.c_uint32),
        ("mode7_gate", ctypes.c_uint32),
        ("parser_status", ctypes.c_uint32),
    ]


class Outputs5a3bcc(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("enters_prefix", ctypes.c_uint32),
        ("callback28_performed", ctypes.c_uint32),
        ("status_0x174_forced_unset", ctypes.c_uint32),
        ("optional_callback60_performed", ctypes.c_uint32),
        ("fixed_callback_count", ctypes.c_uint32),
        ("slot_0x10_loaded_from_0x108", ctypes.c_uint32),
        ("slot_0x14_cleared", ctypes.c_uint32),
        ("slot_0x18_cleared", ctypes.c_uint32),
        ("parser_call_count", ctypes.c_uint32),
        ("first_parser_id", ctypes.c_uint32),
        ("second_parser_id", ctypes.c_uint32),
        ("third_parser_id", ctypes.c_uint32),
        ("exits_prefix", ctypes.c_uint32),
    ]


class Inputs5a3cc6(ctypes.Structure):
    _fields_ = [
        ("incoming_status", ctypes.c_uint32),
        ("slot_0x14_present", ctypes.c_uint32),
        ("mode9_gate", ctypes.c_uint32),
        ("slot_0x18_present", ctypes.c_uint32),
        ("mode7_gate", ctypes.c_uint32),
        ("parser_status", ctypes.c_uint32),
        ("base_flags", ctypes.c_uint32),
        ("mode_byte_0x2f8", ctypes.c_uint32),
        ("mode8_gate", ctypes.c_uint32),
        ("type_word_0x1dc", ctypes.c_uint32),
        ("pointer_0x1e8_present", ctypes.c_uint32),
        ("flag_0x124_set", ctypes.c_uint32),
        ("pointer_0x310_present", ctypes.c_uint32),
        ("dirty_bit_set", ctypes.c_uint32),
        ("feature_probe_allows_0x100", ctypes.c_uint32),
    ]


class Outputs5a3cc6(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("enters_prefix", ctypes.c_uint32),
        ("parser_call_count", ctypes.c_uint32),
        ("first_parser_id", ctypes.c_uint32),
        ("second_parser_id", ctypes.c_uint32),
        ("third_parser_id", ctypes.c_uint32),
        ("exits_prefix", ctypes.c_uint32),
        ("composed_flags", ctypes.c_uint32),
        ("feature_probe_count", ctypes.c_uint32),
        ("flags_stored", ctypes.c_uint32),
    ]


class Inputs5a3e24(ctypes.Structure):
    _fields_ = [
        ("initial_flags", ctypes.c_uint32),
        ("existing_output_flags", ctypes.c_uint32),
        ("use_alt_source", ctypes.c_uint32),
        ("byte_0x1b4", ctypes.c_uint32),
        ("byte_0xcc", ctypes.c_uint32),
        ("table_count", ctypes.c_uint32),
    ]


class Outputs5a3e24(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("source_byte_offset", ctypes.c_uint32),
        ("low_bit_from_source", ctypes.c_uint32),
        ("high_bit_from_source", ctypes.c_uint32),
        ("merged_flags", ctypes.c_uint32),
        ("output_flags_stored", ctypes.c_uint32),
        ("post_merge_call_target", ctypes.c_uint32),
        ("table_loop_entered", ctypes.c_uint32),
        ("table_iterations_planned", ctypes.c_uint32),
    ]


class Inputs5a3fe8(ctypes.Structure):
    _fields_ = [
        ("loop_condition_nonzero", ctypes.c_uint32),
        ("loop_index", ctypes.c_uint32),
        ("loop_limit", ctypes.c_uint32),
        ("allocator_status", ctypes.c_uint32),
        ("allocation_result", ctypes.c_uint32),
        ("pointer_0x1c_present", ctypes.c_uint32),
        ("existing_status_flags", ctypes.c_uint32),
        ("bit0_already_set", ctypes.c_uint32),
        ("copy_geometry", ctypes.c_uint32),
        ("geom_c4", ctypes.c_int32),
        ("geom_c6", ctypes.c_int32),
        ("geom_c8", ctypes.c_int32),
        ("geom_ca", ctypes.c_int32),
        ("half_b2", ctypes.c_uint32),
        ("half_dc", ctypes.c_uint32),
        ("half_de", ctypes.c_uint32),
        ("half_e0", ctypes.c_uint32),
    ]


class Outputs5a3fe8(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("loop_continues", ctypes.c_uint32),
        ("allocator_call_target", ctypes.c_uint32),
        ("allocator_arg_element_size", ctypes.c_uint32),
        ("allocation_status_error", ctypes.c_uint32),
        ("allocation_result_stored", ctypes.c_uint32),
        ("status_flags", ctypes.c_uint32),
        ("pointer_0x1c_stored", ctypes.c_uint32),
        ("geometry_copied", ctypes.c_uint32),
        ("copied_c4", ctypes.c_int32),
        ("copied_c6", ctypes.c_int32),
        ("copied_c8", ctypes.c_int32),
        ("copied_ca", ctypes.c_int32),
        ("copied_b2", ctypes.c_uint32),
        ("copied_dc", ctypes.c_uint32),
        ("copied_de", ctypes.c_uint32),
        ("derived_4a", ctypes.c_uint32),
    ]


class Inputs5a40ca(ctypes.Structure):
    _fields_ = [
        ("use_alternate_geometry", ctypes.c_uint32),
        ("existing_46", ctypes.c_uint32),
        ("existing_48", ctypes.c_uint32),
        ("base_1be", ctypes.c_uint32),
        ("alt_1c0", ctypes.c_int32),
        ("alt_1c2", ctypes.c_int32),
    ]


class Outputs5a40ca(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("writes_46", ctypes.c_uint32),
        ("writes_48", ctypes.c_uint32),
        ("copied_46", ctypes.c_uint32),
        ("copied_48", ctypes.c_uint32),
        ("derived_4a", ctypes.c_uint32),
    ]


class Inputs5a490c(ctypes.Structure):
    _fields_ = [
        ("current_max_index", ctypes.c_uint32),
        ("cursor_index", ctypes.c_uint32),
        ("pair_count", ctypes.c_uint32),
        ("base_offset", ctypes.c_uint32),
        ("accumulated_offset", ctypes.c_uint32),
        ("high_cursor", ctypes.c_uint32),
        ("delta", ctypes.c_uint32),
        ("first_pair", ctypes.c_uint32),
        ("second_pair", ctypes.c_uint32),
    ]


class Outputs5a490c(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("normalized_cursor", ctypes.c_uint32),
        ("next_max_index", ctypes.c_uint32),
        ("scan_base_offset", ctypes.c_uint32),
        ("accumulated_offset", ctypes.c_uint32),
        ("high_cursor", ctypes.c_uint32),
        ("scanned_pairs", ctypes.c_uint32),
        ("selected_index", ctypes.c_uint32),
        ("selected_value", ctypes.c_uint32),
        ("branch_to_record_match", ctypes.c_uint32),
        ("branch_to_outer_loop", ctypes.c_uint32),
    ]


class Inputs5a65b0(ctypes.Structure):
    _fields_ = [
        ("table_base", ctypes.c_uint32),
        ("count_word", ctypes.c_uint32),
        ("low_index", ctypes.c_uint32),
        ("high_index", ctypes.c_uint32),
    ]


class Outputs5a65b0(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("decoded_entry_count", ctypes.c_uint32),
        ("search_active", ctypes.c_uint32),
        ("midpoint_index", ctypes.c_uint32),
        ("midpoint_record_offset", ctypes.c_uint32),
        ("next_compare_prefix_entered", ctypes.c_uint32),
    ]


class Inputs5a3980(ctypes.Structure):
    _fields_ = [
        ("entry_count", ctypes.c_uint32),
        ("first_marker_seen", ctypes.c_uint32),
        ("second_marker_seen", ctypes.c_uint32),
        ("context_flag_value", ctypes.c_uint32),
        ("predicate0_return", ctypes.c_uint32),
        ("predicate1_return", ctypes.c_uint32),
        ("predicate2_return", ctypes.c_uint32),
    ]


class Outputs5a3980(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("marker_scan_performed", ctypes.c_uint32),
        ("first_marker_found", ctypes.c_uint32),
        ("second_marker_found", ctypes.c_uint32),
        ("predicate_call_target", ctypes.c_uint32),
        ("predicate_calls_performed", ctypes.c_uint32),
        ("gate_enabled", ctypes.c_uint32),
    ]


class Inputs5a3a10(ctypes.Structure):
    _fields_ = [
        ("parser_callback_return", ctypes.c_uint32),
        ("marker_gate_enabled", ctypes.c_uint32),
        ("optional_callback", ctypes.c_uint32),
        ("optional_callback_return", ctypes.c_uint32),
        ("fallback_callback", ctypes.c_uint32),
        ("fallback_callback_return", ctypes.c_uint32),
    ]


class Outputs5a3a10(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("parser_success_flag", ctypes.c_uint32),
        ("optional_callback_performed", ctypes.c_uint32),
        ("optional_success_flag", ctypes.c_uint32),
        ("fallback_callback_performed", ctypes.c_uint32),
        ("fallback_return", ctypes.c_uint32),
    ]


class ZeroReturnOutputs(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
    ]


class Outputs5a659a(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("writes_status_word", ctypes.c_uint32),
        ("status_word_value", ctypes.c_uint32),
    ]


class Outputs5a65a2(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("writes_status_word", ctypes.c_uint32),
        ("status_word_value", ctypes.c_uint32),
        ("writes_status_code", ctypes.c_uint32),
        ("status_code_value", ctypes.c_uint32),
    ]


class Inputs5a4802(ctypes.Structure):
    _fields_ = [
        ("selector", ctypes.c_uint32),
        ("parser_return_pointer", ctypes.c_uint32),
        ("range_base", ctypes.c_uint32),
        ("range_count", ctypes.c_uint32),
        ("result_bias", ctypes.c_int32),
        ("table_span", ctypes.c_uint32),
        ("selected_value", ctypes.c_uint32),
    ]


class Outputs5a4802(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("parser_call_target", ctypes.c_uint32),
        ("parser_call_r1", ctypes.c_uint32),
        ("selector_delta", ctypes.c_uint32),
        ("range_check_passed", ctypes.c_uint32),
        ("table_lookup_performed", ctypes.c_uint32),
    ]


class Inputs5a487a(ctypes.Structure):
    _fields_ = [
        ("current_selector", ctypes.c_uint32),
        ("parser_context", ctypes.c_uint32),
        ("parser_return_pointer", ctypes.c_uint32),
        ("record_field0", ctypes.c_uint32),
        ("record_field1", ctypes.c_uint32),
        ("record_signed_field2", ctypes.c_int32),
    ]


class Outputs5a487a(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("parser_call_target", ctypes.c_uint32),
        ("parser_call_r0", ctypes.c_uint32),
        ("parser_call_r1", ctypes.c_uint32),
        ("decoded_field0", ctypes.c_uint32),
        ("decoded_field1", ctypes.c_uint32),
        ("decoded_signed_field2", ctypes.c_int32),
        ("decoded_prefix_entered", ctypes.c_uint32),
    ]


class Inputs5a4a66(ctypes.Structure):
    _fields_ = [
        ("current_index", ctypes.c_uint32),
        ("minimum_index", ctypes.c_uint32),
        ("maximum_index", ctypes.c_uint32),
        ("result_bias", ctypes.c_int32),
        ("table_base", ctypes.c_uint32),
        ("stream_limit", ctypes.c_uint32),
        ("decoder_limit", ctypes.c_uint32),
        ("candidate_word", ctypes.c_uint32),
        ("prior_entry_return", ctypes.c_int32),
    ]


class Outputs5a4a66(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("next_index", ctypes.c_uint32),
        ("result_value", ctypes.c_uint32),
        ("prior_entry_call_target", ctypes.c_uint32),
        ("prior_entry_call_r1", ctypes.c_uint32),
        ("prior_entry_performed", ctypes.c_uint32),
        ("table_lookup_performed", ctypes.c_uint32),
        ("computed_range_performed", ctypes.c_uint32),
    ]


class Inputs5a4b36(ctypes.Structure):
    _fields_ = [
        ("record_offset", ctypes.c_uint32),
        ("stream_limit", ctypes.c_uint32),
        ("mode", ctypes.c_uint32),
        ("declared_payload_length", ctypes.c_uint32),
        ("count_word", ctypes.c_uint32),
        ("split_word_a", ctypes.c_uint32),
        ("split_word_b", ctypes.c_uint32),
        ("split_log2", ctypes.c_uint32),
    ]


class Outputs5a4b36(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("error_call_target", ctypes.c_uint32),
        ("error_call_r1", ctypes.c_uint32),
        ("error_call_count", ctypes.c_uint32),
        ("effective_payload_length", ctypes.c_uint32),
        ("entry_count", ctypes.c_uint32),
        ("table0_offset", ctypes.c_uint32),
        ("table1_offset", ctypes.c_uint32),
        ("table2_offset", ctypes.c_uint32),
        ("table3_offset", ctypes.c_uint32),
        ("loop_prefix_entered", ctypes.c_uint32),
    ]


class Inputs5a66cc(ctypes.Structure):
    _fields_ = [
        ("context", ctypes.c_uint32),
        ("callback_owner", ctypes.c_uint32),
        ("callback_arg", ctypes.c_uint32),
        ("parser_arg_r3", ctypes.c_uint32),
        ("parser_return_pointer", ctypes.c_uint32),
        ("first_offset", ctypes.c_uint32),
        ("second_offset", ctypes.c_uint32),
        ("first_path_accepts", ctypes.c_uint32),
        ("callback_target", ctypes.c_uint32),
        ("callback_return", ctypes.c_uint32),
        ("fallback_return", ctypes.c_uint32),
    ]


class Outputs5a66cc(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("pair_parser_call_target", ctypes.c_uint32),
        ("first_parser_call_target", ctypes.c_uint32),
        ("fallback_parser_call_target", ctypes.c_uint32),
        ("selected_offset", ctypes.c_uint32),
        ("callback_target", ctypes.c_uint32),
        ("callback_performed", ctypes.c_uint32),
        ("fallback_performed", ctypes.c_uint32),
    ]


class Inputs5a674a(ctypes.Structure):
    _fields_ = [
        ("context", ctypes.c_uint32),
        ("callback_arg", ctypes.c_uint32),
        ("parser_arg_r2", ctypes.c_uint32),
        ("parser_return_pointer", ctypes.c_uint32),
        ("first_offset", ctypes.c_uint32),
        ("second_offset", ctypes.c_uint32),
        ("first_path_accepts", ctypes.c_uint32),
        ("fallback_accepts", ctypes.c_uint32),
    ]


class Outputs5a674a(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_int32),
        ("pair_parser_call_target", ctypes.c_uint32),
        ("first_parser_call_target", ctypes.c_uint32),
        ("fallback_parser_call_target", ctypes.c_uint32),
        ("selected_offset", ctypes.c_uint32),
        ("first_path_checked", ctypes.c_uint32),
        ("fallback_checked", ctypes.c_uint32),
    ]


class RuntimeLiblc3Am145SemanticModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmpdir = tempfile.TemporaryDirectory()
        cls.lib_path = Path(cls.tmpdir.name) / "libam145_semantic.dylib"
        subprocess.run(
            [
                "clang",
                "-std=c11",
                "-shared",
                "-fPIC",
                "-O2",
                "-Wall",
                "-Wextra",
                "-Werror",
                str(SOURCE),
                "-o",
                str(cls.lib_path),
            ],
            cwd=ROOT,
            check=True,
        )
        cls.lib = ctypes.CDLL(str(cls.lib_path))
        cls.model = cls.lib.open_cfw_am145_0x5a6e34_semantic_model
        cls.model.argtypes = [Inputs5a6e34]
        cls.model.restype = Outputs5a6e34
        cls.model_5a6e4a = cls.lib.open_cfw_am145_0x5a6e4a_semantic_model
        cls.model_5a6e4a.argtypes = [Inputs5a6e4a]
        cls.model_5a6e4a.restype = Outputs5a6e4a
        cls.model_5a6f5c = cls.lib.open_cfw_am145_0x5a6f5c_semantic_model
        cls.model_5a6f5c.argtypes = [Inputs5a6f5c]
        cls.model_5a6f5c.restype = Outputs5a6f5c
        cls.model_5a6eb6 = cls.lib.open_cfw_am145_0x5a6eb6_semantic_model
        cls.model_5a6eb6.argtypes = [Inputs5a6eb6]
        cls.model_5a6eb6.restype = Outputs5a6eb6
        cls.model_5a6c52 = cls.lib.open_cfw_am145_0x5a6c52_semantic_model
        cls.model_5a6c52.argtypes = [Inputs5a6c52]
        cls.model_5a6c52.restype = Outputs5a6c52
        cls.model_5a6c94 = cls.lib.open_cfw_am145_0x5a6c94_semantic_model
        cls.model_5a6c94.argtypes = [CallbackTailInputs]
        cls.model_5a6c94.restype = CallbackTailOutputs
        cls.model_5a6ca2 = cls.lib.open_cfw_am145_0x5a6ca2_semantic_model
        cls.model_5a6ca2.argtypes = [CallbackTailInputs]
        cls.model_5a6ca2.restype = CallbackTailOutputs
        cls.model_5a6cb0 = cls.lib.open_cfw_am145_0x5a6cb0_semantic_model
        cls.model_5a6cb0.argtypes = [Inputs5a6cb0]
        cls.model_5a6cb0.restype = Outputs5a6cb0
        cls.model_5a6d10 = cls.lib.open_cfw_am145_0x5a6d10_semantic_model
        cls.model_5a6d10.argtypes = [Inputs5a6d10]
        cls.model_5a6d10.restype = Outputs5a6d10
        cls.model_5a6c7c = cls.lib.open_cfw_am145_0x5a6c7c_semantic_model
        cls.model_5a6c7c.argtypes = [Inputs5a6c7c]
        cls.model_5a6c7c.restype = Outputs5a6c7c
        cls.model_5a6c5e = cls.lib.open_cfw_am145_0x5a6c5e_semantic_model
        cls.model_5a6c5e.argtypes = [Inputs5a6c5e]
        cls.model_5a6c5e.restype = Outputs5a6c5e
        cls.model_5a67d2 = cls.lib.open_cfw_am145_0x5a67d2_semantic_model
        cls.model_5a67d2.argtypes = [Inputs5a67d2]
        cls.model_5a67d2.restype = Outputs5a67d2
        cls.model_5a6822 = cls.lib.open_cfw_am145_0x5a6822_semantic_model
        cls.model_5a6822.argtypes = [Inputs5a6822]
        cls.model_5a6822.restype = Outputs5a6822
        cls.model_5a63c8 = cls.lib.open_cfw_am145_0x5a63c8_semantic_model
        cls.model_5a63c8.argtypes = [Inputs5a63c8]
        cls.model_5a63c8.restype = Outputs5a63c8
        cls.model_5a340c = cls.lib.open_cfw_am145_0x5a340c_semantic_model
        cls.model_5a340c.argtypes = [Inputs5a340c]
        cls.model_5a340c.restype = Outputs5a340c
        cls.model_5a34ca = cls.lib.open_cfw_am145_0x5a34ca_semantic_model
        cls.model_5a34ca.argtypes = [Inputs5a34ca]
        cls.model_5a34ca.restype = Outputs5a34ca
        cls.model_5a35a4 = cls.lib.open_cfw_am145_0x5a35a4_semantic_model
        cls.model_5a35a4.argtypes = [Inputs5a35a4]
        cls.model_5a35a4.restype = Outputs5a35a4
        cls.model_5a36ac = cls.lib.open_cfw_am145_0x5a36ac_semantic_model
        cls.model_5a36ac.argtypes = [Inputs5a36ac]
        cls.model_5a36ac.restype = Outputs5a36ac
        cls.model_5a3798 = cls.lib.open_cfw_am145_0x5a3798_semantic_model
        cls.model_5a3798.argtypes = [Inputs5a3798]
        cls.model_5a3798.restype = Outputs5a3798
        cls.model_5a3ab0 = cls.lib.open_cfw_am145_0x5a3ab0_semantic_model
        cls.model_5a3ab0.argtypes = [Inputs5a3ab0]
        cls.model_5a3ab0.restype = Outputs5a3ab0
        cls.model_5a3bcc = cls.lib.open_cfw_am145_0x5a3bcc_semantic_model
        cls.model_5a3bcc.argtypes = [Inputs5a3bcc]
        cls.model_5a3bcc.restype = Outputs5a3bcc
        cls.model_5a3cc6 = cls.lib.open_cfw_am145_0x5a3cc6_semantic_model
        cls.model_5a3cc6.argtypes = [Inputs5a3cc6]
        cls.model_5a3cc6.restype = Outputs5a3cc6
        cls.model_5a3e24 = cls.lib.open_cfw_am145_0x5a3e24_semantic_model
        cls.model_5a3e24.argtypes = [Inputs5a3e24]
        cls.model_5a3e24.restype = Outputs5a3e24
        cls.model_5a3fe8 = cls.lib.open_cfw_am145_0x5a3fe8_semantic_model
        cls.model_5a3fe8.argtypes = [Inputs5a3fe8]
        cls.model_5a3fe8.restype = Outputs5a3fe8
        cls.model_5a40ca = cls.lib.open_cfw_am145_0x5a40ca_semantic_model
        cls.model_5a40ca.argtypes = [Inputs5a40ca]
        cls.model_5a40ca.restype = Outputs5a40ca
        cls.model_5a490c = cls.lib.open_cfw_am145_0x5a490c_semantic_model
        cls.model_5a490c.argtypes = [Inputs5a490c]
        cls.model_5a490c.restype = Outputs5a490c
        cls.model_5a65b0 = cls.lib.open_cfw_am145_0x5a65b0_semantic_model
        cls.model_5a65b0.argtypes = [Inputs5a65b0]
        cls.model_5a65b0.restype = Outputs5a65b0
        cls.model_5a3980 = cls.lib.open_cfw_am145_0x5a3980_semantic_model
        cls.model_5a3980.argtypes = [Inputs5a3980]
        cls.model_5a3980.restype = Outputs5a3980
        cls.model_5a3a10 = cls.lib.open_cfw_am145_0x5a3a10_semantic_model
        cls.model_5a3a10.argtypes = [Inputs5a3a10]
        cls.model_5a3a10.restype = Outputs5a3a10
        cls.model_5a6596 = cls.lib.open_cfw_am145_0x5a6596_semantic_model
        cls.model_5a6596.argtypes = []
        cls.model_5a6596.restype = ZeroReturnOutputs
        cls.model_5a659a = cls.lib.open_cfw_am145_0x5a659a_semantic_model
        cls.model_5a659a.argtypes = []
        cls.model_5a659a.restype = Outputs5a659a
        cls.model_5a65a2 = cls.lib.open_cfw_am145_0x5a65a2_semantic_model
        cls.model_5a65a2.argtypes = []
        cls.model_5a65a2.restype = Outputs5a65a2
        cls.model_5a4802 = cls.lib.open_cfw_am145_0x5a4802_semantic_model
        cls.model_5a4802.argtypes = [Inputs5a4802]
        cls.model_5a4802.restype = Outputs5a4802
        cls.model_5a487a = cls.lib.open_cfw_am145_0x5a487a_semantic_model
        cls.model_5a487a.argtypes = [Inputs5a487a]
        cls.model_5a487a.restype = Outputs5a487a
        cls.model_5a4a66 = cls.lib.open_cfw_am145_0x5a4a66_semantic_model
        cls.model_5a4a66.argtypes = [Inputs5a4a66]
        cls.model_5a4a66.restype = Outputs5a4a66
        cls.model_5a4b36 = cls.lib.open_cfw_am145_0x5a4b36_semantic_model
        cls.model_5a4b36.argtypes = [Inputs5a4b36]
        cls.model_5a4b36.restype = Outputs5a4b36
        cls.model_5a66cc = cls.lib.open_cfw_am145_0x5a66cc_semantic_model
        cls.model_5a66cc.argtypes = [Inputs5a66cc]
        cls.model_5a66cc.restype = Outputs5a66cc
        cls.model_5a674a = cls.lib.open_cfw_am145_0x5a674a_semantic_model
        cls.model_5a674a.argtypes = [Inputs5a674a]
        cls.model_5a674a.restype = Outputs5a674a

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmpdir.cleanup()

    def test_null_callback_returns_literal_error(self) -> None:
        out = self.model(Inputs5a6e34(0x20001000, 0x20002000, 0, 0x1234))

        self.assertEqual(out.r0, 0x96)
        self.assertEqual(out.call_target, 0)
        self.assertEqual(out.call_r0, 0)
        self.assertEqual(out.callback_performed, 0)

    def test_present_callback_is_indirect_tail_boundary(self) -> None:
        out = self.model(
            Inputs5a6e34(0x20001000, 0x20002000, 0x005A7001, 0x89ABCDEF)
        )

        self.assertEqual(out.r0, 0x89ABCDEF)
        self.assertEqual(out.call_target, 0x005A7001)
        self.assertEqual(out.call_r0, 0x20001000)
        self.assertEqual(out.callback_performed, 1)

    def test_parser_prefix_returns_callback_failure(self) -> None:
        out = self.model_5a6e4a(
            Inputs5a6e4a(0x20001000, 0x20002000, 0x005A9000, 7, 12, 0, 4)
        )

        self.assertEqual(out.r0, 7)
        self.assertEqual(out.parser_call_target, 0x005A9000)
        self.assertEqual(out.parser_call_r0, 0x20001000)
        self.assertEqual(out.parser_call_r2, 0x20002000)
        self.assertEqual(out.records_scan_entered, 0)

    def test_parser_prefix_rejects_short_decoded_length(self) -> None:
        out = self.model_5a6e4a(
            Inputs5a6e4a(0x20001000, 0x20002000, 0x005A9000, 0, 3, 0, 4)
        )

        self.assertEqual(out.r0, 0x8E)
        self.assertEqual(out.copy_call_target, 0x004F09B2)
        self.assertEqual(out.records_scan_entered, 0)

    def test_parser_prefix_returns_copy_failure(self) -> None:
        out = self.model_5a6e4a(
            Inputs5a6e4a(0x20001000, 0x20002000, 0x005A9000, 0, 12, 5, 4)
        )

        self.assertEqual(out.r0, 5)
        self.assertEqual(out.copy_call_r0, 0x20002000)
        self.assertEqual(out.copy_call_r1, 12)
        self.assertEqual(out.copy_call_r2_is_context_buffer, 1)
        self.assertEqual(out.records_scan_entered, 0)

    def test_parser_prefix_success_clamps_record_count(self) -> None:
        out = self.model_5a6e4a(
            Inputs5a6e4a(0x20001000, 0x20002000, 0x005A9000, 0, 12, 0, 0x40)
        )

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.stored_length, 12)
        self.assertEqual(out.clamped_record_count, 0x20)
        self.assertEqual(out.records_scan_entered, 1)

    def test_nested_record_scan_skips_non_extension_flags(self) -> None:
        out = self.model_5a6f5c(Inputs5a6f5c(2, 0x20, 0x40, 3, 0x10))

        self.assertEqual(out.extension_flag_matches, 0)
        self.assertEqual(out.nested_scan_entered, 0)
        self.assertEqual(out.feature_mask, 0)

    def test_nested_record_scan_requires_header_bytes(self) -> None:
        out = self.model_5a6f5c(Inputs5a6f5c(1, 0x20, 0x26, 3, 0x10))

        self.assertEqual(out.extension_flag_matches, 1)
        self.assertEqual(out.enough_header_bytes, 0)
        self.assertEqual(out.nested_scan_entered, 0)

    def test_nested_record_scan_clamps_subrecord_count(self) -> None:
        out = self.model_5a6f5c(Inputs5a6f5c(1, 0x20, 0x34, 5, 0x10))

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.enough_header_bytes, 1)
        self.assertEqual(out.extension_flag_matches, 1)
        self.assertEqual(out.effective_subrecord_count, 2)
        self.assertEqual(out.feature_mask, 0x10)
        self.assertEqual(out.nested_scan_entered, 1)

    def test_record_scan_continues_for_increasing_sorted_word(self) -> None:
        out = self.model_5a6eb6(
            Inputs5a6eb6(2, 0x10, 0x20, 0x20, 0x80, 0x40, 1, 0x08)
        )

        self.assertEqual(out.sorted_scan_continues, 1)
        self.assertEqual(out.current_bit_mask, 0)
        self.assertEqual(out.final_status_store_ready, 0)

    def test_record_scan_marks_current_bit_when_sorted_scan_stops(self) -> None:
        out = self.model_5a6eb6(
            Inputs5a6eb6(1, 0x20, 0x10, 0x20, 0x80, 0x40, 0, 0x08)
        )

        self.assertEqual(out.sorted_scan_continues, 0)
        self.assertEqual(out.current_bit_mask, 0x08)
        self.assertEqual(out.record_payload_accepted, 1)
        self.assertEqual(out.clamped_record_end_offset, 0x60)
        self.assertEqual(out.enters_nested_extension_path, 0)
        self.assertEqual(out.final_status_store_ready, 1)

    def test_record_scan_enters_nested_extension_for_flag_one(self) -> None:
        out = self.model_5a6eb6(
            Inputs5a6eb6(0, 0x20, 0x10, 0x20, 0x80, 0x40, 1, 0x08)
        )

        self.assertEqual(out.record_payload_accepted, 1)
        self.assertEqual(out.enters_nested_extension_path, 1)

    def test_single_call_tail_returns_stack_scratch_result(self) -> None:
        out = self.model_5a6c52(Inputs5a6c52(0xA5A55A5A))

        self.assertEqual(out.r0, 0xA5A55A5A)
        self.assertEqual(out.call_target, 0x005A812E)
        self.assertEqual(out.call_r2_is_stack_scratch, 1)

    def test_callback_tail_at_offset_8_returns_callback_result(self) -> None:
        out = self.model_5a6c94(
            CallbackTailInputs(0x20003000, 0x005A9000, 0x11223344)
        )

        self.assertEqual(out.r0, 0x11223344)
        self.assertEqual(out.call_target, 0x005A9000)
        self.assertEqual(out.call_r0, 0x20003000)
        self.assertEqual(out.callback_table_offset, 0x08)

    def test_callback_tail_at_offset_c_returns_callback_result(self) -> None:
        out = self.model_5a6ca2(
            CallbackTailInputs(0x20004000, 0x005A9004, 0x55667788)
        )

        self.assertEqual(out.r0, 0x55667788)
        self.assertEqual(out.call_target, 0x005A9004)
        self.assertEqual(out.call_r0, 0x20004000)
        self.assertEqual(out.callback_table_offset, 0x0C)

    def test_stream_header_tail_rejects_short_buffer(self) -> None:
        out = self.model_5a6cb0(
            Inputs5a6cb0(0x20005000, 0x20005002, 0x1234, 0x5678)
        )

        self.assertEqual(out.r0, 8)
        self.assertEqual(out.bytes_consumed, 0)
        self.assertEqual(out.short_buffer_error, 1)
        self.assertEqual(out.falls_into_parser_body, 0)

    def test_stream_header_tail_uses_first_nonzero_tag(self) -> None:
        out = self.model_5a6cb0(
            Inputs5a6cb0(0x20005000, 0x20005004, 0x1234, 0x5678)
        )

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.first_tag, 0x1234)
        self.assertEqual(out.second_tag, 0)
        self.assertEqual(out.selected_tag, 0x1234)
        self.assertEqual(out.bytes_consumed, 2)
        self.assertEqual(out.falls_into_parser_body, 1)

    def test_stream_header_tail_reads_second_tag_after_zero(self) -> None:
        out = self.model_5a6cb0(
            Inputs5a6cb0(0x20005000, 0x20005004, 0, 0x5678)
        )

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.first_tag, 0)
        self.assertEqual(out.second_tag, 0x5678)
        self.assertEqual(out.selected_tag, 0x5678)
        self.assertEqual(out.bytes_consumed, 4)
        self.assertEqual(out.falls_into_parser_body, 1)

    def test_tag_record_loop_skips_when_no_record_bytes_remain(self) -> None:
        out = self.model_5a6d10(
            Inputs5a6d10(2, 0x20, 0x26, 0x10, 0x80, 1, 1, 1,
                         0x005A9000, 1)
        )

        self.assertEqual(out.normalized_tag_count, 2)
        self.assertEqual(out.enough_record_bytes, 0)
        self.assertEqual(out.record_offset_accepted, 0)
        self.assertEqual(out.callback_performed, 0)

    def test_tag_record_loop_rejects_out_of_range_offset(self) -> None:
        out = self.model_5a6d10(
            Inputs5a6d10(2, 0x20, 0x30, 0x90, 0x80, 1, 1, 1,
                         0x005A9000, 1)
        )

        self.assertEqual(out.enough_record_bytes, 1)
        self.assertEqual(out.record_offset_accepted, 0)
        self.assertEqual(out.callback_performed, 0)

    def test_tag_record_loop_performs_matched_node_callbacks(self) -> None:
        out = self.model_5a6d10(
            Inputs5a6d10(2, 0x20, 0x30, 0x10, 0x80, 1, 1, 1,
                         0x005A9000, 1)
        )

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.enough_record_bytes, 1)
        self.assertEqual(out.record_offset_accepted, 1)
        self.assertEqual(out.format_call_target, 0x004ECF90)
        self.assertEqual(out.status_call_target, 0x0052F79C)
        self.assertEqual(out.callback_target, 0x005A9000)
        self.assertEqual(out.callback_performed, 1)
        self.assertEqual(out.attach_call_target, 0x004EEE7A)
        self.assertEqual(out.attach_performed, 1)

    def test_runtime_tail_clears_context_slots_after_call(self) -> None:
        out = self.model_5a6c7c(Inputs5a6c7c(0x20005000, 0x12345678))

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.call_target, 0x004F1276)
        self.assertEqual(out.call_r0, 0x20005000)
        self.assertEqual(out.call_r1, 0x12345678)
        self.assertEqual(out.clears_context_offset_0x10, 1)
        self.assertEqual(out.clears_context_offset_0x14, 1)

    def test_literal_pointer_tail_records_indirect_callback_boundary(self) -> None:
        out = self.model_5a6c5e(
            Inputs5a6c5e(0x20006000, 0x20007000, 0x005A9010, 0xCAFEBABE)
        )

        self.assertEqual(out.r0, 0xCAFEBABE)
        self.assertEqual(out.call_target, 0x005A9010)
        self.assertEqual(out.call_r0, 0x20006000)
        self.assertEqual(out.call_r1_is_context, 1)
        self.assertEqual(out.call_r2, 0x20007000)
        self.assertEqual(out.call_r3_literal, 0x005DEC33)
        self.assertEqual(out.stack_arg0, 0)
        self.assertEqual(out.stack_arg1_is_nested, 1)

    def test_delegate_tail_success_decodes_words_and_terminates_table(self) -> None:
        out = self.model_5a67d2(
            Inputs5a67d2(0x20008000, 0x40, 3, 0x20009000, 0)
        )

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.parser_call_target, 0x005A6290)
        self.assertEqual(out.parser_call_r0, 0x20008000)
        self.assertEqual(out.parser_call_r1, 4)
        self.assertEqual(out.parser_call_r2, 0x20009000)
        self.assertEqual(out.output_table_offset, 0x20)
        self.assertEqual(out.source_start_offset, 0x4A)
        self.assertEqual(out.source_stride, 8)
        self.assertEqual(out.decoded_word_count, 3)
        self.assertEqual(out.appends_zero_terminator, 1)

    def test_delegate_tail_parser_failure_returns_zero_without_table_write(self) -> None:
        out = self.model_5a67d2(
            Inputs5a67d2(0x20008000, 0x40, 3, 0x20009000, 1)
        )

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.parser_call_target, 0x005A6290)
        self.assertEqual(out.decoded_word_count, 0)
        self.assertEqual(out.appends_zero_terminator, 0)

    def test_record_prefix_tail_success_enters_decoder_prefix(self) -> None:
        out = self.model_5a6822(
            Inputs5a6822(0x20008000, 0x40, 3, 0x20009000, 0)
        )

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.parser_call_target, 0x005A6290)
        self.assertEqual(out.parser_call_r0, 0x20008000)
        self.assertEqual(out.parser_call_r1, 4)
        self.assertEqual(out.parser_call_r2, 0x20009000)
        self.assertEqual(out.output_table_offset, 0x20)
        self.assertEqual(out.source_start_offset, 0x4A)
        self.assertEqual(out.decoded_record_prefix_entered, 1)

    def test_record_prefix_tail_parser_failure_does_not_enter_decoder(self) -> None:
        out = self.model_5a6822(
            Inputs5a6822(0x20008000, 0x40, 3, 0x20009000, 1)
        )

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.parser_call_target, 0x005A6290)
        self.assertEqual(out.decoded_record_prefix_entered, 0)

    def test_table_validator_accepts_bounded_nested_tables(self) -> None:
        out = self.model_5a63c8(
            Inputs5a63c8(0x100, 0x120, 0x40, 4, 5, 0x20, 0x40, 4, 3)
        )

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.error_call_target, 0x004ECFA4)
        self.assertEqual(out.error_call_r1, 8)
        self.assertEqual(out.error_call_count, 0)
        self.assertEqual(out.sequence_monotonic, 1)
        self.assertEqual(out.first_table_accepted, 1)
        self.assertEqual(out.second_table_accepted, 1)
        self.assertEqual(out.first_nested_table_fits, 1)
        self.assertEqual(out.second_nested_table_fits, 1)

    def test_table_validator_counts_sequence_and_table_errors(self) -> None:
        out = self.model_5a63c8(
            Inputs5a63c8(0x100, 0x50, 0x40, 5, 5, 0x20, 0x120, 20, 3)
        )

        self.assertEqual(out.sequence_monotonic, 0)
        self.assertEqual(out.first_table_accepted, 1)
        self.assertEqual(out.second_table_accepted, 0)
        self.assertEqual(out.first_nested_table_fits, 0)
        self.assertGreaterEqual(out.error_call_count, 3)

    def test_type_gate_prefix_returns_parser_status(self) -> None:
        out = self.model_5a340c(Inputs5a340c(7, 0x10004, 0, 0))

        self.assertEqual(out.r0, 7)
        self.assertEqual(out.clears_status_slots, 1)
        self.assertEqual(out.parser_call_target, 0x005A6D10)
        self.assertEqual(out.parser_status, 7)
        self.assertEqual(out.writes_type_slot, 0)

    def test_type_gate_prefix_rejects_unsupported_tag(self) -> None:
        out = self.model_5a340c(Inputs5a340c(0, 0xDEADBEEF, 0, 0))

        self.assertEqual(out.r0, 2)
        self.assertEqual(out.accepted_tag, 0)
        self.assertEqual(out.unsupported_tag_error, 1)
        self.assertEqual(out.writes_type_slot, 0)

    def test_type_gate_prefix_accepts_known_tag_and_writes_slot(self) -> None:
        out = self.model_5a340c(Inputs5a340c(0, 0x10000, 0, 0))

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.accepted_tag, 1)
        self.assertEqual(out.unsupported_tag_error, 0)
        self.assertEqual(out.writes_type_slot, 1)
        self.assertEqual(out.type_slot_value, 0x10004)

    def test_type_gate_prefix_records_special_tag_recursive_boundary(self) -> None:
        out = self.model_5a340c(Inputs5a340c(0, 0x10004, 1, 0x22))

        self.assertEqual(out.r0, 0x22)
        self.assertEqual(out.special_tag_path_entered, 1)
        self.assertEqual(out.recursive_call_target, 0x005A2E00)
        self.assertEqual(out.writes_type_slot, 0)

    def test_table_alloc_prefix_returns_precheck_error(self) -> None:
        out = self.model_5a34ca(Inputs5a34ca(5, 3, 3, 0, 0x2000A000, 0))

        self.assertEqual(out.r0, 5)
        self.assertEqual(out.precheck_call_target, 0x005A6D10)
        self.assertEqual(out.elements_written, 0)

    def test_table_alloc_prefix_rejects_zero_count(self) -> None:
        out = self.model_5a34ca(Inputs5a34ca(0, 0, 3, 0, 0x2000A000, 0))

        self.assertEqual(out.r0, 8)
        self.assertEqual(out.count_zero_error, 1)
        self.assertEqual(out.allocation_stored_at_offset_0x90, 0)

    def test_table_alloc_prefix_rejects_count_past_capacity(self) -> None:
        out = self.model_5a34ca(Inputs5a34ca(0, 4, 3, 0, 0x2000A000, 0))

        self.assertEqual(out.r0, 0x0A)
        self.assertEqual(out.count_capacity_error, 1)
        self.assertEqual(out.elements_written, 0)

    def test_table_alloc_prefix_writes_allocated_elements(self) -> None:
        out = self.model_5a34ca(Inputs5a34ca(0, 3, 3, 0, 0x2000A000, 0))

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.allocate_call_target, 0x004EDCF2)
        self.assertEqual(out.allocate_call_r1, 4)
        self.assertEqual(out.allocation_stored_at_offset_0x90, 0x2000A000)
        self.assertEqual(out.element_decode_call_target, 0x005A2E00)
        self.assertEqual(out.elements_written, 3)
        self.assertEqual(out.close_call_target, 0x005A2EAE)

    def test_state_prefix_returns_missing_vtable_error(self) -> None:
        out = self.model_5a35a4(Inputs5a35a4(0, 0, 0, 0, 3, 0, 0))

        self.assertEqual(out.r0, 0x0B)
        self.assertEqual(out.vtable_lookup_performed, 1)
        self.assertEqual(out.vtable_lookup_call_target, 0x004EBE6E)
        self.assertEqual(out.cached_vtable_stored, 0)

    def test_state_prefix_returns_parser_delegate_error(self) -> None:
        out = self.model_5a35a4(Inputs5a35a4(1, 0, 9, 0, 3, 0, 0))

        self.assertEqual(out.r0, 9)
        self.assertEqual(out.vtable_lookup_performed, 0)
        self.assertEqual(out.parser_delegate_call_target, 0x005A338C)
        self.assertEqual(out.callback58_performed, 0)

    def test_state_prefix_rejects_positive_index_out_of_bounds(self) -> None:
        out = self.model_5a35a4(Inputs5a35a4(1, 0, 0, 5, 3, 0, 0))

        self.assertEqual(out.r0, 6)
        self.assertEqual(out.normalized_index, 5)
        self.assertEqual(out.negative_index, 0)
        self.assertEqual(out.bounds_error, 1)

    def test_state_prefix_accepts_negative_index_and_records_callback(self) -> None:
        out = self.model_5a35a4(Inputs5a35a4(1, 0, 0, -2, 3, 0, 0x44))

        self.assertEqual(out.r0, 0x44)
        self.assertEqual(out.normalized_index, 1)
        self.assertEqual(out.negative_index, 1)
        self.assertEqual(out.table_lookup_call_target, 0x005A2C00)
        self.assertEqual(out.callback58_performed, 1)
        self.assertEqual(out.callback58_is_indirect_boundary, 1)

    def test_record_header_prefix_zeroes_fields_on_parser_failure(self) -> None:
        out = self.model_5a36ac(
            Inputs5a36ac(7, 0x14, 0, 0x10000, 0x14, 3, 16)
        )

        self.assertEqual(out.parser_call_target, 0x005A338C)
        self.assertEqual(out.parser_call_r2_is_source, 1)
        self.assertEqual(out.parse_failed_zeroes_fields, 1)
        self.assertEqual(out.scalar_reads_attempted, 0)

    def test_record_header_prefix_rejects_short_parser_length(self) -> None:
        out = self.model_5a36ac(
            Inputs5a36ac(0, 0x13, 0, 0x10000, 0x14, 3, 16)
        )

        self.assertEqual(out.parsed_length_ok, 0)
        self.assertEqual(out.parse_failed_zeroes_fields, 1)
        self.assertEqual(out.structure_accepted, 0)

    def test_record_header_prefix_rejects_mismatched_payload_length(self) -> None:
        out = self.model_5a36ac(
            Inputs5a36ac(0, 0x14, 0, 0x10000, 0x14, 3, 20)
        )

        self.assertEqual(out.scalar_reads_attempted, 6)
        self.assertEqual(out.tag_ok, 1)
        self.assertEqual(out.field_size_ok, 1)
        self.assertEqual(out.count_ok, 1)
        self.assertEqual(out.payload_length_ok, 0)
        self.assertEqual(out.structure_accepted, 0)

    def test_record_header_prefix_accepts_valid_structure(self) -> None:
        out = self.model_5a36ac(
            Inputs5a36ac(0, 0x14, 0, 0x10000, 0x14, 3, 16)
        )

        self.assertEqual(out.parsed_length_ok, 1)
        self.assertEqual(out.parse_failed_zeroes_fields, 0)
        self.assertEqual(out.tag_ok, 1)
        self.assertEqual(out.field_size_ok, 1)
        self.assertEqual(out.count_ok, 1)
        self.assertEqual(out.payload_length_ok, 1)
        self.assertEqual(out.structure_accepted, 1)

    def test_grid_copy_prefix_skips_when_clean_and_bounded(self) -> None:
        out = self.model_5a3798(
            Inputs5a3798(0, 0x20, 0x40, 3, 2, 8, 0, 0, 0, 0)
        )

        self.assertEqual(out.dirty_bit_set, 0)
        self.assertEqual(out.allocation_attempts, 0)
        self.assertEqual(out.cleanup_calls, 0)

    def test_grid_copy_prefix_records_allocation_failure_cleanup(self) -> None:
        out = self.model_5a3798(
            Inputs5a3798(0, 0x80, 0x40, 3, 2, 8, 1, 0, 0, 0)
        )

        self.assertEqual(out.dirty_bit_set, 1)
        self.assertEqual(out.allocation_attempts, 2)
        self.assertEqual(out.first_alloc_call_target, 0x004ED9D0)
        self.assertEqual(out.allocations_failed, 1)
        self.assertEqual(out.cleanup_calls, 2)

    def test_grid_copy_prefix_stops_after_row_copy_error(self) -> None:
        out = self.model_5a3798(
            Inputs5a3798(1, 0x20, 0x40, 3, 2, 8, 0, 0, 5, 0)
        )

        self.assertEqual(out.row_copy_call_target, 0x004ED1BE)
        self.assertEqual(out.row_copy_attempts, 3)
        self.assertEqual(out.compare_attempts, 0)
        self.assertEqual(out.cleanup_calls, 2)

    def test_grid_copy_prefix_increments_dimension_after_compare_exhaustion(self) -> None:
        out = self.model_5a3798(
            Inputs5a3798(1, 0x20, 0x40, 3, 2, 8, 0, 0, 0, 2)
        )

        self.assertEqual(out.row_copy_attempts, 3)
        self.assertEqual(out.compare_call_target, 0x004ED1BE)
        self.assertEqual(out.compare_attempts, 2)
        self.assertEqual(out.dimension_incremented, 1)
        self.assertEqual(out.cleanup_calls, 2)

    def test_mode_pair_prefix_rejects_out_of_range_bound(self) -> None:
        out = self.model_5a3ab0(Inputs5a3ab0(0x4001, 0, 0, 0, 0, 0, 0, 0))

        self.assertEqual(out.r0, 8)
        self.assertEqual(out.bound_error, 1)
        self.assertEqual(out.setup_callback_count, 0)
        self.assertEqual(out.exits_prefix, 1)

    def test_mode_pair_prefix_clears_status_for_fallback_chain(self) -> None:
        out = self.model_5a3ab0(Inputs5a3ab0(0x20, 0, 0, 0x8E, 1, 0, 0, 0))

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.setup_callback_count, 4)
        self.assertEqual(out.mode0_entered, 1)
        self.assertEqual(out.status_0xfa_cleared, 1)
        self.assertEqual(out.mode1_entered, 1)

    def test_mode_pair_prefix_context_magic_short_circuits_primary_8e(self) -> None:
        out = self.model_5a3ab0(Inputs5a3ab0(0x20, 0, 0x8E, 0, 0, 1, 0, 0))

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.status_0xfa_cleared, 0)
        self.assertEqual(out.mode1_entered, 1)

    def test_mode_pair_prefix_sets_mode1_success_flag(self) -> None:
        out = self.model_5a3ab0(Inputs5a3ab0(0x20, 0, 0, 0, 0, 0, 0, 0))

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.mode0_primary_call_target, 0x1C)
        self.assertEqual(out.mode0_secondary_call_target, 0x5C)
        self.assertEqual(out.mode1_primary_call_target, 0x1C)
        self.assertEqual(out.mode1_secondary_call_target, 0x5C)
        self.assertEqual(out.flag_0x124_set, 1)

    def test_status_8e_continuation_bypasses_other_statuses(self) -> None:
        out = self.model_5a3bcc(Inputs5a3bcc(0x22, 0, 0, 0, 0, 0, 0, 0, 0))

        self.assertEqual(out.r0, 0x22)
        self.assertEqual(out.enters_prefix, 0)
        self.assertEqual(out.exits_prefix, 1)
        self.assertEqual(out.fixed_callback_count, 0)

    def test_status_8e_continuation_uses_fallback_parser_when_gate_unset(self) -> None:
        out = self.model_5a3bcc(Inputs5a3bcc(0x8E, 1, 1, 0x44, 1, 0, 0, 0, 0))

        self.assertEqual(out.enters_prefix, 1)
        self.assertEqual(out.callback28_performed, 1)
        self.assertEqual(out.status_0x174_forced_unset, 1)
        self.assertEqual(out.optional_callback60_performed, 1)
        self.assertEqual(out.fixed_callback_count, 3)
        self.assertEqual(out.slot_0x10_loaded_from_0x108, 1)
        self.assertEqual(out.slot_0x14_cleared, 1)
        self.assertEqual(out.slot_0x18_cleared, 1)
        self.assertEqual(out.parser_call_count, 1)
        self.assertEqual(out.first_parser_id, 0x15)

    def test_status_8e_continuation_records_full_parser_sequence(self) -> None:
        out = self.model_5a3bcc(Inputs5a3bcc(0x8E, 0, 0, 0, 0, 1, 0, 0, 0))

        self.assertEqual(out.parser_call_count, 3)
        self.assertEqual(out.first_parser_id, 0x10)
        self.assertEqual(out.second_parser_id, 1)
        self.assertEqual(out.third_parser_id, 0x11)
        self.assertEqual(out.exits_prefix, 0)

    def test_status_8e_continuation_exits_on_parser_status(self) -> None:
        out = self.model_5a3bcc(Inputs5a3bcc(0x8E, 0, 0, 0, 0, 1, 0, 0, 5))

        self.assertEqual(out.r0, 5)
        self.assertEqual(out.parser_call_count, 1)
        self.assertEqual(out.first_parser_id, 0x10)
        self.assertEqual(out.exits_prefix, 1)

    def test_flag_prefix_bypasses_nonzero_status(self) -> None:
        out = self.model_5a3cc6(
            Inputs5a3cc6(3, 0, 0, 0, 0, 0, 0x80, 2, 1, 0, 1, 1, 1, 1, 1)
        )

        self.assertEqual(out.r0, 3)
        self.assertEqual(out.enters_prefix, 0)
        self.assertEqual(out.parser_call_count, 0)
        self.assertEqual(out.flags_stored, 0)

    def test_flag_prefix_exits_on_first_parser_status(self) -> None:
        out = self.model_5a3cc6(
            Inputs5a3cc6(0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0)
        )

        self.assertEqual(out.r0, 7)
        self.assertEqual(out.parser_call_count, 1)
        self.assertEqual(out.first_parser_id, 0x10)
        self.assertEqual(out.exits_prefix, 1)

    def test_flag_prefix_records_parser_fallbacks_for_empty_slots(self) -> None:
        out = self.model_5a3cc6(
            Inputs5a3cc6(0, 0, 1, 0, 1, 0, 0, 0, 0, 0x30000, 0, 0, 0, 0, 0)
        )

        self.assertEqual(out.parser_call_count, 3)
        self.assertEqual(out.first_parser_id, 1)
        self.assertEqual(out.second_parser_id, 0x16)
        self.assertEqual(out.flags_stored, 1)
        self.assertEqual(out.composed_flags, 0x18)

    def test_flag_prefix_composes_visible_status_bits(self) -> None:
        out = self.model_5a3cc6(
            Inputs5a3cc6(0, 1, 0, 1, 0, 0, 0x80, 2, 1, 0x100, 1, 1, 1, 1, 1)
        )

        self.assertEqual(out.parser_call_count, 1)
        self.assertEqual(out.first_parser_id, 0x16)
        self.assertEqual(out.feature_probe_count, 3)
        self.assertEqual(
            out.composed_flags,
            0x80 | 0x18 | 0x4000 | 0x1 | 0x4 | 0x20 | 0x40 | 0x100,
        )

    def test_flag_merge_prefix_maps_0x1b4_bits(self) -> None:
        out = self.model_5a3e24(Inputs5a3e24(0x80, 0x10, 0, 0x21, 0, 3))

        self.assertEqual(out.source_byte_offset, 0x1B4)
        self.assertEqual(out.low_bit_from_source, 1)
        self.assertEqual(out.high_bit_from_source, 1)
        self.assertEqual(out.merged_flags, 0x80 | 0x10 | 0x1 | 0x2)
        self.assertEqual(out.output_flags_stored, 1)
        self.assertEqual(out.post_merge_call_target, 0x005A6CB2)
        self.assertEqual(out.table_loop_entered, 1)
        self.assertEqual(out.table_iterations_planned, 3)

    def test_flag_merge_prefix_maps_alternate_0xcc_bits(self) -> None:
        out = self.model_5a3e24(Inputs5a3e24(0, 0, 1, 0, 0x03, 0))

        self.assertEqual(out.source_byte_offset, 0xCC)
        self.assertEqual(out.low_bit_from_source, 1)
        self.assertEqual(out.high_bit_from_source, 1)
        self.assertEqual(out.merged_flags, 0x3)
        self.assertEqual(out.table_loop_entered, 0)

    def test_allocation_prefix_continues_loop_before_allocation(self) -> None:
        out = self.model_5a3fe8(
            Inputs5a3fe8(1, 1, 3, 0, 0x2000A000, 1, 0, 0, 1, 1, 2, 3, 4, 5, 7, 2, 9)
        )

        self.assertEqual(out.loop_continues, 1)
        self.assertEqual(out.allocator_call_target, 0x004ED1D4)
        self.assertEqual(out.allocation_result_stored, 0)

    def test_allocation_prefix_returns_allocator_error(self) -> None:
        out = self.model_5a3fe8(
            Inputs5a3fe8(0, 2, 3, 6, 0x2000A000, 1, 0, 0, 1, 1, 2, 3, 4, 5, 7, 2, 9)
        )

        self.assertEqual(out.r0, 6)
        self.assertEqual(out.allocation_status_error, 1)
        self.assertEqual(out.status_flags, 0)

    def test_allocation_prefix_sets_pointer_status_bits(self) -> None:
        out = self.model_5a3fe8(
            Inputs5a3fe8(0, 2, 3, 0, 0x2000A000, 1, 0, 0, 0, 1, 2, 3, 4, 5, 7, 2, 9)
        )

        self.assertEqual(out.allocation_result_stored, 0x2000A000)
        self.assertEqual(out.pointer_0x1c_stored, 1)
        self.assertEqual(out.status_flags, 0x2)
        self.assertEqual(out.geometry_copied, 0)

    def test_allocation_prefix_defaults_bit0_and_copies_geometry(self) -> None:
        out = self.model_5a3fe8(
            Inputs5a3fe8(0, 2, 3, 0, 0, 0, 0, 0, 1, -1, -2, 3, 4, 5, 7, 2, 9)
        )

        self.assertEqual(out.status_flags, 0x1)
        self.assertEqual(out.geometry_copied, 1)
        self.assertEqual(out.copied_c4, -1)
        self.assertEqual(out.copied_c6, -2)
        self.assertEqual(out.copied_c8, 3)
        self.assertEqual(out.copied_ca, 4)
        self.assertEqual(out.copied_b2, 5)
        self.assertEqual(out.copied_dc, 7)
        self.assertEqual(out.copied_de, 2)
        self.assertEqual(out.derived_4a, 14)

    def test_geometry_4a_prefix_uses_existing_halfwords(self) -> None:
        out = self.model_5a40ca(Inputs5a40ca(0, 9, 4, 0x20, 0, 0))

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.writes_46, 0)
        self.assertEqual(out.writes_48, 0)
        self.assertEqual(out.copied_46, 9)
        self.assertEqual(out.copied_48, 4)
        self.assertEqual(out.derived_4a, 0x25)

    def test_geometry_4a_prefix_refreshes_from_alternate_signed_source(self) -> None:
        out = self.model_5a40ca(Inputs5a40ca(1, 0, 0, 0x10, -2, 3))

        self.assertEqual(out.writes_46, 1)
        self.assertEqual(out.writes_48, 1)
        self.assertEqual(out.copied_46, 0xFFFE)
        self.assertEqual(out.copied_48, 0xFFFD)
        self.assertEqual(out.derived_4a, 0x11)

    def test_record_scan_prefix_selects_first_nonzero_delta_pair(self) -> None:
        out = self.model_5a490c(
            Inputs5a490c(5, 2, 2, 0x20, 0x100, 0x1234, 3, 0, 7)
        )

        self.assertEqual(out.normalized_cursor, 3)
        self.assertEqual(out.next_max_index, 5)
        self.assertEqual(out.scan_base_offset, 0x26)
        self.assertEqual(out.accumulated_offset, 0x126)
        self.assertEqual(out.scanned_pairs, 2)
        self.assertEqual(out.selected_index, 0x1202)
        self.assertEqual(out.selected_value, 7)
        self.assertEqual(out.branch_to_record_match, 1)
        self.assertEqual(out.branch_to_outer_loop, 0)

    def test_record_scan_prefix_advances_outer_loop_when_no_pair_matches(self) -> None:
        out = self.model_5a490c(
            Inputs5a490c(1, 4, 2, 0x10, 0, 0xFF, 0xFFFF, 0, 1)
        )

        self.assertEqual(out.normalized_cursor, 0)
        self.assertEqual(out.next_max_index, 4)
        self.assertEqual(out.scanned_pairs, 2)
        self.assertEqual(out.selected_value, 0)
        self.assertEqual(out.branch_to_record_match, 0)
        self.assertEqual(out.branch_to_outer_loop, 1)
        self.assertEqual(out.high_cursor, 2)

    def test_binary_search_prefix_computes_midpoint_record(self) -> None:
        out = self.model_5a65b0(Inputs5a65b0(0x2000A000, 8, 2, 6))

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.decoded_entry_count, 8)
        self.assertEqual(out.search_active, 1)
        self.assertEqual(out.midpoint_index, 4)
        self.assertEqual(out.midpoint_record_offset, 0x2000A014)
        self.assertEqual(out.next_compare_prefix_entered, 1)

    def test_binary_search_prefix_empty_window_skips_compare(self) -> None:
        out = self.model_5a65b0(Inputs5a65b0(0x2000A000, 8, 8, 0))

        self.assertEqual(out.decoded_entry_count, 8)
        self.assertEqual(out.search_active, 0)
        self.assertEqual(out.midpoint_index, 8)
        self.assertEqual(out.next_compare_prefix_entered, 0)

    def test_marker_gate_records_table_scan_markers(self) -> None:
        out = self.model_5a3980(Inputs5a3980(3, 1, 0, 0, 0, 0, 0))

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.marker_scan_performed, 1)
        self.assertEqual(out.first_marker_found, 1)
        self.assertEqual(out.second_marker_found, 0)
        self.assertEqual(out.predicate_call_target, 0x005A7178)
        self.assertEqual(out.predicate_calls_performed, 3)
        self.assertEqual(out.gate_enabled, 0)

    def test_marker_gate_context_flag_short_circuits_predicates(self) -> None:
        out = self.model_5a3980(Inputs5a3980(3, 1, 1, 1, 0, 0, 0))

        self.assertEqual(out.predicate_calls_performed, 0)
        self.assertEqual(out.gate_enabled, 1)

    def test_marker_gate_predicate_success_enables_gate(self) -> None:
        out = self.model_5a3980(Inputs5a3980(3, 0, 0, 0, 0, 1, 0))

        self.assertEqual(out.predicate_calls_performed, 2)
        self.assertEqual(out.gate_enabled, 1)

    def test_callback_gate_optional_success_skips_fallback_on_parser_miss(self) -> None:
        out = self.model_5a3a10(
            Inputs5a3a10(1, 0, 0x005A9000, 0, 0x005A9010, 0x55)
        )

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.parser_success_flag, 0)
        self.assertEqual(out.optional_callback_performed, 1)
        self.assertEqual(out.optional_success_flag, 1)
        self.assertEqual(out.fallback_callback_performed, 0)
        self.assertEqual(out.fallback_return, 0)

    def test_callback_gate_parser_success_forces_fallback(self) -> None:
        out = self.model_5a3a10(
            Inputs5a3a10(0, 0, 0x005A9000, 0, 0x005A9010, 0x77)
        )

        self.assertEqual(out.parser_success_flag, 1)
        self.assertEqual(out.optional_callback_performed, 1)
        self.assertEqual(out.optional_success_flag, 1)
        self.assertEqual(out.fallback_callback_performed, 1)
        self.assertEqual(out.fallback_return, 0x77)
        self.assertEqual(out.r0, 0x77)

    def test_callback_gate_marker_gate_suppresses_optional_callback(self) -> None:
        out = self.model_5a3a10(
            Inputs5a3a10(1, 1, 0x005A9000, 0, 0x005A9010, 0x88)
        )

        self.assertEqual(out.parser_success_flag, 0)
        self.assertEqual(out.optional_callback_performed, 0)
        self.assertEqual(out.optional_success_flag, 0)
        self.assertEqual(out.fallback_callback_performed, 1)
        self.assertEqual(out.fallback_return, 0x88)
        self.assertEqual(out.r0, 0x88)

    def test_zero_return_leaf_returns_zero(self) -> None:
        out = self.model_5a6596()

        self.assertEqual(out.r0, 0)

    def test_zero_status_leaf_clears_status_word(self) -> None:
        out = self.model_5a659a()

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.writes_status_word, 1)
        self.assertEqual(out.status_word_value, 0)

    def test_error_status_leaf_writes_code_and_minus_one(self) -> None:
        out = self.model_5a65a2()

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.writes_status_word, 1)
        self.assertEqual(out.status_word_value, 0xFFFFFFFF)
        self.assertEqual(out.writes_status_code, 1)
        self.assertEqual(out.status_code_value, 0x0E)

    def test_state_tail_table_lookup_returns_biased_selected_value(self) -> None:
        out = self.model_5a4802(
            Inputs5a4802(0x24, 0x2000A000, 0x20, 8, -3, 0x10, 9)
        )

        self.assertEqual(out.r0, 6)
        self.assertEqual(out.parser_call_target, 0x005A47B0)
        self.assertEqual(out.parser_call_r1, 0x24)
        self.assertEqual(out.selector_delta, 4)
        self.assertEqual(out.range_check_passed, 1)
        self.assertEqual(out.table_lookup_performed, 1)

    def test_state_tail_table_lookup_fails_closed_to_zero(self) -> None:
        cases = [
            Inputs5a4802(0x24, 0, 0x20, 8, -3, 0x10, 9),
            Inputs5a4802(0x10, 0x2000A000, 0x20, 8, -3, 0x10, 9),
            Inputs5a4802(0x24, 0x2000A000, 0x20, 8, -3, 0, 9),
            Inputs5a4802(0x24, 0x2000A000, 0x20, 8, -3, 0x10, 0),
        ]
        for index, inputs in enumerate(cases):
            with self.subTest(index=index):
                out = self.model_5a4802(inputs)

                self.assertEqual(out.r0, 0)
                self.assertEqual(out.parser_call_target, 0x005A47B0)

    def test_selector_record_prefix_decodes_parser_record_fields(self) -> None:
        out = self.model_5a487a(
            Inputs5a487a(0x20, 0x2000A000, 0x2000B000, 0x1234, 0x5678,
                         -2)
        )

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.parser_call_target, 0x005A47B0)
        self.assertEqual(out.parser_call_r0, 0x2000A000)
        self.assertEqual(out.parser_call_r1, 0x21)
        self.assertEqual(out.decoded_field0, 0x1234)
        self.assertEqual(out.decoded_field1, 0x5678)
        self.assertEqual(out.decoded_signed_field2, -2)
        self.assertEqual(out.decoded_prefix_entered, 1)

    def test_selector_record_prefix_skips_decode_on_parser_miss(self) -> None:
        out = self.model_5a487a(
            Inputs5a487a(0xFFFF, 0x2000A000, 0, 0x1234, 0x5678, -2)
        )

        self.assertEqual(out.parser_call_target, 0x005A47B0)
        self.assertEqual(out.parser_call_r1, 0x10000)
        self.assertEqual(out.decoded_prefix_entered, 0)

    def test_large_state_tail_table_hit_updates_result_slots(self) -> None:
        out = self.model_5a4a66(
            Inputs5a4a66(4, 8, 12, -3, 0x2000A000, 0x2000A008, 0x80,
                         11, -1)
        )

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.next_index, 8)
        self.assertEqual(out.result_value, 8)
        self.assertEqual(out.prior_entry_call_target, 0x005A49BC)
        self.assertEqual(out.prior_entry_performed, 0)
        self.assertEqual(out.table_lookup_performed, 1)
        self.assertEqual(out.computed_range_performed, 0)

    def test_large_state_tail_computed_range_hit_without_table(self) -> None:
        out = self.model_5a4a66(
            Inputs5a4a66(9, 8, 12, 4, 0, 0, 20, 0, -1)
        )

        self.assertEqual(out.next_index, 10)
        self.assertEqual(out.result_value, 14)
        self.assertEqual(out.prior_entry_performed, 0)
        self.assertEqual(out.table_lookup_performed, 0)
        self.assertEqual(out.computed_range_performed, 1)

    def test_large_state_tail_falls_back_to_prior_entry_boundary(self) -> None:
        out = self.model_5a4a66(
            Inputs5a4a66(12, 8, 12, -3, 0x2000A000, 0x20009FFE, 0x80,
                         0, 0)
        )

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.next_index, 8)
        self.assertEqual(out.result_value, 0)
        self.assertEqual(out.prior_entry_call_target, 0x005A49BC)
        self.assertEqual(out.prior_entry_call_r1, 13)
        self.assertEqual(out.prior_entry_performed, 1)
        self.assertEqual(out.table_lookup_performed, 0)
        self.assertEqual(out.computed_range_performed, 0)

    def test_record_table_prefix_accepts_consistent_mode2_split(self) -> None:
        out = self.model_5a4b36(
            Inputs5a4b36(0x100, 0x160, 2, 0x60, 8, 4, 4, 1)
        )

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.error_call_target, 0x004ECFA4)
        self.assertEqual(out.error_call_r1, 8)
        self.assertEqual(out.error_call_count, 0)
        self.assertEqual(out.effective_payload_length, 0x60)
        self.assertEqual(out.entry_count, 4)
        self.assertEqual(out.table0_offset, 0x10E)
        self.assertEqual(out.table1_offset, 0x118)
        self.assertEqual(out.table2_offset, 0x120)
        self.assertEqual(out.table3_offset, 0x128)
        self.assertEqual(out.loop_prefix_entered, 1)

    def test_record_table_prefix_clamps_length_and_counts_errors(self) -> None:
        out = self.model_5a4b36(
            Inputs5a4b36(0x100, 0x118, 2, 0x60, 9, 4, 4, 2)
        )

        self.assertEqual(out.effective_payload_length, 0x18)
        self.assertGreaterEqual(out.error_call_count, 3)
        self.assertEqual(out.entry_count, 4)
        self.assertEqual(out.loop_prefix_entered, 1)

    def test_multi_delegate_tail_parser_failure_returns_zero(self) -> None:
        out = self.model_5a66cc(
            Inputs5a66cc(0x2000A000, 0x2000B000, 0x2000C000, 7, 0, 4, 8, 1,
                         0x005A9000, 0x11111111, 0x22222222)
        )

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.pair_parser_call_target, 0x005A6672)
        self.assertEqual(out.first_parser_call_target, 0x005A65B0)
        self.assertEqual(out.fallback_parser_call_target, 0x005A660E)
        self.assertEqual(out.callback_performed, 0)
        self.assertEqual(out.fallback_performed, 0)

    def test_multi_delegate_tail_uses_first_offset_callback_path(self) -> None:
        out = self.model_5a66cc(
            Inputs5a66cc(0x2000A000, 0x2000B000, 0x2000C000, 7, 0x2000D000,
                         4, 8, 1, 0x005A9000, 0x11111111, 0x22222222)
        )

        self.assertEqual(out.r0, 0x11111111)
        self.assertEqual(out.selected_offset, 4)
        self.assertEqual(out.callback_target, 0x005A9000)
        self.assertEqual(out.callback_performed, 1)
        self.assertEqual(out.fallback_performed, 0)

    def test_multi_delegate_tail_uses_second_offset_fallback_path(self) -> None:
        out = self.model_5a66cc(
            Inputs5a66cc(0x2000A000, 0x2000B000, 0x2000C000, 7, 0x2000D000,
                         4, 8, 0, 0x005A9000, 0x11111111, 0x22222222)
        )

        self.assertEqual(out.r0, 0x22222222)
        self.assertEqual(out.selected_offset, 8)
        self.assertEqual(out.callback_performed, 0)
        self.assertEqual(out.fallback_performed, 1)

    def test_multi_delegate_status_tail_parser_failure_returns_minus_one(self) -> None:
        out = self.model_5a674a(
            Inputs5a674a(0x2000A000, 0x2000C000, 7, 0, 4, 8, 1, 1)
        )

        self.assertEqual(out.r0, -1)
        self.assertEqual(out.pair_parser_call_target, 0x005A6672)
        self.assertEqual(out.first_parser_call_target, 0x005A65B0)
        self.assertEqual(out.fallback_parser_call_target, 0x005A660E)
        self.assertEqual(out.first_path_checked, 0)
        self.assertEqual(out.fallback_checked, 0)

    def test_multi_delegate_status_tail_first_path_returns_one(self) -> None:
        out = self.model_5a674a(
            Inputs5a674a(0x2000A000, 0x2000C000, 7, 0x2000D000, 4, 8, 1, 0)
        )

        self.assertEqual(out.r0, 1)
        self.assertEqual(out.selected_offset, 4)
        self.assertEqual(out.first_path_checked, 1)
        self.assertEqual(out.fallback_checked, 0)

    def test_multi_delegate_status_tail_fallback_returns_zero(self) -> None:
        out = self.model_5a674a(
            Inputs5a674a(0x2000A000, 0x2000C000, 7, 0x2000D000, 4, 8, 0, 1)
        )

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.selected_offset, 8)
        self.assertEqual(out.first_path_checked, 1)
        self.assertEqual(out.fallback_checked, 1)

    def test_multi_delegate_status_tail_full_failure_returns_minus_one(self) -> None:
        out = self.model_5a674a(
            Inputs5a674a(0x2000A000, 0x2000C000, 7, 0x2000D000, 4, 8, 0, 0)
        )

        self.assertEqual(out.r0, -1)
        self.assertEqual(out.selected_offset, 8)
        self.assertEqual(out.first_path_checked, 1)
        self.assertEqual(out.fallback_checked, 1)


if __name__ == "__main__":
    unittest.main()
