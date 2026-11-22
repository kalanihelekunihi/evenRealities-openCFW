/* Checked calls into the source-built lower Cordio region. The first-page
 * C MBR validates its descriptor and initializes lower RAM before use. */
#include <stdbool.h>
#include <stdint.h>
#include "nrf.h"
#include "nrf_error.h"
#include "ble.h"
#include "nrf_sdm.h"
#include "../../shared/cordio_region_descriptor.h"
#include "../../mbr/copy_record.h"
#include "cordio_ble_events.h"

#if defined(SVCALL_AS_NORMAL_FUNCTION)
static const volatile r1_cordio_region_descriptor_t *validated_desc;

uint32_t r1_bootloader_cordio_region_init(void)
{
    validated_desc = 0;
    if (*(volatile const uint32_t *)R1_MBR_CORDIO_INIT_TAG_ADDRESS !=
        R1_MBR_CORDIO_INIT_TAG)
        return NRF_ERROR_INVALID_STATE;
    uint32_t (*initialize)(void) =
        (uint32_t (*)(void))(uintptr_t)R1_MBR_CORDIO_INIT_ENTRY;
    if (initialize() != 1u) return NRF_ERROR_INVALID_STATE;
    validated_desc =
        (const volatile r1_cordio_region_descriptor_t *)R1_CORDIO_FLASH_BASE;
    return NRF_SUCCESS;
}

/* These entry points are intentionally separate from Nordic's sd_* API.
 * A DFU host adapter must configure its own WSF handlers and event delivery
 * before enabling BLE or calling the dispatcher. */
bool r1_bootloader_cordio_controller_bootstrap(void)
{
    if (validated_desc == 0) return false;
    bool (*start)(void) =
        (bool (*)(void))(uintptr_t)validated_desc->controller_bootstrap;
    if (!start()) return false;
    void (*flash_register)(void) =
        (void (*)(void))(uintptr_t)validated_desc->dfu_flash_register;
    flash_register();
    return true;
}

bool r1_bootloader_cordio_dispatch_once(void)
{
    if (validated_desc == 0) return false;
    void (*timer_update)(void) =
        (void (*)(void))(uintptr_t)validated_desc->timer_update;
    void (*dispatch)(void) =
        (void (*)(void))(uintptr_t)validated_desc->dispatch_once;
    timer_update();
    dispatch();
    void (*flash_service)(void) =
        (void (*)(void))(uintptr_t)validated_desc->dfu_flash_service;
    flash_service();
    return true;
}

bool r1_bootloader_cordio_dfu_host_start(void)
{
    if (validated_desc == 0) return false;
    bool (*start)(bool (*)(const void *, uint16_t)) =
        (bool (*)(bool (*)(const void *, uint16_t)))
            (uintptr_t)validated_desc->dfu_host_start;
    return start(r1_bootloader_ble_event_publish);
}

bool r1_bootloader_cordio_dfu_host_ready(void)
{
    if (validated_desc == 0) return false;
    bool (*ready)(void) =
        (bool (*)(void))(uintptr_t)validated_desc->dfu_host_ready;
    return ready();
}

uint32_t r1_bootloader_cordio_dfu_ble_enable(void *arena,
                                             uint32_t arena_bytes)
{
    if (validated_desc == 0) return NRF_ERROR_INVALID_STATE;
    uint32_t (*enable)(bool (*)(const void *, uint16_t), void *, uint32_t,
                       uint32_t (*)(const ble_uuid_t *, uint8_t *, uint8_t *)) =
        (uint32_t (*)(bool (*)(const void *, uint16_t), void *, uint32_t,
                      uint32_t (*)(const ble_uuid_t *, uint8_t *, uint8_t *)))
            (uintptr_t)validated_desc->dfu_ble_enable;
    return enable(r1_bootloader_ble_event_publish, arena, arena_bytes,
                  sd_ble_uuid_encode);
}

/* The DFU SDK reaches these GATT/security calls only after sd_ble_enable.
 * That path validates and stores the lower descriptor before registration. */
uint32_t sd_ble_gatts_service_add(uint8_t type, ble_uuid_t const *uuid,
                                   uint16_t *handle)
{
    uint32_t (*add)(uint8_t, ble_uuid_t const *, uint16_t *) =
        (void *)(uintptr_t)validated_desc->gatts_service_add;
    return add(type, uuid, handle);
}

uint32_t sd_ble_gatts_characteristic_add(
    uint16_t service_handle, ble_gatts_char_md_t const *metadata,
    ble_gatts_attr_t const *value, ble_gatts_char_handles_t *handles)
{
    uint32_t (*add)(uint16_t, ble_gatts_char_md_t const *,
                    ble_gatts_attr_t const *, ble_gatts_char_handles_t *) =
        (void *)(uintptr_t)validated_desc->gatts_characteristic_add;
    return add(service_handle, metadata, value, handles);
}

uint32_t sd_ble_gatts_hvx(uint16_t conn_handle,
                           ble_gatts_hvx_params_t const *params)
{
    uint32_t (*send)(uint16_t, ble_gatts_hvx_params_t const *) =
        (void *)(uintptr_t)validated_desc->gatts_hvx;
    return send(conn_handle, params);
}

uint32_t sd_ble_gatts_sys_attr_set(uint16_t conn_handle,
                                    uint8_t const *data, uint16_t length,
                                    uint32_t flags)
{
    uint32_t (*set)(uint16_t, uint8_t const *, uint16_t, uint32_t) =
        (void *)(uintptr_t)validated_desc->gatts_sys_attr_set;
    return set(conn_handle, data, length, flags);
}

uint32_t sd_ble_gatts_rw_authorize_reply(
    uint16_t conn_handle, ble_gatts_rw_authorize_reply_params_t const *reply)
{
    uint32_t (*respond)(uint16_t,
                         ble_gatts_rw_authorize_reply_params_t const *) =
        (void *)(uintptr_t)validated_desc->gatts_authorize_reply;
    return respond(conn_handle, reply);
}

uint32_t sd_ble_gatts_value_get(uint16_t conn_handle,
                                 uint16_t handle, ble_gatts_value_t *value)
{
    uint32_t (*get)(uint16_t, uint16_t, ble_gatts_value_t *) =
        (void *)(uintptr_t)validated_desc->dfu_gatts_value_get;
    return get(conn_handle, handle, value);
}

uint32_t sd_ble_gap_sec_params_reply(
    uint16_t conn_handle, uint8_t status,
    ble_gap_sec_params_t const *parameters,
    ble_gap_sec_keyset_t const *keys)
{
    uint32_t (*reply)(uint16_t, uint8_t, const ble_gap_sec_params_t *,
                      const ble_gap_sec_keyset_t *) =
        (void *)(uintptr_t)validated_desc->dfu_sec_params_reply;
    return reply(conn_handle, status, parameters, keys);
}

uint32_t sd_ble_gap_sec_info_reply(
    uint16_t conn_handle, ble_gap_enc_info_t const *enc_info,
    ble_gap_irk_t const *id_info, ble_gap_sign_info_t const *sign_info)
{
    uint32_t (*reply)(uint16_t, const ble_gap_enc_info_t *,
                      const ble_gap_irk_t *, const ble_gap_sign_info_t *) =
        (void *)(uintptr_t)validated_desc->dfu_sec_info_reply;
    return reply(conn_handle, enc_info, id_info, sign_info);
}

uint32_t sd_softdevice_disable(void)
{
    uint32_t (*disable)(void) =
        (void *)(uintptr_t)validated_desc->dfu_manager_disable;
    return disable();
}

bool r1_bootloader_cordio_set_bd_addr(const uint8_t address[6])
{
    if (validated_desc == 0 || address == 0) return false;
    void (*set_address)(const uint8_t *) =
        (void (*)(const uint8_t *))(uintptr_t)validated_desc->ll_set_bd_addr;
    set_address(address);
    return true;
}

/* The bootloader vectors share one C dispatcher. The active exception
 * number identifies the lower controller ISR without six separate veneers. */
void r1_bootloader_cordio_irq_forward(void)
{
    if (validated_desc == 0) return;
    uint32_t entry;
    switch (SCB->ICSR & SCB_ICSR_VECTACTIVE_Msk) {
    case 16u + POWER_CLOCK_IRQn: entry = validated_desc->clock_irq; break;
    case 16u + RADIO_IRQn: entry = validated_desc->radio_irq; break;
    case 16u + TIMER0_IRQn: entry = validated_desc->timer0_irq; break;
    case 16u + TIMER1_IRQn: entry = validated_desc->timer1_irq; break;
    case 16u + CCM_AAR_IRQn: entry = validated_desc->ccm_aar_irq; break;
    case 16u + RTC1_IRQn: entry = validated_desc->rtc1_irq; break;
    default: return;
    }
    ((void (*)(void))(uintptr_t)entry)();
}

uint32_t r1_bootloader_cordio_dfu_cfg_set(uint32_t cfg_id,
                                            ble_cfg_t const *cfg)
{
    if (validated_desc == 0) return NRF_ERROR_INVALID_STATE;
    uint32_t (*set)(uint32_t, ble_cfg_t const *) =
        (uint32_t (*)(uint32_t, ble_cfg_t const *))
            (uintptr_t)validated_desc->dfu_cfg_set;
    return set(cfg_id, cfg);
}

bool r1_bootloader_cordio_dfu_cfg_ready(void)
{
    if (validated_desc == 0) return false;
    bool (*ready)(void) =
        (bool (*)(void))(uintptr_t)validated_desc->dfu_cfg_ready;
    return ready();
}

uint32_t r1_bootloader_cordio_dfu_manager_enable(
    nrf_clock_lf_cfg_t const *clock, nrf_fault_handler_t fault_handler)
{
    if (validated_desc == 0) return NRF_ERROR_INVALID_STATE;
    uint32_t (*enable)(nrf_clock_lf_cfg_t const *, nrf_fault_handler_t) =
        (uint32_t (*)(nrf_clock_lf_cfg_t const *, nrf_fault_handler_t))
            (uintptr_t)validated_desc->dfu_manager_enable;
    return enable(clock, fault_handler);
}

uint32_t sd_ble_gap_device_name_set(ble_gap_conn_sec_mode_t const *permission,
                                    uint8_t const *name, uint16_t length)
{
    if (validated_desc == 0) return NRF_ERROR_INVALID_STATE;
    uint32_t (*set)(ble_gap_conn_sec_mode_t const *, uint8_t const *, uint16_t) =
        (uint32_t (*)(ble_gap_conn_sec_mode_t const *, uint8_t const *, uint16_t))
            (uintptr_t)validated_desc->gap_device_name_set;
    return set(permission, name, length);
}

uint32_t sd_ble_gap_device_name_get(uint8_t *name, uint16_t *length)
{
    if (validated_desc == 0) return NRF_ERROR_INVALID_STATE;
    uint32_t (*get)(uint8_t *, uint16_t *) =
        (uint32_t (*)(uint8_t *, uint16_t *))
            (uintptr_t)validated_desc->gap_device_name_get;
    return get(name, length);
}

uint32_t sd_ble_gap_ppcp_set(ble_gap_conn_params_t const *params)
{
    if (validated_desc == 0) return NRF_ERROR_INVALID_STATE;
    uint32_t (*set)(ble_gap_conn_params_t const *) =
        (uint32_t (*)(ble_gap_conn_params_t const *))
            (uintptr_t)validated_desc->gap_ppcp_set;
    return set(params);
}

uint32_t sd_ble_gap_adv_set_configure(uint8_t *handle,
                                      ble_gap_adv_data_t const *data,
                                      ble_gap_adv_params_t const *params)
{
    if (validated_desc == 0) return NRF_ERROR_INVALID_STATE;
    uint32_t (*configure)(uint8_t *, ble_gap_adv_data_t const *,
                          ble_gap_adv_params_t const *) =
        (uint32_t (*)(uint8_t *, ble_gap_adv_data_t const *,
                      ble_gap_adv_params_t const *))
            (uintptr_t)validated_desc->gap_adv_configure;
    return configure(handle, data, params);
}

uint32_t sd_ble_gap_adv_start(uint8_t handle, uint8_t conn_tag)
{
    if (validated_desc == 0) return NRF_ERROR_INVALID_STATE;
    uint32_t (*start)(uint8_t, uint8_t) =
        (uint32_t (*)(uint8_t, uint8_t))
            (uintptr_t)validated_desc->gap_adv_start;
    return start(handle, conn_tag);
}

uint32_t sd_ble_gap_adv_stop(uint8_t handle)
{
    if (validated_desc == 0) return NRF_ERROR_INVALID_STATE;
    uint32_t (*stop)(uint8_t) =
        (uint32_t (*)(uint8_t))
            (uintptr_t)validated_desc->gap_adv_stop;
    return stop(handle);
}

uint32_t sd_evt_get(uint32_t *event_id)
{
    if (validated_desc == 0) return NRF_ERROR_INVALID_STATE;
    uint32_t (*get)(uint32_t *) =
        (uint32_t (*)(uint32_t *))(uintptr_t)validated_desc->soc_evt_get;
    return get(event_id);
}

uint32_t sd_flash_page_erase(uint32_t page_number)
{
    if (validated_desc == 0) return NRF_ERROR_INVALID_STATE;
    uint32_t (*erase)(uint32_t) =
        (uint32_t (*)(uint32_t))(uintptr_t)validated_desc->dfu_flash_erase;
    return erase(page_number);
}

uint32_t sd_flash_write(uint32_t *destination, uint32_t const *source,
                        uint32_t words)
{
    if (validated_desc == 0) return NRF_ERROR_INVALID_STATE;
    uint32_t (*write)(uint32_t *, uint32_t const *, uint32_t) =
        (uint32_t (*)(uint32_t *, uint32_t const *, uint32_t))
            (uintptr_t)validated_desc->dfu_flash_write;
    return write(destination, source, words);
}

uint32_t sd_ble_gap_disconnect(uint16_t conn_handle, uint8_t reason)
{
    if (validated_desc == 0) return NRF_ERROR_INVALID_STATE;
    uint32_t (*disconnect)(uint16_t, uint8_t) =
        (uint32_t (*)(uint16_t, uint8_t))
            (uintptr_t)validated_desc->dfu_gap_disconnect;
    return disconnect(conn_handle, reason);
}

uint32_t sd_ble_gap_conn_param_update(uint16_t conn_handle,
                                      ble_gap_conn_params_t const *params)
{
    if (validated_desc == 0) return NRF_ERROR_INVALID_STATE;
    uint32_t (*update)(uint16_t, ble_gap_conn_params_t const *) =
        (uint32_t (*)(uint16_t, ble_gap_conn_params_t const *))
            (uintptr_t)validated_desc->dfu_gap_conn_param_update;
    return update(conn_handle, params);
}

uint32_t sd_ble_gap_data_length_update(
    uint16_t conn_handle, ble_gap_data_length_params_t const *params,
    ble_gap_data_length_limitation_t *limitation)
{
    if (validated_desc == 0) return NRF_ERROR_INVALID_STATE;
    uint32_t (*update)(uint16_t, ble_gap_data_length_params_t const *,
                       ble_gap_data_length_limitation_t *) =
        (uint32_t (*)(uint16_t, ble_gap_data_length_params_t const *,
                      ble_gap_data_length_limitation_t *))
            (uintptr_t)validated_desc->dfu_gap_data_length_update;
    return update(conn_handle, params, limitation);
}

uint32_t sd_ble_gap_phy_update(uint16_t conn_handle,
                               ble_gap_phys_t const *phys)
{
    if (validated_desc == 0) return NRF_ERROR_INVALID_STATE;
    uint32_t (*update)(uint16_t, ble_gap_phys_t const *) =
        (uint32_t (*)(uint16_t, ble_gap_phys_t const *))
            (uintptr_t)validated_desc->dfu_gap_phy_update;
    return update(conn_handle, phys);
}

uint32_t sd_ble_gatts_exchange_mtu_reply(uint16_t conn_handle,
                                          uint16_t server_rx_mtu)
{
    if (validated_desc == 0) return NRF_ERROR_INVALID_STATE;
    uint32_t (*reply)(uint16_t, uint16_t) =
        (uint32_t (*)(uint16_t, uint16_t))
            (uintptr_t)validated_desc->dfu_gatts_exchange_mtu_reply;
    return reply(conn_handle, server_rx_mtu);
}
#endif
