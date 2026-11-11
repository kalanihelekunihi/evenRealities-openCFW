#ifndef R1_NATIVE_TASK_CONTEXTS_H
#define R1_NATIVE_TASK_CONTEXTS_H
#include <stddef.h>
/* Shared declarations for the existing 16-byte task-context prefix owners. */
struct r1_event_context {void (*create)(void),(*stop)(void);void *thread,*queue;};
struct r1_tx_context {void (*create)(void),(*stop)(void);void *thread,*queue;};
_Static_assert(sizeof(struct r1_event_context)==16 &&
               offsetof(struct r1_event_context,thread)==8,"event task prefix");
_Static_assert(sizeof(struct r1_tx_context)==16 &&
               offsetof(struct r1_tx_context,thread)==8,"transmit task prefix");
extern struct r1_event_context r1_event_storage,r1_event_system,r1_event_sensor;
extern struct r1_tx_context r1_tx_channel1,r1_tx_shared;
struct r1_nfc_charge_lifecycle {void (*create)(void),(*stop)(void);};
struct r1_bae8_rx_lifecycle {void (*create)(void),(*stop)(void);};
struct r1_factory_lifecycle {void (*create)(void),(*stop)(void);};
struct r1_task_lifecycle {void (*create)(void),(*stop)(void);};
_Static_assert(sizeof(struct r1_task_lifecycle)==8,"lifecycle prefix");
extern struct r1_nfc_charge_lifecycle r1_nfc_charge_lifecycle;
extern struct r1_bae8_rx_lifecycle r1_bae8_rx_lifecycle;
extern struct r1_factory_lifecycle r1_factory_rx_lifecycle;
extern struct r1_task_lifecycle r1_ble_io_lifecycle,r1_touch_io_lifecycle;
#endif
