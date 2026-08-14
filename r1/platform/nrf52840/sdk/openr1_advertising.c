#include "openr1_advertising.h"

#include <stddef.h>
#include <stdint.h>
#include <string.h>

#include "ble_advdata.h"
#include "nrf_sdh_ble.h"
#include "ble_advertising.h"
#include "ble_gap.h"
#include "nrf_error.h"

#define OPENR1_CONNECTION_CONFIGURATION_TAG 1u
#define OPENR1_APPEARANCE_GENERIC_KEYRING UINT16_C(0x0240)
#define OPENR1_COMPANY_IDENTIFIER UINT16_C(0x5245)
#define OPENR1_FAST_INTERVAL UINT16_C(0x00a0)
#define OPENR1_FAST_TIMEOUT_10MS UINT16_C(0x1770)
#define OPENR1_SLOW_INTERVAL UINT16_C(0x0640)
#define OPENR1_NAME_NORMAL_LENGTH 14u
#define OPENR1_NAME_FACTORY_LENGTH 18u
#define OPENR1_MANUFACTURER_BASE_LENGTH 6u
#define OPENR1_PRODUCT_SERIAL_LENGTH 15u

BLE_ADVERTISING_DEF(advertising);

static uint32_t last_error;
static bool advertising_active;

/* The module reports mode transitions it drives itself (boot start, fast/slow
   timeout transitions, disconnect restart) through this handler so the local
   active flag tracks the real advertiser state. It does not report the
   SoftDevice stopping the advertiser when a connection is established; that
   transition is resynchronized by openr1_advertising_connection_established. */
static void on_advertising_event(ble_adv_evt_t event) {
    if (event == BLE_ADV_EVT_IDLE) {
        advertising_active = false;
    } else if (event != BLE_ADV_EVT_WHITELIST_REQUEST &&
               event != BLE_ADV_EVT_PEER_ADDR_REQUEST) {
        advertising_active = true;
    }
}

static char hexadecimal(uint8_t value) {
    value &= 0x0fu;
    if (value < 10u) {
        return (char)((uint8_t)'0' + value);
    }
    return (char)((uint8_t)'A' + value - 10u);
}

static size_t build_name(char output[OPENR1_NAME_FACTORY_LENGTH],
                         const ble_gap_addr_t *address, bool factory_mode) {
    static const char prefix[] = "EVEN R1_";
    memcpy(output, prefix, sizeof prefix - 1u);
    const uint8_t selected[3] = {
        address->addr[3], address->addr[2], address->addr[1]
    };
    size_t offset = sizeof prefix - 1u;
    for (size_t index = 0u; index < 3u; ++index) {
        output[offset++] = hexadecimal((uint8_t)(selected[index] >> 4u));
        output[offset++] = hexadecimal(selected[index]);
    }
    if (factory_mode) {
        static const char suffix[] = "_FAC";
        memcpy(&output[offset], suffix, sizeof suffix - 1u);
        offset += sizeof suffix - 1u;
    }
    return offset;
}

static uint32_t configure_gap(const ble_gap_addr_t *address, bool factory_mode) {
    char name[OPENR1_NAME_FACTORY_LENGTH];
    const size_t name_length = build_name(name, address, factory_mode);
    const size_t expected = factory_mode ? OPENR1_NAME_FACTORY_LENGTH
                                         : OPENR1_NAME_NORMAL_LENGTH;
    if (name_length != expected) {
        return NRF_ERROR_INTERNAL;
    }
    ble_gap_conn_sec_mode_t open;
    BLE_GAP_CONN_SEC_MODE_SET_OPEN(&open);
    uint32_t error = sd_ble_gap_device_name_set(
        &open, (const uint8_t *)name, (uint16_t)name_length);
    if (error == NRF_SUCCESS) {
        error = sd_ble_gap_appearance_set(OPENR1_APPEARANCE_GENERIC_KEYRING);
    }
    if (error == NRF_SUCCESS) {
        const ble_gap_conn_params_t preferred = {
            .min_conn_interval = 12u,
            .max_conn_interval = 24u,
            .slave_latency = 4u,
            .conn_sup_timeout = 600u,
        };
        error = sd_ble_gap_ppcp_set(&preferred);
    }
    return error;
}

static void on_advertising_error(uint32_t error) {
    last_error = error;
}

uint32_t openr1_advertising_initialize(bool factory_mode,
                                        const uint8_t product_serial[15],
                                        bool serial_provisioned) {
    ble_gap_addr_t address;
    uint32_t error = sd_ble_gap_addr_get(&address);
    if (error != NRF_SUCCESS) {
        last_error = error;
        return error;
    }
    error = configure_gap(&address, factory_mode);
    if (error != NRF_SUCCESS) {
        last_error = error;
        return error;
    }

    uint8_t manufacturer[OPENR1_MANUFACTURER_BASE_LENGTH +
                         OPENR1_PRODUCT_SERIAL_LENGTH];
    memcpy(manufacturer, address.addr, OPENR1_MANUFACTURER_BASE_LENGTH);
    size_t manufacturer_length = OPENR1_MANUFACTURER_BASE_LENGTH;
    if (serial_provisioned) {
        if (product_serial == NULL) {
            last_error = NRF_ERROR_NULL;
            return last_error;
        }
        memcpy(&manufacturer[manufacturer_length], product_serial,
               OPENR1_PRODUCT_SERIAL_LENGTH);
        manufacturer_length += OPENR1_PRODUCT_SERIAL_LENGTH;
    }
    ble_advdata_manuf_data_t manufacturer_data = {
        .company_identifier = OPENR1_COMPANY_IDENTIFIER,
        .data = {
            .p_data = manufacturer,
            .size = (uint16_t)manufacturer_length,
        },
    };
    ble_advertising_init_t configuration;
    memset(&configuration, 0, sizeof configuration);
    configuration.advdata.name_type = BLE_ADVDATA_FULL_NAME;
    configuration.advdata.include_appearance = true;
    configuration.advdata.flags = BLE_GAP_ADV_FLAGS_LE_ONLY_GENERAL_DISC_MODE;
    configuration.srdata.p_manuf_specific_data = &manufacturer_data;
    configuration.config.ble_adv_fast_enabled = true;
    configuration.config.ble_adv_fast_interval = OPENR1_FAST_INTERVAL;
    configuration.config.ble_adv_fast_timeout =
        factory_mode ? 0u : OPENR1_FAST_TIMEOUT_10MS;
    configuration.config.ble_adv_slow_enabled = !factory_mode;
    configuration.config.ble_adv_slow_interval = OPENR1_SLOW_INTERVAL;
    configuration.config.ble_adv_slow_timeout = 0u;
    configuration.config.ble_adv_on_disconnect_disabled = false;
    configuration.evt_handler = on_advertising_event;
    configuration.error_handler = on_advertising_error;

    error = ble_advertising_init(&advertising, &configuration);
    if (error == NRF_SUCCESS) {
        ble_advertising_conn_cfg_tag_set(
            &advertising, OPENR1_CONNECTION_CONFIGURATION_TAG);
    }
    last_error = error;
    return error;
}

uint32_t openr1_advertising_start(void) {
    if (advertising_active) {
        return NRF_SUCCESS;
    }
    const uint32_t error = ble_advertising_start(&advertising, BLE_ADV_MODE_FAST);
    if (error == NRF_SUCCESS) {
        advertising_active = true;
    }
    last_error = error;
    return error;
}

uint32_t openr1_advertising_stop(void) {
    if (!advertising_active) {
        return NRF_SUCCESS;
    }
    uint32_t error = sd_ble_gap_adv_stop(advertising.adv_handle);
    if (error == NRF_ERROR_INVALID_STATE) {
        /* The SoftDevice already stopped the set; the desired state holds. */
        advertising_active = false;
        return NRF_SUCCESS;
    }
    if (error == NRF_SUCCESS) {
        advertising_active = false;
    }
    last_error = error;
    return error;
}

void openr1_advertising_connection_established(bool peripheral_role) {
    /* Only a peripheral-role connect stops this advertiser set. */
    if (peripheral_role) {
        advertising_active = false;
    }
}

uint32_t openr1_advertising_set_role_occupancy(bool phone_occupied,
                                               bool glasses_occupied) {
    if (phone_occupied && glasses_occupied) {
        return openr1_advertising_stop();
    }
    return openr1_advertising_start();
}

uint32_t openr1_advertising_last_error(void) {
    return last_error;
}
