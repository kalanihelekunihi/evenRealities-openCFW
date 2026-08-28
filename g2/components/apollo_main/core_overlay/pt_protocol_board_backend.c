/* SPDX-License-Identifier: MIT */
#include "pt_protocol_board_backend.h"
#include "pt_protocol_board_leaf_candidates.h"


enum {
    OPEN_CFW_PT_SYSTEM_DATA_PRODUCT_SERIAL = 0U,
    OPEN_CFW_PT_SYSTEM_DATA_TIME = 1U,
    OPEN_CFW_PT_SYSTEM_DATA_PANEL_CURRENT = 5U
};


static void copy_bytes(void *destination, const void *source, size_t length)
{
    uint8_t *output = destination;
    const uint8_t *input = source;
    size_t index;
    for (index = 0U; index < length; ++index) output[index] = input[index];
}


static uint32_t read_u32_le(const uint8_t *input)
{
    return (uint32_t)input[0] |
        ((uint32_t)input[1] << 8U) |
        ((uint32_t)input[2] << 16U) |
        ((uint32_t)input[3] << 24U);
}


static void write_u32_le(uint8_t *output, uint32_t value)
{
    output[0] = (uint8_t)value;
    output[1] = (uint8_t)(value >> 8U);
    output[2] = (uint8_t)(value >> 16U);
    output[3] = (uint8_t)(value >> 24U);
}


static int32_t read_i32_le(const uint8_t *input)
{
    return (int32_t)read_u32_le(input);
}


static uint32_t absolute_i32(int32_t value)
{
    return value < 0 ? (uint32_t)(0U - (uint32_t)value) : (uint32_t)value;
}


static int32_t divide_i32_by_10(int32_t value)
{
    uint32_t dividend = absolute_i32(value);
    uint32_t quotient = 0U;
    uint32_t remainder = 0U;
    unsigned int bit = 32U;
    while (bit != 0U) {
        --bit;
        remainder = (remainder << 1U) | ((dividend >> bit) & 1U);
        if (remainder >= 10U) {
            remainder -= 10U;
            quotient |= (uint32_t)1U << bit;
        }
    }
    return value < 0 ? (int32_t)(0U - quotient) : (int32_t)quotient;
}


static uint32_t divide_u32_by_1000(uint32_t value)
{
    uint32_t quotient = 0U;
    uint32_t remainder = 0U;
    unsigned int bit = 32U;
    while (bit != 0U) {
        --bit;
        remainder = (remainder << 1U) | ((value >> bit) & 1U);
        if (remainder >= 1000U) {
            remainder -= 1000U;
            quotient |= (uint32_t)1U << bit;
        }
    }
    return quotient;
}


static uint64_t divide_u64_by_u32(uint64_t value, uint32_t denominator)
{
    uint64_t quotient = 0U;
    uint64_t remainder = 0U;
    unsigned int bit;
    if (denominator == 0U) return 0U;
    for (bit = 0U; bit < 64U; ++bit) {
        remainder = (remainder << 1U) |
            ((value & 0x8000000000000000ULL) != 0U);
        value <<= 1U;
        quotient <<= 1U;
        if (remainder >= denominator) {
            remainder -= denominator;
            quotient |= 1U;
        }
    }
    return quotient;
}


static uint64_t multiply_u32_u32(uint32_t left, uint32_t right)
{
    uint64_t result = 0U;
    uint64_t addend = left;
    while (right != 0U) {
        if ((right & 1U) != 0U) result += addend;
        addend <<= 1U;
        right >>= 1U;
    }
    return result;
}


static uint64_t shift_left_u64(uint64_t value, unsigned int shift);
static uint64_t shift_right_u64(uint64_t value, unsigned int shift);


static uint32_t rounded_positive_double_to_u32(double value)
{
    union { double value; uint64_t bits; } decoded = {value};
    uint64_t fraction = decoded.bits & 0x000FFFFFFFFFFFFFULL;
    unsigned int exponent = (unsigned int)(
        (decoded.bits >> 52U) & 0x7FFU);
    int power;
    uint64_t significand;
    uint64_t integer;
    uint64_t remainder;
    unsigned int shift;
    if ((decoded.bits >> 63U) != 0U || exponent == 0x7FFU) return 0U;
    if (exponent == 0U) return 0U;
    power = (int)exponent - 1023;
    if (power < -1) return 0U;
    if (power > 31) return 0xFFFFFFFFU;
    significand = fraction | 0x0010000000000000ULL;
    if (power >= 52) {
        integer = significand;
        shift = (unsigned int)(power - 52);
        while (shift != 0U) { integer <<= 1U; --shift; }
    } else {
        shift = (unsigned int)(52 - power);
        integer = shift_right_u64(significand, shift);
        remainder = significand - shift_left_u64(integer, shift);
        if (shift != 0U && remainder >=
                shift_left_u64(1ULL, shift - 1U)) ++integer;
    }
    return integer > 0xFFFFFFFFULL ? 0xFFFFFFFFU : (uint32_t)integer;
}


static uint32_t read_ambient_measurement(
    const struct open_cfw_pt_board_calls *calls)
{
    return calls->ambient_read == NULL ? 0U :
        rounded_positive_double_to_u32(calls->ambient_read());
}


static int copy_text(char *destination, size_t capacity, const char *source)
{
    size_t index = 0U;
    if (destination == NULL || capacity == 0U || source == NULL)
        return OPEN_CFW_PT_INVALID_ARGUMENT;
    while (index + 1U < capacity && source[index] != '\0') {
        destination[index] = source[index];
        ++index;
    }
    destination[index] = '\0';
    return OPEN_CFW_PT_OK;
}


static int parse_version_4(const char *text, uint8_t output[4])
{
    unsigned int part;
    size_t position = 0U;
    if (text == NULL || output == NULL) return 0;
    for (part = 0U; part < 4U; ++part) {
        unsigned int value = 0U;
        unsigned int digits = 0U;
        while (text[position] >= '0' && text[position] <= '9') {
            value = value * 10U + (unsigned int)(text[position] - '0');
            if (value > 255U) return 0;
            ++position;
            ++digits;
        }
        if (digits == 0U || (part < 3U && text[position] != '.') ||
            (part == 3U && text[position] != '\0')) return 0;
        output[part] = (uint8_t)value;
        if (part < 3U) ++position;
    }
    return 1;
}


static int text_equal_32(const char left[32], const char right[32])
{
    size_t index;
    for (index = 0U; index < 32U; ++index) {
        if (left[index] != right[index]) return 0;
        if (left[index] == '\0') return 1;
    }
    return 1;
}


static void reset_audio_file_state(struct open_cfw_pt_board_backend *board)
{
    const struct open_cfw_pt_board_calls *calls = board->calls;
    size_t index;
    if (calls->audio_handle_slot != NULL &&
        *calls->audio_handle_slot != NULL && calls->file_close != NULL)
        (void)calls->file_close(*calls->audio_handle_slot);
    if (calls->audio_handle_slot != NULL) *calls->audio_handle_slot = NULL;
    if (calls->audio_active != NULL) *calls->audio_active = 0U;
    if (calls->audio_length_state != NULL) *calls->audio_length_state = 0U;
    if (calls->audio_offset_state != NULL) *calls->audio_offset_state = 0U;
    if (calls->audio_path_state_32 != NULL)
        for (index = 0U; index < 32U; ++index)
            calls->audio_path_state_32[index] = 0U;
}


static __attribute__((noinline)) uint64_t shift_left_u64(
    uint64_t value, unsigned int shift)
{
#pragma clang loop unroll(disable)
    while (shift != 0U) {
        value <<= 1U;
        --shift;
    }
    return value;
}


static __attribute__((noinline)) uint64_t shift_right_u64(
    uint64_t value, unsigned int shift)
{
#pragma clang loop unroll(disable)
    while (shift != 0U) {
        value >>= 1U;
        --shift;
    }
    return value;
}


static int scaled_less_than_epsilon(uint64_t difference, unsigned int exponent)
{
    const uint64_t epsilon_mantissa = 0x00A7C5ACULL;
    if (difference == 0U) return 1;
    if (exponent >= 110U) {
        unsigned int shift = exponent - 110U;
        if (shift >= 64U || difference >
            shift_right_u64(epsilon_mantissa - 1U, shift)) return 0;
        return 1;
    }
    {
        unsigned int shift = 110U - exponent;
        if (shift >= 64U) return 1;
        return difference < shift_left_u64(epsilon_mantissa, shift);
    }
}


static int float_close(float left, float right)
{
    union { float value; uint32_t bits; } a = {left}, b = {right};
    uint32_t ma;
    uint32_t mb;
    unsigned int ea;
    unsigned int eb;
    unsigned int delta;
    uint64_t difference;
    if ((a.bits & 0x7F800000U) == 0x7F800000U ||
        (b.bits & 0x7F800000U) == 0x7F800000U) return 0;
    ea = (a.bits >> 23U) & 0xFFU;
    eb = (b.bits >> 23U) & 0xFFU;
    ma = a.bits & 0x7FFFFFU;
    mb = b.bits & 0x7FFFFFU;
    if (ea != 0U) ma |= 0x800000U; else ea = 1U;
    if (eb != 0U) mb |= 0x800000U; else eb = 1U;
    if (ma == 0U && mb == 0U) return 1;
    if ((a.bits ^ b.bits) >> 31U) {
        if (ea >= eb) {
            delta = ea - eb;
            if (delta >= 40U) return 0;
            difference = shift_left_u64((uint64_t)ma, delta) + mb;
            return scaled_less_than_epsilon(difference, eb);
        }
        delta = eb - ea;
        if (delta >= 40U) return 0;
        difference = shift_left_u64((uint64_t)mb, delta) + ma;
        return scaled_less_than_epsilon(difference, ea);
    }
    if (ea == eb) {
        difference = ma >= mb ? (uint64_t)(ma - mb) : (uint64_t)(mb - ma);
        return scaled_less_than_epsilon(difference, ea);
    }
    if (ea > eb) {
        delta = ea - eb;
        if (delta >= 40U) return 0;
        difference = shift_left_u64((uint64_t)ma, delta) - mb;
        return scaled_less_than_epsilon(difference, eb);
    }
    delta = eb - ea;
    if (delta >= 40U) return 0;
    difference = shift_left_u64((uint64_t)mb, delta) - ma;
    return scaled_less_than_epsilon(difference, ea);
}


static int perform(
    enum open_cfw_pt_platform_operation operation,
    uintptr_t a0, uintptr_t a1, uintptr_t a2, uintptr_t a3, uintptr_t a4,
    void *context)
{
    struct open_cfw_pt_board_backend *board = context;
    const struct open_cfw_pt_board_calls *calls;
    (void)a4;
    if (board == NULL) return OPEN_CFW_PT_INVALID_ARGUMENT;
    calls = board->calls;
    if (calls == NULL) return OPEN_CFW_PT_INVALID_ARGUMENT;

    switch (operation) {
    case OPEN_CFW_PT_OP_SET_BOX_DETECTED:
        if (calls->set_local_lid == NULL) break;
        calls->set_local_lid((uint8_t)(a0 != 0U));
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_CODEC_DELAY:
        if (calls->codec_mic_delay_1bit == NULL) break;
        return calls->codec_mic_delay_1bit() == 0 ?
            OPEN_CFW_PT_OK : OPEN_CFW_PT_HANDLER_FAILED;
    case OPEN_CFW_PT_OP_STORE_TERMINAL_MODE:
        /* Stock command 0x61 writes system-data index 5 (panel current). */
        if (calls->system_data_write == NULL) break;
        {
            uint8_t value = (uint8_t)a0;
            return calls->system_data_write(
                OPEN_CFW_PT_SYSTEM_DATA_PANEL_CURRENT, &value) == 0 ?
                OPEN_CFW_PT_OK : OPEN_CFW_PT_HANDLER_FAILED;
        }
    case OPEN_CFW_PT_OP_LOAD_TERMINAL_MODE:
        if (a0 == 0U || calls->system_data_get == NULL) break;
        {
            const uint8_t *stored = calls->system_data_get(
                OPEN_CFW_PT_SYSTEM_DATA_PANEL_CURRENT);
            if (stored == NULL) break;
            *(uint8_t *)a0 = *stored;
            return OPEN_CFW_PT_OK;
        }
    case OPEN_CFW_PT_OP_POST_INPUT_MESSAGE:
        if (calls->post_input_message_id3 == NULL) break;
        calls->post_input_message_id3();
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_GET_PRODUCT_MODE:
        if (a0 == 0U || calls->product_mode_read == NULL) break;
        *(uint8_t *)a0 = calls->product_mode_read();
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_SET_PRODUCT_MODE:
        if (calls->product_mode_update == NULL) break;
        calls->product_mode_update((uint8_t)a0);
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_PRODUCTION_RESET:
        if (calls->production_reset == NULL) break;
        calls->production_reset();
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_READ_TOUCH_DIAGNOSTIC:
        if (a0 == 0U || a1 == 0U || calls->touch_proximity == NULL ||
            calls->touch_read_differences == NULL) break;
        {
            uint8_t raw[10];
            if (calls->touch_read_differences(raw) != 0) break;
            *(uint8_t *)a0 = calls->touch_proximity();
            *(int16_t *)a1 = (int16_t)((uint16_t)raw[8] |
                ((uint16_t)raw[9] << 8U));
            return OPEN_CFW_PT_OK;
        }
    case OPEN_CFW_PT_OP_WRITE_PSN_14:
        if (a0 == 0U || a1 != 14U || calls->psn_write_otp == NULL ||
            calls->system_data_write == NULL ||
            calls->system_data_read == NULL || calls->memory_compare == NULL)
            break;
        {
            char serial[15];
            const void *stored;
            copy_bytes(serial, (const void *)a0, 14U);
            serial[14] = '\0';
            if (calls->psn_write_otp(serial) != 0 ||
                calls->system_data_write(
                    OPEN_CFW_PT_SYSTEM_DATA_PRODUCT_SERIAL, serial) != 0)
                break;
            stored = calls->system_data_read(
                OPEN_CFW_PT_SYSTEM_DATA_PRODUCT_SERIAL);
            if (stored == NULL ||
                calls->memory_compare(serial, stored, 14U) != 0) break;
            return OPEN_CFW_PT_OK;
        }
    case OPEN_CFW_PT_OP_WRITE_SENSOR_CALIBRATION_36:
        if (a0 == 0U || a1 != 36U ||
            calls->sensor_calibration_update == NULL) break;
        {
            float matrix[9];
            copy_bytes(matrix, (const void *)a0, 36U);
            calls->sensor_calibration_update(NULL, NULL, matrix);
            return OPEN_CFW_PT_OK;
        }
    case OPEN_CFW_PT_OP_BUZZER_TEST:
        if (a0 != 0U) {
            if (calls->buzzer_start == NULL) break;
            calls->buzzer_start((uint32_t)a1, (uint8_t)a2);
        } else {
            if (calls->buzzer_stop == NULL) break;
            calls->buzzer_stop();
        }
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_BUZZER_READ:
        if (a0 == 0U || a1 == 0U || calls->buzzer_frequency_get == NULL ||
            calls->buzzer_duty_get == NULL) break;
        *(uint32_t *)a0 = calls->buzzer_frequency_get();
        *(uint8_t *)a1 = calls->buzzer_duty_get();
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_BUZZER_WRITE:
        if (calls->buzzer_update == NULL) break;
        calls->buzzer_update((uint32_t)a0, (uint8_t)a1);
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_UPDATE_ONBOARDING:
        if (calls->onboarding_update == NULL) break;
        {
            uint8_t value = (uint8_t)(a0 != 0U);
            return calls->onboarding_update(0U, &value) == 0 ?
                OPEN_CFW_PT_OK : OPEN_CFW_PT_HANDLER_FAILED;
        }
    case OPEN_CFW_PT_OP_SET_CHARGER_TEST:
        if (a0 != 0U) {
            if (calls->charger_test_enable == NULL) break;
            calls->charger_test_enable();
        } else {
            if (calls->charger_test_disable == NULL) break;
            calls->charger_test_disable();
        }
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_READ_IDENTIFIER_6:
        if (a0 == 0U || a1 != 6U || calls->identifier_record_link == NULL ||
            *calls->identifier_record_link == NULL) break;
        copy_bytes((void *)a0, *calls->identifier_record_link + 1U, 6U);
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_READ_SYSTEM_TEXT:
        if (a0 > 1U || a1 == 0U || calls->system_data_get == NULL) break;
        return copy_text((char *)a1, (size_t)a2,
            calls->system_data_get((uint8_t)a0));
    case OPEN_CFW_PT_OP_SET_SYNC_READY:
        if (calls->sync_ready == NULL) break;
        *calls->sync_ready = (uint8_t)(a0 != 0U);
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_READ_BOOLEAN_FLAG:
        if (a0 == 0U || calls->boolean_flag == NULL) break;
        *(uint8_t *)a0 = (uint8_t)(*calls->boolean_flag != 0U);
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_READ_PAIR_STATE:
        if (a0 == 0U || a1 == 0U || calls->pair_state == NULL) break;
        *(uint8_t *)a0 = calls->pair_state[0x2CU];
        *(uint8_t *)a1 = calls->pair_state[0x2DU];
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_READ_SESSION_STATUS:
        if (a0 == 0U || calls->session_record == NULL) break;
        {
            struct open_cfw_pt_session_status *status =
                (struct open_cfw_pt_session_status *)a0;
            const uint8_t *record = calls->session_record;
            status->state = record[0xAAU];
            status->reference.hour = read_u32_le(record + 0x48U);
            status->reference.minute = read_u32_le(record + 0x4CU);
            status->reference.second = read_u32_le(record + 0x50U);
            status->first.hour = read_u32_le(record + 0x70U);
            status->first.minute = read_u32_le(record + 0x74U);
            status->first.second = read_u32_le(record + 0x78U);
            status->second.hour = read_u32_le(record + 0x98U);
            status->second.minute = read_u32_le(record + 0x9CU);
            status->second.second = read_u32_le(record + 0xA0U);
            status->flag_a = record[0xA9U];
            status->flag_b = record[0xA8U];
            status->flag_c = record[0xABU];
            return OPEN_CFW_PT_OK;
        }
    case OPEN_CFW_PT_OP_READ_DIAGNOSTIC_BLOB_36:
        if (a0 == 0U || a1 != 36U || calls->diagnostic_blob_36 == NULL)
            break;
        copy_bytes((void *)a0, calls->diagnostic_blob_36, 36U);
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_READ_FONT_VERSION:
        if (a1 == 0U || calls->font_version == NULL) break;
        return copy_text((char *)a1, (size_t)a2, calls->font_version());
    case OPEN_CFW_PT_OP_READ_DISPLAY_VALUE:
        if (a0 == 0U || calls->display_value == NULL) break;
        *(uint8_t *)a0 = *calls->display_value;
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_SET_DISPLAY_RUNTIME_FLAG:
        if (calls->display_runtime_flag == NULL) break;
        *calls->display_runtime_flag = (uint8_t)(a0 != 0U);
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_GET_AGING_MODE:
        if (a0 == 0U || calls->aging_mode == NULL) break;
        *(uint8_t *)a0 = (uint8_t)(*calls->aging_mode != 0U);
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_SET_TEST_SCREEN:
        if (calls->screen_show == NULL || calls->screen_hide == NULL ||
            calls->display_state == NULL ||
            calls->display_brightness == NULL ||
            calls->display_stage_1 == NULL ||
            calls->display_stage_2 == NULL ||
            calls->display_stage_3 == NULL) break;
        if (a1 != 0U) {
            uint32_t delay = a0 == 0x10FU ? 50U : 100U;
            uint32_t brightness = a0 == 0x10FU ? 10U : 0x3FU;
            calls->screen_show((uint16_t)a0, 0U, 0U);
            calls->display_brightness(delay, 0x1BBCU, brightness);
            calls->display_stage_1(0x60U);
            calls->display_stage_2(0U, 0U);
            calls->display_stage_3(0x20U);
        } else {
            const uint8_t *state = calls->display_state();
            if (state != NULL && *state == 1U)
                calls->screen_hide((uint16_t)a0, 0U, 0U);
        }
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_SET_DISPLAY_PARAMETERS:
        if (calls->pair_state_mutable == NULL ||
            calls->display_state == NULL || calls->screen_show == NULL ||
            calls->display_brightness == NULL ||
            calls->display_stage_1 == NULL ||
            calls->display_stage_2 == NULL ||
            calls->display_stage_3 == NULL ||
            calls->display_offset == NULL) break;
        calls->pair_state_mutable[0x2CU] = (uint8_t)a0;
        calls->pair_state_mutable[0x2DU] = (uint8_t)a1;
        if (a2 != 0U) {
            uint8_t first = (uint8_t)a0;
            uint8_t second = (uint8_t)a1;
            if (calls->system_data_write == NULL ||
                calls->system_data_write(3U, &first) != 0 ||
                calls->system_data_write(4U, &second) != 0) break;
        }
        {
            const uint8_t *state = calls->display_state();
            if (state == NULL || *state != 1U) {
                calls->screen_show(0x10BU, 0U, 0U);
                calls->display_brightness(100U, 0x1BBCU, 0x3FU);
                calls->display_stage_1(0x60U);
                calls->display_stage_2(0U, 0U);
                calls->display_stage_3(0x20U);
            }
        }
        calls->display_offset((uint8_t)a0, (uint8_t)a1);
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_SET_AGING_MODE:
        if (calls->aging_mode_mutable == NULL ||
            calls->session_record_mutable == NULL ||
            calls->time_capture == NULL || calls->system_data_write == NULL ||
            calls->screen_show == NULL || calls->screen_hide == NULL) break;
        {
            uint8_t captured[40];
            uint8_t *record = calls->session_record_mutable;
            if (a0 != 0U) {
                if (calls->system_data_reset_aging == NULL ||
                    calls->time_configure == NULL ||
                    calls->time_configuration == NULL) break;
                *calls->aging_mode_mutable = 1U;
                calls->system_data_reset_aging();
                calls->time_configure(read_u32_le(
                    calls->time_configuration + 4U),
                    (int)(int8_t)calls->time_configuration[8U]);
                calls->screen_show(0x104U, 0U, 0U);
                calls->time_capture(captured);
                copy_bytes(record + 0x30U, captured, sizeof(captured));
                record[0xAAU] = (uint8_t)(record[0xAAU] + 1U);
                if (calls->system_data_write(6U, record + 0x30U) != 0)
                    break;
            } else {
                *calls->aging_mode_mutable = 0U;
                calls->screen_hide(0x104U, 0U, 0U);
                calls->time_capture(captured);
                record[0xABU] = 1U;
                copy_bytes(record + 0x58U, captured, sizeof(captured));
                if (calls->system_data_write(7U, record + 0x58U) != 0)
                    break;
            }
            return OPEN_CFW_PT_OK;
        }
    case OPEN_CFW_PT_OP_SET_BOX_STATE:
        if (calls->set_local_level == NULL ||
            calls->set_local_charging == NULL) break;
        calls->set_local_level((uint8_t)a0);
        calls->set_local_charging((uint8_t)a1);
        if (a2 != 0U) {
            if (calls->set_local_lid == NULL) break;
            calls->set_local_lid((uint8_t)(a3 != 0U));
        }
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_READ_BOX_SUMMARY_7:
        if (a0 == 0U || a1 != 7U || calls->pair_state == NULL) break;
        {
            uint8_t *output = (uint8_t *)a0;
            int32_t first = read_i32_le(calls->pair_state + 0x0CU);
            int32_t second = read_i32_le(calls->pair_state + 0x10U);
            uint32_t magnitude = absolute_i32(second);
            output[0] = calls->pair_state[4U];
            output[1] = (uint8_t)(divide_i32_by_10(read_i32_le(
                calls->pair_state + 8U)) + 0x38);
            output[2] = (uint8_t)(first < 1);
            output[3] = (uint8_t)absolute_i32(first);
            output[4] = (uint8_t)(second > 0);
            output[5] = (uint8_t)(magnitude >> 8U);
            output[6] = (uint8_t)magnitude;
            return OPEN_CFW_PT_OK;
        }
    case OPEN_CFW_PT_OP_READ_BOX_DETAIL_6:
        if (a0 == 0U || a1 != 6U || calls->pair_state == NULL) break;
        {
            uint8_t *output = (uint8_t *)a0;
            int32_t selector = read_i32_le(calls->pair_state);
            int32_t value = read_i32_le(calls->pair_state + 0x0CU);
            if ((selector == 0 && value < 0) ||
                (selector != 0 && value > 0)) value = -1;
            output[0] = (uint8_t)(read_i32_le(
                calls->pair_state + 0x14U) != 0);
            output[1] = calls->pair_state[9U];
            output[2] = calls->pair_state[8U];
            output[3] = calls->pair_state[4U];
            output[4] = (uint8_t)(value < 1);
            output[5] = (uint8_t)absolute_i32(value);
            return OPEN_CFW_PT_OK;
        }
    case OPEN_CFW_PT_OP_WRITE_TIME_21:
        if (a0 == 0U || a1 != 21U || calls->system_data_write == NULL ||
            calls->system_data_read == NULL || calls->memory_compare == NULL)
            break;
        {
            const void *stored;
            if (calls->system_data_write(OPEN_CFW_PT_SYSTEM_DATA_TIME,
                    (const void *)a0) != 0) break;
            stored = calls->system_data_read(OPEN_CFW_PT_SYSTEM_DATA_TIME);
            if (stored == NULL || calls->memory_compare(
                    (const void *)a0, stored, 21U) != 0) break;
            return OPEN_CFW_PT_OK;
        }
    case OPEN_CFW_PT_OP_UART_SYNC_TEST:
        if (a0 == 0U || calls->uart_sync_write == NULL ||
            calls->delay_ticks == NULL || calls->uart_sync_state == NULL ||
            calls->uart_sync_expected == NULL || calls->memory_compare == NULL)
            break;
        {
            unsigned int remaining = 40U;
            uint8_t *state = (uint8_t *)(uintptr_t)calls->uart_sync_state;
            state[0] = 1U;
            {
                size_t index;
                for (index = 1U; index < 8U; ++index) state[index] = 0U;
            }
            (void)calls->uart_sync_write(calls->uart_sync_expected, 7U, 0U);
            while (remaining != 0U && state[0] != 0U) {
                (void)calls->delay_ticks(1U);
                --remaining;
            }
            *(uint8_t *)a0 = (uint8_t)(state[0] != 0U ||
                calls->memory_compare(state + 1U,
                    calls->uart_sync_expected, 7U) != 0);
            return OPEN_CFW_PT_OK;
        }
    case OPEN_CFW_PT_OP_LENS_SYNC_TEST:
        if (a0 == 0U || calls->lens_side == NULL ||
            calls->lens_sync_send == NULL || calls->delay_ticks == NULL ||
            calls->lens_sync_ready == NULL ||
            calls->lens_sync_template_12 == NULL) break;
        {
            uint8_t payload[12];
            uint8_t side;
            *calls->lens_sync_ready = 0U;
            copy_bytes(payload, calls->lens_sync_template_12, sizeof(payload));
            payload[4] = calls->lens_side();
            side = calls->lens_side();
            payload[5] = side == 1U ? 2U : 1U;
            (void)calls->lens_sync_send(
                0x102U, payload, (uint32_t)sizeof(payload), 0U);
            (void)calls->delay_ticks(20U);
            *(uint8_t *)a0 = (uint8_t)(*calls->lens_sync_ready == 0U);
            return OPEN_CFW_PT_OK;
        }
    case OPEN_CFW_PT_OP_CALIBRATE_AMBIENT:
        if (a1 == 0U || a2 == 0U || calls->ambient_read == NULL) break;
        {
            uint32_t measurement = read_ambient_measurement(calls);
            uint8_t status = 0U;
            *(uint32_t *)a1 = measurement;
            if (a0 == 4U) {
                if (calls->ambient_baseline == NULL) break;
                *calls->ambient_baseline = measurement;
            } else if (a0 == 1U) {
                uint64_t first;
                uint64_t second;
                uint32_t calibration;
                if (calls->ambient_baseline == NULL ||
                    calls->ambient_secondary == NULL ||
                    calls->session_record_mutable == NULL ||
                    calls->system_data_write == NULL) break;
                *calls->ambient_secondary = measurement;
                if (*calls->ambient_baseline != 0U && measurement != 0U) {
                    first = divide_u64_by_u32(
                        22156000000ULL * 1024ULL,
                        *calls->ambient_baseline);
                    second = divide_u64_by_u32(
                        4210700000ULL * 1024ULL, measurement);
                    calibration = (uint32_t)divide_u64_by_u32(
                        first + second, 2048U);
                    write_u32_le(
                        calls->session_record_mutable + 0x28U, calibration);
                    if (calls->system_data_write(2U,
                            calls->session_record_mutable + 0x28U) != 0)
                        break;
                }
            }
            if (measurement >= 80001U) status = 1U;
            else if (measurement == 0U) status = 2U;
            *(uint8_t *)a2 = status;
            return OPEN_CFW_PT_OK;
        }
    case OPEN_CFW_PT_OP_STORAGE_READY:
        if (a0 == 0U || calls->pair_state == NULL) break;
        *(uint8_t *)a0 = (uint8_t)(read_i32_le(
            calls->pair_state + 4U) >= 50);
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_STORAGE_SELF_TEST:
        if (a0 == 0U || calls->file_open == NULL ||
            calls->file_close == NULL || calls->file_read == NULL ||
            calls->file_write == NULL || calls->storage_test_path == NULL ||
            calls->file_read_mode == NULL || calls->file_write_mode == NULL)
            break;
        {
            uint32_t written_value = 1U;
            uint32_t read_value = 0U;
            void *file;
            size_t index;
            int passed = 1;
            file = calls->file_open(
                calls->storage_test_path, calls->file_write_mode);
            if (file == NULL) passed = 0;
            else {
                if (calls->file_write(&written_value, 1U, 4U, file) != 4U)
                    passed = 0;
                (void)calls->file_close(file);
            }
            if (passed) {
                file = calls->file_open(
                    calls->storage_test_path, calls->file_read_mode);
                if (file == NULL) passed = 0;
                else {
                    if (calls->file_read(&read_value, 1U, 4U, file) != 4U ||
                        read_value != written_value) passed = 0;
                    (void)calls->file_close(file);
                }
            }
            for (index = 0U; index < 4U; ++index) {
                if (calls->storage_required_paths[index] == NULL) {
                    passed = 0;
                    continue;
                }
                file = calls->file_open(calls->storage_required_paths[index],
                    calls->file_read_mode);
                if (file == NULL) passed = 0;
                else (void)calls->file_close(file);
            }
            *(uint8_t *)a0 = (uint8_t)(passed ? 0U : 1U);
            return OPEN_CFW_PT_OK;
        }
    case OPEN_CFW_PT_OP_READ_METADATA_32:
        if (a0 == 0U || a1 != 32U || calls->file_open == NULL ||
            calls->file_close == NULL || calls->file_read == NULL ||
            calls->payload_path == NULL || calls->file_read_mode == NULL)
            break;
        {
            void *file = calls->file_open(
                calls->payload_path, calls->file_read_mode);
            unsigned int received;
            if (file == NULL) break;
            received = calls->file_read((void *)a0, 1U, 32U, file);
            (void)calls->file_close(file);
            if (received != 32U) break;
            if (calls->metadata_word != NULL)
                *calls->metadata_word = read_u32_le((uint8_t *)a0 + 28U);
            return OPEN_CFW_PT_OK;
        }
    case OPEN_CFW_PT_OP_OPEN_PAYLOAD:
        if (calls->file_open == NULL || calls->payload_path == NULL ||
            calls->file_read_mode == NULL ||
            calls->payload_handle_slot == NULL) break;
        if (*calls->payload_handle_slot != NULL) {
            if (calls->file_close == NULL) break;
            (void)calls->file_close(*calls->payload_handle_slot);
            *calls->payload_handle_slot = NULL;
        }
        *calls->payload_handle_slot = calls->file_open(
            calls->payload_path, calls->file_read_mode);
        if (*calls->payload_handle_slot == NULL) break;
        if (calls->payload_active != NULL) *calls->payload_active = 1U;
        if (calls->payload_open_seconds != NULL && calls->tick_count != NULL)
            *calls->payload_open_seconds = divide_u32_by_1000(
                calls->tick_count());
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_READ_PAYLOAD_AT:
        if (a1 == 0U || a3 == 0U || calls->payload_handle_slot == NULL ||
            *calls->payload_handle_slot == NULL ||
            a0 > 0x7FFFFFFFU || a2 > 0xFFFFFFFFU ||
            calls->file_seek == NULL || calls->file_tell == NULL ||
            calls->file_read == NULL) break;
        if (calls->file_seek(
                *calls->payload_handle_slot, (int)a0, 0U) != 0 ||
            calls->file_tell(*calls->payload_handle_slot) != (int)a0) break;
        *(size_t *)a3 = (size_t)calls->file_read(
            (void *)a1, 1U, (unsigned int)a2,
            *calls->payload_handle_slot);
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_CLOSE_PAYLOAD:
        if (calls->payload_handle_slot != NULL &&
            *calls->payload_handle_slot != NULL) {
            if (calls->file_close == NULL ||
                calls->file_close(*calls->payload_handle_slot) != 0) break;
            *calls->payload_handle_slot = NULL;
        }
        if (calls->payload_handle_slot != NULL)
            *calls->payload_handle_slot = NULL;
        if (calls->payload_active != NULL) *calls->payload_active = 0U;
        if (calls->payload_open_seconds != NULL)
            *calls->payload_open_seconds = 0U;
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_OTA_INITIALIZE:
        if (calls->ota_set_interface == NULL) break;
        calls->ota_set_interface(1U, 0U, NULL, 0U);
        if (calls->ota_stock_sequence != NULL) *calls->ota_stock_sequence = 0U;
        if (calls->ota_stock_initialized != NULL)
            *calls->ota_stock_initialized = 1U;
        if (calls->ota_stock_staging_length != NULL)
            *calls->ota_stock_staging_length = 0U;
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_OTA_DISPATCH:
        if (calls->ota_frame_dispatch == NULL) break;
        if (a0 == 0U || a0 == 2U || a0 == 3U) {
            uint8_t command = (uint8_t)a0;
            if (calls->ota_frame_dispatch(0xC0U, &command, 1U) != 0) break;
            if (a0 == 0U && calls->thread_get_id != NULL &&
                calls->thread_set_priority != NULL) {
                void *thread = calls->thread_get_id();
                if (thread == NULL ||
                    calls->thread_set_priority(thread, 0x2F) != 0) break;
            }
            return OPEN_CFW_PT_OK;
        }
        if (a0 == 1U) {
            uint8_t frame[129];
            if (a1 == 0U || a2 != 128U) break;
            frame[0] = 1U;
            copy_bytes(frame + 1U, (const void *)a1, 128U);
            return calls->ota_frame_dispatch(
                0xC0U, frame, (uint16_t)sizeof(frame)) == 0 ?
                OPEN_CFW_PT_OK : OPEN_CFW_PT_HANDLER_FAILED;
        }
        if (a0 == 4U) {
            if ((a1 == 0U && a2 != 0U) || a2 > 6000U ||
                calls->ota_async_data == NULL ||
                calls->ota_async_length == NULL ||
                calls->ota_async_ready == NULL) break;
            if (a2 != 0U)
                copy_bytes(calls->ota_async_data, (const void *)a1, a2);
            *calls->ota_async_length = (uint32_t)a2;
            *calls->ota_async_ready = 1U;
            return OPEN_CFW_PT_OK;
        }
        break;
    case OPEN_CFW_PT_OP_OTA_STATUS:
        if (a0 == 0U || calls->ota_status == NULL) break;
        *(uint8_t *)a0 = *calls->ota_status;
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_AUDIO_READ_VERSION_5:
        if (a0 == 0U || a1 != 5U || calls->firmware_version == NULL ||
            calls->audio_status_get == NULL) break;
        {
            const uint8_t *status;
            if (!parse_version_4(calls->firmware_version, (uint8_t *)a0))
                break;
            status = calls->audio_status_get(1U);
            if (status == NULL) break;
            ((uint8_t *)a0)[4] = *status;
            return OPEN_CFW_PT_OK;
        }
    case OPEN_CFW_PT_OP_AUDIO_READ_METRICS_32:
        if (a0 == 0U || a1 != 32U || calls->ambient_read == NULL ||
            calls->session_record == NULL) break;
        {
            uint8_t *output = (uint8_t *)a0;
            uint32_t measurement = read_ambient_measurement(calls);
            int32_t calibration = read_i32_le(calls->session_record + 0x28U);
            uint32_t adjusted = 0U;
            size_t index;
            for (index = 0U; index < 32U; ++index) output[index] = 0U;
            write_u32_le(output, measurement);
            if (calibration > 0)
                adjusted = (uint32_t)divide_u64_by_u32(
                    multiply_u32_u32((uint32_t)calibration, measurement) +
                    500000U, 1000000U);
            write_u32_le(output + 28U, adjusted);
            return OPEN_CFW_PT_OK;
        }
    case OPEN_CFW_PT_OP_AUDIO_READ_CHUNK:
        if (a2 == 0U || a3 == 0U || a4 == 0U ||
            calls->audio_path_format == NULL || calls->file_open == NULL ||
            calls->file_close == NULL || calls->file_read == NULL ||
            calls->file_seek == NULL || calls->file_size == NULL ||
            calls->file_read_mode == NULL ||
            calls->audio_handle_slot == NULL ||
            calls->audio_length_state == NULL ||
            calls->audio_offset_state == NULL ||
            calls->audio_path_state_32 == NULL) break;
        {
            char path[32];
            uint32_t remaining;
            uint32_t amount;
            unsigned int received;
            size_t index;
            for (index = 0U; index < sizeof(path); ++index) path[index] = '\0';
            calls->audio_path_format((uint8_t)a0, path, sizeof(path));
            path[sizeof(path) - 1U] = '\0';
            if (*calls->audio_handle_slot == NULL ||
                !text_equal_32(path,
                    (const char *)calls->audio_path_state_32)) {
                int length;
                if (*calls->audio_handle_slot != NULL)
                    (void)calls->file_close(*calls->audio_handle_slot);
                *calls->audio_handle_slot = calls->file_open(
                    path, calls->file_read_mode);
                if (*calls->audio_handle_slot == NULL) break;
                length = calls->file_size(*calls->audio_handle_slot);
                if (length < 1 || length >= 0x4B001) {
                    (void)calls->file_close(*calls->audio_handle_slot);
                    *calls->audio_handle_slot = NULL;
                    break;
                }
                *calls->audio_length_state = (uint32_t)length;
                *calls->audio_offset_state = 0U;
                copy_bytes(calls->audio_path_state_32, path, sizeof(path));
            }
            if (a1 != 0U) {
                *calls->audio_offset_state =
                    *calls->audio_offset_state < 210U ? 0U :
                    *calls->audio_offset_state - 210U;
            }
            remaining = *calls->audio_length_state -
                *calls->audio_offset_state;
            amount = remaining < 210U ? remaining : 210U;
            if (calls->file_seek(*calls->audio_handle_slot,
                    (int)*calls->audio_offset_state, 0U) != 0) break;
            received = calls->file_read((void *)a2, 1U, amount,
                *calls->audio_handle_slot);
            if (received != amount) break;
            *calls->audio_offset_state += amount;
            *(uint16_t *)a3 = (uint16_t)amount;
            *(int *)a4 = *calls->audio_offset_state >=
                *calls->audio_length_state;
            if (*(int *)a4 != 0) {
                (void)calls->file_close(*calls->audio_handle_slot);
                *calls->audio_handle_slot = NULL;
                *calls->audio_length_state = 0U;
                *calls->audio_offset_state = 0U;
                for (index = 0U; index < 32U; ++index)
                    calls->audio_path_state_32[index] = 0U;
            }
            return OPEN_CFW_PT_OK;
        }
    case OPEN_CFW_PT_OP_AUDIO_CONTROL:
        if (a0 > 1U || a1 > 3U) break;
        reset_audio_file_state(board);
        if (a1 == 0U) {
            if (a0 == 0U) {
                if (calls->audio_channel_0_start == NULL) break;
                calls->audio_channel_0_start((uint8_t)a2);
            } else {
                if (calls->audio_channel_1_start == NULL) break;
                calls->audio_channel_1_start();
            }
        } else if (a1 == 1U) {
            if (a0 == 0U) {
                if (calls->audio_channel_0_stop == NULL) break;
                calls->audio_channel_0_stop();
            } else {
                if (calls->audio_channel_1_stop == NULL) break;
                calls->audio_channel_1_stop();
            }
        } else if (a1 == 2U) {
            if (calls->audio_codec_route == NULL) break;
            calls->audio_codec_route(0x86U, (uint32_t)(a0 == 0U));
        } else {
            uint8_t payload[12];
            const uint8_t *template_12 = a0 == 0U ?
                calls->audio_channel_0_template_12 :
                calls->audio_channel_1_template_12;
            uint8_t side;
            if (template_12 == NULL || calls->lens_side == NULL ||
                calls->lens_sync_send == NULL) break;
            copy_bytes(payload, template_12, sizeof(payload));
            payload[4] = calls->lens_side();
            side = calls->lens_side();
            payload[5] = side == 1U ? 2U : 1U;
            if (calls->lens_sync_send(0x102U, payload,
                    (uint32_t)sizeof(payload), 0U) != 0) break;
        }
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_READ_IMU_SAMPLE_36:
        if (a0 == 0U || a1 != 36U || calls->imu_latest_sample == NULL)
            break;
        {
            const float *sample = calls->imu_latest_sample();
            if (sample == NULL) break;
            copy_bytes((void *)a0, sample, 36U);
            return OPEN_CFW_PT_OK;
        }
    case OPEN_CFW_PT_OP_READ_TOUCH_DIFFERENCES:
        if (a0 == 0U || calls->touch_read_differences == NULL) break;
        {
            uint8_t raw[10];
            int16_t *output = (int16_t *)a0;
            size_t index;
            if (calls->touch_read_differences(raw) != 0) break;
            for (index = 0U; index < 5U; ++index)
                output[index] = (int16_t)((uint16_t)raw[index * 2U] |
                    ((uint16_t)raw[index * 2U + 1U] << 8U));
            return OPEN_CFW_PT_OK;
        }
    case OPEN_CFW_PT_OP_READ_CALIBRATION_ORIENTATION:
        if (a0 == 0U || a1 == 0U ||
            calls->sensor_calibration_initialize == NULL ||
            calls->sensor_calibration_read == NULL ||
            calls->imu_orientation == NULL ||
            calls->calibration_reference_matrix == NULL) break;
        {
            float vector_a[3];
            float vector_b[3];
            float matrix[9];
            const float *orientation;
            size_t index;
            int matches = 1;
            calls->sensor_calibration_initialize();
            (void)calls->sensor_calibration_read(
                vector_a, vector_b, matrix);
            for (index = 0U; index < 9U; ++index) {
                if (!float_close(matrix[index],
                        calls->calibration_reference_matrix[index])) {
                    matches = 0;
                    break;
                }
            }
            orientation = calls->imu_orientation();
            if (orientation == NULL) break;
            *(int *)a0 = matches;
            copy_bytes((void *)a1, orientation, 12U);
            return OPEN_CFW_PT_OK;
        }
    case OPEN_CFW_PT_OP_READ_PLATFORM_IDENTIFIER:
        if (a1 == 0U) break;
        if (a0 == 0U) {
            if (calls->touch_platform_identifier == NULL) break;
            *(uint32_t *)a1 = *calls->touch_platform_identifier;
        } else if (a0 == 1U) {
            if (calls->apollo_platform_identifier == NULL) break;
            *(uint32_t *)a1 = *calls->apollo_platform_identifier;
        } else if (a0 == 2U) {
            if (calls->codec_platform_identifier == NULL) break;
            *(uint32_t *)a1 = calls->codec_platform_identifier();
        } else {
            break;
        }
        return OPEN_CFW_PT_OK;
    case OPEN_CFW_PT_OP_READ_HARDWARE_IDENTIFIER:
        if (a1 == 0U) break;
        {
            uint32_t value = 0U;
            if (a0 == 0U) {
                if (calls->hardware_identifier_0 == NULL) break;
                (void)calls->hardware_identifier_0(&value);
            } else if (a0 == 1U) {
                if (calls->hardware_identifier_1 == NULL) break;
                (void)calls->hardware_identifier_1(&value);
                value &= 0x00FFFFFFU;
            } else if (a0 == 2U) {
                if (calls->hardware_identifier_2 == NULL) break;
                (void)calls->hardware_identifier_2(&value);
                value &= 0xFFU;
            } else if (a0 == 3U) {
                if (calls->imu_who_am_i == NULL) break;
                (void)calls->imu_who_am_i(&value);
            } else if (a0 == 4U) {
                if (calls->mag_who_am_i == NULL) break;
                (void)calls->mag_who_am_i(&value);
            } else if (a0 == 5U) {
                if (calls->display_hardware_identifier == NULL) break;
                value = calls->display_hardware_identifier() & 0xFFFFU;
            } else if (a0 == 6U) {
                uint8_t device[60];
                uint16_t low;
                uint16_t high;
                if (calls->ambient_identifier_initialize == NULL ||
                    calls->ambient_identifier_assign == NULL ||
                    calls->ambient_identifier_step_1 == NULL ||
                    calls->ambient_identifier_step_2 == NULL ||
                    calls->ambient_identifier_low == NULL ||
                    calls->ambient_identifier_high == NULL) break;
                calls->ambient_identifier_initialize();
                calls->ambient_identifier_assign(device);
                calls->ambient_identifier_step_1(device);
                calls->ambient_identifier_step_2(device);
                low = calls->ambient_identifier_low(device);
                high = calls->ambient_identifier_high(device);
                value = (uint32_t)low | ((uint32_t)high << 16U);
            } else if (a0 == 7U) {
                if (calls->touch_platform_identifier == NULL) break;
                value = *calls->touch_platform_identifier;
            } else {
                break;
            }
            *(uint32_t *)a1 = value;
            return OPEN_CFW_PT_OK;
        }
    case OPEN_CFW_PT_OP_POST_RESPONSE:
        if (a0 == 0U || a2 == 0U || a3 < 5U) break;
        {
            const uint8_t *request = (const uint8_t *)a0;
            const uint8_t *response = (const uint8_t *)a2;
            uint8_t command = response[4];
            size_t index;
            if (command == 0x01U) {
                if (a3 < 9U) break;
                if (response[8] == 0U) {
                    if (calls->delay_ticks == NULL ||
                        calls->system_reset == NULL) break;
                    (void)calls->delay_ticks(1000U);
                    calls->system_reset();
                }
            } else if (command == 0x06U) {
                if (calls->file_open == NULL || calls->file_close == NULL ||
                    calls->file_remove == NULL ||
                    calls->file_read_mode == NULL) break;
                for (index = 0U; index < 3U; ++index) {
                    void *file;
                    const char *path = calls->cleanup_paths[index];
                    if (path == NULL) continue;
                    file = calls->file_open(path, calls->file_read_mode);
                    if (file != NULL) {
                        (void)calls->file_close(file);
                        (void)calls->file_remove(path);
                    }
                }
            } else if (command == 0x0BU) {
                if (calls->delay_ticks == NULL ||
                    calls->system_reset == NULL) break;
                (void)calls->delay_ticks(1000U);
                calls->system_reset();
            } else if (command == 0x13U) {
                if (calls->box_state_updated == NULL) break;
                calls->box_state_updated();
            } else if (command == 0x3EU) {
                if (a1 < 5U) break;
                if (request[4] == 0U) {
                    if (calls->aging_mode_mutable == NULL ||
                        calls->delay_ticks == NULL ||
                        calls->system_reset == NULL) break;
                    *calls->aging_mode_mutable = 0U;
                    (void)calls->delay_ticks(2000U);
                    calls->system_reset();
                }
            } else if (command == 0x54U) {
                if (calls->ota_async_ready == NULL ||
                    calls->ota_async_length == NULL ||
                    calls->ota_async_data == NULL ||
                    calls->ota_frame_dispatch == NULL) break;
                if (*calls->ota_async_ready != 0U) {
                    *calls->ota_async_ready = 0U;
                    (void)calls->ota_frame_dispatch(
                        0xC1U, calls->ota_async_data,
                        (uint16_t)*calls->ota_async_length);
                    *calls->ota_async_length = 0U;
                }
            } else if (command == 0x66U) {
                if (calls->display_postprocess == NULL) break;
                calls->display_postprocess();
            } else if (command == 0x6CU) {
                if (calls->display_value_mutable == NULL ||
                    calls->font_crc_check_0 == NULL ||
                    calls->font_crc_check_1 == NULL) break;
                *calls->display_value_mutable = 0U;
                *calls->display_value_mutable = (uint8_t)(
                    *calls->display_value_mutable | calls->font_crc_check_0());
                *calls->display_value_mutable = (uint8_t)(
                    *calls->display_value_mutable | calls->font_crc_check_1());
            }
            return OPEN_CFW_PT_OK;
        }
    default:
        break;
    }
    return OPEN_CFW_PT_HANDLER_FAILED;
}


int open_cfw_pt_board_backend_initialize(
    struct open_cfw_pt_board_backend *board,
    const struct open_cfw_pt_board_calls *calls,
    struct open_cfw_pt_platform_backend *backend)
{
    if (board == NULL || calls == NULL || backend == NULL)
        return OPEN_CFW_PT_INVALID_ARGUMENT;
    board->calls = calls;
    backend->perform = perform;
    backend->context = board;
    return OPEN_CFW_PT_OK;
}


#define FUNCTION(type, address) ((type)(uintptr_t)((address) | 1U))
#if defined(OPEN_CFW_PT_PRODUCTION_SOURCE_PROVIDERS)
#define RETAINED_FUNCTION(type, address, symbol) (symbol)
#else
#define RETAINED_FUNCTION(type, address, symbol) FUNCTION(type, address)
#endif

int open_cfw_pt_board_backend_initialize_production(
    struct open_cfw_pt_board_backend *board,
    struct open_cfw_pt_platform_backend *backend)
{
    /*
     * This table is valid only for the authenticated G2 Apollo layout after
     * applying the canonical core overlay. The analyzer pins every field,
     * address, ABI, and data extent below: 43 callable entries route to named
     * source overlays, while 40 callable entries route through semantic-C
     * providers. Those providers still use the separately audited second-order
     * retained ABI documented in the header. The 53 stock-layout data entries
     * are a deliberately supported ABI split into authenticated immutable-flash
     * and runtime-SRAM bindings. Keeping every seam visible prevents the
     * complete 56-operation behavior surface from being mistaken for complete
     * source ownership.
     */
    static const struct open_cfw_pt_board_calls calls = {
        .set_local_lid = FUNCTION(void (*)(uint8_t), 0x004AC744U),
        .set_local_level = FUNCTION(void (*)(uint8_t), 0x004AC718U),
        .set_local_charging = FUNCTION(void (*)(uint8_t), 0x004AC72EU),
        .codec_mic_delay_1bit = FUNCTION(int32_t (*)(void), 0x0057D870U),
        .system_data_write = FUNCTION(
            int (*)(uint8_t, const void *), 0x004AF11CU),
        .system_data_get = FUNCTION(void *(*)(uint8_t), 0x004AF73AU),
        .system_data_read = FUNCTION(void *(*)(uint8_t), 0x004AF7B8U),
        .post_input_message_id3 = RETAINED_FUNCTION(
            void (*)(void), 0x005130A6U,
            open_cfw_pt_board_post_input_message_id3),
        .product_mode_read = FUNCTION(uint8_t (*)(void), 0x004ABE8CU),
        .product_mode_update = FUNCTION(void (*)(uint8_t), 0x004ABE66U),
        .touch_proximity = FUNCTION(uint8_t (*)(void), 0x00502DAEU),
        .touch_read_differences = FUNCTION(
            int32_t (*)(uint8_t [10]), 0x0055B6A8U),
        .psn_write_otp = FUNCTION(int (*)(const char *), 0x004AFFC0U),
        .memory_compare = FUNCTION(
            int (*)(const void *, const void *, unsigned int), 0x004751C8U),
        .sensor_calibration_update = FUNCTION(
            void (*)(const float *, const float *, const float [9]),
            0x0050999EU),
        .buzzer_start = RETAINED_FUNCTION(
            void (*)(uint32_t, uint8_t), 0x00502C88U,
            open_cfw_pt_board_buzzer_start),
        .buzzer_stop = RETAINED_FUNCTION(
            void (*)(void), 0x00502D4CU, open_cfw_pt_board_buzzer_stop),
        .buzzer_frequency_get = FUNCTION(
            uint32_t (*)(void), 0x0058FA60U),
        .buzzer_duty_get = FUNCTION(uint8_t (*)(void), 0x0058FA66U),
        .buzzer_update = FUNCTION(
            void (*)(uint32_t, uint8_t), 0x0058FA6CU),
        .onboarding_update = FUNCTION(
            int (*)(uint8_t, const uint8_t *), 0x004A7820U),
        .production_reset = RETAINED_FUNCTION(
            void (*)(void), 0x0058F950U, open_cfw_pt_board_production_reset),
        .charger_test_disable = RETAINED_FUNCTION(
            void (*)(void), 0x005128F8U,
            open_cfw_pt_board_charger_test_disable),
        .charger_test_enable = RETAINED_FUNCTION(
            void (*)(void), 0x0051299CU,
            open_cfw_pt_board_charger_test_enable),
        .identifier_record_link =
            (const uint8_t *const *)(uintptr_t)0x20003844U,
        .sync_ready = (volatile uint8_t *)(uintptr_t)0x20075003U,
        .boolean_flag = (const uint8_t *)(uintptr_t)0x20075019U,
        .pair_state = (const uint8_t *)(uintptr_t)0x20073B18U,
        .pair_state_mutable = (volatile uint8_t *)(uintptr_t)0x20073B18U,
        .session_record = (const uint8_t *)(uintptr_t)0x20003994U,
        .session_record_mutable = (uint8_t *)(uintptr_t)0x20003994U,
        .diagnostic_blob_36 = (const uint8_t *)(uintptr_t)0x2000396CU,
        .font_version = FUNCTION(const char *(*)(void), 0x0046D584U),
        .display_value = (const uint8_t *)(uintptr_t)0x20004552U,
        .display_runtime_flag =
            (volatile uint8_t *)(uintptr_t)0x20004551U,
        .aging_mode = (const uint8_t *)(uintptr_t)0x20075019U,
        .aging_mode_mutable =
            (volatile uint8_t *)(uintptr_t)0x20075019U,
        .imu_latest_sample = FUNCTION(const float *(*)(void), 0x004A5B90U),
        .sensor_calibration_initialize = FUNCTION(
            void (*)(void), 0x004A6BCEU),
        .sensor_calibration_read = FUNCTION(
            int (*)(float [3], float [3], float [9]), 0x005099F8U),
        .imu_orientation = FUNCTION(
            const float *(*)(void), 0x004A5D38U),
        .calibration_reference_matrix =
            (const float *)(uintptr_t)0x00758E08U,
        .touch_platform_identifier =
            (const uint32_t *)(uintptr_t)0x20074508U,
        .apollo_platform_identifier =
            (const uint32_t *)(uintptr_t)0x20074940U,
        .codec_platform_identifier = RETAINED_FUNCTION(
            uint32_t (*)(void), 0x0052DEE6U,
            open_cfw_pt_board_codec_platform_identifier),
        .file_open = FUNCTION(
            void *(*)(const void *, const char *), 0x00474550U),
        .file_close = FUNCTION(int (*)(void *), 0x004745F4U),
        .file_read = FUNCTION(
            unsigned int (*)(void *, unsigned int, unsigned int, void *),
            0x00474634U),
        .file_write = FUNCTION(
            unsigned int (*)(const void *, unsigned int, unsigned int, void *),
            0x00474682U),
        .file_seek = FUNCTION(
            int (*)(void *, int, unsigned int), 0x00474814U),
        .file_tell = FUNCTION(int (*)(void *), 0x00474870U),
        .file_size = FUNCTION(int (*)(void *), 0x004748B4U),
        .file_remove = FUNCTION(int (*)(const void *), 0x0047498CU),
        .tick_count = FUNCTION(uint32_t (*)(void), 0x00454EFEU),
        .payload_path = (const char *)(uintptr_t)0x00782BF0U,
        .file_read_mode = (const char *)(uintptr_t)0x00575E78U,
        .file_write_mode = (const char *)(uintptr_t)0x0057301CU,
        .storage_test_path = (const char *)(uintptr_t)0x0078BD20U,
        .storage_required_paths = {
            (const char *)(uintptr_t)0x007705F0U,
            (const char *)(uintptr_t)0x00782BF0U,
            (const char *)(uintptr_t)0x00782C04U,
            (const char *)(uintptr_t)0x00782C18U,
        },
        .cleanup_paths = {
            (const char *)(uintptr_t)0x00770430U,
            (const char *)(uintptr_t)0x0077AC9CU,
            (const char *)(uintptr_t)0x0077ACB4U,
        },
        .metadata_word = (volatile uint32_t *)(uintptr_t)0x200748E8U,
        .payload_handle_slot = (void *volatile *)(uintptr_t)0x200748E4U,
        .payload_active = (volatile uint8_t *)(uintptr_t)0x20075009U,
        .payload_open_seconds =
            (volatile uint32_t *)(uintptr_t)0x200748ECU,
        .ota_set_interface = FUNCTION(
            void (*)(uint32_t, uint32_t, void *, uint32_t), 0x004487E4U),
        .ota_frame_dispatch = FUNCTION(
            int (*)(uint8_t, const uint8_t *, uint16_t), 0x00448670U),
        .thread_get_id = FUNCTION(void *(*)(void), 0x004491AAU),
        .thread_set_priority = FUNCTION(
            int (*)(void *, int), 0x004491B2U),
        .ota_stock_sequence = (volatile uint8_t *)(uintptr_t)0x20075005U,
        .ota_stock_initialized =
            (volatile uint8_t *)(uintptr_t)0x2007500AU,
        .ota_stock_staging_length =
            (volatile uint32_t *)(uintptr_t)0x200748DCU,
        .ota_async_data = (uint8_t *)(uintptr_t)0x20059EF8U,
        .ota_async_length = (volatile uint32_t *)(uintptr_t)0x200748E0U,
        .ota_async_ready = (volatile uint8_t *)(uintptr_t)0x20075008U,
        .ota_status = (const uint8_t *)(uintptr_t)0x20075007U,
        .system_reset = RETAINED_FUNCTION(
            void (*)(void), 0x0044B0AEU, open_cfw_pt_board_system_reset),
        .box_state_updated = FUNCTION(void (*)(void), 0x004AC798U),
        .display_postprocess = RETAINED_FUNCTION(
            void (*)(void), 0x00542D4CU,
            open_cfw_pt_board_display_postprocess),
        .font_crc_check_0 = RETAINED_FUNCTION(
            uint8_t (*)(void), 0x0058F486U,
            open_cfw_pt_board_font_crc_check_0),
        .font_crc_check_1 = RETAINED_FUNCTION(
            uint8_t (*)(void), 0x0058F490U,
            open_cfw_pt_board_font_crc_check_1),
        .display_value_mutable =
            (volatile uint8_t *)(uintptr_t)0x20004552U,
        .hardware_identifier_0 = RETAINED_FUNCTION(
            int (*)(uint32_t *), 0x00512C84U,
            open_cfw_pt_board_hardware_identifier_0),
        .hardware_identifier_1 = RETAINED_FUNCTION(
            int (*)(uint32_t *), 0x004700B4U,
            open_cfw_pt_board_hardware_identifier_1),
        .hardware_identifier_2 = RETAINED_FUNCTION(
            int (*)(uint32_t *), 0x00512B20U,
            open_cfw_pt_board_hardware_identifier_2),
        .imu_who_am_i = FUNCTION(int (*)(uint32_t *), 0x004A6456U),
        .mag_who_am_i = FUNCTION(int (*)(uint32_t *), 0x004A64C8U),
        .display_hardware_identifier = RETAINED_FUNCTION(
            uint32_t (*)(void), 0x004CA070U,
            open_cfw_pt_board_display_hardware_identifier),
        .ambient_identifier_initialize = RETAINED_FUNCTION(
            void (*)(void), 0x0058F936U,
            open_cfw_pt_board_ambient_identifier_initialize),
        .ambient_identifier_assign = FUNCTION(
            void (*)(void *), 0x005135E0U),
        .ambient_identifier_step_1 = RETAINED_FUNCTION(
            void (*)(void *), 0x0058F8CCU,
            open_cfw_pt_board_ambient_identifier_step_1),
        .ambient_identifier_step_2 = RETAINED_FUNCTION(
            void (*)(void *), 0x0058F8D8U,
            open_cfw_pt_board_ambient_identifier_step_2),
        .ambient_identifier_low = RETAINED_FUNCTION(
            uint16_t (*)(void *), 0x0058F922U,
            open_cfw_pt_board_ambient_identifier_low),
        .ambient_identifier_high = RETAINED_FUNCTION(
            uint16_t (*)(void *), 0x0058F92CU,
            open_cfw_pt_board_ambient_identifier_high),
        .uart_sync_write = RETAINED_FUNCTION(
            int (*)(const uint8_t *, uint32_t, uint32_t), 0x00541790U,
            open_cfw_pt_board_uart_sync_write),
        .delay_ticks = FUNCTION(int (*)(uint32_t), 0x00449376U),
        .uart_sync_state = (volatile uint8_t *)(uintptr_t)0x20074080U,
        .uart_sync_expected = (const uint8_t *)(uintptr_t)0x0078E44CU,
        .lens_side = FUNCTION(uint8_t (*)(void), 0x0045A568U),
        .lens_sync_send = RETAINED_FUNCTION(
            int (*)(uint32_t, const void *, uint32_t, uint32_t),
            0x004651E0U, open_cfw_pt_board_lens_sync_send),
        .lens_sync_ready = (volatile uint8_t *)(uintptr_t)0x20075004U,
        .lens_sync_template_12 =
            (const uint8_t *)(uintptr_t)0x0078BD68U,
        .screen_show = RETAINED_FUNCTION(
            void (*)(uint16_t, uint32_t, uint32_t), 0x004441ECU,
            open_cfw_pt_board_screen_show),
        .screen_hide = RETAINED_FUNCTION(
            void (*)(uint16_t, uint32_t, uint32_t), 0x004443CCU,
            open_cfw_pt_board_screen_hide),
        .display_state = RETAINED_FUNCTION(
            const uint8_t *(*)(void), 0x0044347AU,
            open_cfw_pt_board_display_state),
        .display_brightness = RETAINED_FUNCTION(
            void (*)(uint32_t, uint32_t, uint32_t), 0x004CA1EEU,
            open_cfw_pt_board_display_brightness),
        .display_stage_1 = RETAINED_FUNCTION(
            void (*)(uint32_t), 0x0046C984U,
            open_cfw_pt_board_display_stage_1),
        .display_stage_2 = RETAINED_FUNCTION(
            void (*)(uint32_t, uint32_t), 0x0046C9DCU,
            open_cfw_pt_board_display_stage_2),
        .display_stage_3 = RETAINED_FUNCTION(
            void (*)(uint32_t), 0x0046C9AAU,
            open_cfw_pt_board_display_stage_3),
        .display_offset = RETAINED_FUNCTION(
            void (*)(uint8_t, uint8_t), 0x004CA24AU,
            open_cfw_pt_board_display_offset),
        .audio_status_get = RETAINED_FUNCTION(
            const uint8_t *(*)(uint32_t), 0x0050938EU,
            open_cfw_pt_board_audio_status_get),
        .firmware_version = (const char *)(uintptr_t)0x0078BD44U,
        .audio_path_format = RETAINED_FUNCTION(
            void (*)(uint8_t, char *, uint32_t), 0x0057B352U,
            open_cfw_pt_board_audio_path_format),
        .audio_channel_0_start = RETAINED_FUNCTION(
            void (*)(uint8_t), 0x0058F69AU,
            open_cfw_pt_board_audio_channel_0_start),
        .audio_channel_0_stop = RETAINED_FUNCTION(
            void (*)(void), 0x0058F7B0U,
            open_cfw_pt_board_audio_channel_0_stop),
        .audio_channel_1_start = RETAINED_FUNCTION(
            void (*)(void), 0x0058F74AU,
            open_cfw_pt_board_audio_channel_1_start),
        .audio_channel_1_stop = RETAINED_FUNCTION(
            void (*)(void), 0x0058F806U,
            open_cfw_pt_board_audio_channel_1_stop),
        .audio_codec_route = RETAINED_FUNCTION(
            void (*)(uint32_t, uint32_t), 0x0053A5BEU,
            open_cfw_pt_board_audio_codec_route),
        .audio_channel_0_template_12 =
            (const uint8_t *)(uintptr_t)0x0078BD50U,
        .audio_channel_1_template_12 =
            (const uint8_t *)(uintptr_t)0x0078BD5CU,
        .audio_handle_slot = (void *volatile *)(uintptr_t)0x200748D0U,
        .audio_active = (volatile uint8_t *)(uintptr_t)0x20075006U,
        .audio_length_state =
            (volatile uint32_t *)(uintptr_t)0x200748D4U,
        .audio_offset_state =
            (volatile uint32_t *)(uintptr_t)0x200748D8U,
        .audio_path_state_32 = (uint8_t *)(uintptr_t)0x2007393CU,
        .system_data_reset_aging = FUNCTION(void (*)(void), 0x004AFC10U),
        .time_configure = RETAINED_FUNCTION(
            void (*)(uint32_t, int), 0x0044A1FEU,
            open_cfw_pt_board_time_configure),
        .time_capture = RETAINED_FUNCTION(
            void (*)(void *), 0x0044A19AU, open_cfw_pt_board_time_capture),
        .time_configuration = (const uint8_t *)(uintptr_t)0x2000380CU,
        .ambient_read = RETAINED_FUNCTION(
            double (*)(void), 0x0058F8E4U, open_cfw_pt_board_ambient_read),
        .ambient_baseline =
            (volatile uint32_t *)(uintptr_t)0x200748C8U,
        .ambient_secondary =
            (volatile uint32_t *)(uintptr_t)0x200748C4U,
    };
    return open_cfw_pt_board_backend_initialize(board, &calls, backend);
}

#undef FUNCTION
#undef RETAINED_FUNCTION
