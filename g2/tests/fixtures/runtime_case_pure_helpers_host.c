/* SPDX-License-Identifier: MIT */
#include "runtime_case_pure_helpers.h"

#include <stdint.h>


struct sink {
    uint8_t bytes[16];
    size_t used;
};


static void emit(uint8_t value, void *context)
{
    struct sink *sink = context;
    if (sink->used < sizeof(sink->bytes)) {
        sink->bytes[sink->used++] = value;
    }
}


int main(void)
{
    uint8_t frame[4] = {0x5AU, 0xA5U, 0x01U, 0U};
    uint8_t large_frame[130];
    struct sink sink = {{0}, 0U};
    const uint64_t value = UINT64_C(0xFEDCBA9876543210);
    uint32_t index;

    for (index = 0U; index <= 80U; ++index) {
        uint64_t left = index < 64U ? value << index : 0U;
        uint64_t right = index < 64U ? value >> index : 0U;
        if (open_cfw_case_shift_left64(value, index) != left) return 1;
        if (open_cfw_case_shift_right64(value, index) != right) return 2;
    }
    if (open_cfw_case_finalize_length_checksum(NULL, 1U)) return 3;
    if (open_cfw_case_finalize_length_checksum(frame, 0U)) return 4;
    if (open_cfw_case_finalize_length_checksum(frame, 131U)) return 5;
    if (!open_cfw_case_finalize_length_checksum(frame, sizeof(frame))) return 6;
    if (frame[3] != (uint8_t)(4U + 0x7DU + 0x5AU + 0xA5U + 1U)) return 7;
    for (index = 0U; index < sizeof(large_frame); ++index) {
        large_frame[index] = (uint8_t)index;
    }
    if (!open_cfw_case_finalize_length_checksum(
            large_frame, sizeof(large_frame))) return 8;
    {
        uint8_t expected = (uint8_t)(sizeof(large_frame) + 0x7DU);
        for (index = 0U; index + 1U < sizeof(large_frame); ++index) {
            expected = (uint8_t)(expected + (uint8_t)index);
        }
        if (large_frame[sizeof(large_frame) - 1U] != expected) return 9;
    }
    for (index = 0U; index < 256U; ++index) {
        uint8_t expected = 0U;
        if (index >= (uint32_t)'0' && index <= (uint32_t)'9') {
            expected = (uint8_t)(index - (uint32_t)'0');
        } else if (index >= (uint32_t)'a' && index <= (uint32_t)'f') {
            expected = (uint8_t)(index - (uint32_t)'a' + 10U);
        } else if (index >= (uint32_t)'A' && index <= (uint32_t)'F') {
            expected = (uint8_t)(index - (uint32_t)'A' + 10U);
        }
        if (open_cfw_case_hex_value((uint8_t)index) != expected) return 10;
    }
    if (open_cfw_case_starts_with_de(NULL) ||
        open_cfw_case_starts_with_de("") ||
        !open_cfw_case_starts_with_de("de") ||
        !open_cfw_case_starts_with_de("De") ||
        !open_cfw_case_starts_with_de("dE") ||
        !open_cfw_case_starts_with_de("DE") ||
        open_cfw_case_starts_with_de("DF")) return 11;
    if (open_cfw_case_emit_left_padding(-1, 0x2000U, emit, &sink) != 0U ||
        open_cfw_case_emit_left_padding(
            INT32_MIN, 0x2000U, emit, &sink) != 0U) return 12;
    if (open_cfw_case_emit_right_padding(-1, 0U, emit, &sink) != 0U ||
        open_cfw_case_emit_right_padding(
            INT32_MIN, 0U, emit, &sink) != 0U) return 13;
    if (open_cfw_case_emit_left_padding(3, 0U, emit, &sink) != 0U) return 14;
    if (open_cfw_case_emit_right_padding(3, 0x2000U, emit, &sink) != 0U) return 15;
    if (open_cfw_case_emit_left_padding(3, 0x2000U, NULL, &sink) != 0U) return 16;
    if (open_cfw_case_emit_left_padding(3, 0x2000U, emit, &sink) != 3U) return 17;
    if (open_cfw_case_emit_right_padding(2, 0x10000U, emit, &sink) != 2U) return 18;
    if (open_cfw_case_emit_right_padding(2, 0U, emit, &sink) != 2U) return 19;
    if (sink.used != 7U || sink.bytes[0] != ' ' ||
        sink.bytes[3] != '0' || sink.bytes[5] != ' ') return 20;
    return 0;
}
