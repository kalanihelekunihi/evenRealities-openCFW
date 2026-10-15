#include <stdint.h>

extern uint32_t audio_ble_pair_timestamp_counter_20074344;
extern uint32_t audio_ble_privacy_rewrite_record(uint8_t *);
extern uint8_t audio_ble_pair_record_validate(uint8_t *);
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t, const char *, const char *, const char *,
                               uint32_t, const char *, ...);
extern uint32_t compressed_log_output(uint32_t, const char *, const char *, ...);

static const char module[] = "ble.smpdb";
static const char path[] =
    "D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\common\\app_db.c";
static const char function[] = "AppDbValidateRecord";
static const char validating[] =
    "AppDbValidateRecord: Validating record with keyMask=0x%02x";
static const char validating_compact[] =
    "[ble.smpdb]AppDbValidateRecord: Validating record with keyMask=0x%02x";
static const char validated[] =
    "AppDbValidateRecord: Record validated successfully, valid=TRUE, keyMask=0x%02x";
static const char validated_compact[] =
    "[ble.smpdb]AppDbValidateRecord: Record validated successfully, valid=TRUE, keyMask=0x%02x";
static const char saved[] = "AppDbValidateRecord: Record successfully saved to Flash";
static const char saved_compact[] =
    "[ble.smpdb]AppDbValidateRecord: Record successfully saved to Flash";

static uint32_t compact_enabled(void)
{
    if ((audio_log_flags() & 1u) != 0u)
        return 1u;
    return (audio_log_flags() & 4u) != 0u;
}

/* Native 0x47a49c, including its three diagnostic stages. */
void audio_ble_master_pair_state_47a49c(uint32_t address, uint8_t mode)
{
    volatile uint8_t *record = (volatile uint8_t *)(uintptr_t)address;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 0x2c5u, validating, mode);
    if (compact_enabled() != 0u)
        (void)compressed_log_output(0x10400000u, validating_compact,
                                    validating_compact, mode);
    record[0x30u] = 1u;
    record[0x2fu] = 1u;
    record[0x2eu] = mode;
    uint32_t stamp = ++audio_ble_pair_timestamp_counter_20074344;
    *(volatile uint32_t *)(void *)(record + 0xc4u) = stamp;
    if ((audio_log_flags() & 2u) != 0u)
        audio_log_extended(4u, module, path, function, 0x2ccu, validated, mode);
    if (compact_enabled() != 0u)
        (void)compressed_log_output(0x10400000u, validated_compact,
                                    validated_compact, mode);
    uint32_t saved_to_flash = audio_ble_privacy_rewrite_record((uint8_t *)(uintptr_t)address);
    (void)audio_ble_pair_record_validate((uint8_t *)(uintptr_t)address);
    if (saved_to_flash == 1u) {
        if ((audio_log_flags() & 2u) != 0u)
            audio_log_extended(4u, module, path, function, 0x2d3u, saved);
        if (compact_enabled() != 0u)
            (void)compressed_log_output(0x10000000u, saved_compact, saved_compact);
    }
}
