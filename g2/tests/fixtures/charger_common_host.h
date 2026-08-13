#ifndef OPEN_CFW_CHARGER_COMMON_HOST_H
#define OPEN_CFW_CHARGER_COMMON_HOST_H

#include <stdint.h>

typedef struct {
    uint8_t reserved0[8];
    int32_t peer_soc;
    uint8_t peer_is_charging;
    uint8_t reserved1[3];
    int32_t soc;
    uint8_t is_charging;
    uint8_t reserved2[3];
} open_cfw_test_charger_runtime_type;

typedef struct {
    int32_t soc;
    uint8_t is_charging;
    uint8_t reserved[3];
} open_cfw_test_charger_info_type;

typedef struct {
    uint8_t reserved0[4];
    int32_t soc;
    uint8_t reserved1[4];
    int32_t current;
    uint8_t reserved2[5];
    uint8_t charge_state;
} open_cfw_test_charger_driver_type;

extern open_cfw_test_charger_runtime_type open_cfw_test_charger_runtime;
extern open_cfw_test_charger_info_type open_cfw_test_charger_local_info;
extern open_cfw_test_charger_driver_type open_cfw_test_charger_driver;
extern void *open_cfw_test_charger_mutex;

void *open_cfw_test_charger_create_mutex(void);
void open_cfw_test_charger_delete_mutex(void *);
int open_cfw_test_charger_lock_mutex(void *, uint32_t);
void open_cfw_test_charger_unlock_mutex(void *);
void open_cfw_test_charger_start_sync_timer(void);
void open_cfw_test_charger_stop_sync_timer(void);
uint8_t open_cfw_test_charger_role(void);
void open_cfw_test_charger_send_message(uint16_t, const void *, uint16_t, uint8_t);
void open_cfw_test_charger_publish(uint8_t, int32_t);
void open_cfw_test_charger_diagnostic(uint32_t);

#define OPEN_CFW_CHARGER_RUNTIME_ADDRESS \
    ((uintptr_t)&open_cfw_test_charger_runtime)
#define OPEN_CFW_CHARGER_LOCAL_INFO_ADDRESS \
    ((uintptr_t)&open_cfw_test_charger_local_info)
#define OPEN_CFW_CHARGER_DRIVER_STATE_ADDRESS \
    ((uintptr_t)&open_cfw_test_charger_driver)
#define OPEN_CFW_CHARGER_MUTEX_ADDRESS \
    ((uintptr_t)&open_cfw_test_charger_mutex)
#define OPEN_CFW_CHARGER_CREATE_MUTEX() open_cfw_test_charger_create_mutex()
#define OPEN_CFW_CHARGER_DELETE_MUTEX(mutex) open_cfw_test_charger_delete_mutex(mutex)
#define OPEN_CFW_CHARGER_LOCK_MUTEX(mutex, timeout) \
    open_cfw_test_charger_lock_mutex((mutex), (timeout))
#define OPEN_CFW_CHARGER_UNLOCK_MUTEX(mutex) open_cfw_test_charger_unlock_mutex(mutex)
#define OPEN_CFW_CHARGER_START_SYNC_TIMER() open_cfw_test_charger_start_sync_timer()
#define OPEN_CFW_CHARGER_STOP_SYNC_TIMER() open_cfw_test_charger_stop_sync_timer()
#define OPEN_CFW_CHARGER_ROLE() open_cfw_test_charger_role()
#define OPEN_CFW_CHARGER_SEND_MESSAGE(service, message, length, flags) \
    open_cfw_test_charger_send_message((service), (message), (length), (flags))
#define OPEN_CFW_CHARGER_PUBLISH(field, value) \
    open_cfw_test_charger_publish((field), (value))
#define OPEN_CFW_CHARGER_DIAGNOSTIC(code) open_cfw_test_charger_diagnostic(code)

extern uint8_t open_cfw_test_charger_role_value;
extern int open_cfw_test_charger_lock_result;
extern uint32_t open_cfw_test_charger_create_count;
extern uint32_t open_cfw_test_charger_delete_count;
extern uint32_t open_cfw_test_charger_lock_count;
extern uint32_t open_cfw_test_charger_unlock_count;
extern uint32_t open_cfw_test_charger_start_count;
extern uint32_t open_cfw_test_charger_stop_count;
extern uint32_t open_cfw_test_charger_send_count;
extern uint32_t open_cfw_test_charger_publish_count;
extern uint32_t open_cfw_test_charger_diagnostic_count;
extern uint16_t open_cfw_test_charger_last_service;
extern uint16_t open_cfw_test_charger_last_length;
extern uint8_t open_cfw_test_charger_last_message[12];
extern uint8_t open_cfw_test_charger_last_field;
extern int32_t open_cfw_test_charger_last_value;
extern uint32_t open_cfw_test_charger_last_diagnostic;

void open_cfw_test_charger_reset(void);

#endif
