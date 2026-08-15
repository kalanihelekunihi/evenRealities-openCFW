/*
 * Provenance banner
 * -----------------
 * Independently reconstructed C for the five-function GXCAS GXT310 family in
 * the R1 application image. This is decompilation-derived behavior, not
 * vendor source. See gxt310.h and
 * docs/correlation/GXT310-REDUCTION-CORRELATION.md for per-function evidence.
 */

#include "gxt310/gxt310.h"

static bool address_valid(uint8_t address) {
    return address == GXT310_CHANNEL_0_ADDRESS ||
           address == GXT310_CHANNEL_2_ADDRESS;
}

static void report_failure(gxt310_provider *provider,
                           gxt310_failure_operation operation,
                           uint8_t address) {
    if (provider != NULL && provider->failure != NULL) {
        provider->failure(provider->failure_context, operation, address);
    }
}

void gxt310_provider_initialize(gxt310_provider *provider,
                                gxt310_write_fn write,
                                void *write_context,
                                gxt310_failure_fn failure,
                                void *failure_context) {
    if (provider == NULL) {
        return;
    }
    provider->write = write;
    provider->write_context = write_context;
    provider->failure = failure;
    provider->failure_context = failure_context;
}

uint32_t gxt310_switch_mode(gxt310_provider *provider, uint8_t address,
                            bool enabled) {
    if (provider == NULL || provider->write == NULL || !address_valid(address)) {
        report_failure(provider, GXT310_FAILURE_SWITCH_MODE, address);
        return GXT310_STATUS_FAILURE;
    }

    /* Stock constants at 0x0006F6B4: little-endian word 0x0000C200.
     * The disable path ORs bit zero before writing exactly two bytes. */
    const uint8_t command[GXT310_COMMAND_BYTES] = {
        enabled ? UINT8_C(0x00) : UINT8_C(0x01),
        UINT8_C(0xC2),
    };
    if (!provider->write(provider->write_context, address,
                         GXT310_WRITE_OPERATION, command, sizeof(command))) {
        report_failure(provider, GXT310_FAILURE_SWITCH_MODE, address);
        return GXT310_STATUS_FAILURE;
    }
    return GXT310_STATUS_SUCCESS;
}

uint32_t gxt310_trigger_one_shot(gxt310_provider *provider, uint8_t address) {
    if (provider == NULL || provider->write == NULL || !address_valid(address)) {
        report_failure(provider, GXT310_FAILURE_TRIGGER_ONE_SHOT, address);
        return GXT310_STATUS_FAILURE;
    }

    /* Stock constant at 0x0006F794: little-endian word 0x0000C101. */
    static const uint8_t command[GXT310_COMMAND_BYTES] = {
        UINT8_C(0x01), UINT8_C(0xC1),
    };
    if (!provider->write(provider->write_context, address,
                         GXT310_WRITE_OPERATION, command, sizeof(command))) {
        report_failure(provider, GXT310_FAILURE_TRIGGER_ONE_SHOT, address);
        return GXT310_STATUS_FAILURE;
    }
    return GXT310_STATUS_SUCCESS;
}

uint32_t gxt310_channel_0_switch_mode(gxt310_provider *provider, bool enabled) {
    return gxt310_switch_mode(provider, GXT310_CHANNEL_0_ADDRESS, enabled);
}

uint32_t gxt310_channel_0_trigger_one_shot(gxt310_provider *provider) {
    return gxt310_trigger_one_shot(provider, GXT310_CHANNEL_0_ADDRESS);
}

uint32_t gxt310_channel_2_switch_mode(gxt310_provider *provider, bool enabled) {
    return gxt310_switch_mode(provider, GXT310_CHANNEL_2_ADDRESS, enabled);
}

uint32_t gxt310_channel_2_trigger_one_shot(gxt310_provider *provider) {
    return gxt310_trigger_one_shot(provider, GXT310_CHANNEL_2_ADDRESS);
}

uint32_t gxt310_enable_pair(gxt310_provider *provider) {
    /* Stock calls both channels even if the first fails, then returns the
     * bitwise AND of their 0/1 statuses. */
    const uint32_t channel_0 =
        gxt310_channel_0_switch_mode(provider, true);
    const uint32_t channel_2 =
        gxt310_channel_2_switch_mode(provider, true);
    return channel_0 & channel_2;
}
