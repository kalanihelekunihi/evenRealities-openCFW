/*
 * SPDX-License-Identifier: GPL-3.0-only
 *
 * Clean-room behavioral reconstruction of the retained G2 2.2.6.10
 * platform/service/eAT/at_buzzer.c command handler.  The authenticated
 * behavior and fixed provider/literal ABI are documented in
 * docs/research/g2-at-buzzer-recovery.md.  No stock object bytes are copied.
 */

#include <stdint.h>

#define OPEN_CFW_AT_BUZZER_STRING(address) \
    ((const char *)(uintptr_t)(address))

#ifndef OPEN_CFW_AT_BUZZER_COMMAND_NOTE
#define OPEN_CFW_AT_BUZZER_COMMAND_NOTE OPEN_CFW_AT_BUZZER_STRING(0x0078cb94u)
#endif
#ifndef OPEN_CFW_AT_BUZZER_COMMAND_PLAY
#define OPEN_CFW_AT_BUZZER_COMMAND_PLAY OPEN_CFW_AT_BUZZER_STRING(0x0078cb9cu)
#endif
#ifndef OPEN_CFW_AT_BUZZER_COMMAND_START
#define OPEN_CFW_AT_BUZZER_COMMAND_START OPEN_CFW_AT_BUZZER_STRING(0x0078cba4u)
#endif
#ifndef OPEN_CFW_AT_BUZZER_COMMAND_STOP
#define OPEN_CFW_AT_BUZZER_COMMAND_STOP OPEN_CFW_AT_BUZZER_STRING(0x0078cbb4u)
#endif

#ifndef OPEN_CFW_AT_BUZZER_MISSING
#define OPEN_CFW_AT_BUZZER_MISSING OPEN_CFW_AT_BUZZER_STRING(0x0075e150u)
#endif
#ifndef OPEN_CFW_AT_BUZZER_USAGE
#define OPEN_CFW_AT_BUZZER_USAGE OPEN_CFW_AT_BUZZER_STRING(0x0078a310u)
#endif
#ifndef OPEN_CFW_AT_BUZZER_USAGE_NOTE
#define OPEN_CFW_AT_BUZZER_USAGE_NOTE OPEN_CFW_AT_BUZZER_STRING(0x00747b5cu)
#endif
#ifndef OPEN_CFW_AT_BUZZER_USAGE_PLAY
#define OPEN_CFW_AT_BUZZER_USAGE_PLAY OPEN_CFW_AT_BUZZER_STRING(0x00769b14u)
#endif
#ifndef OPEN_CFW_AT_BUZZER_USAGE_START
#define OPEN_CFW_AT_BUZZER_USAGE_START OPEN_CFW_AT_BUZZER_STRING(0x007522e0u)
#endif
#ifndef OPEN_CFW_AT_BUZZER_USAGE_STOP
#define OPEN_CFW_AT_BUZZER_USAGE_STOP OPEN_CFW_AT_BUZZER_STRING(0x0077e1a4u)
#endif
#ifndef OPEN_CFW_AT_BUZZER_NOTE_MISSING
#define OPEN_CFW_AT_BUZZER_NOTE_MISSING OPEN_CFW_AT_BUZZER_STRING(0x00747b84u)
#endif
#ifndef OPEN_CFW_AT_BUZZER_NOTE_USAGE
#define OPEN_CFW_AT_BUZZER_NOTE_USAGE OPEN_CFW_AT_BUZZER_STRING(0x00731b14u)
#endif
#ifndef OPEN_CFW_AT_BUZZER_NOTE_INVALID
#define OPEN_CFW_AT_BUZZER_NOTE_INVALID OPEN_CFW_AT_BUZZER_STRING(0x00727164u)
#endif
#ifndef OPEN_CFW_AT_BUZZER_NOTE_RANGE
#define OPEN_CFW_AT_BUZZER_NOTE_RANGE OPEN_CFW_AT_BUZZER_STRING(0x0073c4b0u)
#endif
#ifndef OPEN_CFW_AT_BUZZER_NOTE_RANGE_HELP
#define OPEN_CFW_AT_BUZZER_NOTE_RANGE_HELP OPEN_CFW_AT_BUZZER_STRING(0x00752304u)
#endif
#ifndef OPEN_CFW_AT_BUZZER_NOTE_STATUS
#define OPEN_CFW_AT_BUZZER_NOTE_STATUS OPEN_CFW_AT_BUZZER_STRING(0x00747bd4u)
#endif
#ifndef OPEN_CFW_AT_BUZZER_PLAY_MISSING
#define OPEN_CFW_AT_BUZZER_PLAY_MISSING OPEN_CFW_AT_BUZZER_STRING(0x00752328u)
#endif
#ifndef OPEN_CFW_AT_BUZZER_PLAY_USAGE
#define OPEN_CFW_AT_BUZZER_PLAY_USAGE OPEN_CFW_AT_BUZZER_STRING(0x0075e190u)
#endif
#ifndef OPEN_CFW_AT_BUZZER_PLAY_RANGE
#define OPEN_CFW_AT_BUZZER_PLAY_RANGE OPEN_CFW_AT_BUZZER_STRING(0x0073c4dcu)
#endif
#ifndef OPEN_CFW_AT_BUZZER_PLAY_STATUS
#define OPEN_CFW_AT_BUZZER_PLAY_STATUS OPEN_CFW_AT_BUZZER_STRING(0x00775584u)
#endif
#ifndef OPEN_CFW_AT_BUZZER_START_MISSING
#define OPEN_CFW_AT_BUZZER_START_MISSING OPEN_CFW_AT_BUZZER_STRING(0x00747bfcu)
#endif
#ifndef OPEN_CFW_AT_BUZZER_START_USAGE
#define OPEN_CFW_AT_BUZZER_START_USAGE OPEN_CFW_AT_BUZZER_STRING(0x00747c24u)
#endif
#ifndef OPEN_CFW_AT_BUZZER_START_INVALID
#define OPEN_CFW_AT_BUZZER_START_INVALID OPEN_CFW_AT_BUZZER_STRING(0x007271ccu)
#endif
#ifndef OPEN_CFW_AT_BUZZER_START_RANGE
#define OPEN_CFW_AT_BUZZER_START_RANGE OPEN_CFW_AT_BUZZER_STRING(0x0073c508u)
#endif
#ifndef OPEN_CFW_AT_BUZZER_START_RANGE_HELP
#define OPEN_CFW_AT_BUZZER_START_RANGE_HELP OPEN_CFW_AT_BUZZER_STRING(0x0075e1d0u)
#endif
#ifndef OPEN_CFW_AT_BUZZER_START_STATUS
#define OPEN_CFW_AT_BUZZER_START_STATUS OPEN_CFW_AT_BUZZER_STRING(0x0075234cu)
#endif
#ifndef OPEN_CFW_AT_BUZZER_STOP_STATUS
#define OPEN_CFW_AT_BUZZER_STOP_STATUS OPEN_CFW_AT_BUZZER_STRING(0x00785110u)
#endif
#ifndef OPEN_CFW_AT_BUZZER_UNKNOWN
#define OPEN_CFW_AT_BUZZER_UNKNOWN OPEN_CFW_AT_BUZZER_STRING(0x00747c4cu)
#endif
#ifndef OPEN_CFW_AT_BUZZER_UNKNOWN_HELP
#define OPEN_CFW_AT_BUZZER_UNKNOWN_HELP OPEN_CFW_AT_BUZZER_STRING(0x0075e210u)
#endif
#ifndef OPEN_CFW_AT_BUZZER_OK
#define OPEN_CFW_AT_BUZZER_OK OPEN_CFW_AT_BUZZER_STRING(0x00785100u)
#endif

#ifndef OPEN_CFW_AT_BUZZER_OUTPUT
void open_cfw_retained_at_buzzer_output(const char *format, ...);
#define OPEN_CFW_AT_BUZZER_OUTPUT(...) \
    open_cfw_retained_at_buzzer_output(__VA_ARGS__)
#endif
#ifndef OPEN_CFW_AT_BUZZER_PLAY_NOTE
void open_cfw_retained_buzzer_play_note(uint8_t note, uint8_t tone, uint8_t beat);
#define OPEN_CFW_AT_BUZZER_PLAY_NOTE(note, tone, beat) \
    open_cfw_retained_buzzer_play_note((note), (tone), (beat))
#endif
#ifndef OPEN_CFW_AT_BUZZER_PLAY
void open_cfw_retained_buzzer_play(uint32_t type);
#define OPEN_CFW_AT_BUZZER_PLAY(type) open_cfw_retained_buzzer_play((type))
#endif
#ifndef OPEN_CFW_AT_BUZZER_START
void open_cfw_retained_buzzer_start(uint32_t frequency, uint8_t duty);
#define OPEN_CFW_AT_BUZZER_START(frequency, duty) \
    open_cfw_retained_buzzer_start((frequency), (duty))
#endif
#ifndef OPEN_CFW_AT_BUZZER_STOP
void open_cfw_retained_buzzer_stop(void);
#define OPEN_CFW_AT_BUZZER_STOP() open_cfw_retained_buzzer_stop()
#endif

static __attribute__((always_inline)) inline int
open_cfw_at_buzzer_prefix(const char *text, const char *prefix, uint32_t count)
{
    while (count != 0u) {
        if (*text != *prefix) {
            return 0;
        }
        ++text;
        ++prefix;
        --count;
    }
    return 1;
}

static __attribute__((always_inline)) inline const char *
open_cfw_at_buzzer_skip_space(const char *text)
{
    while (*text == ' ' || *text == '\t' || *text == '\r' || *text == '\n') {
        ++text;
    }
    return text;
}

static __attribute__((always_inline)) inline int open_cfw_at_buzzer_parse_signed(
    const char **cursor, int32_t *value
)
{
    const char *text = open_cfw_at_buzzer_skip_space(*cursor);
    uint32_t magnitude = 0u;
    uint32_t negative = 0u;
    uint32_t digits = 0u;

    if (*text == '+' || *text == '-') {
        negative = (uint32_t)(*text == '-');
        ++text;
    }
    while (*text >= '0' && *text <= '9') {
        uint32_t digit = (uint32_t)(*text - '0');
        if (magnitude > 214748364u
            || (magnitude == 214748364u
                && digit > (negative != 0u ? 8u : 7u))) {
            return 0;
        }
        magnitude = magnitude * 10u + digit;
        ++digits;
        ++text;
    }
    if (digits == 0u) {
        return 0;
    }
    *value = negative != 0u
        ? (int32_t)(0u - magnitude)
        : (int32_t)magnitude;
    *cursor = text;
    return 1;
}

static __attribute__((always_inline)) inline int open_cfw_at_buzzer_parse_list(
    const char *text, int32_t *values, uint32_t count
)
{
    uint32_t parsed = 0u;
    while (parsed < count) {
        if (!open_cfw_at_buzzer_parse_signed(&text, &values[parsed])) {
            return (int)parsed;
        }
        ++parsed;
        if (parsed != count) {
            text = open_cfw_at_buzzer_skip_space(text);
            if (*text != ',') {
                return (int)parsed;
            }
            ++text;
        }
    }
    return (int)parsed;
}

static int32_t open_cfw_at_buzzer_atoi(const char *text)
{
    int32_t value = 0;
    if (!open_cfw_at_buzzer_parse_signed(&text, &value)) {
        return 0;
    }
    return value;
}

int open_cfw_at_buzzer_test(const char *parameter)
{
    const char *comma;
    const char *arguments;
    char subcommand[16];
    uint32_t length = 0u;
    int32_t values[3] = {0, 0, 0};
    int parsed;

    if (parameter == (const char *)0) {
        OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_MISSING);
        OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_USAGE);
        OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_USAGE_NOTE);
        OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_USAGE_PLAY);
        OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_USAGE_START);
        OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_USAGE_STOP);
        return 0;
    }

    comma = parameter;
    while (*comma != '\0' && *comma != ',') {
        ++comma;
    }
    while (parameter[length] != '\0' && parameter + length != comma
           && length < 15u) {
        subcommand[length] = parameter[length];
        ++length;
    }
    subcommand[length] = '\0';
    arguments = *comma == ',' ? comma + 1 : (const char *)0;

    if (open_cfw_at_buzzer_prefix(
            subcommand, OPEN_CFW_AT_BUZZER_COMMAND_NOTE, 4u
        )) {
        if (arguments == (const char *)0) {
            OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_NOTE_MISSING);
            OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_NOTE_USAGE);
            return 0;
        }
        parsed = open_cfw_at_buzzer_parse_list(arguments, values, 3u);
        if (parsed != 3) {
            OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_NOTE_INVALID, parsed);
            OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_NOTE_USAGE);
            return 0;
        }
        if ((uint32_t)values[0] >= 8u || (uint32_t)values[1] >= 4u
            || (uint32_t)(values[2] - 1) >= 100u) {
            OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_NOTE_RANGE);
            OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_NOTE_RANGE_HELP);
            return 0;
        }
        OPEN_CFW_AT_BUZZER_OUTPUT(
            OPEN_CFW_AT_BUZZER_NOTE_STATUS, values[0], values[1], values[2]
        );
        OPEN_CFW_AT_BUZZER_PLAY_NOTE(
            (uint8_t)values[0], (uint8_t)values[1], (uint8_t)values[2]
        );
    } else if (open_cfw_at_buzzer_prefix(
                   subcommand, OPEN_CFW_AT_BUZZER_COMMAND_PLAY, 4u
               )) {
        if (arguments == (const char *)0) {
            OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_PLAY_MISSING);
            OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_PLAY_USAGE);
            return 0;
        }
        values[0] = open_cfw_at_buzzer_atoi(arguments);
        if ((uint32_t)values[0] >= 11u) {
            OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_PLAY_RANGE);
            return 0;
        }
        OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_PLAY_STATUS, values[0]);
        OPEN_CFW_AT_BUZZER_PLAY((uint32_t)values[0]);
    } else if (open_cfw_at_buzzer_prefix(
                   subcommand, OPEN_CFW_AT_BUZZER_COMMAND_START, 5u
               )) {
        if (arguments == (const char *)0) {
            OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_START_MISSING);
            OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_START_USAGE);
            return 0;
        }
        parsed = open_cfw_at_buzzer_parse_list(arguments, values, 2u);
        if (parsed != 2) {
            OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_START_INVALID, parsed);
            OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_START_USAGE);
            return 0;
        }
        if ((uint32_t)(values[0] - 1) >= 20000u
            || (uint32_t)values[1] >= 101u) {
            OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_START_RANGE);
            OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_START_RANGE_HELP);
            return 0;
        }
        OPEN_CFW_AT_BUZZER_OUTPUT(
            OPEN_CFW_AT_BUZZER_START_STATUS, values[0], values[1]
        );
        OPEN_CFW_AT_BUZZER_START((uint32_t)values[0], (uint8_t)values[1]);
    } else if (open_cfw_at_buzzer_prefix(
                   subcommand, OPEN_CFW_AT_BUZZER_COMMAND_STOP, 4u
               )) {
        OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_STOP_STATUS);
        OPEN_CFW_AT_BUZZER_STOP();
    } else {
        OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_UNKNOWN, subcommand);
        OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_UNKNOWN_HELP);
        return 0;
    }

    OPEN_CFW_AT_BUZZER_OUTPUT(OPEN_CFW_AT_BUZZER_OK);
    return 1;
}
