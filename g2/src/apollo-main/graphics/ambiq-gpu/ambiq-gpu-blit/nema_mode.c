/* Stock Nema mode command encoder at 0x513924..0x513e2d. */
#include <stdint.h>

extern volatile uint8_t audio_uart_nema_boot_state_200043a8[];
extern volatile uint32_t audio_uart_ambiq_unit_cell[1];
extern void display_driver_nema_select_522a16(uint32_t);
extern void display_driver_nema_cache_4b1588(uint32_t);
extern uint32_t audio_uart_nema_child_514846(uint32_t, uint32_t);
extern void audio_uart_nema_instruction_upload_522920(const uint32_t *,
                                                       uint32_t, uint32_t);

/* Both tables are copied from the authenticated s200 v2.2.6.10 Main payload. */
static const uint32_t format_words[28] = {
    0x1e, 0x1d, 0x00, 0x08, 0x04, 0x0c, 0x05, 0x0d,
    0x01, 0x09, 0x11, 0x15, 0x0f, 0x0e, 0x00, 0x04,
    0x00, 0x04, 0x01, 0x05, 0x01, 0x05, 0x0c, 0x0c,
    0x6e65735b, 0x5f726f73, 0x5d736c61, 0x20534c41,
};
static const uint32_t blend_words[4] = {0x400, 0, 0x800, 0xc00};

static uint32_t state_word(unsigned offset)
{
    return *(volatile uint32_t *)(void *)(audio_uart_nema_boot_state_200043a8 + offset);
}

static uint8_t unit_byte(unsigned offset)
{
    volatile const uint8_t *unit =
        (volatile const uint8_t *)(uintptr_t)audio_uart_ambiq_unit_cell[0];
    return unit[offset];
}

static void emit_pair(uint32_t *commands, uint32_t *count, uint32_t first,
                      uint32_t second)
{
    commands[*count * 2u] = first;
    commands[*count * 2u + 1u] = second;
    ++*count;
}

void display_driver_nema_mode_513924(uint32_t mode, uint32_t target,
                                      uint32_t blend, uint32_t source)
{
    uint32_t commands[16] = {0};
    uint32_t count = 0;
    uint32_t rop_result = 0;
    uint32_t sign;
    uint32_t preserve;
    uint32_t alpha;
    uint32_t fmt;
    uint32_t srcfmt;
    uint32_t high;
    uint32_t bit23;
    uint32_t bit21;
    uint32_t bit22;
    uint32_t bit30;
    uint32_t bit27;
    uint32_t bit28;
    uint32_t bit26;
    uint32_t bit29;
    uint32_t output;
    uint32_t marker;
    uint32_t aux;
    uint32_t indexed;
    uint32_t use_extra;
    uint32_t cmdflag;
    uint32_t left_shift;
    uint32_t right_shift;
    uint32_t aux_byte;
    uint32_t special;

    if (audio_uart_nema_boot_state_200043a8[1] != 0u) {
        display_driver_nema_select_522a16(0x20202020u);
        blend = UINT32_MAX;
        source = UINT32_MAX;
        mode = 0x101u;
        display_driver_nema_cache_4b1588(0u);
    }
    sign = mode >> 31;
    preserve = (mode >> 25) & 1u;
    alpha = (mode >> 20) & 1u;
    fmt = mode & 15u;
    srcfmt = (mode >> 8) & 15u;
    high = mode & 0xfff00000u;
    bit23 = (mode >> 23) & 1u;
    bit21 = (mode >> 21) & 1u;
    bit22 = (mode >> 22) & 1u;
    bit30 = (mode >> 30) & 1u;
    bit27 = (mode >> 27) & 1u;
    bit28 = (mode >> 28) & 1u;
    bit26 = (mode >> 26) & 1u;
    bit29 = (mode >> 29) & 1u;
    if (target > 3u) target = 0u;
    if (blend > 3u) blend = UINT32_MAX;
    aux_byte = source & 255u;
    if (source > 3u) {
        aux_byte = 2u;
        source = target;
    }
    rop_result = 0u;
    if (audio_uart_nema_boot_state_200043a8[0] != 0u) {
        uint32_t value = 0u;
        if (sign != 0u) {
            value |= 0x80000000u;
            sign = 0u;
            mode &= 0x7fffffffu;
        }
        if (preserve != 0u) {
            value |= 0x02000000u;
            preserve = 0u;
            mode &= 0xfdffffffu;
        }
        if ((mode & 0x01000000u) != 0u || source != target) {
            audio_uart_nema_child_514846(0x1d0u, value | 1u);
            alpha = 0u;
        } else {
            value |= fmt | (srcfmt << 8);
            srcfmt = 0u;
            fmt = 1u;
            rop_result = audio_uart_nema_child_514846(0x1d0u, value);
            mode = (mode & 0xfff00000u) | 1u;
        }
    }
    sign |= preserve;
    if (mode == 1u) rop_result = unit_byte(10u);
    if (mode == 1u && rop_result == 0u && target == 0u) {
        if ((int32_t)blend < 0) {
            audio_uart_nema_child_514846(0x118u, 0x90000000u);
            output = 0x141f001fu | (state_word(4u) << 16);
        } else {
            audio_uart_nema_child_514846(0x118u, 0u);
            output = blend_words[blend] | (state_word(4u) << 16) | 0x141f801fu;
        }
        audio_uart_nema_child_514846(0x11cu, output);
        return;
    }

    indexed = fmt >= 6u || sign != 0u || srcfmt != 0u;
    use_extra = indexed ? 3u : 0u;
    cmdflag = 1u;
    if (bit28 == 0u) marker = 3u;
    else marker = 1u;
    if (preserve == 0u) aux = sign << 21;
    else aux = 0x100000u;
    if (alpha != 0u) left_shift = 0x17u;
    else if (bit29 != 0u) left_shift = 0x11u;
    else if (bit26 != 0u) left_shift = 4u;
    else left_shift = 0x1du;
    right_shift = bit28 == 0u && bit27 == 0u ? 0xeu : 0xcu;
    output = 0u;
    if (unit_byte(10u) == 0u) {
        if ((int32_t)blend < 0) {
            if (indexed) {
                indexed = 0u;
                use_extra = 0u;
                output = blend_words[source] | 0xb000u;
            }
        } else {
            cmdflag = 0u;
            output = blend_words[blend] | 0x8000u;
        }
        special = bit23 != 0u || bit22 != 0u;
        if (special) output = bit23 != 0u ? 0xcc00u : 0xdc00u;
        if (bit21 == 0u || blend == UINT32_MAX) {
            if (special) emit_pair(commands, &count, 0x000c100bu | (blend << 7), 0x2000u);
        } else {
            commands[0] = 0x080c100bu | (blend << 7);
            commands[1] = 0x2000u;
            commands[2] = (aux_byte << 7) | 0x100bu;
            commands[3] = 0u;
            count = 2u;
        }
        if (special) emit_pair(commands, &count, 0x000c0000u, 0x0081a042u);
    } else {
        commands[0] = 0x00f40182u;
        commands[1] = 0x02009408u;
        count = 1u;
        output = 0xfc00u;
        if ((int32_t)blend >= 0) {
            emit_pair(commands, &count, 0x000c100bu | (blend << 7), 0x2000u);
            cmdflag = 0u;
        }
    }
    special = srcfmt < 2u && high == 0u && (int32_t)blend < 0 && source == target;
    if (special) {
        left_shift = srcfmt == 0u ? 0x2000u : 0x800u;
        right_shift = srcfmt == 0u ? 0x800000u : 0x200000u;
        emit_pair(commands, &count, 0x080c0002u | (target << 7),
                  left_shift | (format_words[fmt] << 14) |
                  (format_words[12u + fmt] << 5) | right_shift | 0x8a000006u);
    } else {
        special = fmt < 6u && alpha == 0u && bit29 == 0u && bit26 == 0u &&
                  bit27 == 0u && bit28 == 0u;
        if (!special) {
            uint32_t first = srcfmt | use_extra;
            if (first == 0u) first = sign;
            if (first != 0u) {
                if (left_shift != 0x1du || right_shift != 0xeu || bit30 != 0u || use_extra != 0u)
                    emit_pair(commands, &count,
                              use_extra | (source << 7) | (bit30 << 20) | 0x080c0000u,
                              marker | (right_shift << 5) | (left_shift << 14) |
                              ((alpha != 0u ? 7u : 4u) << 11) | 4u);
            } else if (fmt == 1u && bit30 == 0u) {
                emit_pair(commands, &count,
                          (bit30 << 20) | (target << 7) | 0x080c0002u,
                          marker | (right_shift << 5) | (left_shift << 14) |
                          ((alpha != 0u ? 7u : 4u) << 11) | 0x80000004u);
                special = 0u;
            } else if (left_shift != 0x1du || right_shift != 0xeu ||
                       bit30 != 0u || use_extra != 0u) {
                emit_pair(commands, &count,
                          use_extra | (source << 7) | (bit30 << 20) | 0x080c0000u,
                          marker | (right_shift << 5) | (left_shift << 14) |
                          ((alpha != 0u ? 7u : 4u) << 11) | 4u);
            }
            if (fmt != 1u || first != 0u || bit30 != 0u) special = 1u;
            use_extra = 0u;
            indexed = 0u;
            bit30 = 0u;
        }
        if (special) {
            uint32_t prefix = bit30 << 20;
            uint32_t first = srcfmt == 0u ? sign : bit30;
            uint32_t destination = source;
            uint32_t flags = 0u;
            uint32_t addr = 0x080c0000u;
            uint32_t shift_a = 0x1000u;
            uint32_t shift_b = 0x400000u;
            if (srcfmt == 0u && first == 0u) {
                flags = 0x80000000u;
                addr = 0x080c0002u;
                destination = target;
                emit_pair(commands, &count,
                          prefix | addr | use_extra | ((uint8_t)destination << 7),
                          0x0a002007u | flags | (format_words[fmt] << 14) |
                          (format_words[12u + fmt] << 5));
                goto finish_commands;
            } else if (!indexed && bit30 == 0u && fmt <= 1u) {
                if (fmt == 0u) {
                    shift_a = 0x2000u;
                    shift_b = 0x800000u;
                } else {
                    shift_a = 0u;
                    shift_b = 0u;
                }
            } else {
                emit_pair(commands, &count,
                          prefix | addr | use_extra | ((uint8_t)destination << 7),
                          0x0a002007u | flags | (format_words[fmt] << 14) |
                          (format_words[12u + fmt] << 5));
                if (flags != 0u) goto finish_commands;
            }
            emit_pair(commands, &count, aux | (target << 7) | 0x004e0002u,
                      shift_b | shift_a | (format_words[srcfmt] << 14) |
                      (format_words[12u + srcfmt] << 5) | 0x80080206u);
        }
    }
finish_commands:
    audio_uart_nema_child_514846(0x118u, cmdflag != 0u ? 0x90000000u : 0u);
    audio_uart_nema_instruction_upload_522920(commands, count, 0u);
    output |= ((0x20u - count) | state_word(4u) | blend_words[source]) << 16;
    output |= 0x10000000u;
    audio_uart_nema_child_514846(0x11cu, output);
}
