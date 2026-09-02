/* SPDX-License-Identifier: MIT */

#include <stdint.h>

#define OPEN_CFW_EM9305_ENTRY(name) \
    __attribute__((used, noinline, aligned(2), section(".text.entry." name)))

extern uint8_t open_cfw_em9305_load_u8_303e50_impl(void);
extern uint8_t open_cfw_em9305_load_u8_303e5c_impl(void);
extern uint8_t open_cfw_em9305_load_u8_303f50_impl(void);
extern uint32_t open_cfw_em9305_load_u32_303f68_impl(void);
extern uint32_t open_cfw_em9305_equals_one_3047b0_impl(void);
extern void open_cfw_em9305_store_u32_3069b8_impl(uint32_t value);
extern uint32_t open_cfw_em9305_nonzero_307c08_impl(void);
extern uint32_t open_cfw_em9305_nonzero_307dd8_impl(void);
extern uint16_t open_cfw_em9305_load_u16_30f368_impl(void);
extern void open_cfw_em9305_set_bit23_30f710_impl(void);
extern void open_cfw_em9305_set_bit23_30f720_impl(void);
extern void open_cfw_em9305_store_u8_310480_impl(uint8_t value);
extern void open_cfw_em9305_store_u8_31048c_impl(uint8_t value);
extern uint32_t open_cfw_em9305_load_u32_3108f4_impl(void);
extern void open_cfw_em9305_store_u16_311f84_impl(uint16_t value);
extern void open_cfw_em9305_store_u8_3122f0_impl(uint8_t value);
extern void open_cfw_em9305_zero_144_31369c_impl(void);
extern uint16_t open_cfw_em9305_load_u16_313760_impl(void);
extern uint8_t open_cfw_em9305_load_offset23_31b2f8_impl(const uint8_t *base);
extern void open_cfw_em9305_store_40_32cac4_impl(uint8_t *base);
extern void open_cfw_em9305_store_30_32cacc_impl(uint8_t *base);
extern void open_cfw_em9305_store_48_32cad4_impl(uint8_t *base);
extern void open_cfw_em9305_store_34_32cadc_impl(uint8_t *base);

#define OPEN_CFW_EM9305_RETURN_WRAPPER(return_type, name, arguments, call) \
    OPEN_CFW_EM9305_ENTRY(#name) return_type name arguments { return call; }
#define OPEN_CFW_EM9305_VOID_WRAPPER(name, arguments, call) \
    OPEN_CFW_EM9305_ENTRY(#name) void name arguments { call; }

OPEN_CFW_EM9305_RETURN_WRAPPER(
    uint8_t, open_cfw_em9305_load_u8_303e50, (void),
    open_cfw_em9305_load_u8_303e50_impl()
)
OPEN_CFW_EM9305_RETURN_WRAPPER(
    uint8_t, open_cfw_em9305_load_u8_303e5c, (void),
    open_cfw_em9305_load_u8_303e5c_impl()
)
OPEN_CFW_EM9305_RETURN_WRAPPER(
    uint8_t, open_cfw_em9305_load_u8_303f50, (void),
    open_cfw_em9305_load_u8_303f50_impl()
)
OPEN_CFW_EM9305_RETURN_WRAPPER(
    uint32_t, open_cfw_em9305_load_u32_303f68, (void),
    open_cfw_em9305_load_u32_303f68_impl()
)
OPEN_CFW_EM9305_RETURN_WRAPPER(
    uint32_t, open_cfw_em9305_equals_one_3047b0, (void),
    open_cfw_em9305_equals_one_3047b0_impl()
)
OPEN_CFW_EM9305_VOID_WRAPPER(
    open_cfw_em9305_store_u32_3069b8, (uint32_t value),
    open_cfw_em9305_store_u32_3069b8_impl(value)
)
OPEN_CFW_EM9305_RETURN_WRAPPER(
    uint32_t, open_cfw_em9305_nonzero_307c08, (void),
    open_cfw_em9305_nonzero_307c08_impl()
)
OPEN_CFW_EM9305_RETURN_WRAPPER(
    uint32_t, open_cfw_em9305_nonzero_307dd8, (void),
    open_cfw_em9305_nonzero_307dd8_impl()
)
OPEN_CFW_EM9305_RETURN_WRAPPER(
    uint16_t, open_cfw_em9305_load_u16_30f368, (void),
    open_cfw_em9305_load_u16_30f368_impl()
)
OPEN_CFW_EM9305_VOID_WRAPPER(
    open_cfw_em9305_set_bit23_30f710, (void),
    open_cfw_em9305_set_bit23_30f710_impl()
)
OPEN_CFW_EM9305_VOID_WRAPPER(
    open_cfw_em9305_set_bit23_30f720, (void),
    open_cfw_em9305_set_bit23_30f720_impl()
)
OPEN_CFW_EM9305_VOID_WRAPPER(
    open_cfw_em9305_store_u8_310480, (uint8_t value),
    open_cfw_em9305_store_u8_310480_impl(value)
)
OPEN_CFW_EM9305_VOID_WRAPPER(
    open_cfw_em9305_store_u8_31048c, (uint8_t value),
    open_cfw_em9305_store_u8_31048c_impl(value)
)
OPEN_CFW_EM9305_RETURN_WRAPPER(
    uint32_t, open_cfw_em9305_load_u32_3108f4, (void),
    open_cfw_em9305_load_u32_3108f4_impl()
)
OPEN_CFW_EM9305_VOID_WRAPPER(
    open_cfw_em9305_store_u16_311f84, (uint16_t value),
    open_cfw_em9305_store_u16_311f84_impl(value)
)
OPEN_CFW_EM9305_VOID_WRAPPER(
    open_cfw_em9305_store_u8_3122f0, (uint8_t value),
    open_cfw_em9305_store_u8_3122f0_impl(value)
)
OPEN_CFW_EM9305_VOID_WRAPPER(
    open_cfw_em9305_zero_144_31369c, (void),
    open_cfw_em9305_zero_144_31369c_impl()
)
OPEN_CFW_EM9305_RETURN_WRAPPER(
    uint16_t, open_cfw_em9305_load_u16_313760, (void),
    open_cfw_em9305_load_u16_313760_impl()
)
OPEN_CFW_EM9305_RETURN_WRAPPER(
    uint8_t, open_cfw_em9305_load_offset23_31b2f8,
    (const uint8_t *base), open_cfw_em9305_load_offset23_31b2f8_impl(base)
)
OPEN_CFW_EM9305_VOID_WRAPPER(
    open_cfw_em9305_store_40_32cac4, (uint8_t *base),
    open_cfw_em9305_store_40_32cac4_impl(base)
)
OPEN_CFW_EM9305_VOID_WRAPPER(
    open_cfw_em9305_store_30_32cacc, (uint8_t *base),
    open_cfw_em9305_store_30_32cacc_impl(base)
)
OPEN_CFW_EM9305_VOID_WRAPPER(
    open_cfw_em9305_store_48_32cad4, (uint8_t *base),
    open_cfw_em9305_store_48_32cad4_impl(base)
)
OPEN_CFW_EM9305_VOID_WRAPPER(
    open_cfw_em9305_store_34_32cadc, (uint8_t *base),
    open_cfw_em9305_store_34_32cadc_impl(base)
)
