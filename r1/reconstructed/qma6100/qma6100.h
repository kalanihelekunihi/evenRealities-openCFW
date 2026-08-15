#ifndef OPENR1_RECONSTRUCTED_QMA6100_H
#define OPENR1_RECONSTRUCTED_QMA6100_H

/*
 * Provenance banner
 * -----------------
 * Family:         qst_qma6100_v1_0_lineage_unlicensed plus the directly
 *                 coupled r1_qst_qma6100_provider_adapter closure.
 * Stock image:    R1 application image, load base 0x00027000, sha256
 *                 0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a.
 * Evidence:       Ghidra decompiler output, raw Thumb bytes for four missed
 *                 wrappers, and SHA-pinned ownership/evidence scripts under
 *                 r1/tools/evidence/.
 * Status:         RECONSTRUCTED FROM DECOMPILATION EVIDENCE; NOT QST OR EVEN
 *                 REALITIES SOURCE. Owner-authorized under
 *                 docs/SOURCE-ADMISSION.md (2026-08-14).
 *
 * This module reduces the complete 17-entry QMA closure: the three formerly
 * gated provider bodies at 0x86E34/0x87188/0x871C4, four operation-table
 * wrappers at 0x6F404..0x6F49B, and ten transport/configuration adapters at
 * 0x86D40..0x87421. See the correlation document for the exact mapping.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define QMA6100_ADDRESS_1 UINT8_C(0x12)
#define QMA6100_ADDRESS_2 UINT8_C(0x13)
#define QMA6100_DEVICE_ID UINT8_C(0xFA)
#define QMA6100P_ID_MASK UINT8_C(0xF0)
#define QMA6100P_ID_VALUE UINT8_C(0x90)
#define QMA6100_FIFO_SAMPLE_BYTES 6u
#define QMA6100_FIFO_MAX_SAMPLES 64u
#define QMA6100_TRANSPORT_ATTEMPTS 5u
#define QMA6100_RESET_POLL_ATTEMPTS 102u
#define QMA6100_FIFO_ERROR UINT32_MAX

enum {
    QMA6100_STATUS_FAILURE = 0,
    QMA6100_STATUS_SUCCESS = 1
};

typedef bool (*qma6100_bus_read_fn)(void *context, uint8_t address,
                                    uint8_t reg, uint8_t *bytes,
                                    size_t length);
typedef bool (*qma6100_bus_write_fn)(void *context, uint8_t address,
                                     uint8_t reg, const uint8_t *bytes,
                                     size_t length);
typedef void (*qma6100_delay_cycles_fn)(void *context, uint32_t cycles);
typedef void (*qma6100_lock_fn)(void *context);
typedef void (*qma6100_event_fn)(void *context);

typedef struct {
    qma6100_bus_read_fn read;
    qma6100_bus_write_fn write;
    qma6100_delay_cycles_fn delay_cycles;
    void *transport_context;
    qma6100_lock_fn acquire;
    qma6100_lock_fn release;
    void *lock_context;
} qma6100_bindings;

typedef struct {
    qma6100_bindings bindings;
    uint8_t address;
    uint8_t chip_id;
    uint16_t scale_lsb_per_g;
    uint16_t axis_sign[3];
    uint16_t axis_map[3];
    qma6100_event_fn double_tap;
    void *double_tap_context;
    qma6100_event_fn any_motion;
    void *any_motion_context;
} qma6100_device;

void qma6100_initialize(qma6100_device *device,
                        const qma6100_bindings *bindings);
void qma6100_bind_events(qma6100_device *device,
                         qma6100_event_fn double_tap,
                         void *double_tap_context,
                         qma6100_event_fn any_motion,
                         void *any_motion_context);
bool qma6100_identity_accepted(uint8_t chip_id);

/* 0x8714C / 0x873F4: five-attempt R1 transport adapters. */
uint32_t qma6100_read_retry(qma6100_device *device, uint8_t reg,
                            uint8_t *bytes, size_t length);
uint32_t qma6100_write_retry(qma6100_device *device, uint8_t reg,
                             uint8_t value);
/* 0x86E48: calls the recovered 64,000-cycle delay callback once per unit. */
void qma6100_delay(qma6100_device *device, uint32_t units);

/* Three formerly opaque provider interiors. */
uint8_t qma6100_chip_id(qma6100_device *device);          /* 0x86E34 */
uint32_t qma6100_set_range(qma6100_device *device,
                           uint8_t range);                /* 0x87188 */
uint32_t qma6100_soft_reset(qma6100_device *device);      /* 0x871C4 */

/* Recovered product/provider integration closure. */
uint32_t qma6100_any_motion_configure(qma6100_device *device,
                                      uint8_t route, bool enabled);
uint32_t qma6100_identity_and_configure(qma6100_device *device,
                                        uint16_t rate_hz);
uint32_t qma6100_configure(qma6100_device *device, uint16_t rate_hz);
void qma6100_interrupt(qma6100_device *device);
uint32_t qma6100_read_fifo(qma6100_device *device, uint8_t *bytes,
                           size_t maximum_samples);
uint32_t qma6100_step_configure(qma6100_device *device, bool enabled);
uint32_t qma6100_tap_configure(qma6100_device *device, uint8_t mask,
                               uint8_t route, bool enabled);

/* Four operation-table wrapper roles, with the recovered lock bracketing and
 * arithmetic-right-shift normalization. */
uint32_t qma6100_probe_wrapper(qma6100_device *device, uint8_t *chip_id);
uint32_t qma6100_configure_wrapper(qma6100_device *device,
                                   uint16_t requested_rate_hz);
void qma6100_interrupt_wrapper(qma6100_device *device);
uint32_t qma6100_fifo_wrapper(qma6100_device *device, uint8_t *bytes,
                              size_t maximum_samples);

#endif
