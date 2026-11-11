#include <stdint.h>

extern uint32_t r1_glasses_connection_handle_get(void);
extern int32_t r1_ble_tx_queue_dispatch_type2(uint32_t, const void *, uint32_t);
extern uint32_t r1_st25dvxxkc_field_seen_get(void);
extern int32_t r1_native_delayed_cancel(void (*)(uint32_t), uint32_t);
extern void r1_legacy_pair_hook_nop(uint32_t);
extern uint32_t r1_native_charger_state_get(void);
extern uint32_t r1_charge_state_byte_get(void);
extern uint32_t r1_kv_nv_r1_addr_set(const void *);
extern uint32_t r1_temperature_calibration_read(void *);
extern int32_t r1_native_memcmp(const uint8_t *, const uint8_t *, uint32_t);
extern uint32_t r1_batcfg_word_4c_get(void);
extern uint32_t r1_kv_nv_r1_word_set_b(uint32_t);
extern uint32_t r1_product_sn_letter_decode(void);
extern const uint8_t *r1_touch_model_table_get(uint32_t);
extern uint32_t r1_batcfg_byte0_get(void);
extern uint32_t r1_batcfg_flag1_get(void);
extern uint32_t r1_batcfg_word1_signed_get(void);
extern uint32_t r1_kv_power_byte_set(uint32_t);
extern uint32_t r1_kv_power_field_set(uint32_t);
extern uint32_t r1_legacy_battery_hook_nop(uint32_t);
extern uint32_t r1_device_info_configuration_byte78_get(void);
extern uint32_t r1_device_info_configuration_word74_get(void);
extern void r1_factory_mode_start(uint32_t, uint32_t);
extern uint32_t r1_factory_mode_stop(void);
extern void r1_kv_nv_r1_byte_set_a(uint32_t);
extern void r1_kv_nv_r1_word_set_a(uint32_t);

/* Stock 0x8967c: only the exact invalid handle suppresses dispatch.
 * Length and payload pass through unchanged; the queue result is narrowed
 * to its low byte. The motion adapter supplies a synchronous stack packet. */
uint32_t r1_legacy_bounded_reply_send(const void *payload, uint32_t length)
{
    uint32_t handle = r1_glasses_connection_handle_get();
    if (handle == 0xffffu)
        return 1;
    return (uint8_t)r1_ble_tx_queue_dispatch_type2(handle, payload, length);
}

/* Stock 0x62584: a legacy version request selects one of the two ten-byte
 * identifiers. Unknown selectors leave the caller's packet bytes intact. */
uint32_t r1_legacy_cmd_version_reply(uint32_t handle, void *packet)
{
    (void)handle;
    static const uint8_t firmware_version[10] = {
        '2', '.', '2', '.', '6', '.', '0', '0', '0', '9'
    };
    static const uint8_t hardware_version[10] = {
        '6', '0', '3', 'M', 'V', '1', '.', '9', '.', '3'
    };
    uint8_t *bytes = (uint8_t *)packet;
    const uint8_t *version = 0;
    if (bytes[3] == 0u)
        version = firmware_version;
    else if (bytes[3] == 1u)
        version = hardware_version;
    if (version != 0) {
        for (unsigned i = 0; i < 10u; ++i)
            bytes[4u + i] = version[i];
    }
    return r1_legacy_bounded_reply_send(packet, 14u);
}

/* Stock 0x62834: the fixed five-byte status response. */
uint32_t r1_legacy_reply_status_ff(uint32_t handle, void *packet)
{
    (void)handle;
    ((uint8_t *)packet)[4] = 0xffu;
    return r1_legacy_bounded_reply_send(packet, 5u);
}

/* Stock 0x628ae: only selector zero queries and returns the NFC field flag. */
uint32_t r1_legacy_reply_nfc_field_seen(uint32_t handle, void *packet)
{
    (void)handle;
    uint8_t *bytes = (uint8_t *)packet;
    if (bytes[3] != 0u)
        return 0u;
    bytes[4] = (uint8_t)r1_st25dvxxkc_field_seen_get();
    return r1_legacy_bounded_reply_send(packet, 5u);
}

/* Stock 0x4e1f8: cancel the pair hook on every selector; only selector one
 * writes a response status byte before the five-byte reply. */
uint32_t r1_legacy_cmd_cancel_event_reply(uint32_t handle, void *packet)
{
    (void)handle;
    uint8_t *bytes = (uint8_t *)packet;
    if (bytes[3] == 1u)
        bytes[4] = 1u;
    (void)r1_native_delayed_cancel(r1_legacy_pair_hook_nop, 0u);
    return r1_legacy_bounded_reply_send(packet, 5u);
}

/* Stock 0x62546: selector zero reports a charge-dependent type byte;
 * selector one reports the raw charger state. Every selector replies. */
uint32_t r1_legacy_cmd_battery_type_reply(uint32_t handle, void *packet)
{
    (void)handle;
    uint8_t *bytes = (uint8_t *)packet;
    if (bytes[3] == 0u) {
        uint32_t state = r1_native_charger_state_get();
        if (state == 0u)
            bytes[4] = (uint8_t)r1_charge_state_byte_get();
        else if (state == 1u)
            bytes[4] = 0x65u;
        else if (state == 2u)
            bytes[4] = 0x66u;
    } else if (bytes[3] == 1u) {
        bytes[4] = (uint8_t)r1_native_charger_state_get();
    }
    return r1_legacy_bounded_reply_send(packet, 5u);
}

/* Stock 0x62412: write the requested six-byte address, read it back, and
 * acknowledge only an exact match. Other selectors do not send a reply. */
uint32_t r1_legacy_cmd_mac_compare_reply(uint32_t handle, void *packet)
{
    (void)handle;
    uint8_t *bytes = (uint8_t *)packet;
    if (bytes[3] != 0u)
        return 0u;
    _Alignas(4) uint8_t readback[8] = {0};
    (void)r1_kv_nv_r1_addr_set(bytes + 4);
    (void)r1_temperature_calibration_read(readback);
    bytes[4] = (r1_native_memcmp(readback, bytes + 4, 6u) == 0) ? 1u : 0u;
    return r1_legacy_bounded_reply_send(packet, 5u);
}

/* Stock 0x62bec: selector zero returns the persisted low byte, or derives
 * it from the product model table when the word is erased. Selector one
 * persists the requested byte, reads it back, and sends the same reply. */
uint32_t r1_legacy_sn_derived_command(uint32_t handle, void *packet)
{
    (void)handle;
    uint8_t *bytes = (uint8_t *)packet;
    uint32_t value;
    if (bytes[3] == 0u) {
        value = r1_batcfg_word_4c_get();
        if (value == UINT32_MAX) {
            const uint8_t *model =
                r1_touch_model_table_get(r1_product_sn_letter_decode());
            value = model[0];
        }
    } else if (bytes[3] == 1u) {
        (void)r1_kv_nv_r1_word_set_b(bytes[4]);
        value = r1_batcfg_word_4c_get();
    } else {
        return 0u;
    }
    bytes[4] = (uint8_t)value;
    return r1_legacy_bounded_reply_send(packet, 5u);
}

/* Stock 0x62840: power-record byte, signed field, and flag read/write
 * commands. Only selectors zero through four send a reply. */
uint32_t r1_legacy_power_config_command(uint32_t handle, void *packet)
{
    (void)handle;
    uint8_t *bytes = (uint8_t *)packet;
    uint32_t selector = bytes[3];
    if (selector == 0u) {
        (void)r1_kv_power_byte_set(bytes[4]);
        bytes[4] = (uint8_t)r1_batcfg_byte0_get();
        return r1_legacy_bounded_reply_send(packet, 5u);
    }
    if (selector == 1u) {
        bytes[4] = (uint8_t)r1_batcfg_byte0_get();
        return r1_legacy_bounded_reply_send(packet, 5u);
    }
    if (selector == 3u) {
        uint32_t requested = (uint32_t)bytes[4] |
                             ((uint32_t)bytes[5] << 8u);
        if (requested == 0u)
            requested = 1u;
        (void)r1_kv_power_field_set((uint32_t)(int32_t)(int16_t)requested);
        (void)r1_legacy_battery_hook_nop(1u);
        selector = 2u;
    }
    if (selector == 2u) {
        uint32_t value = r1_batcfg_word1_signed_get();
        bytes[4] = (uint8_t)value;
        bytes[5] = (uint8_t)(value >> 8u);
        return r1_legacy_bounded_reply_send(packet, 6u);
    }
    if (selector == 4u) {
        bytes[4] = (uint8_t)r1_batcfg_flag1_get();
        return r1_legacy_bounded_reply_send(packet, 5u);
    }
    return 0u;
}

/* Stock 0x62388: factory-mode subcommands and device-configuration reads.
 * The passed handle gates reply calls independently of the global sender. */
uint32_t r1_legacy_subcommand_plan(uint32_t handle, void *packet)
{
    uint8_t *bytes = (uint8_t *)packet;
    uint32_t enabled = r1_device_info_configuration_byte78_get() & 0x10u;
    switch (bytes[3]) {
    case 0u:
        if (enabled != 0u) {
            bytes[4] = 0x12u;
            bytes[5] = 0x34u;
            if (handle != 0xffffu)
                return r1_legacy_bounded_reply_send(packet, 6u);
        } else {
            r1_factory_mode_start(handle, 1u);
        }
        return 0u;
    case 1u:
        for (uint32_t i = 4u; i < 36u; ++i)
            bytes[i] = 0u;
        bytes[4] = (uint8_t)r1_device_info_configuration_byte78_get();
        if (handle != 0xffffu)
            return r1_legacy_bounded_reply_send(packet, 5u);
        return 0u;
    case 2u:
        bytes[4] = r1_factory_mode_stop() != 0u ? 1u : 0u;
        if (handle != 0xffffu)
            return r1_legacy_bounded_reply_send(packet, 5u);
        return 0u;
    case 3u: {
        uint32_t value = r1_device_info_configuration_word74_get();
        bytes[4] = (uint8_t)value;
        bytes[5] = (uint8_t)(value >> 8u);
        bytes[6] = (uint8_t)(value >> 16u);
        bytes[7] = (uint8_t)(value >> 24u);
        if (handle != 0xffffu)
            return r1_legacy_bounded_reply_send(packet, 8u);
        return 0u;
    }
    case 4u:
        (void)r1_factory_mode_stop();
        r1_kv_nv_r1_byte_set_a(0u);
        r1_kv_nv_r1_word_set_a(0u);
        return 0u;
    default:
        return 0u;
    }
}
