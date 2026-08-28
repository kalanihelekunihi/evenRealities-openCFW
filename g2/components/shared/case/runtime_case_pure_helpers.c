/*
 * SPDX-License-Identifier: MIT
 *
 * Clean-room charging-case pure helpers derived from authenticated behavioral
 * contracts. This original C contains no stock instruction encodings and is
 * an isolated source candidate, not a production-routed replacement.
 */
#include "runtime_case_pure_helpers.h"


uint64_t open_cfw_case_shift_left64(uint64_t value, uint32_t shift)
{
    return shift < 64U ? value << shift : 0U;
}


uint64_t open_cfw_case_shift_right64(uint64_t value, uint32_t shift)
{
    return shift < 64U ? value >> shift : 0U;
}


bool open_cfw_case_finalize_length_checksum(uint8_t *frame, size_t length)
{
    size_t index;
    uint8_t checksum;
    if (frame == NULL || length == 0U || length > 130U) {
        return false;
    }
    checksum = (uint8_t)(length + 0x7DU);
    for (index = 0U; index + 1U < length; ++index) {
        checksum = (uint8_t)(checksum + frame[index]);
    }
    frame[length - 1U] = checksum;
    return true;
}


uint8_t open_cfw_case_hex_value(uint8_t character)
{
    if (character >= (uint8_t)'0' && character <= (uint8_t)'9') {
        return (uint8_t)(character - (uint8_t)'0');
    }
    if (character >= (uint8_t)'a' && character <= (uint8_t)'f') {
        return (uint8_t)(character - (uint8_t)'a' + 10U);
    }
    if (character >= (uint8_t)'A' && character <= (uint8_t)'F') {
        return (uint8_t)(character - (uint8_t)'A' + 10U);
    }
    return 0U;
}


bool open_cfw_case_starts_with_de(const char *text)
{
    if (text == NULL) {
        return false;
    }
    return (text[0] == 'd' || text[0] == 'D')
        && (text[1] == 'e' || text[1] == 'E');
}


static size_t emit_repeated(int32_t count, uint8_t value,
                            open_cfw_case_emit_fn emit, void *context)
{
    int32_t emitted;
    if (emit == NULL) {
        return 0U;
    }
    for (emitted = 0U; emitted < count; ++emitted) {
        emit(value, context);
    }
    return (size_t)emitted;
}


size_t open_cfw_case_emit_left_padding(int32_t count, uint32_t flags,
                                       open_cfw_case_emit_fn emit,
                                       void *context)
{
    if ((flags & 0x2000U) == 0U) {
        return 0U;
    }
    return emit_repeated(count, (uint8_t)' ', emit, context);
}


size_t open_cfw_case_emit_right_padding(int32_t count, uint32_t flags,
                                        open_cfw_case_emit_fn emit,
                                        void *context)
{
    uint8_t value;
    if ((flags & 0x2000U) != 0U) {
        return 0U;
    }
    value = (flags & 0x10000U) != 0U ? (uint8_t)'0' : (uint8_t)' ';
    return emit_repeated(count, value, emit, context);
}
