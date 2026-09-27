import ctypes
import math
import subprocess
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SOURCE = (
    ROOT /
    "components/apollo_main/core_overlay/runtime_liblc3_am142_semantic_model.c"
)


class Inputs(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_int32),
        ("r1", ctypes.c_int32),
        ("s2", ctypes.c_float),
        ("s3", ctypes.c_float),
        ("s4", ctypes.c_float),
        ("s16", ctypes.c_float),
        ("delta_words", ctypes.c_uint32 * 3),
        ("coefficients", ctypes.c_float * 3),
    ]


class Outputs(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_int32),
        ("r2", ctypes.c_int32),
        ("r4", ctypes.c_int32),
        ("s4", ctypes.c_float),
        ("s5", ctypes.c_float),
        ("s6", ctypes.c_float),
        ("s7", ctypes.c_float),
        ("s16", ctypes.c_float),
        ("stack_zero_words", ctypes.c_uint32 * 3),
        ("branch_to_0x0059a45c", ctypes.c_int),
    ]


class Inputs59aa84(ctypes.Structure):
    _fields_ = [
        ("context_0x1c", ctypes.c_uint32),
    ]


class Outputs59aa84(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("call_target", ctypes.c_uint32),
        ("call_r0", ctypes.c_uint32),
        ("cleared_byte_offset", ctypes.c_uint32),
        ("cleared_byte_value", ctypes.c_uint32),
    ]


class Inputs59af42(ctypes.Structure):
    _fields_ = [
        ("context_0x1c", ctypes.c_uint32),
        ("stacked_r4", ctypes.c_uint32),
    ]


class Outputs59af42(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("r4", ctypes.c_uint32),
        ("call_target", ctypes.c_uint32),
        ("call_r0", ctypes.c_uint32),
        ("cleared_byte_offset", ctypes.c_uint32),
        ("cleared_byte_value", ctypes.c_uint32),
        ("return_restored_r4_from_stack", ctypes.c_uint32),
    ]


class Inputs59af54(ctypes.Structure):
    _fields_ = [
        ("object", ctypes.c_uint32),
        ("context_0x1c", ctypes.c_uint32),
        ("context_flag_0x2c", ctypes.c_uint32),
        ("slot_0x18_current", ctypes.c_uint32),
        ("arg_field_0x00", ctypes.c_uint32),
        ("arg_field_0x04", ctypes.c_uint32),
        ("arg_field_0x08", ctypes.c_uint32),
        ("arg_field_0x0c", ctypes.c_uint32),
        ("first_call_return", ctypes.c_uint32),
        ("second_call_return", ctypes.c_uint32),
        ("stacked_r4", ctypes.c_uint32),
        ("stacked_r5", ctypes.c_uint32),
        ("stacked_r6", ctypes.c_uint32),
    ]


class Outputs59af54(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("r4", ctypes.c_uint32),
        ("r5", ctypes.c_uint32),
        ("r6", ctypes.c_uint32),
        ("first_call_performed", ctypes.c_uint32),
        ("first_call_target", ctypes.c_uint32),
        ("first_call_r0", ctypes.c_uint32),
        ("first_call_r1", ctypes.c_uint32),
        ("first_call_r2", ctypes.c_uint32),
        ("second_call_performed", ctypes.c_uint32),
        ("second_call_target", ctypes.c_uint32),
        ("second_call_r0", ctypes.c_uint32),
        ("second_call_r1", ctypes.c_uint32),
        ("second_call_r2", ctypes.c_uint32),
        ("slot_store_performed", ctypes.c_uint32),
        ("slot_store_value", ctypes.c_uint32),
        ("return_restored_registers_from_stack", ctypes.c_uint32),
    ]


class Inputs59afa0(ctypes.Structure):
    _fields_ = [
        ("object", ctypes.c_uint32),
        ("context_0x1c", ctypes.c_uint32),
        ("context_flag_0x2c", ctypes.c_uint32),
        ("slot_0x18_current", ctypes.c_uint32),
        ("arg_field_0x00", ctypes.c_uint32),
        ("arg_field_0x04", ctypes.c_uint32),
        ("arg_field_0x08", ctypes.c_uint32),
        ("arg_field_0x0c", ctypes.c_uint32),
        ("arg_field_0x10", ctypes.c_uint32),
        ("arg_field_0x14", ctypes.c_uint32),
        ("arg_field_0x18", ctypes.c_uint32),
        ("arg_field_0x1c", ctypes.c_uint32),
        ("first_call_return", ctypes.c_uint32),
        ("second_call_return", ctypes.c_uint32),
        ("stacked_r4", ctypes.c_uint32),
        ("stacked_r5", ctypes.c_uint32),
        ("stacked_r6", ctypes.c_uint32),
    ]


class Outputs59afa0(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("r4", ctypes.c_uint32),
        ("r5", ctypes.c_uint32),
        ("r6", ctypes.c_uint32),
        ("first_call_performed", ctypes.c_uint32),
        ("first_call_target", ctypes.c_uint32),
        ("first_call_r0", ctypes.c_uint32),
        ("first_call_r1", ctypes.c_uint32),
        ("first_call_r2", ctypes.c_uint32),
        ("second_call_performed", ctypes.c_uint32),
        ("second_call_target", ctypes.c_uint32),
        ("second_call_r0", ctypes.c_uint32),
        ("second_call_r1", ctypes.c_uint32),
        ("fallback_call_count", ctypes.c_uint32),
        ("fallback_call_target", ctypes.c_uint32),
        ("fallback0_r1", ctypes.c_uint32),
        ("fallback0_r2", ctypes.c_uint32),
        ("fallback0_r3", ctypes.c_uint32),
        ("fallback1_r1", ctypes.c_uint32),
        ("fallback1_r2", ctypes.c_uint32),
        ("fallback1_r3", ctypes.c_uint32),
        ("fallback2_r1", ctypes.c_uint32),
        ("fallback2_r2", ctypes.c_uint32),
        ("fallback2_r3", ctypes.c_uint32),
        ("slot_store_performed", ctypes.c_uint32),
        ("slot_store_value", ctypes.c_uint32),
        ("return_restored_registers_from_stack", ctypes.c_uint32),
    ]


class Inputs59aec8(ctypes.Structure):
    _fields_ = [
        ("object_field_0x00", ctypes.c_uint32),
        ("object_field_0x0c", ctypes.c_uint32),
        ("arg_r1", ctypes.c_uint32),
        ("helper_return", ctypes.c_uint32),
        ("stacked_r4", ctypes.c_uint32),
    ]


class Outputs59aec8(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("r4", ctypes.c_uint32),
        ("helper_call_performed", ctypes.c_uint32),
        ("helper_call_target", ctypes.c_uint32),
        ("helper_call_r0", ctypes.c_uint32),
        ("helper_call_r1", ctypes.c_uint32),
        ("initial_range_rejected", ctypes.c_uint32),
        ("arg_threshold_rejected", ctypes.c_uint32),
        ("helper_range_rejected", ctypes.c_uint32),
        ("return_restored_r4_from_stack", ctypes.c_uint32),
    ]


class Inputs59af1e(ctypes.Structure):
    _fields_ = [
        ("object", ctypes.c_uint32),
        ("object_word_0x00", ctypes.c_uint32),
        ("field_0x6c", ctypes.c_uint32),
        ("field_0x74", ctypes.c_uint32),
        ("stacked_r0", ctypes.c_uint32),
        ("stacked_r4", ctypes.c_uint32),
        ("stacked_r5", ctypes.c_uint32),
    ]


class Outputs59af1e(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("r4", ctypes.c_uint32),
        ("r5", ctypes.c_uint32),
        ("cleanup_performed", ctypes.c_uint32),
        ("first_call_target", ctypes.c_uint32),
        ("first_call_r0", ctypes.c_uint32),
        ("first_call_r1", ctypes.c_uint32),
        ("first_clear_offset", ctypes.c_uint32),
        ("first_clear_value", ctypes.c_uint32),
        ("second_call_target", ctypes.c_uint32),
        ("second_call_r0", ctypes.c_uint32),
        ("second_call_r1", ctypes.c_uint32),
        ("second_clear_offset", ctypes.c_uint32),
        ("second_clear_value", ctypes.c_uint32),
        ("return_restored_registers_from_stack", ctypes.c_uint32),
    ]


class Inputs59b00e(ctypes.Structure):
    _fields_ = [
        ("object", ctypes.c_uint32),
        ("arg_r1", ctypes.c_uint32),
        ("arg_r2", ctypes.c_uint32),
        ("runtime_call_return", ctypes.c_uint32),
        ("stacked_r0", ctypes.c_uint32),
        ("stacked_r4", ctypes.c_uint32),
        ("stacked_r5", ctypes.c_uint32),
        ("stacked_r6", ctypes.c_uint32),
        ("stacked_r7", ctypes.c_uint32),
    ]


class Outputs59b00e(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("r4", ctypes.c_uint32),
        ("r5", ctypes.c_uint32),
        ("r6", ctypes.c_uint32),
        ("r7", ctypes.c_uint32),
        ("runtime_call_target", ctypes.c_uint32),
        ("runtime_call_r0", ctypes.c_uint32),
        ("runtime_call_r1", ctypes.c_uint32),
        ("runtime_call_r2", ctypes.c_uint32),
        ("runtime_call_return", ctypes.c_uint32),
        ("store_arg_r1_offset", ctypes.c_uint32),
        ("store_arg_r1_value", ctypes.c_uint32),
        ("store_arg_r2_offset", ctypes.c_uint32),
        ("store_arg_r2_value", ctypes.c_uint32),
        ("literal0_offset", ctypes.c_uint32),
        ("literal0_value", ctypes.c_uint32),
        ("literal1_offset", ctypes.c_uint32),
        ("literal1_value", ctypes.c_uint32),
        ("literal2_offset", ctypes.c_uint32),
        ("literal2_value", ctypes.c_uint32),
        ("return_restored_registers_from_stack", ctypes.c_uint32),
    ]


class Inputs59b272(ctypes.Structure):
    _fields_ = [
        ("object", ctypes.c_uint32),
        ("arg_r2", ctypes.c_uint32),
        ("object_field_0x04", ctypes.c_uint32),
        ("dispatch_table_0x224", ctypes.c_uint32),
        ("callback_0x20", ctypes.c_uint32),
        ("callback_return", ctypes.c_uint32),
        ("stacked_r1", ctypes.c_uint32),
        ("stacked_r2", ctypes.c_uint32),
        ("stacked_r4", ctypes.c_uint32),
    ]


class Outputs59b272(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("r1", ctypes.c_uint32),
        ("r2", ctypes.c_uint32),
        ("r3", ctypes.c_uint32),
        ("r4", ctypes.c_uint32),
        ("table_load_base", ctypes.c_uint32),
        ("table_load_offset", ctypes.c_uint32),
        ("callback_load_base", ctypes.c_uint32),
        ("callback_load_offset", ctypes.c_uint32),
        ("stack_arg0_value", ctypes.c_uint32),
        ("callback_call_target", ctypes.c_uint32),
        ("callback_call_r0", ctypes.c_uint32),
        ("callback_call_r2", ctypes.c_uint32),
        ("callback_call_r3", ctypes.c_uint32),
        ("return_restored_registers_from_stack", ctypes.c_uint32),
    ]


class Inputs59b2aa(ctypes.Structure):
    _fields_ = [
        ("object", ctypes.c_uint32),
        ("nested_0x218", ctypes.c_uint32),
        ("nested_field_0x180", ctypes.c_uint32),
        ("nested_field_0x184", ctypes.c_uint32),
        ("nested_field_0x188", ctypes.c_uint32),
        ("call_return", ctypes.c_uint32),
        ("saved_r3", ctypes.c_uint32),
        ("saved_r4", ctypes.c_uint32),
        ("saved_r5", ctypes.c_uint32),
        ("saved_r6", ctypes.c_uint32),
        ("saved_r7", ctypes.c_uint32),
    ]


class Outputs59b2aa(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("r4", ctypes.c_uint32),
        ("r5", ctypes.c_uint32),
        ("r6", ctypes.c_uint32),
        ("r7", ctypes.c_uint32),
        ("helper_call_target", ctypes.c_uint32),
        ("helper_call_r0", ctypes.c_uint32),
        ("helper_call_r1", ctypes.c_uint32),
        ("store_arg_r1_value", ctypes.c_uint32),
        ("store_arg_r2_value", ctypes.c_uint32),
        ("store_arg_r3_value", ctypes.c_uint32),
        ("return_restored_registers_from_stack", ctypes.c_uint32),
    ]


class Inputs59b33e(ctypes.Structure):
    _fields_ = [
        ("object", ctypes.c_uint32),
        ("arg_r1", ctypes.c_uint32),
        ("arg_r2", ctypes.c_uint32),
        ("object_field_0x230", ctypes.c_uint32),
        ("object_field_0x238", ctypes.c_uint32),
        ("table_0x240", ctypes.c_uint32),
        ("table_word_index", ctypes.c_uint32),
        ("table_word_index_plus_1", ctypes.c_uint32),
        ("stacked_r1", ctypes.c_uint32),
        ("stacked_r4", ctypes.c_uint32),
        ("stacked_r5", ctypes.c_uint32),
        ("stacked_r6", ctypes.c_uint32),
        ("stacked_r7", ctypes.c_uint32),
    ]


class Outputs59b33e(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("r1", ctypes.c_uint32),
        ("r4", ctypes.c_uint32),
        ("r5", ctypes.c_uint32),
        ("r6", ctypes.c_uint32),
        ("r7", ctypes.c_uint32),
        ("init_call_target", ctypes.c_uint32),
        ("init_call_r0", ctypes.c_uint32),
        ("init_call_r1", ctypes.c_uint32),
        ("init_call_r2", ctypes.c_uint32),
        ("computed_index", ctypes.c_uint32),
        ("bounds_rejected", ctypes.c_uint32),
        ("store_arg_r2_0x04", ctypes.c_uint32),
        ("store_arg_r2_0x08", ctypes.c_uint32),
        ("store_arg_r2_0x0c", ctypes.c_uint32),
        ("return_restored_registers_from_stack", ctypes.c_uint32),
    ]


class Inputs59b382(ctypes.Structure):
    _fields_ = [
        ("object", ctypes.c_uint32),
        ("arg_r1", ctypes.c_uint32),
        ("arg_r2", ctypes.c_uint32),
        ("object_field_0x04", ctypes.c_uint32),
        ("object_field_0x214", ctypes.c_uint32),
        ("callback_0x250", ctypes.c_uint32),
        ("callback_context_0x34", ctypes.c_uint32),
        ("helper_return", ctypes.c_uint32),
        ("callback_return", ctypes.c_uint32),
        ("stack_word0", ctypes.c_uint32),
        ("stack_word1", ctypes.c_uint32),
        ("stacked_r1", ctypes.c_uint32),
        ("stacked_r2", ctypes.c_uint32),
        ("stacked_r3", ctypes.c_uint32),
        ("stacked_r4", ctypes.c_uint32),
        ("stacked_r5", ctypes.c_uint32),
        ("stacked_r6", ctypes.c_uint32),
        ("stacked_r7", ctypes.c_uint32),
    ]


class Outputs59b382(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("r1", ctypes.c_uint32),
        ("r2", ctypes.c_uint32),
        ("r3", ctypes.c_uint32),
        ("r4", ctypes.c_uint32),
        ("r5", ctypes.c_uint32),
        ("r6", ctypes.c_uint32),
        ("r7", ctypes.c_uint32),
        ("init_call_target", ctypes.c_uint32),
        ("init_call_r0", ctypes.c_uint32),
        ("init_call_r1", ctypes.c_uint32),
        ("init_call_r2", ctypes.c_uint32),
        ("helper_call_performed", ctypes.c_uint32),
        ("helper_call_target", ctypes.c_uint32),
        ("helper_call_r0", ctypes.c_uint32),
        ("helper_call_r1", ctypes.c_uint32),
        ("callback_call_performed", ctypes.c_uint32),
        ("callback_call_target", ctypes.c_uint32),
        ("callback_call_r0", ctypes.c_uint32),
        ("callback_call_r1", ctypes.c_uint32),
        ("callback_call_r2_is_stack_pair", ctypes.c_uint32),
        ("callback_call_r3_is_stack_word1", ctypes.c_uint32),
        ("store_arg_r2_0x04", ctypes.c_uint32),
        ("store_arg_r2_0x08", ctypes.c_uint32),
        ("store_arg_r2_0x0c", ctypes.c_uint32),
        ("return_restored_registers_from_stack", ctypes.c_uint32),
    ]


class Inputs59b3de(ctypes.Structure):
    _fields_ = [
        ("object", ctypes.c_uint32),
        ("arg_r1", ctypes.c_uint32),
        ("arg_r1_field_0x04", ctypes.c_uint32),
        ("arg_r1_field_0x08", ctypes.c_uint32),
        ("object_field_0x04", ctypes.c_uint32),
        ("callback_0x254", ctypes.c_uint32),
        ("callback_return", ctypes.c_uint32),
        ("stacked_r0", ctypes.c_uint32),
    ]


class Outputs59b3de(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("callback_call_target", ctypes.c_uint32),
        ("callback_call_r0", ctypes.c_uint32),
        ("callback_call_r1", ctypes.c_uint32),
        ("callback_call_r2", ctypes.c_uint32),
        ("callback_call_return", ctypes.c_uint32),
        ("callback_load_offset", ctypes.c_uint32),
        ("return_restored_from_stack", ctypes.c_uint32),
    ]


class Inputs59b454(ctypes.Structure):
    _fields_ = [
        ("object_field_0x04", ctypes.c_uint32),
        ("arg_r1_field_0x04", ctypes.c_uint32),
        ("arg_r1_field_0x08", ctypes.c_uint32),
        ("nested_0x80", ctypes.c_uint32),
        ("callback_context_0x34", ctypes.c_uint32),
        ("callback_receiver_0x04", ctypes.c_uint32),
        ("callback_slot_0x04", ctypes.c_uint32),
        ("callback_return", ctypes.c_uint32),
        ("stacked_r0", ctypes.c_uint32),
        ("stacked_r1", ctypes.c_uint32),
        ("stacked_r2", ctypes.c_uint32),
    ]


class Outputs59b454(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("r1", ctypes.c_uint32),
        ("r2", ctypes.c_uint32),
        ("stack_word0", ctypes.c_uint32),
        ("stack_word1", ctypes.c_uint32),
        ("callback_performed", ctypes.c_uint32),
        ("callback_call_target", ctypes.c_uint32),
        ("callback_call_r0", ctypes.c_uint32),
        ("callback_call_r1_is_stack_pair", ctypes.c_uint32),
        ("callback_call_return", ctypes.c_uint32),
        ("return_restored_registers_from_stack", ctypes.c_uint32),
    ]


class Inputs59c052(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("stacked_r0", ctypes.c_uint32),
    ]


class Outputs59c052(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("call_target", ctypes.c_uint32),
        ("call_r0", ctypes.c_uint32),
        ("call_offset", ctypes.c_uint32),
        ("return_restored_from_stack", ctypes.c_uint32),
    ]


class Inputs59b52c(ctypes.Structure):
    _fields_ = [
        ("object", ctypes.c_uint32),
        ("nested_0x1c", ctypes.c_uint32),
        ("nested_call_arg_0x0c", ctypes.c_uint32),
        ("stacked_r0", ctypes.c_uint32),
    ]


class Outputs59b52c(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("zero_store_offset", ctypes.c_uint32),
        ("zero_store_value", ctypes.c_uint32),
        ("call_target", ctypes.c_uint32),
        ("call_r0", ctypes.c_uint32),
        ("return_restored_from_stack", ctypes.c_uint32),
    ]


class Inputs59b53c(ctypes.Structure):
    _fields_ = [
        ("object", ctypes.c_uint32),
        ("nested_0x1c", ctypes.c_uint32),
        ("nested_field_0x0c", ctypes.c_uint32),
        ("first_call_return", ctypes.c_uint32),
        ("second_call_return", ctypes.c_uint32),
        ("stacked_r4", ctypes.c_uint32),
    ]


class Outputs59b53c(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("r4", ctypes.c_uint32),
        ("first_call_target", ctypes.c_uint32),
        ("first_call_r0", ctypes.c_uint32),
        ("first_call_return", ctypes.c_uint32),
        ("second_call_target", ctypes.c_uint32),
        ("second_call_r0", ctypes.c_uint32),
        ("return_restored_r4_from_stack", ctypes.c_uint32),
    ]


class Inputs59b654(ctypes.Structure):
    _fields_ = [
        ("object", ctypes.c_uint32),
        ("call_return", ctypes.c_uint32),
        ("stacked_r4", ctypes.c_uint32),
    ]


class Outputs59b654(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("r4", ctypes.c_uint32),
        ("call_target", ctypes.c_uint32),
        ("call_r0", ctypes.c_uint32),
        ("call_r1", ctypes.c_uint32),
        ("call_r2", ctypes.c_uint32),
        ("call_return", ctypes.c_uint32),
        ("return_restored_r4_from_stack", ctypes.c_uint32),
    ]


class Inputs59cb44(ctypes.Structure):
    _fields_ = [
        ("object", ctypes.c_uint32),
        ("object_word_0x00", ctypes.c_uint32),
        ("r1", ctypes.c_uint32),
        ("stacked_r1", ctypes.c_uint32),
    ]


class Outputs59cb44(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("r1", ctypes.c_uint32),
        ("failure_call_performed", ctypes.c_uint32),
        ("failure_call_target", ctypes.c_uint32),
        ("failure_call_r0", ctypes.c_uint32),
        ("failure_call_r1", ctypes.c_uint32),
        ("size_store_offset", ctypes.c_uint32),
        ("size_store_value", ctypes.c_uint32),
        ("word_count_store_offset", ctypes.c_uint32),
        ("word_count_store_value", ctypes.c_uint32),
        ("flag_store_offset_0", ctypes.c_uint32),
        ("flag_store_offset_1", ctypes.c_uint32),
        ("flag_store_value", ctypes.c_uint32),
    ]


class Inputs59cb6c(ctypes.Structure):
    _fields_ = [
        ("object", ctypes.c_uint32),
        ("arg_r1", ctypes.c_uint32),
        ("arg_r2", ctypes.c_uint32),
        ("object_field_0x0c", ctypes.c_uint32),
        ("setup_call_return", ctypes.c_uint32),
        ("byte_call_return", ctypes.c_uint32),
        ("stacked_r4", ctypes.c_uint32),
        ("stacked_r5", ctypes.c_uint32),
        ("stacked_r6", ctypes.c_uint32),
    ]


class Outputs59cb6c(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("r4", ctypes.c_uint32),
        ("r5", ctypes.c_uint32),
        ("r6", ctypes.c_uint32),
        ("setup_call_target", ctypes.c_uint32),
        ("setup_call_r0", ctypes.c_uint32),
        ("setup_call_r1", ctypes.c_uint32),
        ("byte_loop_performed", ctypes.c_uint32),
        ("byte_loop_count", ctypes.c_uint32),
        ("byte_call_target", ctypes.c_uint32),
        ("byte_call_r0", ctypes.c_uint32),
        ("first_byte_store_offset", ctypes.c_uint32),
        ("last_byte_store_offset", ctypes.c_uint32),
        ("byte_store_value", ctypes.c_uint32),
        ("return_restored_registers_from_stack", ctypes.c_uint32),
    ]


class Inputs59cb1e(ctypes.Structure):
    _fields_ = [
        ("object", ctypes.c_uint32),
        ("arg_r1", ctypes.c_uint32),
        ("call_return", ctypes.c_uint32),
        ("stacked_r4", ctypes.c_uint32),
        ("stacked_r5", ctypes.c_uint32),
        ("stacked_r6", ctypes.c_uint32),
    ]


class Outputs59cb1e(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("r4", ctypes.c_uint32),
        ("r5", ctypes.c_uint32),
        ("r6", ctypes.c_uint32),
        ("call_target", ctypes.c_uint32),
        ("call_r0", ctypes.c_uint32),
        ("call_r1", ctypes.c_uint32),
        ("call_r2", ctypes.c_uint32),
        ("call_return", ctypes.c_uint32),
        ("store_offset", ctypes.c_uint32),
        ("store_value", ctypes.c_uint32),
        ("return_restored_registers_from_stack", ctypes.c_uint32),
    ]


class Inputs59cb98(ctypes.Structure):
    _fields_ = [
        ("object", ctypes.c_uint32),
        ("arg_r1", ctypes.c_uint32),
        ("object_field_0x0c", ctypes.c_uint32),
        ("setup_call_return", ctypes.c_uint32),
        ("tail_byte_before_mask", ctypes.c_uint32),
        ("stacked_r0", ctypes.c_uint32),
        ("stacked_r4", ctypes.c_uint32),
        ("stacked_r5", ctypes.c_uint32),
    ]


class Outputs59cb98(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("r4", ctypes.c_uint32),
        ("r5", ctypes.c_uint32),
        ("setup_call_target", ctypes.c_uint32),
        ("setup_call_r0", ctypes.c_uint32),
        ("setup_call_r1", ctypes.c_uint32),
        ("fill_performed", ctypes.c_uint32),
        ("fill_count", ctypes.c_uint32),
        ("fill_first_offset", ctypes.c_uint32),
        ("fill_last_offset", ctypes.c_uint32),
        ("fill_value", ctypes.c_uint32),
        ("tail_mask", ctypes.c_uint32),
        ("tail_store_offset", ctypes.c_uint32),
        ("tail_store_value", ctypes.c_uint32),
        ("return_restored_registers_from_stack", ctypes.c_uint32),
    ]


class Inputs59c530(ctypes.Structure):
    _fields_ = [
        ("base", ctypes.c_uint32),
        ("arg_r1", ctypes.c_uint32),
        ("arg_r2", ctypes.c_uint32),
        ("saved_low_0x2dd0", ctypes.c_uint32),
        ("saved_high_0x2dd4", ctypes.c_uint32),
        ("predicate_return", ctypes.c_uint32),
        ("field_0x2dd8", ctypes.c_uint32),
        ("field_0x2ddc", ctypes.c_uint32),
        ("callback", ctypes.c_uint32),
        ("helper_result_low", ctypes.c_uint32),
        ("helper_result_high", ctypes.c_uint32),
    ]


class Outputs59c530(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("saved_low", ctypes.c_uint32),
        ("saved_high", ctypes.c_uint32),
        ("predicate_call_target", ctypes.c_uint32),
        ("predicate_call_r0", ctypes.c_uint32),
        ("fallback_call_performed", ctypes.c_uint32),
        ("fallback_call_target", ctypes.c_uint32),
        ("fallback_call_r0", ctypes.c_uint32),
        ("fallback_call_r1", ctypes.c_uint32),
        ("fallback_call_r2", ctypes.c_uint32),
        ("helper_call_target", ctypes.c_uint32),
        ("helper_call_r0", ctypes.c_uint32),
        ("helper_call_r1", ctypes.c_uint32),
        ("helper_call_r3", ctypes.c_uint32),
        ("callback_call_target", ctypes.c_uint32),
        ("callback_call_r0", ctypes.c_uint32),
        ("callback_call_r1_is_saved_pair", ctypes.c_uint32),
        ("restored_low_0x2dd0", ctypes.c_uint32),
        ("restored_high_0x2dd4", ctypes.c_uint32),
        ("stored_arg_r1_0x2db8", ctypes.c_uint32),
        ("stored_arg_r2_0x2dbc", ctypes.c_uint32),
    ]


class Inputs59c060(ctypes.Structure):
    _fields_ = [
        ("r1", ctypes.c_uint32),
        ("r3", ctypes.c_uint32),
        ("ip", ctypes.c_uint32),
        ("sl", ctypes.c_uint32),
    ]


class Outputs59c060(ctypes.Structure):
    _fields_ = [
        ("r2", ctypes.c_uint32),
        ("r3", ctypes.c_uint32),
        ("ip", ctypes.c_uint32),
        ("lr", ctypes.c_uint32),
        ("branch_to_0x0059c086", ctypes.c_int),
    ]


class Inputs59ba4a(ctypes.Structure):
    _fields_ = [
        ("r1", ctypes.c_uint32),
        ("r4", ctypes.c_int32),
    ]


class Outputs59ba4a(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("branch_to_0x0059b8b2", ctypes.c_int),
    ]


class Inputs59a3d2(ctypes.Structure):
    _fields_ = [
        ("stack_word_0x10c", ctypes.c_int32),
        ("stack_float_0x4c", ctypes.c_float),
        ("s6", ctypes.c_float),
        ("s7", ctypes.c_float),
        ("s8", ctypes.c_float),
        ("s16", ctypes.c_float),
    ]


class Outputs59a3d2(ctypes.Structure):
    _fields_ = [
        ("lr", ctypes.c_int32),
        ("r2", ctypes.c_int32),
        ("s9", ctypes.c_float),
        ("s10", ctypes.c_float),
        ("s11", ctypes.c_float),
        ("s12", ctypes.c_float),
        ("branch_to_0x0059a420", ctypes.c_int),
    ]


class Inputs4ec718(ctypes.Structure):
    _fields_ = [
        ("sl", ctypes.c_uint32),
    ]


class Outputs4ec718(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("call_target", ctypes.c_uint32),
    ]


class Inputs4ec774(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
    ]


class Outputs4ec774(ctypes.Structure):
    _fields_ = [
        ("r0", ctypes.c_uint32),
        ("r1", ctypes.c_uint32),
        ("r2", ctypes.c_uint32),
        ("sb", ctypes.c_uint32),
        ("call_target", ctypes.c_uint32),
    ]


class RuntimeLiblc3Am142SemanticModelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.tmpdir = tempfile.TemporaryDirectory()
        cls.lib_path = Path(cls.tmpdir.name) / "libam142_semantic.dylib"
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
        cls.model = cls.lib.open_cfw_am142_0x59a312_semantic_model
        cls.model.argtypes = [Inputs]
        cls.model.restype = Outputs
        cls.model_59aa84 = cls.lib.open_cfw_am142_0x59aa84_semantic_model
        cls.model_59aa84.argtypes = [Inputs59aa84]
        cls.model_59aa84.restype = Outputs59aa84
        cls.model_59af42 = cls.lib.open_cfw_am142_0x59af42_semantic_model
        cls.model_59af42.argtypes = [Inputs59af42]
        cls.model_59af42.restype = Outputs59af42
        cls.model_59af54 = cls.lib.open_cfw_am142_0x59af54_semantic_model
        cls.model_59af54.argtypes = [Inputs59af54]
        cls.model_59af54.restype = Outputs59af54
        cls.model_59afa0 = cls.lib.open_cfw_am142_0x59afa0_semantic_model
        cls.model_59afa0.argtypes = [Inputs59afa0]
        cls.model_59afa0.restype = Outputs59afa0
        cls.model_59aec8 = cls.lib.open_cfw_am142_0x59aec8_semantic_model
        cls.model_59aec8.argtypes = [Inputs59aec8]
        cls.model_59aec8.restype = Outputs59aec8
        cls.model_59af1e = cls.lib.open_cfw_am142_0x59af1e_semantic_model
        cls.model_59af1e.argtypes = [Inputs59af1e]
        cls.model_59af1e.restype = Outputs59af1e
        cls.model_59b00e = cls.lib.open_cfw_am142_0x59b00e_semantic_model
        cls.model_59b00e.argtypes = [Inputs59b00e]
        cls.model_59b00e.restype = Outputs59b00e
        cls.model_59b272 = cls.lib.open_cfw_am142_0x59b272_semantic_model
        cls.model_59b272.argtypes = [Inputs59b272]
        cls.model_59b272.restype = Outputs59b272
        cls.model_59b2aa = cls.lib.open_cfw_am142_0x59b2aa_semantic_model
        cls.model_59b2aa.argtypes = [Inputs59b2aa]
        cls.model_59b2aa.restype = Outputs59b2aa
        cls.model_59b33e = cls.lib.open_cfw_am142_0x59b33e_semantic_model
        cls.model_59b33e.argtypes = [Inputs59b33e]
        cls.model_59b33e.restype = Outputs59b33e
        cls.model_59b382 = cls.lib.open_cfw_am142_0x59b382_semantic_model
        cls.model_59b382.argtypes = [Inputs59b382]
        cls.model_59b382.restype = Outputs59b382
        cls.model_59b3de = cls.lib.open_cfw_am142_0x59b3de_semantic_model
        cls.model_59b3de.argtypes = [Inputs59b3de]
        cls.model_59b3de.restype = Outputs59b3de
        cls.model_59b454 = cls.lib.open_cfw_am142_0x59b454_semantic_model
        cls.model_59b454.argtypes = [Inputs59b454]
        cls.model_59b454.restype = Outputs59b454
        cls.model_59c052 = cls.lib.open_cfw_am142_0x59c052_semantic_model
        cls.model_59c052.argtypes = [Inputs59c052]
        cls.model_59c052.restype = Outputs59c052
        cls.model_59b52c = cls.lib.open_cfw_am142_0x59b52c_semantic_model
        cls.model_59b52c.argtypes = [Inputs59b52c]
        cls.model_59b52c.restype = Outputs59b52c
        cls.model_59b53c = cls.lib.open_cfw_am142_0x59b53c_semantic_model
        cls.model_59b53c.argtypes = [Inputs59b53c]
        cls.model_59b53c.restype = Outputs59b53c
        cls.model_59b654 = cls.lib.open_cfw_am142_0x59b654_semantic_model
        cls.model_59b654.argtypes = [Inputs59b654]
        cls.model_59b654.restype = Outputs59b654
        cls.model_59cb44 = cls.lib.open_cfw_am142_0x59cb44_semantic_model
        cls.model_59cb44.argtypes = [Inputs59cb44]
        cls.model_59cb44.restype = Outputs59cb44
        cls.model_59cb6c = cls.lib.open_cfw_am142_0x59cb6c_semantic_model
        cls.model_59cb6c.argtypes = [Inputs59cb6c]
        cls.model_59cb6c.restype = Outputs59cb6c
        cls.model_59cb1e = cls.lib.open_cfw_am142_0x59cb1e_semantic_model
        cls.model_59cb1e.argtypes = [Inputs59cb1e]
        cls.model_59cb1e.restype = Outputs59cb1e
        cls.model_59cb98 = cls.lib.open_cfw_am142_0x59cb98_semantic_model
        cls.model_59cb98.argtypes = [Inputs59cb98]
        cls.model_59cb98.restype = Outputs59cb98
        cls.model_59c530 = cls.lib.open_cfw_am142_0x59c530_semantic_model
        cls.model_59c530.argtypes = [Inputs59c530]
        cls.model_59c530.restype = Outputs59c530
        cls.model_59c060 = cls.lib.open_cfw_am142_0x59c060_semantic_model
        cls.model_59c060.argtypes = [Inputs59c060]
        cls.model_59c060.restype = Outputs59c060
        cls.model_59ba4a = cls.lib.open_cfw_am142_0x59ba4a_semantic_model
        cls.model_59ba4a.argtypes = [Inputs59ba4a]
        cls.model_59ba4a.restype = Outputs59ba4a
        cls.model_59a3d2 = cls.lib.open_cfw_am142_0x59a3d2_semantic_model
        cls.model_59a3d2.argtypes = [Inputs59a3d2]
        cls.model_59a3d2.restype = Outputs59a3d2
        cls.model_4ec718 = cls.lib.open_cfw_am142_0x4ec718_semantic_model
        cls.model_4ec718.argtypes = [Inputs4ec718]
        cls.model_4ec718.restype = Outputs4ec718
        cls.model_4ec774 = cls.lib.open_cfw_am142_0x4ec774_semantic_model
        cls.model_4ec774.argtypes = [Inputs4ec774]
        cls.model_4ec774.restype = Outputs4ec774

    @classmethod
    def tearDownClass(cls) -> None:
        cls.tmpdir.cleanup()

    def test_delegate_tail_clears_context_flag_byte(self) -> None:
        out = self.model_59aa84(Inputs59aa84(0x20001000))

        self.assertEqual(out.call_target, 0x005999A6)
        self.assertEqual(out.call_r0, 0x20001000)
        self.assertEqual(out.r0, 0)
        self.assertEqual(out.cleared_byte_offset, 0x2000102C)
        self.assertEqual(out.cleared_byte_value, 0)

    def test_preserved_r4_delegate_tail_clears_context_flag_byte(self) -> None:
        out = self.model_59af42(Inputs59af42(0x20001000, 0xBEEFBEEF))

        self.assertEqual(out.call_target, 0x005999A6)
        self.assertEqual(out.call_r0, 0)
        self.assertEqual(out.r0, 0)
        self.assertEqual(out.r4, 0xBEEFBEEF)
        self.assertEqual(out.cleared_byte_offset, 0x2000102C)
        self.assertEqual(out.cleared_byte_value, 0)
        self.assertEqual(out.return_restored_r4_from_stack, 1)

    def test_runtime_call_branch_tail_rejects_invalid_object_range(self) -> None:
        out = self.model_59aec8(Inputs59aec8(0, 4, 0x20, 2, 0xBEEFBEEF))

        self.assertEqual(out.r0, 0x24)
        self.assertEqual(out.r4, 0xBEEFBEEF)
        self.assertEqual(out.initial_range_rejected, 1)
        self.assertEqual(out.helper_call_performed, 0)
        self.assertEqual(out.return_restored_r4_from_stack, 1)

    def test_dual_am141_call_tail_stores_first_result_when_available(self) -> None:
        out = self.model_59af54(
            Inputs59af54(
                0x20000000,
                0x20001000,
                0,
                0,
                0xAAAA0001,
                0xBBBB0002,
                0xCCCC0003,
                0xDDDD0004,
                0x11112222,
                0x33334444,
                0x44444444,
                0x55555555,
                0x66666666,
            )
        )

        self.assertEqual(out.r0, 0x11112222)
        self.assertEqual(out.first_call_performed, 1)
        self.assertEqual(out.first_call_target, 0x00599978)
        self.assertEqual(out.first_call_r0, 0x20001000)
        self.assertEqual(out.first_call_r1, 0xAAAA0001)
        self.assertEqual(out.first_call_r2, 0xBBBB0002)
        self.assertEqual(out.second_call_performed, 0)
        self.assertEqual(out.slot_store_performed, 1)
        self.assertEqual(out.slot_store_value, 0x11112222)
        self.assertEqual(out.r4, 0x44444444)
        self.assertEqual(out.r5, 0x55555555)
        self.assertEqual(out.r6, 0x66666666)
        self.assertEqual(out.return_restored_registers_from_stack, 1)

    def test_dual_am141_call_tail_falls_back_to_second_call(self) -> None:
        out = self.model_59af54(
            Inputs59af54(
                0x20000000,
                0x20001000,
                0,
                0,
                0xAAAA0001,
                0xBBBB0002,
                0xCCCC0003,
                0xDDDD0004,
                0,
                0x33334444,
                1,
                2,
                3,
            )
        )

        self.assertEqual(out.r0, 0x33334444)
        self.assertEqual(out.first_call_performed, 1)
        self.assertEqual(out.second_call_performed, 1)
        self.assertEqual(out.second_call_target, 0x005998E8)
        self.assertEqual(out.second_call_r0, 0x20001000)
        self.assertEqual(out.second_call_r1, 0xCCCC0003)
        self.assertEqual(out.second_call_r2, 0xDDDD0004)
        self.assertEqual(out.slot_store_performed, 1)
        self.assertEqual(out.slot_store_value, 0x33334444)

    def test_dual_am141_call_tail_suppresses_store_when_slot_is_filled(self) -> None:
        out = self.model_59af54(
            Inputs59af54(
                0x20000000,
                0x20001000,
                1,
                0xCAFEBABE,
                0xAAAA0001,
                0xBBBB0002,
                0xCCCC0003,
                0xDDDD0004,
                0x11112222,
                0x33334444,
                1,
                2,
                3,
            )
        )

        self.assertEqual(out.first_call_performed, 0)
        self.assertEqual(out.second_call_performed, 1)
        self.assertEqual(out.r0, 0x33334444)
        self.assertEqual(out.slot_store_performed, 0)
        self.assertEqual(out.slot_store_value, 0)

    def test_multi_am141_call_tail_stores_primary_result(self) -> None:
        out = self.model_59afa0(
            Inputs59afa0(
                0x20000000,
                0x20001000,
                0,
                0,
                0xA0,
                0xA4,
                0xB0,
                0xB4,
                0xC0,
                0xC4,
                0xD0,
                0xD4,
                0x11112222,
                0x33334444,
                1,
                2,
                3,
            )
        )

        self.assertEqual(out.r0, 0x11112222)
        self.assertEqual(out.first_call_performed, 1)
        self.assertEqual(out.first_call_target, 0x00599978)
        self.assertEqual(out.first_call_r0, 0x20001000)
        self.assertEqual(out.first_call_r1, 0xA0)
        self.assertEqual(out.first_call_r2, 0xA4)
        self.assertEqual(out.second_call_performed, 0)
        self.assertEqual(out.fallback_call_count, 0)
        self.assertEqual(out.slot_store_performed, 1)
        self.assertEqual(out.slot_store_value, 0x11112222)
        self.assertEqual(out.return_restored_registers_from_stack, 1)

    def test_multi_am141_call_tail_stores_secondary_result(self) -> None:
        out = self.model_59afa0(
            Inputs59afa0(
                0x20000000,
                0x20001000,
                1,
                0,
                0xA0,
                0xA4,
                0xB0,
                0xB4,
                0xC0,
                0xC4,
                0xD0,
                0xD4,
                0,
                0x33334444,
                1,
                2,
                3,
            )
        )

        self.assertEqual(out.first_call_performed, 0)
        self.assertEqual(out.second_call_performed, 1)
        self.assertEqual(out.second_call_target, 0x0059987E)
        self.assertEqual(out.second_call_r0, 0x20001000)
        self.assertEqual(out.second_call_r1, 3)
        self.assertEqual(out.r0, 0x33334444)
        self.assertEqual(out.fallback_call_count, 0)
        self.assertEqual(out.slot_store_performed, 1)
        self.assertEqual(out.slot_store_value, 0x33334444)

    def test_multi_am141_call_tail_falls_back_to_three_submissions(self) -> None:
        out = self.model_59afa0(
            Inputs59afa0(
                0x20000000,
                0x20001000,
                1,
                0xCAFEBABE,
                0xA0,
                0xA4,
                0xB0,
                0xB4,
                0xC0,
                0xC4,
                0xD0,
                0xD4,
                0,
                0,
                1,
                2,
                3,
            )
        )

        self.assertEqual(out.first_call_performed, 0)
        self.assertEqual(out.second_call_performed, 1)
        self.assertEqual(out.fallback_call_count, 3)
        self.assertEqual(out.fallback_call_target, 0x005998AA)
        self.assertEqual(out.fallback0_r1, 0xB0)
        self.assertEqual(out.fallback0_r2, 0xB4)
        self.assertEqual(out.fallback0_r3, 0)
        self.assertEqual(out.fallback1_r1, 0xC0)
        self.assertEqual(out.fallback1_r2, 0xC4)
        self.assertEqual(out.fallback1_r3, 0)
        self.assertEqual(out.fallback2_r1, 0xD0)
        self.assertEqual(out.fallback2_r2, 0xD4)
        self.assertEqual(out.fallback2_r3, 1)
        self.assertEqual(out.slot_store_performed, 0)
        self.assertEqual(out.return_restored_registers_from_stack, 1)

    def test_runtime_call_branch_tail_rejects_large_argument(self) -> None:
        out = self.model_59aec8(Inputs59aec8(1, 4, 0x8000, 2, 0xBEEFBEEF))

        self.assertEqual(out.r0, 0xA4)
        self.assertEqual(out.arg_threshold_rejected, 1)
        self.assertEqual(out.helper_call_performed, 0)
        self.assertEqual(out.return_restored_r4_from_stack, 1)

    def test_runtime_call_branch_tail_rejects_helper_result_outside_bounds(self) -> None:
        out = self.model_59aec8(Inputs59aec8(10, 20, 0x21, 20, 0xBEEFBEEF))

        self.assertEqual(out.r0, 0xA4)
        self.assertEqual(out.helper_call_performed, 1)
        self.assertEqual(out.helper_call_target, 0x004EC774)
        self.assertEqual(out.helper_call_r0, 0x07D00000)
        self.assertEqual(out.helper_call_r1, 0x00210000)
        self.assertEqual(out.helper_range_rejected, 1)
        self.assertEqual(out.return_restored_r4_from_stack, 1)

    def test_runtime_call_branch_tail_accepts_helper_result_inside_bounds(self) -> None:
        out = self.model_59aec8(Inputs59aec8(10, 20, 0x21, 12, 0xBEEFBEEF))

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.helper_call_performed, 1)
        self.assertEqual(out.helper_call_target, 0x004EC774)
        self.assertEqual(out.helper_call_r0, 0x07D00000)
        self.assertEqual(out.helper_call_r1, 0x00210000)
        self.assertEqual(out.helper_range_rejected, 0)
        self.assertEqual(out.return_restored_r4_from_stack, 1)

    def test_repeated_runtime_cleanup_tail_clears_two_fields(self) -> None:
        out = self.model_59af1e(
            Inputs59af1e(
                0x20001000,
                0x20002000,
                0xAAAA0001,
                0xBBBB0002,
                0x11111111,
                0x22222222,
                0x33333333,
            )
        )

        self.assertEqual(out.cleanup_performed, 1)
        self.assertEqual(out.first_call_target, 0x004F1276)
        self.assertEqual(out.first_call_r0, 0x20002000)
        self.assertEqual(out.first_call_r1, 0xAAAA0001)
        self.assertEqual(out.first_clear_offset, 0x2000106C)
        self.assertEqual(out.first_clear_value, 0)
        self.assertEqual(out.second_call_target, 0x004F1276)
        self.assertEqual(out.second_call_r0, 0x20002000)
        self.assertEqual(out.second_call_r1, 0xBBBB0002)
        self.assertEqual(out.second_clear_offset, 0x20001074)
        self.assertEqual(out.second_clear_value, 0)
        self.assertEqual(out.r0, 0x11111111)
        self.assertEqual(out.r4, 0x22222222)
        self.assertEqual(out.r5, 0x33333333)
        self.assertEqual(out.return_restored_registers_from_stack, 1)

    def test_repeated_runtime_cleanup_tail_skips_null_object(self) -> None:
        out = self.model_59af1e(
            Inputs59af1e(0, 0x20002000, 0xAAAA0001, 0xBBBB0002, 1, 2, 3)
        )

        self.assertEqual(out.cleanup_performed, 0)
        self.assertEqual(out.r0, 1)
        self.assertEqual(out.r4, 2)
        self.assertEqual(out.r5, 3)
        self.assertEqual(out.return_restored_registers_from_stack, 1)

    def test_literal_runtime_call_tail_initializes_object(self) -> None:
        out = self.model_59b00e(
            Inputs59b00e(
                0x20001000,
                0xAAAA0001,
                0xBBBB0002,
                0xCCCC0003,
                0x11111111,
                0x22222222,
                0x33333333,
                0x44444444,
                0x55555555,
            )
        )

        self.assertEqual(out.runtime_call_target, 0x00404104)
        self.assertEqual(out.runtime_call_r0, 0x20001000)
        self.assertEqual(out.runtime_call_r1, 0x20)
        self.assertEqual(out.runtime_call_r2, 0)
        self.assertEqual(out.runtime_call_return, 0xCCCC0003)
        self.assertEqual(out.store_arg_r1_offset, 0x20001014)
        self.assertEqual(out.store_arg_r1_value, 0xAAAA0001)
        self.assertEqual(out.store_arg_r2_offset, 0x20001018)
        self.assertEqual(out.store_arg_r2_value, 0xBBBB0002)
        self.assertEqual(out.literal0_offset, 0x20001000)
        self.assertEqual(out.literal0_value, 0x005D2F23)
        self.assertEqual(out.literal1_offset, 0x20001004)
        self.assertEqual(out.literal1_value, 0x005D2F35)
        self.assertEqual(out.literal2_offset, 0x2000100C)
        self.assertEqual(out.literal2_value, 0x005D2F81)
        self.assertEqual(out.r0, 0x11111111)
        self.assertEqual(out.r4, 0x22222222)
        self.assertEqual(out.r5, 0x33333333)
        self.assertEqual(out.r6, 0x44444444)
        self.assertEqual(out.r7, 0x55555555)
        self.assertEqual(out.return_restored_registers_from_stack, 1)

    def test_dynamic_callback_tail_sets_zero_stack_arg(self) -> None:
        out = self.model_59b272(
            Inputs59b272(
                0x20000000,
                0x33333333,
                0x20001000,
                0x20002000,
                0x00590001,
                0xAABBCCDD,
                0x11111111,
                0x22222222,
                0x44444444,
            )
        )

        self.assertEqual(out.table_load_base, 0x20001000)
        self.assertEqual(out.table_load_offset, 0x224)
        self.assertEqual(out.callback_load_base, 0x20002000)
        self.assertEqual(out.callback_load_offset, 0x20)
        self.assertEqual(out.stack_arg0_value, 0)
        self.assertEqual(out.callback_call_target, 0x00590001)
        self.assertEqual(out.callback_call_r0, 0x20001000)
        self.assertEqual(out.callback_call_r2, 0)
        self.assertEqual(out.callback_call_r3, 0x33333333)
        self.assertEqual(out.r0, 0xAABBCCDD)
        self.assertEqual(out.r1, 0x11111111)
        self.assertEqual(out.r2, 0x22222222)
        self.assertEqual(out.r3, 0x33333333)
        self.assertEqual(out.r4, 0x44444444)
        self.assertEqual(out.return_restored_registers_from_stack, 1)

    def test_three_store_delegate_tail_converts_nested_fields(self) -> None:
        out = self.model_59b2aa(
            Inputs59b2aa(
                0x20000000,
                0x20002000,
                0x00001234,
                0x00000056,
                0x00000078,
                0xAABBCCDD,
                0x11111111,
                0x22222222,
                0x33333333,
                0x44444444,
                0x55555555,
            )
        )

        self.assertEqual(out.helper_call_target, 0x004EC774)
        self.assertEqual(out.helper_call_r0, 0x00001234)
        self.assertEqual(out.helper_call_r1, 0x03E80000)
        self.assertEqual(out.store_arg_r1_value, 0xAABBCCDD)
        self.assertEqual(out.store_arg_r2_value, 0x00560000)
        self.assertEqual(out.store_arg_r3_value, 0x00780000)
        self.assertEqual(out.r0, 0x11111111)
        self.assertEqual(out.r4, 0x22222222)
        self.assertEqual(out.r5, 0x33333333)
        self.assertEqual(out.r6, 0x44444444)
        self.assertEqual(out.r7, 0x55555555)
        self.assertEqual(out.return_restored_registers_from_stack, 1)

    def test_table_output_tail_rejects_out_of_bounds_index(self) -> None:
        out = self.model_59b33e(
            Inputs59b33e(
                0x20000000,
                5,
                0x20003000,
                10,
                5,
                0x20004000,
                0xAAAA0001,
                0xBBBB0002,
                0x11111111,
                0x22222222,
                0x33333333,
                0x44444444,
                0x55555555,
            )
        )

        self.assertEqual(out.init_call_target, 0x00404104)
        self.assertEqual(out.init_call_r0, 0x20003000)
        self.assertEqual(out.init_call_r1, 0x10)
        self.assertEqual(out.init_call_r2, 0)
        self.assertEqual(out.computed_index, 10)
        self.assertEqual(out.bounds_rejected, 1)
        self.assertEqual(out.r0, 1)
        self.assertEqual(out.r1, 0x11111111)
        self.assertEqual(out.r4, 0x22222222)
        self.assertEqual(out.r5, 0x33333333)
        self.assertEqual(out.r6, 0x44444444)
        self.assertEqual(out.r7, 0x55555555)
        self.assertEqual(out.return_restored_registers_from_stack, 1)

    def test_table_output_tail_copies_selected_pair(self) -> None:
        out = self.model_59b33e(
            Inputs59b33e(
                0x20000000,
                4,
                0x20003000,
                10,
                2,
                0x20004000,
                0xAAAA0001,
                0xBBBB0002,
                0x11111111,
                0x22222222,
                0x33333333,
                0x44444444,
                0x55555555,
            )
        )

        self.assertEqual(out.computed_index, 6)
        self.assertEqual(out.bounds_rejected, 0)
        self.assertEqual(out.store_arg_r2_0x0c, 0xAAAA0001)
        self.assertEqual(out.store_arg_r2_0x04, 0xAAAA0001)
        self.assertEqual(out.store_arg_r2_0x08, 0xBBBB0002)
        self.assertEqual(out.r0, 0)
        self.assertEqual(out.r1, 0x11111111)
        self.assertEqual(out.return_restored_registers_from_stack, 1)

    def test_runtime_then_am141_tail_uses_existing_callback(self) -> None:
        out = self.model_59b382(
            Inputs59b382(
                0x20000000,
                0x11,
                0x20003000,
                0x20004000,
                0x20005000,
                0x00590081,
                0x20006000,
                0,
                0,
                0x22,
                0x33,
                1,
                2,
                3,
                4,
                5,
                6,
                7,
            )
        )

        self.assertEqual(out.init_call_target, 0x00404104)
        self.assertEqual(out.init_call_r0, 0x20003000)
        self.assertEqual(out.init_call_r1, 0x10)
        self.assertEqual(out.init_call_r2, 0)
        self.assertEqual(out.helper_call_performed, 0)
        self.assertEqual(out.callback_call_performed, 1)
        self.assertEqual(out.callback_call_target, 0x00590081)
        self.assertEqual(out.callback_call_r0, 0x20004000)
        self.assertEqual(out.callback_call_r1, 0x11)
        self.assertEqual(out.store_arg_r2_0x04, 0x22)
        self.assertEqual(out.store_arg_r2_0x08, 0x55)
        self.assertEqual(out.store_arg_r2_0x0c, 0x22)
        self.assertEqual(out.r0, 0)
        self.assertEqual(out.r1, 1)
        self.assertEqual(out.r7, 7)
        self.assertEqual(out.return_restored_registers_from_stack, 1)

    def test_runtime_then_am141_tail_returns_error_for_negative_helper(self) -> None:
        out = self.model_59b382(
            Inputs59b382(
                0x20000000,
                0x11,
                0x20003000,
                0x20004000,
                0x20005000,
                0x00590081,
                0,
                0xFFFFFFFF,
                0,
                0x22,
                0x33,
                1,
                2,
                3,
                4,
                5,
                6,
                7,
            )
        )

        self.assertEqual(out.helper_call_performed, 1)
        self.assertEqual(out.helper_call_target, 0x0059A1B6)
        self.assertEqual(out.helper_call_r0, 0x20005000)
        self.assertEqual(out.helper_call_r1, 0x11)
        self.assertEqual(out.callback_call_performed, 0)
        self.assertEqual(out.r0, 0x12)
        self.assertEqual(out.return_restored_registers_from_stack, 1)

    def test_runtime_then_am141_tail_uses_helper_result_as_callback_arg(self) -> None:
        out = self.model_59b382(
            Inputs59b382(
                0x20000000,
                0x11,
                0x20003000,
                0x20004000,
                0x20005000,
                0x00590081,
                0,
                0x44,
                0x99,
                0x22,
                0x33,
                1,
                2,
                3,
                4,
                5,
                6,
                7,
            )
        )

        self.assertEqual(out.helper_call_performed, 1)
        self.assertEqual(out.callback_call_performed, 1)
        self.assertEqual(out.callback_call_r1, 0x44)
        self.assertEqual(out.r0, 0x99)
        self.assertEqual(out.store_arg_r2_0x04, 0)
        self.assertEqual(out.store_arg_r2_0x08, 0)
        self.assertEqual(out.store_arg_r2_0x0c, 0)

    def test_delta_callback_tail_restores_r0_from_stack(self) -> None:
        out = self.model_59b3de(
            Inputs59b3de(
                0x20000000,
                0x20003000,
                0x20,
                0x54,
                0x20001000,
                0x00590021,
                0xAABBCCDD,
                0xFEEDBEEF,
            )
        )

        self.assertEqual(out.callback_call_target, 0x00590021)
        self.assertEqual(out.callback_call_r0, 0x20001000)
        self.assertEqual(out.callback_call_r1, 0x20003004)
        self.assertEqual(out.callback_call_r2, 0x34)
        self.assertEqual(out.callback_call_return, 0xAABBCCDD)
        self.assertEqual(out.callback_load_offset, 0x254)
        self.assertEqual(out.r0, 0xFEEDBEEF)
        self.assertEqual(out.return_restored_from_stack, 1)

    def test_guarded_callback_tail_calls_nested_slot(self) -> None:
        out = self.model_59b454(
            Inputs59b454(
                0x20001000,
                0x20,
                0x54,
                0x20002000,
                0x20003000,
                0x20004000,
                0x00590041,
                0xAABBCCDD,
                0x11111111,
                0x22222222,
                0x33333333,
            )
        )

        self.assertEqual(out.stack_word0, 0x20)
        self.assertEqual(out.stack_word1, 0x34)
        self.assertEqual(out.callback_performed, 1)
        self.assertEqual(out.callback_call_target, 0x00590041)
        self.assertEqual(out.callback_call_r0, 0x20004000)
        self.assertEqual(out.callback_call_r1_is_stack_pair, 1)
        self.assertEqual(out.callback_call_return, 0xAABBCCDD)
        self.assertEqual(out.r0, 0x11111111)
        self.assertEqual(out.r1, 0x22222222)
        self.assertEqual(out.r2, 0x33333333)
        self.assertEqual(out.return_restored_registers_from_stack, 1)

    def test_guarded_callback_tail_skips_null_context(self) -> None:
        out = self.model_59b454(
            Inputs59b454(
                0x20001000,
                0x44,
                0x90,
                0x20002000,
                0,
                0x20004000,
                0x00590041,
                0xAABBCCDD,
                0x11111111,
                0x22222222,
                0x33333333,
            )
        )

        self.assertEqual(out.stack_word0, 0x44)
        self.assertEqual(out.stack_word1, 0x4C)
        self.assertEqual(out.callback_performed, 0)
        self.assertEqual(out.r0, 0x11111111)
        self.assertEqual(out.r1, 0x22222222)
        self.assertEqual(out.r2, 0x33333333)
        self.assertEqual(out.return_restored_registers_from_stack, 1)

    def test_am141_delegate_tail_restores_return_register_from_stack(self) -> None:
        out = self.model_59c052(Inputs59c052(0x20000000, 0xCAFEBABE))

        self.assertEqual(out.call_target, 0x0059A32E)
        self.assertEqual(out.call_offset, 0x2D5C)
        self.assertEqual(out.call_r0, 0x20002D5C)
        self.assertEqual(out.r0, 0xCAFEBABE)
        self.assertEqual(out.return_restored_from_stack, 1)

    def test_runtime_call_tail_clears_object_word_and_restores_r0(self) -> None:
        out = self.model_59b52c(
            Inputs59b52c(0x20002000, 0x20003000, 0x12345678, 0xDEADBEEF)
        )

        self.assertEqual(out.zero_store_offset, 0x20002010)
        self.assertEqual(out.zero_store_value, 0)
        self.assertEqual(out.call_target, 0x004ECBC8)
        self.assertEqual(out.call_r0, 0x12345678)
        self.assertEqual(out.r0, 0xDEADBEEF)
        self.assertEqual(out.return_restored_from_stack, 1)

    def test_local_runtime_call_tail_flushes_nested_context(self) -> None:
        out = self.model_59b53c(
            Inputs59b53c(
                0x20002000,
                0x20003000,
                0x12345678,
                0xAAAAAAAA,
                0xBBBBBBBB,
                0xCCCCCCCC,
            )
        )

        self.assertEqual(out.first_call_target, 0x005999A6)
        self.assertEqual(out.first_call_r0, 0x20003000)
        self.assertEqual(out.first_call_return, 0xAAAAAAAA)
        self.assertEqual(out.second_call_target, 0x004ECE9A)
        self.assertEqual(out.second_call_r0, 0x12345678)
        self.assertEqual(out.r0, 0xBBBBBBBB)
        self.assertEqual(out.r4, 0xCCCCCCCC)
        self.assertEqual(out.return_restored_r4_from_stack, 1)

    def test_runtime_init_delegate_tail_uses_fixed_small_extent(self) -> None:
        out = self.model_59b654(
            Inputs59b654(0x20004000, 0x12345678, 0xA5A5A5A5)
        )

        self.assertEqual(out.call_target, 0x00404104)
        self.assertEqual(out.call_r0, 0x20004000)
        self.assertEqual(out.call_r1, 0x14)
        self.assertEqual(out.call_r2, 0)
        self.assertEqual(out.call_return, 0x12345678)
        self.assertEqual(out.r0, 0x12345678)
        self.assertEqual(out.r4, 0xA5A5A5A5)
        self.assertEqual(out.return_restored_r4_from_stack, 1)

    def test_local_setup_tail_accepts_length_and_sets_flags(self) -> None:
        out = self.model_59cb44(
            Inputs59cb44(0x20004000, 0x20005000, 0x60, 0xA5A5A5A5)
        )

        self.assertEqual(out.r0, 0x60)
        self.assertEqual(out.r1, 0xA5A5A5A5)
        self.assertEqual(out.failure_call_performed, 0)
        self.assertEqual(out.failure_call_target, 0x0059AA2A)
        self.assertEqual(out.size_store_offset, 0x20004008)
        self.assertEqual(out.size_store_value, 0x60)
        self.assertEqual(out.word_count_store_offset, 0x2000400C)
        self.assertEqual(out.word_count_store_value, 12)
        self.assertEqual(out.flag_store_offset_0, 0x20004004)
        self.assertEqual(out.flag_store_offset_1, 0x20004005)
        self.assertEqual(out.flag_store_value, 1)

    def test_local_setup_tail_rejects_length_with_error_call(self) -> None:
        out = self.model_59cb44(
            Inputs59cb44(0x20004000, 0x20005000, 0x61, 0xA5A5A5A5)
        )

        self.assertEqual(out.r0, 0)
        self.assertEqual(out.r1, 0xA5A5A5A5)
        self.assertEqual(out.failure_call_performed, 1)
        self.assertEqual(out.failure_call_target, 0x0059AA2A)
        self.assertEqual(out.failure_call_r0, 0x20005000)
        self.assertEqual(out.failure_call_r1, 0x12)
        self.assertEqual(out.size_store_value, 0)
        self.assertEqual(out.word_count_store_value, 0)
        self.assertEqual(out.flag_store_value, 0)

    def test_setup_then_byte_fill_tail_skips_loop_when_setup_rejects(self) -> None:
        out = self.model_59cb6c(
            Inputs59cb6c(
                0x20004000,
                0x20005000,
                0x60,
                12,
                0,
                0xAB,
                0x11111111,
                0x22222222,
                0x33333333,
            )
        )

        self.assertEqual(out.setup_call_target, 0x0059CB44)
        self.assertEqual(out.setup_call_r0, 0x20004000)
        self.assertEqual(out.setup_call_r1, 0x60)
        self.assertEqual(out.byte_loop_performed, 0)
        self.assertEqual(out.byte_loop_count, 0)
        self.assertEqual(out.r4, 0x11111111)
        self.assertEqual(out.r5, 0x22222222)
        self.assertEqual(out.r6, 0x33333333)
        self.assertEqual(out.return_restored_registers_from_stack, 1)

    def test_setup_then_byte_fill_tail_fills_declared_byte_count(self) -> None:
        out = self.model_59cb6c(
            Inputs59cb6c(
                0x20004000,
                0x20005000,
                0x60,
                12,
                0x60,
                0x1AB,
                0x11111111,
                0x22222222,
                0x33333333,
            )
        )

        self.assertEqual(out.byte_loop_performed, 1)
        self.assertEqual(out.byte_loop_count, 12)
        self.assertEqual(out.byte_call_target, 0x0059EDB8)
        self.assertEqual(out.byte_call_r0, 0x20005000)
        self.assertEqual(out.first_byte_store_offset, 0x20004010)
        self.assertEqual(out.last_byte_store_offset, 0x2000401B)
        self.assertEqual(out.byte_store_value, 0xAB)
        self.assertEqual(out.r0, 0x1AB)
        self.assertEqual(out.return_restored_registers_from_stack, 1)

    def test_runtime_init_delegate_tail_stores_original_argument(self) -> None:
        out = self.model_59cb1e(
            Inputs59cb1e(
                0x20004000,
                0xDEADBEEF,
                0x12345678,
                0x11111111,
                0x22222222,
                0x33333333,
            )
        )

        self.assertEqual(out.call_target, 0x00404104)
        self.assertEqual(out.call_r0, 0x20004000)
        self.assertEqual(out.call_r1, 0x1C)
        self.assertEqual(out.call_r2, 0)
        self.assertEqual(out.call_return, 0x12345678)
        self.assertEqual(out.store_offset, 0x20004000)
        self.assertEqual(out.store_value, 0xDEADBEEF)
        self.assertEqual(out.r0, 0x12345678)
        self.assertEqual(out.r4, 0x11111111)
        self.assertEqual(out.r5, 0x22222222)
        self.assertEqual(out.r6, 0x33333333)
        self.assertEqual(out.return_restored_registers_from_stack, 1)

    def test_setup_mask_tail_skips_fill_when_setup_rejects(self) -> None:
        out = self.model_59cb98(
            Inputs59cb98(
                0x20004000,
                0x13,
                12,
                0,
                0xFF,
                0xAAAAAAAA,
                0xBBBBBBBB,
                0xCCCCCCCC,
            )
        )

        self.assertEqual(out.setup_call_target, 0x0059CB44)
        self.assertEqual(out.setup_call_r0, 0x20004000)
        self.assertEqual(out.setup_call_r1, 0x13)
        self.assertEqual(out.fill_performed, 0)
        self.assertEqual(out.fill_count, 0)
        self.assertEqual(out.tail_mask, 0x1F)
        self.assertEqual(out.r0, 0xAAAAAAAA)
        self.assertEqual(out.r4, 0xBBBBBBBB)
        self.assertEqual(out.r5, 0xCCCCCCCC)
        self.assertEqual(out.return_restored_registers_from_stack, 1)

    def test_setup_mask_tail_fills_and_masks_tail_byte(self) -> None:
        out = self.model_59cb98(
            Inputs59cb98(
                0x20004000,
                0x13,
                12,
                0x13,
                0xFF,
                0xAAAAAAAA,
                0xBBBBBBBB,
                0xCCCCCCCC,
            )
        )

        self.assertEqual(out.fill_performed, 1)
        self.assertEqual(out.fill_count, 12)
        self.assertEqual(out.fill_first_offset, 0x20004010)
        self.assertEqual(out.fill_last_offset, 0x2000401B)
        self.assertEqual(out.fill_value, 0xFF)
        self.assertEqual(out.tail_mask, 0x1F)
        self.assertEqual(out.tail_store_offset, 0x2000401B)
        self.assertEqual(out.tail_store_value, 0xE0)
        self.assertEqual(out.return_restored_registers_from_stack, 1)

    def assertModel59c530(self, predicate_return: int, fallback_performed: int) -> None:
        out = self.model_59c530(
            Inputs59c530(
                0x20000000,
                0x11111111,
                0x22222222,
                0xAAAA0001,
                0xBBBB0002,
                predicate_return,
                0x33333333,
                0x44444444,
                0x00590001,
                0xCCCC0003,
                0xDDDD0004,
            )
        )

        self.assertEqual(out.saved_low, 0xAAAA0001)
        self.assertEqual(out.saved_high, 0xBBBB0002)
        self.assertEqual(out.predicate_call_target, 0x0059B70A)
        self.assertEqual(out.predicate_call_r0, 0x20000008)
        self.assertEqual(out.fallback_call_performed, fallback_performed)
        self.assertEqual(out.fallback_call_target, 0x0059C774)
        self.assertEqual(out.fallback_call_r0, 0x20000000)
        self.assertEqual(out.fallback_call_r1, 0x33333333)
        self.assertEqual(out.fallback_call_r2, 0x44444444)
        self.assertEqual(out.helper_call_target, 0x0059C060)
        self.assertEqual(out.helper_call_r0, 0x20000000)
        self.assertEqual(out.helper_call_r1, 0x20000008)
        self.assertEqual(out.helper_call_r3, 0x11111111)
        self.assertEqual(out.callback_call_target, 0x00590001)
        self.assertEqual(out.callback_call_r0, 0x00590001)
        self.assertEqual(out.callback_call_r1_is_saved_pair, 1)
        self.assertEqual(out.restored_low_0x2dd0, 0xCCCC0003)
        self.assertEqual(out.restored_high_0x2dd4, 0xDDDD0004)
        self.assertEqual(out.stored_arg_r1_0x2db8, 0x11111111)
        self.assertEqual(out.stored_arg_r2_0x2dbc, 0x22222222)

    def test_local_call_branch_tail_skips_fallback_when_predicate_succeeds(self) -> None:
        self.assertModel59c530(1, 0)

    def test_local_call_branch_tail_calls_fallback_when_predicate_misses(self) -> None:
        self.assertModel59c530(0, 1)

    def assertModel(self, input_row: Inputs) -> None:
        out = self.model(input_row)
        deltas = [int(x) for x in input_row.delta_words]
        coeffs = [float(x) for x in input_row.coefficients]

        expected_r4 = input_row.r1 - input_row.r0
        expected_r0 = input_row.r0 - deltas[0] - deltas[1]
        expected_r2 = expected_r0 - deltas[2]
        expected_s4 = input_row.s3 - input_row.s4
        expected_s5 = expected_s4 - float(deltas[0])
        expected_s6 = expected_s5 - float(deltas[1]) - float(deltas[2] * deltas[2])
        expected_s16 = (
            input_row.s16
            - input_row.s4 * input_row.s2
            - float(deltas[0]) * coeffs[0]
            - float(deltas[1]) * coeffs[1]
            - float(deltas[2]) * coeffs[2]
        )

        self.assertEqual(out.r4, expected_r4)
        self.assertEqual(out.r0, expected_r0)
        self.assertEqual(out.r2, expected_r2)
        self.assertEqual(list(out.stack_zero_words), [0, 0, 0])
        self.assertEqual(out.branch_to_0x0059a45c, int(expected_r2 >= 10))
        self.assertTrue(math.isclose(out.s4, expected_s4, rel_tol=1e-6))
        self.assertTrue(math.isclose(out.s5, expected_s5, rel_tol=1e-6))
        self.assertTrue(math.isclose(out.s6, expected_s6, rel_tol=1e-6))
        self.assertTrue(math.isclose(out.s7, float(deltas[2]), rel_tol=1e-6))
        self.assertTrue(math.isclose(out.s16, expected_s16, rel_tol=1e-6))

    def test_branch_taken_case(self) -> None:
        self.assertModel(
            Inputs(
                100,
                130,
                1.5,
                20.0,
                3.0,
                50.0,
                (ctypes.c_uint32 * 3)(10, 20, 30),
                (ctypes.c_float * 3)(0.25, 0.5, 0.75),
            )
        )

    def test_branch_not_taken_case(self) -> None:
        self.assertModel(
            Inputs(
                42,
                45,
                -0.5,
                7.0,
                -2.0,
                12.0,
                (ctypes.c_uint32 * 3)(12, 15, 20),
                (ctypes.c_float * 3)(1.0, -2.0, 0.125),
            )
        )

    def test_zero_delta_case(self) -> None:
        self.assertModel(
            Inputs(
                10,
                11,
                0.0,
                4.0,
                4.0,
                -3.5,
                (ctypes.c_uint32 * 3)(0, 0, 0),
                (ctypes.c_float * 3)(3.0, 5.0, 7.0),
            )
        )

    def assertModel59c060(self, input_row: Inputs59c060) -> None:
        mask = 0xFFFFFFFF
        out = self.model_59c060(input_row)
        expected_lr = (input_row.sl - input_row.ip) & mask
        expected_ip = (input_row.r1 - input_row.ip) & mask
        expected_r2 = (input_row.sl - input_row.r3) & mask
        expected_r2 = (expected_r2 * expected_ip) & mask
        expected_r2 = (expected_r2 + expected_lr * input_row.r3) & mask
        expected_r3 = (expected_lr + ((expected_lr << 1) & mask)) & mask
        expected_r3 = (expected_r3 << 4) & mask

        self.assertEqual(out.lr, expected_lr)
        self.assertEqual(out.ip, expected_ip)
        self.assertEqual(out.r2, expected_r2)
        self.assertEqual(out.r3, expected_r3)
        self.assertEqual(out.branch_to_0x0059c086, 1)

    def test_0x59c060_integer_cluster(self) -> None:
        self.assertModel59c060(Inputs59c060(37, 11, 5, 29))

    def test_0x59c060_wraparound_cluster(self) -> None:
        self.assertModel59c060(Inputs59c060(3, 0xFFFFFFF0, 17, 7))

    def assertModel59ba4a(self, input_row: Inputs59ba4a) -> None:
        out = self.model_59ba4a(input_row)
        self.assertEqual(out.r0, (input_row.r1 + 0x400) & 0xFFFFFFFF)
        self.assertEqual(out.branch_to_0x0059b8b2, int(input_row.r4 <= 1))

    def test_0x59ba4a_branch_taken_at_threshold(self) -> None:
        self.assertModel59ba4a(Inputs59ba4a(0x1234, 1))

    def test_0x59ba4a_branch_taken_for_negative_r4(self) -> None:
        self.assertModel59ba4a(Inputs59ba4a(0x20, -7))

    def test_0x59ba4a_branch_not_taken(self) -> None:
        self.assertModel59ba4a(Inputs59ba4a(0x1234, 2))

    def test_0x59ba4a_r0_wraparound(self) -> None:
        self.assertModel59ba4a(Inputs59ba4a(0xFFFFFE80, 0))

    def assertModel59a3d2(self, input_row: Inputs59a3d2) -> None:
        out = self.model_59a3d2(input_row)
        shifted_lr = (input_row.stack_word_0x10c & 0xFFFFFFFF) << 1
        expected_lr = ctypes.c_int32(shifted_lr & 0xFFFFFFFF).value
        expected_s9 = input_row.s16 + input_row.stack_float_0x4c
        expected_s10 = float(expected_lr) + input_row.s6 + 1.0
        expected_s9_squared = expected_s9 * expected_s9
        expected_s11 = expected_s9_squared * input_row.s8
        expected_s12 = expected_s10 * input_row.s7

        self.assertEqual(out.r2, 1)
        self.assertEqual(out.lr, expected_lr)
        self.assertTrue(math.isclose(out.s9, expected_s9_squared, rel_tol=1e-6))
        self.assertTrue(math.isclose(out.s10, expected_s10, rel_tol=1e-6))
        self.assertTrue(math.isclose(out.s11, expected_s11, rel_tol=1e-6))
        self.assertTrue(math.isclose(out.s12, expected_s12, rel_tol=1e-6))
        self.assertEqual(
            out.branch_to_0x0059a420,
            int(expected_s12 >= expected_s11),
        )

    def test_0x59a3d2_branch_taken(self) -> None:
        self.assertModel59a3d2(Inputs59a3d2(3, 0.25, 1.5, 2.0, 0.5, 0.75))

    def test_0x59a3d2_branch_not_taken(self) -> None:
        self.assertModel59a3d2(Inputs59a3d2(1, 5.0, 0.0, 1.0, 3.0, 4.0))

    def test_0x59a3d2_negative_stack_word(self) -> None:
        self.assertModel59a3d2(Inputs59a3d2(-4, -1.25, 2.5, -0.5, 1.5, 3.0))

    def test_0x4ec718_call_shim(self) -> None:
        out = self.model_4ec718(Inputs4ec718(0xA5A55A5A))
        self.assertEqual(out.r0, 0xA5A55A5A)
        self.assertEqual(out.call_target, 0x0044104C)

    def test_0x4ec774_call_shim(self) -> None:
        out = self.model_4ec774(Inputs4ec774(0x13572468))
        self.assertEqual(out.sb, 0x13572468)
        self.assertEqual(out.r0, 0x13572468)
        self.assertEqual(out.r1, 0)
        self.assertEqual(out.r2, 3)
        self.assertEqual(out.call_target, 0x0043F09A)


if __name__ == "__main__":
    unittest.main()
