#include "openr1_nfc_zephyr.h"

#include <errno.h>
#include <limits.h>
#include <string.h>

#include <zephyr/device.h>
#include <zephyr/devicetree.h>
#include <zephyr/drivers/gpio.h>
#include <zephyr/kernel.h>
#include <zephyr/sys/atomic.h>

#include "openr1/r1_st25dvxxkc.h"
#include "openr1_twim1_zephyr.h"
#include "st25dvxxkc.h"
#include "st25dvxxkc_reg.h"

#define OPENR1_NFC_NODE DT_NODELABEL(openr1_nfc)
#define OPENR1_NFC_FLAG_UPDATE BIT(0)
#define OPENR1_NFC_FLAG_GPO BIT(1)
#define OPENR1_NFC_FLAGS (OPENR1_NFC_FLAG_UPDATE | OPENR1_NFC_FLAG_GPO)
#define OPENR1_NFC_REGISTER_BYTES 2u
#define OPENR1_NFC_MAX_WRITE_BYTES 256u
#define OPENR1_NFC_MAILBOX_BYTES R1_ST25DVXXKC_MAILBOX_CAPACITY

typedef struct {
    int (*initialize)(void);
    int (*bind_resources)(const openr1_nfc_zephyr_resource_ops *, void *);
    int (*set_frame_handler)(openr1_nfc_zephyr_frame_handler, void *);
    int (*set_enabled)(bool);
    bool (*is_provisioned)(void);
    bool (*is_active)(void);
    uint8_t (*ic_reference)(void);
    uint32_t (*last_error)(void);
} openr1_nfc_zephyr_api;

static const struct gpio_dt_spec nfc_gpo =
    GPIO_DT_SPEC_GET(OPENR1_NFC_NODE, nfc_gpo_gpios);

K_MUTEX_DEFINE(nfc_state_mutex);
K_EVENT_DEFINE(nfc_events);

static struct gpio_callback nfc_gpo_callback;
static ST25DVxxKC_Object_t nfc_tag;
static r1_st25dvxxkc_adapter nfc_adapter;
static const openr1_nfc_zephyr_resource_ops *resource_ops;
static void *resource_context;
static openr1_nfc_zephyr_frame_handler frame_handler;
static void *frame_context;
static atomic_t requested_active;
static atomic_t nfc_active;
static atomic_t last_error;
static bool bus_active;
static bool callback_registered;
static bool gpo_configured;
static bool power_active;
static bool dock_lease_active;
static bool module_initialized;

static bool resources_complete(void) {
    return resource_ops != NULL && resource_ops->acquire_power != NULL &&
           resource_ops->release_power != NULL &&
           resource_ops->acquire_dock_bus != NULL &&
           resource_ops->release_dock_bus != NULL;
}

static bool valid_wire_address(uint16_t device_address) {
    const uint16_t data_address = (uint16_t)ST25DVXXKC_ADDR_DATA_I2C;
    const uint16_t system_address =
        (uint16_t)(ST25DVXXKC_ADDR_DATA_I2C |
                   ST25DVXXKC_ADDR_SYSTEMMEMORY_BIT_I2C |
                   ST25DVXXKC_ADDR_MODE_BIT_I2C);
    return device_address == data_address || device_address == system_address;
}

static int32_t bus_initialize(void) {
    if (bus_active) {
        return 0;
    }
    const int error = openr1_twim1_zephyr_acquire(
        OPENR1_TWIM1_ZEPHYR_OWNER_NFC);
    if (error != 0) {
        atomic_set(&last_error, error);
        return -1;
    }
    bus_active = true;
    return 0;
}

static int32_t bus_deinitialize(void) {
    if (!bus_active) {
        return 0;
    }
    const int error = openr1_twim1_zephyr_release(
        OPENR1_TWIM1_ZEPHYR_OWNER_NFC);
    if (error != 0) {
        atomic_set(&last_error, error);
        return -1;
    }
    bus_active = false;
    return 0;
}

static int32_t bus_read(uint16_t device_address, uint16_t register_address,
                        uint8_t *bytes, uint16_t length) {
    if (!bus_active || !dock_lease_active ||
        !valid_wire_address(device_address) || bytes == NULL || length == 0u) {
        return -1;
    }
    const uint8_t register_bytes[OPENR1_NFC_REGISTER_BYTES] = {
        (uint8_t)(register_address >> 8u), (uint8_t)register_address,
    };
    const int error = openr1_twim1_zephyr_write_read(
        OPENR1_TWIM1_ZEPHYR_OWNER_NFC, (uint16_t)(device_address >> 1u),
        register_bytes, sizeof register_bytes, bytes, length);
    if (error != 0) {
        atomic_set(&last_error, error);
        return -1;
    }
    return 0;
}

static int32_t bus_write(uint16_t device_address, uint16_t register_address,
                         const uint8_t *bytes, uint16_t length) {
    if (!bus_active || !dock_lease_active ||
        !valid_wire_address(device_address) ||
        length > OPENR1_NFC_MAX_WRITE_BYTES ||
        (length != 0u && bytes == NULL)) {
        return -1;
    }
    uint8_t frame[OPENR1_NFC_REGISTER_BYTES + OPENR1_NFC_MAX_WRITE_BYTES];
    frame[0] = (uint8_t)(register_address >> 8u);
    frame[1] = (uint8_t)register_address;
    if (length != 0u) {
        memcpy(frame + OPENR1_NFC_REGISTER_BYTES, bytes, length);
    }
    const int error = openr1_twim1_zephyr_write(
        OPENR1_TWIM1_ZEPHYR_OWNER_NFC, (uint16_t)(device_address >> 1u),
        frame, (size_t)length + OPENR1_NFC_REGISTER_BYTES);
    if (error != 0) {
        atomic_set(&last_error, error);
        return -1;
    }
    return 0;
}

static int32_t bus_is_ready(uint16_t device_address, uint32_t trials) {
    (void)trials;
    if (!bus_active || !dock_lease_active ||
        !valid_wire_address(device_address)) {
        return -1;
    }
    k_sleep(K_TICKS(10));
    return 0;
}

static int32_t bus_get_tick(void) {
    return (int32_t)k_uptime_ticks();
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

static int32_t provider_present_password(void *context, uint32_t msb,
                                         uint32_t lsb) {
    (void)context;
    const ST25DVxxKC_PASSWD_t password = {msb, lsb};
    return ST25DVxxKC_PresentI2CPassword(&nfc_tag, password);
}

static int32_t provider_read_mailbox_mode(void *context, bool *enabled) {
    (void)context;
    ST25DVxxKC_EN_STATUS_E mode = ST25DVXXKC_DISABLE;
    const int32_t status = ST25DVxxKC_ReadMBMode(&nfc_tag, &mode);
    if (status == NFCTAG_OK) {
        *enabled = mode == ST25DVXXKC_ENABLE;
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
    return ST25DVxxKC_ReadMailboxData(
        &nfc_tag, bytes, offset, (uint16_t)length);
}

static void provider_delay(void *context, uint32_t ticks) {
    (void)context;
    k_sleep(K_TICKS(ticks));
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

static void gpo_interrupt(const struct device *port,
                          struct gpio_callback *callback,
                          gpio_port_pins_t pins) {
    (void)port;
    (void)callback;
    (void)pins;
    (void)k_event_post(&nfc_events, OPENR1_NFC_FLAG_GPO);
}

static void gpo_close(void) {
    if (gpo_configured) {
        (void)gpio_pin_interrupt_configure_dt(&nfc_gpo, GPIO_INT_DISABLE);
        gpo_configured = false;
    }
    (void)gpio_pin_configure_dt(&nfc_gpo, GPIO_DISCONNECTED);
}

static bool gpo_open(void) {
    int error = gpio_pin_configure_dt(&nfc_gpo, GPIO_INPUT);
    if (error != 0) {
        atomic_set(&last_error, error);
        return false;
    }
    if (!callback_registered) {
        gpio_init_callback(&nfc_gpo_callback, gpo_interrupt,
                           BIT(nfc_gpo.pin));
        error = gpio_add_callback(nfc_gpo.port, &nfc_gpo_callback);
        if (error == 0) {
            callback_registered = true;
        }
    }
    if (error == 0) {
        error = gpio_pin_interrupt_configure_dt(
            &nfc_gpo, GPIO_INT_EDGE_TO_ACTIVE);
    }
    if (error != 0) {
        atomic_set(&last_error, error);
        return false;
    }
    gpo_configured = true;
    return true;
}

static void deactivate(void) {
    atomic_clear(&nfc_active);
    gpo_close();
    r1_st25dvxxkc_deactivate(&nfc_adapter);
    if (dock_lease_active) {
        resource_ops->release_dock_bus(resource_context);
        dock_lease_active = false;
    }
    if (power_active) {
        resource_ops->release_power(resource_context);
        power_active = false;
    }
}

static void activate(void) {
    if (atomic_get(&nfc_active) != 0 || !resources_complete() ||
        !resource_ops->acquire_power(resource_context)) {
        atomic_set(&last_error, -EACCES);
        return;
    }
    power_active = true;
    if (!resource_ops->acquire_dock_bus(resource_context)) {
        atomic_set(&last_error, -EBUSY);
        resource_ops->release_power(resource_context);
        power_active = false;
        return;
    }
    dock_lease_active = true;
    const r1_error error = r1_st25dvxxkc_activate(&nfc_adapter);
    if (error != R1_OK || !gpo_open()) {
        atomic_set(&last_error, error != R1_OK ? (atomic_val_t)error : -EIO);
        deactivate();
        return;
    }
    atomic_set(&nfc_active, 1);
}

static void nfc_worker(void *first, void *second, void *third) {
    (void)first;
    (void)second;
    (void)third;
    for (;;) {
        const uint32_t flags = k_event_wait(
            &nfc_events, OPENR1_NFC_FLAGS, true, K_FOREVER);
        if ((flags & OPENR1_NFC_FLAG_UPDATE) != 0u) {
            if (atomic_get(&requested_active) != 0) {
                activate();
            } else {
                deactivate();
            }
        }
        if ((flags & OPENR1_NFC_FLAG_GPO) != 0u &&
            atomic_get(&nfc_active) != 0) {
            bool received = false;
            const r1_error error = r1_st25dvxxkc_poll(
                &nfc_adapter, &received);
            (void)received;
            if (error != R1_OK) {
                atomic_set(&last_error, (atomic_val_t)error);
            }
        }
    }
}

K_THREAD_DEFINE(openr1_nfc_thread, 2048, nfc_worker,
                NULL, NULL, NULL, K_LOWEST_APPLICATION_THREAD_PRIO, 0, 0);

int openr1_nfc_zephyr_initialize(void) {
    if (module_initialized) {
        return -EALREADY;
    }
    if (!gpio_is_ready_dt(&nfc_gpo)) {
        return -ENODEV;
    }
    int error = openr1_twim1_zephyr_initialize();
    if (error != 0 && error != -EALREADY) {
        return error;
    }
    memset(&nfc_tag, 0, sizeof nfc_tag);
    atomic_clear(&requested_active);
    atomic_clear(&nfc_active);
    atomic_clear(&last_error);
    bus_active = false;
    callback_registered = false;
    gpo_configured = false;
    power_active = false;
    dock_lease_active = false;
    gpo_close();
    r1_st25dvxxkc_adapter_initialize(&nfc_adapter);
    const r1_error provider_error = r1_st25dvxxkc_adapter_bind(
        &nfc_adapter, &provider_ops, NULL);
    if (provider_error != R1_OK) {
        return -EIO;
    }
    r1_st25dvxxkc_set_frame_callback(&nfc_adapter, forward_frame, NULL);
    module_initialized = true;
    return 0;
}

int openr1_nfc_zephyr_bind_resources(
    const openr1_nfc_zephyr_resource_ops *operations, void *context) {
    if (!module_initialized) {
        return -EACCES;
    }
    if (operations == NULL || operations->acquire_power == NULL ||
        operations->release_power == NULL ||
        operations->acquire_dock_bus == NULL ||
        operations->release_dock_bus == NULL) {
        return -EINVAL;
    }
    if (k_mutex_lock(&nfc_state_mutex, K_FOREVER) != 0) {
        return -EDEADLK;
    }
    const bool busy = atomic_get(&nfc_active) != 0 || power_active ||
                      dock_lease_active || bus_active;
    if (!busy) {
        resource_ops = operations;
        resource_context = context;
    }
    (void)k_mutex_unlock(&nfc_state_mutex);
    return busy ? -EBUSY : 0;
}

int openr1_nfc_zephyr_set_frame_handler(
    openr1_nfc_zephyr_frame_handler handler, void *context) {
    if (!module_initialized) {
        return -EACCES;
    }
    if (atomic_get(&nfc_active) != 0) {
        return -EBUSY;
    }
    frame_handler = handler;
    frame_context = context;
    return 0;
}

int openr1_nfc_zephyr_set_enabled(bool enabled) {
    if (!module_initialized) {
        return -EACCES;
    }
    if (enabled && !resources_complete()) {
        return -EACCES;
    }
    atomic_set(&requested_active, enabled ? 1 : 0);
    (void)k_event_post(&nfc_events, OPENR1_NFC_FLAG_UPDATE);
    return 0;
}

bool openr1_nfc_zephyr_is_provisioned(void) {
    return module_initialized && resources_complete();
}

bool openr1_nfc_zephyr_is_active(void) {
    return atomic_get(&nfc_active) != 0;
}

uint8_t openr1_nfc_zephyr_ic_reference(void) {
    return nfc_adapter.ic_reference;
}

uint32_t openr1_nfc_zephyr_last_error(void) {
    return (uint32_t)atomic_get(&last_error);
}

__attribute__((used, section(".openr1_platform_api")))
static const openr1_nfc_zephyr_api nfc_zephyr_api = {
    openr1_nfc_zephyr_initialize,
    openr1_nfc_zephyr_bind_resources,
    openr1_nfc_zephyr_set_frame_handler,
    openr1_nfc_zephyr_set_enabled,
    openr1_nfc_zephyr_is_provisioned,
    openr1_nfc_zephyr_is_active,
    openr1_nfc_zephyr_ic_reference,
    openr1_nfc_zephyr_last_error,
};
