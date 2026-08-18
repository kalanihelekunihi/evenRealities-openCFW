#ifndef OPENR1_NRF52840_SDK_DATABASES_H
#define OPENR1_NRF52840_SDK_DATABASES_H

#include <stdbool.h>
#include <stdint.h>

#include "nrf.h"
#include "app_error.h"

#include "openr1/r1_health_db.h"
#include "openr1/r1_event_bus.h"
#include "openr1/r1_kv_store.h"
#include "openr1/r1_nv_recovery.h"
#include "openr1/r1_sleep_db.h"

/*
 * Production storage wiring: binds the three recovered R1 databases to the
 * FAL partition table over the nRF52840 internal-flash port.
 *
 * openr1_databases_initialize() runs on the SoftDevice event thread during
 * startup.  It binds the kv.bin four-snapshot class store synchronously (the
 * portable initializer only reads flash), loads the persisted REG1 flag (kv
 * dev_info byte 24 bit 1), resets the platform private event bus and binds its
 * per-window queue sink and consumer thread (openr1_event_bus.c), and starts
 * the storage worker that runs the health TSDB startup controller and the
 * sleep.db FAL partition bind in the recovered order (stock startup task
 * 0x000926DC: 0x00070030 health startup before the 0x0008DD8C -> 0x0005B0F8
 * sleep bind).  After those binds the worker stays resident to apply deferred
 * REG1 persist requests, because openr1_storage.c rejects flash mutations
 * from the SoftDevice event thread; FlashDB may format an empty health.db
 * partition during fdb_tsdb_init.
 *
 * Fail-explicit policy: any failure is recorded in the startup result and the
 * last-error word, the affected database stays unbound (its accessor returns
 * NULL), and no recovery path ever erases or rewrites existing state.  See
 * docs/correlation/STORAGE-PRODUCTION-WIRING-CORRELATION.md.
 */

ret_code_t openr1_databases_initialize(void);

/* True once the kv.bin store has been opened (defaults or a strict snapshot). */
bool openr1_databases_kv_ready(void);
/* True once the health TSDB startup controller completed every stage. */
bool openr1_databases_health_ready(void);
/* True once the sleep.db journal is bound to its FAL partition. */
bool openr1_databases_sleep_ready(void);

/* Sticky first-failure word; zero when no failure has been recorded. */
uint32_t openr1_databases_last_error(void);
/* Retained health-startup outcome, valid after the worker has run. */
const r1_health_db_startup_result *openr1_databases_health_startup(void);

/* Database handles; NULL while the corresponding database is not ready. */
r1_kv_store *openr1_databases_kv_store(void);
r1_sleep_db *openr1_databases_sleep_db(void);
/* The platform private event bus.  Always valid storage; publishes return
 * R1_ERROR_UNSUPPORTED until the per-window queue sink was bound during
 * openr1_databases_initialize (openr1_event_bus.c). */
r1_event_bus *openr1_databases_event_bus(void);
/* The provider-owned FlashDB TSDB object (r1_health_db_provider_handle seam);
 * NULL until the health startup controller completed. */
void *openr1_databases_health_handle(void);

/* The persisted normalized REG1 enable flag (kv dev_info byte 24 bit 1),
 * loaded when kv.bin opens; false until then. */
bool openr1_databases_reg1_enabled(void);
/* Defers a REG1 flag persist to the storage worker (kv dev_info byte 24 bit
 * 1).  Safe to call from the SoftDevice event thread: the request is
 * recorded and the worker performs the kv set/commit because openr1_storage
 * rejects flash mutations on that thread.  The regulator SVC
 * (sd_power_dcdc_mode_set) stays deliberately scoped out. */
ret_code_t openr1_databases_persist_reg1(bool enabled);
/* Copies a CRC-validated fill-only recovery request into the bounded storage
 * queue. The worker commits all affected KV classes atomically and resets
 * only after a changed generation is durable. */
ret_code_t openr1_databases_queue_nv_recovery(
    const uint8_t body[R1_NV_RECOVERY_BODY_BYTES], uint16_t expected_crc);
ret_code_t openr1_databases_queue_remove_ring(void);

#endif
