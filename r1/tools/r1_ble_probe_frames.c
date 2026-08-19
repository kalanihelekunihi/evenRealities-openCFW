#include <stdint.h>
#include <stdio.h>

#include "openr1/r1_protocol.h"

static int emit(const char *name, uint16_t serial, uint8_t subcommand,
                const uint8_t *payload, size_t payload_length) {
    const r1_model model = {
        .version = R1_PROTOCOL_VERSION,
        .module = 1u,
        .module_version = R1_MODULE_VERSION,
        .serial = serial,
        .status = 0u,
        .command = 0u,
        .subcommand = subcommand,
        .payload = payload,
        .payload_length = payload_length,
    };
    uint8_t logical[R1_BLE_VALUE_MAX];
    size_t logical_length = 0u;
    if (r1_model_encode(&model, R1_CHECKSUM_PHONE_COMPACT_CCITT,
                        logical, sizeof logical, &logical_length) != R1_OK) {
        return 1;
    }
    r1_fragment_set fragments;
    if (r1_fragment_message(logical, logical_length, &fragments) != R1_OK ||
        fragments.count != 1u) {
        return 1;
    }
    (void)printf("%s=", name);
    for (size_t index = 0u; index < fragments.fragments[0].length; ++index) {
        (void)printf("%02X", fragments.fragments[0].bytes[index]);
    }
    (void)putchar('\n');
    return 0;
}

static void emit_channel1_nonmutating(void) {
    /* Legacy opcode 0x89 reads byte 3 as the command-valid flag. Keeping it
     * zero exercises bounded routing and the seven-byte response path without
     * changing wear, secondary-mode, touch, regulator, or radio policy. */
    static const uint8_t frame[] = {0u, 0u, 0x89u, 0u, 0u, 0u, 0u};
    (void)printf("channel1-nonmutating=");
    for (size_t index = 0u; index < sizeof frame; ++index) {
        (void)printf("%02X", frame[index]);
    }
    (void)putchar('\n');
}

int main(void) {
    static const uint8_t phone_role[] = {1u};
    if (emit("pair-role-phone", UINT16_C(0x3f00), 0x08u,
             phone_role, sizeof phone_role) != 0) {
        return 1;
    }
    if (emit("device-info", UINT16_C(0x3f01), 0x02u, NULL, 0u) != 0) {
        return 1;
    }
    if (emit("device-status", UINT16_C(0x4000), 0x01u, NULL, 0u) != 0) {
        return 1;
    }
    emit_channel1_nonmutating();
    return 0;
}
