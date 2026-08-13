#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include "openr1/r1_dispatch.h"
#include "openr1/r1_protocol.h"
#include "openr1/r1_state.h"

static int nibble(char value) {
    if (value >= '0' && value <= '9') {
        return value - '0';
    }
    if (value >= 'a' && value <= 'f') {
        return value - 'a' + 10;
    }
    if (value >= 'A' && value <= 'F') {
        return value - 'A' + 10;
    }
    return -1;
}

static bool parse_hex(const char *text, uint8_t *bytes, size_t capacity, size_t *length) {
    const size_t characters = strlen(text);
    if ((characters & 1u) != 0u || characters / 2u > capacity) {
        return false;
    }
    *length = characters / 2u;
    for (size_t index = 0u; index < *length; ++index) {
        const int high = nibble(text[index * 2u]);
        const int low = nibble(text[index * 2u + 1u]);
        if (high < 0 || low < 0) {
            return false;
        }
        bytes[index] = (uint8_t)((unsigned int)high << 4u | (unsigned int)low);
    }
    return true;
}

static void print_hex(const uint8_t *bytes, size_t length) {
    for (size_t index = 0u; index < length; ++index) {
        (void)printf("%02x", (unsigned int)bytes[index]);
    }
    (void)putchar('\n');
}

static void usage(const char *program) {
    (void)fprintf(stderr,
        "usage: %s SUBCOMMAND_HEX get|set [PAYLOAD_HEX] [authorized]\n", program);
}

int main(int argc, char **argv) {
    if (argc < 3 || argc > 5) {
        usage(argv[0]);
        return 2;
    }
    errno = 0;
    char *end = NULL;
    const unsigned long parsed = strtoul(argv[1], &end, 16);
    if (errno != 0 || end == argv[1] || *end != '\0' || parsed > UINT8_MAX ||
        (strcmp(argv[2], "get") != 0 && strcmp(argv[2], "set") != 0)) {
        usage(argv[0]);
        return 2;
    }

    uint8_t payload[R1_BLE_VALUE_MAX];
    size_t payload_length = 0u;
    if (argc >= 4 && strcmp(argv[3], "authorized") != 0 &&
        !parse_hex(argv[3], payload, sizeof payload, &payload_length)) {
        (void)fprintf(stderr, "invalid payload hex\n");
        return 2;
    }
    const bool authorized = (argc >= 4 && strcmp(argv[argc - 1], "authorized") == 0);
    r1_device_state state;
    r1_state_initialize(&state);
    r1_session session = {authorized, authorized, authorized, R1_ROLE_PHONE};
    const r1_model request = {
        R1_PROTOCOL_VERSION, 1u, R1_MODULE_VERSION, 1u,
        strcmp(argv[2], "set") == 0 ? 2u : 0u,
        0u, (uint8_t)parsed, payload, payload_length
    };
    r1_dispatch_result result;
    const r1_error dispatch_error = r1_dispatch(&state, &session, &request, &result);
    (void)printf("dispatch=%u responses=%zu\n", (unsigned int)dispatch_error, result.count);
    for (size_t response_index = 0u; response_index < result.count; ++response_index) {
        r1_fragment_set fragments;
        const r1_error fragment_error = r1_fragment_message(
            result.models[response_index], result.lengths[response_index], &fragments);
        if (fragment_error != R1_OK) {
            (void)fprintf(stderr, "response fragmentation failed: %u\n",
                          (unsigned int)fragment_error);
            return 1;
        }
        for (size_t fragment_index = 0u; fragment_index < fragments.count; ++fragment_index) {
            print_hex(fragments.fragments[fragment_index].bytes,
                      fragments.fragments[fragment_index].length);
        }
    }
    return result.count > 0u ? 0 : 1;
}
