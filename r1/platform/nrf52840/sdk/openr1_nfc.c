#include "openr1_nfc.h"

#include <limits.h>
#include <stddef.h>
#include <string.h>

#include "FreeRTOS.h"
#include "app_timer.h"
#include "cmsis_os2.h"
#include "nrf_gpio.h"
#include "nrfx_gpiote.h"
#include "nrfx_twim.h"
#include "st25dvxxkc.h"
#include "st25dvxxkc_reg.h"
#include "task.h"

#include "openr1/r1_st25dvxxkc.h"

#include "openr1_twim1_arbiter.h"

#define OPENR1_NFC_TWIM_SCL_PIN NRF_GPIO_PIN_MAP(1, 11)
#define OPENR1_NFC_TWIM_SDA_PIN NRF_GPIO_PIN_MAP(1, 14)
#define OPENR1_NFC_GPO_PIN NRF_GPIO_PIN_MAP(0, 3)
#define OPENR1_NFC_TWIM_PRIORITY 2u
#define OPENR1_NFC_FLAG_UPDATE UINT32_C(0x01)
#define OPENR1_NFC_FLAG_GPO UINT32_C(0x02)
#define OPENR1_NFC_FLAGS (OPENR1_NFC_FLAG_UPDATE | OPENR1_NFC_FLAG_GPO)
#define OPENR1_NFC_THREAD_STACK_WORDS (configMINIMAL_STACK_SIZE * 2u)
#define OPENR1_NFC_REGISTER_BYTES 2u
#define OPENR1_NFC_MAX_WRITE_BYTES 256u

/*
 * The TWIM1 hardware instance is owned by openr1_twim1_arbiter; this client
 * only keeps its recovered pin/frequency/priority configuration and passes it
 * to the arbiter on acquisition. NFC runs in the dock context, so its
 * acquisition performs the documented handoff from the worn motion context.
 */
static const nrfx_twim_config_t nfc_bus_configuration = {
    .scl = OPENR1_NFC_TWIM_SCL_PIN,
    .sda = OPENR1_NFC_TWIM_SDA_PIN,
    .frequency = NRF_TWIM_FREQ_400K,
    .interrupt_priority = OPENR1_NFC_TWIM_PRIORITY,
    .hold_bus_uninit = false,
};
static ST25DVxxKC_Object_t nfc_tag;
static r1_st25dvxxkc_adapter nfc_adapter;
static osThreadId_t nfc_thread;
static StaticTask_t nfc_control_block;
static StackType_t nfc_stack[OPENR1_NFC_THREAD_STACK_WORDS];
static const openr1_nfc_resource_ops *resource_ops;
static void *resource_context;
static openr1_nfc_frame_handler frame_handler;
static void *frame_context;
static volatile uint32_t last_error;
static bool twim_active;
static bool gpo_configured;
static bool power_active;
static bool bus_lease_active;
static bool nfc_active;
static bool requested_active;

static bool resources_complete(void) {
    return resource_ops != NULL && resource_ops->acquire_power != NULL &&
           resource_ops->release_power != NULL &&
           resource_ops->acquire_i2c5 != NULL &&
           resource_ops->release_i2c5 != NULL;
}

static int32_t bus_initialize(void) {
    if (twim_active) {
        return 0;
    }
    const nrfx_err_t error = openr1_twim1_acquire(
        OPENR1_TWIM1_CLIENT_NFC, &nfc_bus_configuration);
    if (error != NRFX_SUCCESS) {
        last_error = error;
        return -1;
    }
    twim_active = true;
    return 0;
}

static int32_t bus_deinitialize(void) {
    if (twim_active) {
        const nrfx_err_t error = openr1_twim1_release(OPENR1_TWIM1_CLIENT_NFC);
        if (error != NRFX_SUCCESS) {
            last_error = error;
            return -1;
        }
        twim_active = false;
    }
    return 0;
}

static bool valid_wire_address(uint16_t device_address) {
    const uint16_t data_address = (uint16_t)ST25DVXXKC_ADDR_DATA_I2C;
    const uint16_t system_address =
        (uint16_t)(ST25DVXXKC_ADDR_DATA_I2C |
                   ST25DVXXKC_ADDR_SYSTEMMEMORY_BIT_I2C |
                   ST25DVXXKC_ADDR_MODE_BIT_I2C);
    return device_address == data_address || device_address == system_address;
}

static int32_t bus_read(uint16_t device_address, uint16_t register_address,
                        uint8_t *bytes, uint16_t length) {
    if (!twim_active || !valid_wire_address(device_address) || bytes == NULL ||
        length == 0u || !bus_lease_active) {
        return -1;
    }
    const uint8_t address[OPENR1_NFC_REGISTER_BYTES] = {
        (uint8_t)(register_address >> 8u), (uint8_t)register_address};
    const uint8_t seven_bit_address = (uint8_t)(device_address >> 1u);
    nrfx_err_t error = openr1_twim1_tx(OPENR1_TWIM1_CLIENT_NFC,
                                       seven_bit_address, address,
                                       sizeof address, true);
    if (error == NRFX_SUCCESS) {
        error = openr1_twim1_rx(OPENR1_TWIM1_CLIENT_NFC, seven_bit_address,
                                bytes, length);
    }
    if (error != NRFX_SUCCESS) {
        last_error = error;
        return -1;
    }
    return 0;
}

static int32_t bus_write(uint16_t device_address, uint16_t register_address,
                         const uint8_t *bytes, uint16_t length) {
    if (!twim_active || !valid_wire_address(device_address) ||
        length > OPENR1_NFC_MAX_WRITE_BYTES ||
        (length != 0u && bytes == NULL) || !bus_lease_active) {
        return -1;
    }
    uint8_t frame[OPENR1_NFC_REGISTER_BYTES + OPENR1_NFC_MAX_WRITE_BYTES];
    frame[0] = (uint8_t)(register_address >> 8u);
    frame[1] = (uint8_t)register_address;
    if (length != 0u) {
        memcpy(frame + OPENR1_NFC_REGISTER_BYTES, bytes, length);
    }
    const uint8_t seven_bit_address = (uint8_t)(device_address >> 1u);
    const nrfx_err_t error = openr1_twim1_tx(
        OPENR1_TWIM1_CLIENT_NFC, seven_bit_address, frame,
        (size_t)length + OPENR1_NFC_REGISTER_BYTES, false);
    if (error != NRFX_SUCCESS) {
        last_error = error;
        return -1;
    }
    return 0;
}

static int32_t bus_is_ready(uint16_t device_address, uint32_t trials) {
    (void)trials;
    if (!twim_active || !bus_lease_active ||
        !valid_wire_address(device_address)) {
        return -1;
    }
    (void)osDelay(10u);
    return 0;
}

static int32_t bus_get_tick(void) {
    return (int32_t)app_timer_cnt_get();
}

static int32_t provider_initialize(void *context) {
    (void)context;
    static const ST25DVxxKC_IO_t bus_io = {
        bus_initialize,
        bus_deinitialize,
        bus_is_ready,
        bus_write,
        bus_read,
        bus_get_tick,
        0u,
    };
    int32_t status = ST25DVxxKC_RegisterBusIO(&nfc_tag, &bus_io);
    if (status == NFCTAG_OK) {
        status = St25Dvxxkc_Drv.Init(&nfc_tag);
    }
    return status;
}

static void provider_deinitialize(void *context) {
    (void)context;
    nfc_tag.IsInitialized = 0u;
    (void)bus_deinitialize();
}

static int32_t provider_read_id(void *context, uint8_t *ic_reference) {
    (void)context;
    return St25Dvxxkc_Drv.ReadID(&nfc_tag, ic_reference);
}

static int32_t provider_read_session(void *context, bool *open) {
    (void)context;
    ST25DVxxKC_I2CSSO_STATUS_E session = ST25DVXXKC_SESSION_CLOSED;
    const int32_t status = ST25DVxxKC_ReadI2CSecuritySession_Dyn(
        &nfc_tag, &session);
    if (status == NFCTAG_OK) {
        *open = session == ST25DVXXKC_SESSION_OPEN;
    }
    return status;
}

static int32_t provider_present_password(void *context, uint32_t most_significant,
                                         uint32_t least_significant) {
    (void)context;
    const ST25DVxxKC_PASSWD_t password = {
        most_significant,
        least_significant,
    };
    return ST25DVxxKC_PresentI2CPassword(&nfc_tag, password);
}

static int32_t provider_read_mailbox_mode(void *context, bool *enabled) {
    (void)context;
    ST25DVxxKC_EN_STATUS_E mailbox_mode = ST25DVXXKC_DISABLE;
    const int32_t status = ST25DVxxKC_ReadMBMode(&nfc_tag, &mailbox_mode);
    if (status == NFCTAG_OK) {
        *enabled = mailbox_mode == ST25DVXXKC_ENABLE;
    }
    return status;
}

static int32_t provider_read_mailbox_status(
    void *context, r1_st25dvxxkc_mailbox_status *status) {
    (void)context;
    ST25DVxxKC_MB_CTRL_DYN_STATUS_t provider_status;
    memset(&provider_status, 0, sizeof provider_status);
    const int32_t result = ST25DVxxKC_ReadMBCtrl_Dyn(
        &nfc_tag, &provider_status);
    if (result == NFCTAG_OK) {
        status->mailbox_enabled = provider_status.MbEnable != 0u;
        status->host_put_message = provider_status.HostPutMsg != 0u;
        status->rf_put_message = provider_status.RfPutMsg != 0u;
        status->host_missed_message = provider_status.HostMissMsg != 0u;
        status->rf_missed_message = provider_status.RFMissMsg != 0u;
        status->current_message =
            (r1_st25dvxxkc_message_owner)provider_status.CurrentMsg;
    }
    return result;
}

static int32_t provider_set_mailbox_enabled(void *context) {
    (void)context;
    return ST25DVxxKC_SetMBEN_Dyn(&nfc_tag);
}

static int32_t provider_reset_energy_harvesting(void *context) {
    (void)context;
    return ST25DVxxKC_ResetEHENMode_Dyn(&nfc_tag);
}

static int32_t provider_set_gpo1(void *context, uint8_t configuration) {
    (void)context;
    return ST25DVxxKC_SetGPO1_ALL(&nfc_tag.Ctx, &configuration);
}

static int32_t provider_read_gpo2(void *context, uint8_t *configuration) {
    (void)context;
    return ST25DVxxKC_GetGPO2_ALL(&nfc_tag.Ctx, configuration);
}

static int32_t provider_set_gpo2(void *context, uint8_t configuration) {
    (void)context;
    return ST25DVxxKC_SetGPO2_ALL(&nfc_tag.Ctx, &configuration);
}

static int32_t provider_read_mailbox_length(void *context,
                                            uint8_t *encoded_length) {
    (void)context;
    return ST25DVxxKC_ReadMBLength_Dyn(&nfc_tag, encoded_length);
}

static int32_t provider_read_mailbox(void *context, uint16_t offset,
                                     uint8_t *bytes, size_t length) {
    (void)context;
    if (length > UINT16_MAX) {
        return NFCTAG_ERROR;
    }
    return ST25DVxxKC_ReadMailboxData(&nfc_tag, bytes, offset,
                                     (uint16_t)length);
}

static void provider_delay(void *context, uint32_t ticks) {
    (void)context;
    (void)osDelay(ticks);
}

static const r1_st25dvxxkc_provider_ops provider_ops = {
    provider_initialize,
    provider_deinitialize,
    provider_read_id,
    provider_read_session,
    provider_present_password,
    provider_read_mailbox_mode,
    provider_read_mailbox_status,
    provider_set_mailbox_enabled,
    provider_reset_energy_harvesting,
    provider_set_gpo1,
    provider_read_gpo2,
    provider_set_gpo2,
    provider_read_mailbox_length,
    provider_read_mailbox,
    provider_delay,
};

static void forward_frame(void *context, const uint8_t *bytes, size_t length) {
    (void)context;
    if (frame_handler != NULL) {
        frame_handler(frame_context, bytes, length);
    }
}

static void gpo_interrupt(nrfx_gpiote_pin_t pin,
                          nrf_gpiote_polarity_t action) {
    (void)pin;
    (void)action;
    if (nfc_thread != NULL) {
        (void)osThreadFlagsSet(nfc_thread, OPENR1_NFC_FLAG_GPO);
    }
}

static void gpo_close(void) {
    if (gpo_configured) {
        nrfx_gpiote_in_event_disable(OPENR1_NFC_GPO_PIN);
        nrfx_gpiote_in_uninit(OPENR1_NFC_GPO_PIN);
        gpo_configured = false;
    }
    nrf_gpio_cfg_default(OPENR1_NFC_GPO_PIN);
}

static bool gpo_open(void) {
    if (!nrfx_gpiote_is_init() && nrfx_gpiote_init() != NRFX_SUCCESS) {
        return false;
    }
    nrfx_gpiote_in_config_t configuration =
        NRFX_GPIOTE_CONFIG_IN_SENSE_LOTOHI(false);
    configuration.pull = NRF_GPIO_PIN_NOPULL;
    const nrfx_err_t error = nrfx_gpiote_in_init(
        OPENR1_NFC_GPO_PIN, &configuration, gpo_interrupt);
    if (error != NRFX_SUCCESS) {
        last_error = error;
        return false;
    }
    gpo_configured = true;
    nrfx_gpiote_in_event_enable(OPENR1_NFC_GPO_PIN, true);
    return true;
}

static void deactivate(void) {
    nfc_active = false;
    gpo_close();
    r1_st25dvxxkc_deactivate(&nfc_adapter);
    if (bus_lease_active) {
        resource_ops->release_i2c5(resource_context);
        bus_lease_active = false;
    }
    if (power_active) {
        resource_ops->release_power(resource_context);
        power_active = false;
    }
}

static void activate(void) {
    if (nfc_active || !resources_complete() ||
        !resource_ops->acquire_power(resource_context)) {
        last_error = NRF_ERROR_INVALID_STATE;
        return;
    }
    power_active = true;
    if (!resource_ops->acquire_i2c5(resource_context)) {
        last_error = NRF_ERROR_BUSY;
        resource_ops->release_power(resource_context);
        power_active = false;
        return;
    }
    bus_lease_active = true;
    const r1_error error = r1_st25dvxxkc_activate(&nfc_adapter);
    if (error != R1_OK || !gpo_open()) {
        last_error = error != R1_OK ? (uint32_t)error : NRF_ERROR_INTERNAL;
        deactivate();
        return;
    }
    nfc_active = true;
}

static void nfc_worker(void *argument) {
    (void)argument;
    for (;;) {
        const uint32_t flags = osThreadFlagsWait(
            OPENR1_NFC_FLAGS, osFlagsWaitAny, osWaitForever);
        if ((flags & osFlagsError) != 0u) {
            last_error = flags;
            continue;
        }
        if ((flags & OPENR1_NFC_FLAG_UPDATE) != 0u) {
            bool enable;
            taskENTER_CRITICAL();
            enable = requested_active;
            taskEXIT_CRITICAL();
            if (enable) {
                activate();
            } else {
                deactivate();
            }
        }
        if ((flags & OPENR1_NFC_FLAG_GPO) != 0u && nfc_active) {
            bool received = false;
            const r1_error error = r1_st25dvxxkc_poll(&nfc_adapter, &received);
            (void)received;
            if (error != R1_OK) {
                last_error = (uint32_t)error;
            }
        }
    }
}

ret_code_t openr1_nfc_initialize(void) {
    if (nfc_thread != NULL) {
        return NRF_ERROR_INVALID_STATE;
    }
    r1_st25dvxxkc_adapter_initialize(&nfc_adapter);
    r1_error error = r1_st25dvxxkc_adapter_bind(
        &nfc_adapter, &provider_ops, NULL);
    if (error != R1_OK) {
        return NRF_ERROR_INTERNAL;
    }
    r1_st25dvxxkc_set_frame_callback(&nfc_adapter, forward_frame, NULL);
    static const osThreadAttr_t attributes = {
        .name = "openr1_nfc",
        .cb_mem = &nfc_control_block,
        .cb_size = sizeof nfc_control_block,
        .stack_mem = nfc_stack,
        .stack_size = sizeof nfc_stack,
        .priority = osPriorityNormal,
    };
    nfc_thread = osThreadNew(nfc_worker, NULL, &attributes);
    return nfc_thread == NULL ? NRF_ERROR_NO_MEM : NRF_SUCCESS;
}

ret_code_t openr1_nfc_bind_resources(
    const openr1_nfc_resource_ops *operations, void *context) {
    if (operations == NULL || operations->acquire_power == NULL ||
        operations->release_power == NULL ||
        operations->acquire_i2c5 == NULL ||
        operations->release_i2c5 == NULL) {
        return NRF_ERROR_NULL;
    }
    if (nfc_active || power_active || bus_lease_active) {
        return NRF_ERROR_INVALID_STATE;
    }
    resource_ops = operations;
    resource_context = context;
    return NRF_SUCCESS;
}

ret_code_t openr1_nfc_set_frame_handler(openr1_nfc_frame_handler handler,
                                        void *context) {
    if (nfc_active) {
        return NRF_ERROR_INVALID_STATE;
    }
    frame_handler = handler;
    frame_context = context;
    return NRF_SUCCESS;
}

ret_code_t openr1_nfc_set_enabled(bool enabled) {
    if (nfc_thread == NULL) {
        return NRF_ERROR_INVALID_STATE;
    }
    if (enabled && !resources_complete()) {
        return NRF_ERROR_INVALID_STATE;
    }
    taskENTER_CRITICAL();
    requested_active = enabled;
    taskEXIT_CRITICAL();
    const uint32_t result = osThreadFlagsSet(nfc_thread, OPENR1_NFC_FLAG_UPDATE);
    return (result & osFlagsError) != 0u ? NRF_ERROR_INTERNAL : NRF_SUCCESS;
}

bool openr1_nfc_is_provisioned(void) {
    return resources_complete();
}

bool openr1_nfc_is_active(void) {
    return nfc_active;
}

uint8_t openr1_nfc_ic_reference(void) {
    return nfc_adapter.ic_reference;
}

uint32_t openr1_nfc_last_error(void) {
    return last_error;
}
