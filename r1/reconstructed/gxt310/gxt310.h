#ifndef OPENR1_RECONSTRUCTED_GXT310_H
#define OPENR1_RECONSTRUCTED_GXT310_H

/*
 * Provenance banner
 * -----------------
 * Family:         gxcas_gxt310_candidate.
 * Stock image:    application image, load base 0x00027000, sha256
 *                 0e788d433ea50fd36edb8f21a9c18b6062211e4a36dbc5bd7695ea5827f3aa1a.
 * Evidence:       r1/research/decompilation/application/decompiler-output.c
 *                 and the byte-exact rebuilt application image.
 * Status:         RECONSTRUCTED FROM DECOMPILATION EVIDENCE; NOT GXCAS,
 *                 EVEN REALITIES, OR BRAVECHIP SOURCE. Reduction is
 *                 owner-authorized by docs/SOURCE-ADMISSION.md (2026-08-14).
 *
 * Reduced stock functions (application extents, end-exclusive):
 *
 *   0x00050F9C..<0x00051026  138  enable both recovered GXT310 channels
 *   0x0006F600..<0x0006F638   56  signed big-endian temperature conversion
 *   0x0006F648..<0x0006F6B2  106  shared continuous/shutdown mode writer
 *   0x0006F738..<0x0006F794   92  shared one-shot trigger writer
 *   0x0006F804                   8  channel 0x90 mode folded inventory body
 *   0x0006F818                  98  channel 0x90 one-shot folded inventory body
 *   0x0006F81E                   8  channel 0x94 mode folded inventory body
 *   0x0006F832                   6  channel 0x94 one-shot folded inventory body
 *
 * Ghidra's 8/6-byte veneer extents share compiler-folded bodies with the
 * larger 0x90 implementations. The public API exposes the observable typed
 * operations, not that linker folding.
 */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define GXT310_CHANNEL_0_ADDRESS UINT8_C(0x90)
#define GXT310_CHANNEL_2_ADDRESS UINT8_C(0x94)
#define GXT310_WRITE_OPERATION UINT16_C(1)
#define GXT310_COMMAND_BYTES 2u

enum {
    GXT310_STATUS_FAILURE = 0,
    GXT310_STATUS_SUCCESS = 1
};

typedef bool (*gxt310_write_fn)(void *context, uint8_t address,
                                uint16_t operation, const uint8_t *bytes,
                                size_t length);
typedef bool (*gxt310_read_fn)(void *context, uint8_t address,
                               uint16_t operation, uint8_t *bytes,
                               size_t length);

typedef enum {
    GXT310_FAILURE_SWITCH_MODE = 0,
    GXT310_FAILURE_TRIGGER_ONE_SHOT = 1
} gxt310_failure_operation;

typedef void (*gxt310_failure_fn)(void *context,
                                  gxt310_failure_operation operation,
                                  uint8_t address);

typedef struct {
    gxt310_write_fn write;
    void *write_context;
    gxt310_failure_fn failure;
    void *failure_context;
    gxt310_read_fn read;
    void *read_context;
} gxt310_provider;

void gxt310_provider_initialize(gxt310_provider *provider,
                                gxt310_write_fn write,
                                void *write_context,
                                gxt310_failure_fn failure,
                                void *failure_context);
void gxt310_provider_bind_read(gxt310_provider *provider,
                               gxt310_read_fn read,
                               void *read_context);

/* Shared typed forms of the two compiler-folded channel implementations. */
uint32_t gxt310_switch_mode(gxt310_provider *provider, uint8_t address,
                            bool enabled);
uint32_t gxt310_trigger_one_shot(gxt310_provider *provider, uint8_t address);
uint32_t gxt310_read_temperature_milliunits(gxt310_provider *provider,
                                            uint8_t address,
                                            int32_t *milliunits);

/* Exact stock entry-point roles. */
uint32_t gxt310_channel_0_switch_mode(gxt310_provider *provider, bool enabled);
uint32_t gxt310_channel_0_trigger_one_shot(gxt310_provider *provider);
uint32_t gxt310_channel_2_switch_mode(gxt310_provider *provider, bool enabled);
uint32_t gxt310_channel_2_trigger_one_shot(gxt310_provider *provider);
uint32_t gxt310_enable_pair(gxt310_provider *provider);

#endif
