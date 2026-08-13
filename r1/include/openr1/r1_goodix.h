#ifndef OPENR1_R1_GOODIX_H
#define OPENR1_R1_GOODIX_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#include "openr1/r1_protocol.h"

/*
 * Clean-room product adapter for the proprietary Goodix GH3X2X boundary.
 *
 * The numeric masks are recovered R1 interface values.  Their vendor-private
 * algorithm meaning is intentionally not guessed here.  A licensed provider
 * must implement the operations below; openR1 never synthesizes biometric
 * results when that provider is absent.
 */
#define R1_GOODIX_MASK_STOCK_2000 UINT32_C(0x00002000)
#define R1_GOODIX_MASK_STOCK_4000 UINT32_C(0x00004000)
#define R1_GOODIX_MASK_SWITCH_CLEAR UINT32_C(0x00000042)
#define R1_GOODIX_MASK_SWITCH_2 UINT32_C(0x00000002)
#define R1_GOODIX_MASK_SWITCH_40 UINT32_C(0x00000040)
#define R1_GOODIX_DIAGNOSTIC_SNAPSHOT_BYTES 240u
#define R1_GOODIX_DIAGNOSTIC_REFRESH_TICKS UINT32_C(500)
#define R1_GOODIX_DIAGNOSTIC_OUTPUT_MAX 124u

typedef enum {
    R1_GOODIX_STOCK_PROFILE_2000 = 0,
    R1_GOODIX_STOCK_PROFILE_4000 = 1
} r1_goodix_stock_profile;

typedef enum {
    R1_GOODIX_SWITCH_PROFILE_2 = 0,
    R1_GOODIX_SWITCH_PROFILE_40 = 1
} r1_goodix_switch_selection;

typedef struct {
    int32_t (*initialize)(void *context);
    int32_t (*switch_configuration)(void *context, uint8_t configuration);
    int32_t (*start_sampling)(void *context, uint32_t mask);
    int32_t (*stop_sampling)(void *context, uint32_t mask);
} r1_goodix_provider_ops;

typedef struct {
    bool (*prepare)(void *context);
    void (*shutdown)(void *context);
    void (*delay_ms)(void *context, uint32_t milliseconds);
} r1_goodix_board_ops;

typedef struct {
    const r1_goodix_provider_ops *provider;
    void *provider_context;
    const r1_goodix_board_ops *board;
    void *board_context;
    uint32_t active_mask;
    bool initialized;
    bool prepared;
} r1_goodix_adapter;

void r1_goodix_adapter_initialize(r1_goodix_adapter *adapter);
r1_error r1_goodix_adapter_bind(r1_goodix_adapter *adapter,
                                const r1_goodix_provider_ops *provider,
                                void *provider_context,
                                const r1_goodix_board_ops *board,
                                void *board_context);
r1_error r1_goodix_start_stock_profile(r1_goodix_adapter *adapter,
                                       r1_goodix_stock_profile profile);
r1_error r1_goodix_switch_profile(r1_goodix_adapter *adapter,
                                  r1_goodix_switch_selection profile);
r1_error r1_goodix_stop_stock_profiles(r1_goodix_adapter *adapter);
bool r1_goodix_provider_available(const r1_goodix_adapter *adapter);
bool r1_goodix_diagnostic_refresh_due(uint32_t now_tick,
                                      uint32_t previous_refresh_tick);
r1_error r1_goodix_diagnostic_select(
    uint8_t snapshot[R1_GOODIX_DIAGNOSTIC_SNAPSHOT_BYTES], uint8_t selector,
    uint8_t *output, size_t output_capacity, size_t *written);

#endif
