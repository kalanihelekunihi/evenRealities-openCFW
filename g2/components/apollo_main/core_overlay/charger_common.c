/* Clean-room reconstruction of platform/service/charger/charger_common.c. */

#include <stddef.h>
#include <stdint.h>

void *memcpy(void *destination, const void *source, size_t length);
void *memset(void *destination, int value, size_t length);

typedef struct {
    int32_t soc;
    uint8_t is_charging;
    uint8_t reserved[3];
} open_cfw_charger_battery_info;

typedef struct {
    uint8_t reserved0[8];
    int32_t peer_soc;
    uint8_t peer_is_charging;
    uint8_t reserved1[3];
    int32_t soc;
    uint8_t is_charging;
    uint8_t reserved2[3];
} open_cfw_charger_runtime;

typedef struct {
    uint8_t message_id;
    uint8_t payload_length;
    uint8_t source_role;
    uint8_t destination_role;
    open_cfw_charger_battery_info battery;
} open_cfw_charger_sync_message;

typedef struct {
    uint8_t reserved0[4];
    int32_t soc;
    uint8_t reserved1[4];
    int32_t current;
    uint8_t reserved2[5];
    uint8_t charge_state;
} open_cfw_charger_driver_state;

_Static_assert(sizeof(open_cfw_charger_battery_info) == 8,
    "stock battery information must remain eight bytes");
_Static_assert(offsetof(open_cfw_charger_runtime, peer_soc) == 8,
    "stock peer SOC offset changed");
_Static_assert(offsetof(open_cfw_charger_runtime, soc) == 0x10,
    "stock aggregate SOC offset changed");
_Static_assert(offsetof(open_cfw_charger_runtime, is_charging) == 0x14,
    "stock aggregate charging offset changed");
_Static_assert(sizeof(open_cfw_charger_runtime) == 0x18,
    "stock charger runtime must remain 24 bytes");
_Static_assert(sizeof(open_cfw_charger_sync_message) == 0x0c,
    "stock synchronization message must remain twelve bytes");
_Static_assert(offsetof(open_cfw_charger_driver_state, charge_state) == 0x15,
    "stock driver charge-state offset changed");

#ifndef OPEN_CFW_CHARGER_RUNTIME_ADDRESS
#define OPEN_CFW_CHARGER_RUNTIME_ADDRESS 0x20073b30u
#endif
#ifndef OPEN_CFW_CHARGER_LOCAL_INFO_ADDRESS
#define OPEN_CFW_CHARGER_LOCAL_INFO_ADDRESS 0x20074104u
#endif
#ifndef OPEN_CFW_CHARGER_DRIVER_STATE_ADDRESS
#define OPEN_CFW_CHARGER_DRIVER_STATE_ADDRESS 0x20073b18u
#endif
#ifndef OPEN_CFW_CHARGER_MUTEX_ADDRESS
#define OPEN_CFW_CHARGER_MUTEX_ADDRESS 0x20074370u
#endif

#define OPEN_CFW_CHARGER_RUNTIME \
    (*(open_cfw_charger_runtime *)(uintptr_t)OPEN_CFW_CHARGER_RUNTIME_ADDRESS)
#define OPEN_CFW_CHARGER_LOCAL_INFO \
    (*(open_cfw_charger_battery_info *)(uintptr_t)OPEN_CFW_CHARGER_LOCAL_INFO_ADDRESS)
#define OPEN_CFW_CHARGER_DRIVER_STATE \
    (*(volatile open_cfw_charger_driver_state *)(uintptr_t) \
        OPEN_CFW_CHARGER_DRIVER_STATE_ADDRESS)
#define OPEN_CFW_CHARGER_MUTEX \
    (*(void **)(uintptr_t)OPEN_CFW_CHARGER_MUTEX_ADDRESS)

#ifndef OPEN_CFW_CHARGER_CREATE_MUTEX
void *open_cfw_charger_create_mutex(void);
#define OPEN_CFW_CHARGER_CREATE_MUTEX() open_cfw_charger_create_mutex()
#endif
#ifndef OPEN_CFW_CHARGER_DELETE_MUTEX
void open_cfw_charger_delete_mutex(void *mutex);
#define OPEN_CFW_CHARGER_DELETE_MUTEX(mutex) open_cfw_charger_delete_mutex(mutex)
#endif
#ifndef OPEN_CFW_CHARGER_LOCK_MUTEX
int open_cfw_charger_lock_mutex(void *mutex, uint32_t timeout);
#define OPEN_CFW_CHARGER_LOCK_MUTEX(mutex, timeout) \
    open_cfw_charger_lock_mutex((mutex), (timeout))
#endif
#ifndef OPEN_CFW_CHARGER_UNLOCK_MUTEX
void open_cfw_charger_unlock_mutex(void *mutex);
#define OPEN_CFW_CHARGER_UNLOCK_MUTEX(mutex) open_cfw_charger_unlock_mutex(mutex)
#endif
#ifndef OPEN_CFW_CHARGER_START_SYNC_TIMER
void open_cfw_charger_start_sync_timer(void);
#define OPEN_CFW_CHARGER_START_SYNC_TIMER() open_cfw_charger_start_sync_timer()
#endif
#ifndef OPEN_CFW_CHARGER_STOP_SYNC_TIMER
void open_cfw_charger_stop_sync_timer(void);
#define OPEN_CFW_CHARGER_STOP_SYNC_TIMER() open_cfw_charger_stop_sync_timer()
#endif
#ifndef OPEN_CFW_CHARGER_ROLE
uint8_t open_cfw_charger_role(void);
#define OPEN_CFW_CHARGER_ROLE() open_cfw_charger_role()
#endif
#ifndef OPEN_CFW_CHARGER_SEND_MESSAGE
void open_cfw_charger_send_message(
    uint16_t service, const void *message, uint16_t length, uint8_t flags
);
#define OPEN_CFW_CHARGER_SEND_MESSAGE(service, message, length, flags) \
    open_cfw_charger_send_message((service), (message), (length), (flags))
#endif
#ifndef OPEN_CFW_CHARGER_PUBLISH
void open_cfw_charger_publish(uint8_t field, int32_t value);
#define OPEN_CFW_CHARGER_PUBLISH(field, value) \
    open_cfw_charger_publish((field), (value))
#endif
#ifndef OPEN_CFW_CHARGER_DIAGNOSTIC
#define OPEN_CFW_CHARGER_DIAGNOSTIC(code) ((void)(code))
#endif

static uint8_t open_cfw_charger_initial_sync_active;
static uint16_t open_cfw_charger_initial_sync_poll;
static uint16_t open_cfw_charger_initial_sync_next = 2u;
static uint8_t open_cfw_charger_initial_sync_retries;
static uint8_t open_cfw_charger_charge_debounce;

static uint8_t open_cfw_charger_soc_is_valid(uint32_t soc)
{
    return soc < 101u;
}

static uint8_t open_cfw_charger_aggregate_soc_is_valid(void)
{
    return open_cfw_charger_soc_is_valid((uint32_t)OPEN_CFW_CHARGER_RUNTIME.soc);
}

static uint8_t open_cfw_charger_handle_initial_sync(void)
{
    if (open_cfw_charger_initial_sync_active == 0u) {
        return 0u;
    }
    if (open_cfw_charger_aggregate_soc_is_valid() != 0u) {
        open_cfw_charger_initial_sync_active = 0u;
        OPEN_CFW_CHARGER_DIAGNOSTIC(1u);
        return 0u;
    }
    if (open_cfw_charger_initial_sync_poll != UINT16_MAX) {
        ++open_cfw_charger_initial_sync_poll;
    }
    if (open_cfw_charger_initial_sync_poll >= 16u) {
        open_cfw_charger_initial_sync_active = 0u;
        OPEN_CFW_CHARGER_DIAGNOSTIC(2u);
        return 0u;
    }
    if (open_cfw_charger_initial_sync_retries < 4u &&
        open_cfw_charger_initial_sync_poll >= open_cfw_charger_initial_sync_next) {
        ++open_cfw_charger_initial_sync_retries;
        open_cfw_charger_initial_sync_next =
            (uint16_t)(open_cfw_charger_initial_sync_poll + 2u);
        OPEN_CFW_CHARGER_DIAGNOSTIC(3u);
        return 1u;
    }
    return 0u;
}

int open_cfw_charger_get_local_battery_info(open_cfw_charger_battery_info *info)
{
    const volatile open_cfw_charger_driver_state *driver =
        &OPEN_CFW_CHARGER_DRIVER_STATE;
    int32_t soc;
    if (info == NULL) {
        return -1;
    }
    soc = driver->soc;
    if (soc == 93 && driver->charge_state == 1u) {
        soc = 94;
    } else if (soc == 94) {
        soc = driver->charge_state == 1u ? 96 : 95;
    } else if (soc == 95) {
        soc = driver->charge_state == 1u ? 98 : 97;
    } else if (soc == 96) {
        soc = 99;
    } else if (soc > 96) {
        soc = 100;
    }
    info->soc = soc;
    info->is_charging = driver->current < 0;
    return 0;
}

void open_cfw_charger_init_battery_sync(void)
{
    OPEN_CFW_CHARGER_DIAGNOSTIC(4u);
    OPEN_CFW_CHARGER_MUTEX = OPEN_CFW_CHARGER_CREATE_MUTEX();
    if (OPEN_CFW_CHARGER_MUTEX == NULL) {
        OPEN_CFW_CHARGER_DIAGNOSTIC(5u);
        return;
    }
    memset(&OPEN_CFW_CHARGER_RUNTIME, 0, sizeof(OPEN_CFW_CHARGER_RUNTIME));
    memset(&OPEN_CFW_CHARGER_LOCAL_INFO, 0, sizeof(OPEN_CFW_CHARGER_LOCAL_INFO));
    OPEN_CFW_CHARGER_LOCAL_INFO.soc = -1;
    OPEN_CFW_CHARGER_RUNTIME.soc = -1;
    open_cfw_charger_charge_debounce = 0u;
    open_cfw_charger_initial_sync_active = 1u;
    open_cfw_charger_initial_sync_poll = 0u;
    open_cfw_charger_initial_sync_next = 2u;
    open_cfw_charger_initial_sync_retries = 0u;
    OPEN_CFW_CHARGER_START_SYNC_TIMER();
}

void open_cfw_charger_deinit_battery_sync(void)
{
    OPEN_CFW_CHARGER_DIAGNOSTIC(6u);
    if (OPEN_CFW_CHARGER_MUTEX != NULL) {
        OPEN_CFW_CHARGER_DELETE_MUTEX(OPEN_CFW_CHARGER_MUTEX);
        OPEN_CFW_CHARGER_MUTEX = NULL;
    }
    OPEN_CFW_CHARGER_STOP_SYNC_TIMER();
}

void open_cfw_charger_compare_and_update_soc(void)
{
    open_cfw_charger_battery_info current;
    int32_t aggregate;
    if (open_cfw_charger_get_local_battery_info(&current) != 0) {
        OPEN_CFW_CHARGER_DIAGNOSTIC(7u);
        return;
    }
    if (OPEN_CFW_CHARGER_MUTEX == NULL) {
        OPEN_CFW_CHARGER_DIAGNOSTIC(8u);
        return;
    }
    if (OPEN_CFW_CHARGER_LOCK_MUTEX(OPEN_CFW_CHARGER_MUTEX, UINT32_MAX) != 0) {
        OPEN_CFW_CHARGER_DIAGNOSTIC(9u);
        return;
    }
    aggregate = OPEN_CFW_CHARGER_LOCAL_INFO.soc < OPEN_CFW_CHARGER_RUNTIME.peer_soc
        ? OPEN_CFW_CHARGER_LOCAL_INFO.soc : OPEN_CFW_CHARGER_RUNTIME.peer_soc;
    OPEN_CFW_CHARGER_RUNTIME.soc = aggregate;
    OPEN_CFW_CHARGER_UNLOCK_MUTEX(OPEN_CFW_CHARGER_MUTEX);
    if (open_cfw_charger_initial_sync_active != 0u &&
        open_cfw_charger_aggregate_soc_is_valid() != 0u) {
        open_cfw_charger_initial_sync_active = 0u;
        OPEN_CFW_CHARGER_DIAGNOSTIC(10u);
    }
    OPEN_CFW_CHARGER_PUBLISH(0u, aggregate);
}

void open_cfw_charger_compare_and_update_is_charging(void)
{
    open_cfw_charger_battery_info current;
    uint8_t aggregate = 0u;
    uint8_t changed;
    if (open_cfw_charger_get_local_battery_info(&current) != 0) {
        OPEN_CFW_CHARGER_DIAGNOSTIC(7u);
        return;
    }
    if (OPEN_CFW_CHARGER_MUTEX == NULL) {
        OPEN_CFW_CHARGER_DIAGNOSTIC(8u);
        return;
    }
    if (OPEN_CFW_CHARGER_LOCK_MUTEX(OPEN_CFW_CHARGER_MUTEX, UINT32_MAX) != 0) {
        OPEN_CFW_CHARGER_DIAGNOSTIC(9u);
        return;
    }
    if (OPEN_CFW_CHARGER_RUNTIME.peer_is_charging == 1u) {
        aggregate = OPEN_CFW_CHARGER_LOCAL_INFO.is_charging == 1u ||
            OPEN_CFW_CHARGER_LOCAL_INFO.soc == 100;
    } else if (OPEN_CFW_CHARGER_LOCAL_INFO.is_charging == 1u &&
        OPEN_CFW_CHARGER_RUNTIME.peer_soc == 100) {
        aggregate = 1u;
    }
    changed = aggregate != OPEN_CFW_CHARGER_RUNTIME.is_charging;
    OPEN_CFW_CHARGER_RUNTIME.is_charging = aggregate;
    OPEN_CFW_CHARGER_UNLOCK_MUTEX(OPEN_CFW_CHARGER_MUTEX);
    if (changed != 0u) {
        OPEN_CFW_CHARGER_PUBLISH(1u, aggregate);
    }
}

void open_cfw_charger_send_battery_info(uint8_t message_id)
{
    open_cfw_charger_sync_message message;
    open_cfw_charger_battery_info current;
    uint8_t role;
    memset(&message, 0, sizeof(message));
    memset(&current, 0, sizeof(current));
    if (open_cfw_charger_get_local_battery_info(&current) != 0) {
        OPEN_CFW_CHARGER_DIAGNOSTIC(7u);
        return;
    }
    role = OPEN_CFW_CHARGER_ROLE();
    message.message_id = message_id;
    message.payload_length = 8u;
    message.source_role = role;
    message.destination_role = role == 1u ? 2u : 1u;
    memcpy(&message.battery, &OPEN_CFW_CHARGER_LOCAL_INFO,
        sizeof(message.battery));
    OPEN_CFW_CHARGER_SEND_MESSAGE(0x0105u, &message, sizeof(message), 0u);
}

void open_cfw_charger_request_notify_battery_info_from_peer(void)
{
    open_cfw_charger_sync_message message;
    uint8_t role;
    memset(&message, 0, sizeof(message));
    role = OPEN_CFW_CHARGER_ROLE();
    message.message_id = 4u;
    message.source_role = role;
    message.destination_role = role == 1u ? 2u : 1u;
    OPEN_CFW_CHARGER_SEND_MESSAGE(0x0105u, &message, sizeof(message), 0u);
}

void open_cfw_charger_on_battery_level_changed(void)
{
    open_cfw_charger_battery_info current;
    int32_t old_soc;
    uint8_t charge_changed = 0u;
    uint8_t role = OPEN_CFW_CHARGER_ROLE();
    memset(&current, 0, sizeof(current));
    (void)open_cfw_charger_get_local_battery_info(&current);
    old_soc = OPEN_CFW_CHARGER_LOCAL_INFO.soc;
    if (old_soc != current.soc) {
        OPEN_CFW_CHARGER_LOCAL_INFO.soc = current.soc;
    }
    if (OPEN_CFW_CHARGER_LOCAL_INFO.is_charging == current.is_charging) {
        open_cfw_charger_charge_debounce = 0u;
    } else {
        ++open_cfw_charger_charge_debounce;
        if (OPEN_CFW_CHARGER_DRIVER_STATE.soc < 98 ||
            open_cfw_charger_charge_debounce > 3u) {
            open_cfw_charger_charge_debounce = 0u;
            OPEN_CFW_CHARGER_LOCAL_INFO.is_charging = current.is_charging;
            charge_changed = 1u;
        }
    }
    if (old_soc == current.soc && charge_changed == 0u &&
        open_cfw_charger_handle_initial_sync() != 1u) {
        return;
    }
    OPEN_CFW_CHARGER_DIAGNOSTIC(11u);
    if (role == 1u) {
        open_cfw_charger_send_battery_info(3u);
    } else {
        open_cfw_charger_request_notify_battery_info_from_peer();
    }
}

void open_cfw_charger_receive_battery_info_from_peer(
    const open_cfw_charger_sync_message *message
)
{
    if (message == NULL) {
        OPEN_CFW_CHARGER_DIAGNOSTIC(12u);
        return;
    }
    OPEN_CFW_CHARGER_DIAGNOSTIC(13u);
    (void)OPEN_CFW_CHARGER_ROLE();
    if (OPEN_CFW_CHARGER_MUTEX == NULL) {
        OPEN_CFW_CHARGER_DIAGNOSTIC(8u);
        return;
    }
    if (OPEN_CFW_CHARGER_LOCK_MUTEX(OPEN_CFW_CHARGER_MUTEX, UINT32_MAX) != 0) {
        OPEN_CFW_CHARGER_DIAGNOSTIC(9u);
        return;
    }
    OPEN_CFW_CHARGER_RUNTIME.peer_soc = message->battery.soc;
    OPEN_CFW_CHARGER_RUNTIME.peer_is_charging = message->battery.is_charging;
    OPEN_CFW_CHARGER_UNLOCK_MUTEX(OPEN_CFW_CHARGER_MUTEX);
    if (message->message_id == 3u) {
        open_cfw_charger_send_battery_info(2u);
        open_cfw_charger_compare_and_update_soc();
        open_cfw_charger_compare_and_update_is_charging();
    } else if (message->message_id == 2u) {
        open_cfw_charger_compare_and_update_soc();
        open_cfw_charger_compare_and_update_is_charging();
    }
}

int32_t open_cfw_charger_get_soc(void)
{
    return OPEN_CFW_CHARGER_RUNTIME.soc;
}

uint8_t open_cfw_charger_get_is_charging(void)
{
    return OPEN_CFW_CHARGER_RUNTIME.is_charging;
}
