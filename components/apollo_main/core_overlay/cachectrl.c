/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 cache-controller implementation adapted from AmbiqSuite
 * SDK 5.1.0. The reviewed stock spans, callers, register addresses, and host
 * behavioral evidence are recorded in EVIDENCE.md.
 */

#define OPEN_CFW_CACHE_STATUS_SUCCESS 0U
#define OPEN_CFW_CACHE_STATUS_FAIL 1U

#define OPEN_CFW_CACHE_POWER_STATE_ADDRESS 0xE001E300U
#define OPEN_CFW_CACHE_POWER_STATE_MASK 0x00000300U

#define OPEN_CFW_CACHE_CCR_ADDRESS 0xE000ED14U
#define OPEN_CFW_CACHE_CCR_IC_MASK 0x00020000U
#define OPEN_CFW_CACHE_CCR_DC_MASK 0x00010000U

#define OPEN_CFW_CACHE_ICIALLU_ADDRESS 0xE000EF50U
#define OPEN_CFW_CACHE_CSSELR_ADDRESS 0xE000ED84U
#define OPEN_CFW_CACHE_CCSIDR_ADDRESS 0xE000ED80U
#define OPEN_CFW_CACHE_DCISW_ADDRESS 0xE000EF60U
#define OPEN_CFW_CACHE_DCCSW_ADDRESS 0xE000EF6CU
#define OPEN_CFW_CACHE_DCCISW_ADDRESS 0xE000EF74U
#define OPEN_CFW_CACHE_DCIMVAC_ADDRESS 0xE000EF5CU
#define OPEN_CFW_CACHE_DCCIMVAC_ADDRESS 0xE000EF70U
#define OPEN_CFW_CACHE_DCCMVAC_ADDRESS 0xE000EF68U

#define OPEN_CFW_CACHE_PREFETCH_CONFIG_ADDRESS 0x200001C8U
#define OPEN_CFW_CACHE_PREFETCH_CONTROL_ADDRESS 0xE001E004U

#ifndef OPEN_CFW_CACHE_READ
#define OPEN_CFW_CACHE_READ(address) \
    (*(const volatile unsigned int *)(address))
#endif

#ifndef OPEN_CFW_CACHE_WRITE
#define OPEN_CFW_CACHE_WRITE(address, value) \
    (*(volatile unsigned int *)(address) = (value))
#endif

#ifndef OPEN_CFW_CACHE_PREFETCH_CONFIG
#define OPEN_CFW_CACHE_PREFETCH_CONFIG \
    ((const volatile unsigned char *) \
        OPEN_CFW_CACHE_PREFETCH_CONFIG_ADDRESS)
#endif

#ifndef OPEN_CFW_CACHE_DSB
static inline void open_cfw_cache_dsb(void)
{
    __asm__ volatile("dsb 0xF" : : : "memory");
}
#define OPEN_CFW_CACHE_DSB() open_cfw_cache_dsb()
#endif

#ifndef OPEN_CFW_CACHE_ISB
static inline void open_cfw_cache_isb(void)
{
    __asm__ volatile("isb 0xF" : : : "memory");
}
#define OPEN_CFW_CACHE_ISB() open_cfw_cache_isb()
#endif

typedef struct {
    unsigned int start_address;
    int size;
} open_cfw_cache_range;

static __attribute__((always_inline)) inline void
open_cfw_cache_maintain_all(unsigned int operation_address)
{
    unsigned int cache_geometry;
    unsigned int set_index;
    unsigned int way_index;

    OPEN_CFW_CACHE_WRITE(OPEN_CFW_CACHE_CSSELR_ADDRESS, 0U);
    OPEN_CFW_CACHE_DSB();
    cache_geometry = OPEN_CFW_CACHE_READ(OPEN_CFW_CACHE_CCSIDR_ADDRESS);
    set_index = (cache_geometry >> 13U) & 0x7FFFU;
    do {
        way_index = (cache_geometry >> 3U) & 0x3FFU;
        do {
            OPEN_CFW_CACHE_WRITE(
                operation_address,
                ((set_index & 0x1FFU) << 5U) |
                    (way_index << 30U)
            );
        } while (way_index-- != 0U);
    } while (set_index-- != 0U);
    OPEN_CFW_CACHE_DSB();
    OPEN_CFW_CACHE_ISB();
}

static __attribute__((always_inline)) inline void
open_cfw_cache_maintain_range(
    unsigned int operation_address,
    const open_cfw_cache_range *range
)
{
    unsigned int address;
    unsigned int remaining;

    if (range->size < 1) {
        return;
    }

    address = range->start_address;
    remaining = (address & 0x1FU) + (unsigned int)range->size;
    OPEN_CFW_CACHE_DSB();
    do {
        OPEN_CFW_CACHE_WRITE(operation_address, address);
        address += 32U;
        remaining -= 32U;
    } while ((int)remaining > 0);
    OPEN_CFW_CACHE_DSB();
    OPEN_CFW_CACHE_ISB();
}

/*
 * ABI-compatible source replacement for stock
 * 0x00474EB4...0x00474EF9.
 */
__attribute__((used, noinline))
unsigned int open_cfw_cache_icache_enable(void)
{
    unsigned int control;

    if ((OPEN_CFW_CACHE_READ(OPEN_CFW_CACHE_POWER_STATE_ADDRESS) &
         OPEN_CFW_CACHE_POWER_STATE_MASK) != 0U) {
        return OPEN_CFW_CACHE_STATUS_FAIL;
    }

    control = OPEN_CFW_CACHE_READ(OPEN_CFW_CACHE_CCR_ADDRESS);
    if ((control & OPEN_CFW_CACHE_CCR_IC_MASK) == 0U) {
        OPEN_CFW_CACHE_DSB();
        OPEN_CFW_CACHE_ISB();
        OPEN_CFW_CACHE_WRITE(OPEN_CFW_CACHE_ICIALLU_ADDRESS, 0U);
        OPEN_CFW_CACHE_DSB();
        OPEN_CFW_CACHE_ISB();
        control = OPEN_CFW_CACHE_READ(OPEN_CFW_CACHE_CCR_ADDRESS);
        OPEN_CFW_CACHE_WRITE(
            OPEN_CFW_CACHE_CCR_ADDRESS,
            control | OPEN_CFW_CACHE_CCR_IC_MASK
        );
        OPEN_CFW_CACHE_DSB();
        OPEN_CFW_CACHE_ISB();
    }

    return OPEN_CFW_CACHE_STATUS_SUCCESS;
}

/*
 * ABI-compatible source replacement for stock
 * 0x00474EFA...0x00474F31.
 */
__attribute__((used, noinline))
unsigned int open_cfw_cache_icache_disable(void)
{
    unsigned int control;

    if ((OPEN_CFW_CACHE_READ(OPEN_CFW_CACHE_POWER_STATE_ADDRESS) &
         OPEN_CFW_CACHE_POWER_STATE_MASK) != 0U) {
        return OPEN_CFW_CACHE_STATUS_FAIL;
    }

    OPEN_CFW_CACHE_DSB();
    OPEN_CFW_CACHE_ISB();
    control = OPEN_CFW_CACHE_READ(OPEN_CFW_CACHE_CCR_ADDRESS);
    OPEN_CFW_CACHE_WRITE(
        OPEN_CFW_CACHE_CCR_ADDRESS,
        control & ~OPEN_CFW_CACHE_CCR_IC_MASK
    );
    OPEN_CFW_CACHE_WRITE(OPEN_CFW_CACHE_ICIALLU_ADDRESS, 0U);
    OPEN_CFW_CACHE_DSB();
    OPEN_CFW_CACHE_ISB();
    return OPEN_CFW_CACHE_STATUS_SUCCESS;
}

/*
 * ABI-compatible source replacement for stock
 * 0x00474F32...0x00475013. The stock ABI truncates b_clean to eight bits.
 */
__attribute__((used, noinline))
unsigned int open_cfw_cache_dcache_enable(unsigned int b_clean)
{
    const volatile unsigned char *config;
    unsigned int prefetch_control;
    unsigned int control;

    if ((OPEN_CFW_CACHE_READ(OPEN_CFW_CACHE_POWER_STATE_ADDRESS) &
         OPEN_CFW_CACHE_POWER_STATE_MASK) != 0U) {
        return OPEN_CFW_CACHE_STATUS_FAIL;
    }

    config = OPEN_CFW_CACHE_PREFETCH_CONFIG;
    prefetch_control =
        (((unsigned int)config[0] & 7U) << 7U) |
        (((unsigned int)config[1] & 7U) << 4U) |
        (((unsigned int)config[2] & 7U) << 1U) |
        1U;
    OPEN_CFW_CACHE_WRITE(
        OPEN_CFW_CACHE_PREFETCH_CONTROL_ADDRESS,
        prefetch_control
    );

    control = OPEN_CFW_CACHE_READ(OPEN_CFW_CACHE_CCR_ADDRESS);
    if ((control & OPEN_CFW_CACHE_CCR_DC_MASK) == 0U) {
        open_cfw_cache_maintain_all(OPEN_CFW_CACHE_DCISW_ADDRESS);
        control = OPEN_CFW_CACHE_READ(OPEN_CFW_CACHE_CCR_ADDRESS);
        OPEN_CFW_CACHE_WRITE(
            OPEN_CFW_CACHE_CCR_ADDRESS,
            control | OPEN_CFW_CACHE_CCR_DC_MASK
        );
        OPEN_CFW_CACHE_DSB();
        OPEN_CFW_CACHE_ISB();
    }

    if ((unsigned char)b_clean != 0U) {
        open_cfw_cache_maintain_all(OPEN_CFW_CACHE_DCCSW_ADDRESS);
    }

    return OPEN_CFW_CACHE_STATUS_SUCCESS;
}

/*
 * ABI-compatible source replacement for stock
 * 0x00475014...0x0047510D. The stock ABI truncates b_clean to eight bits.
 */
__attribute__((used, noinline))
unsigned int open_cfw_cache_dcache_invalidate(
    const open_cfw_cache_range *range,
    unsigned int b_clean
)
{
    if ((OPEN_CFW_CACHE_READ(OPEN_CFW_CACHE_CCR_ADDRESS) &
         OPEN_CFW_CACHE_CCR_DC_MASK) == 0U) {
        OPEN_CFW_CACHE_DSB();
        OPEN_CFW_CACHE_ISB();
        return OPEN_CFW_CACHE_STATUS_SUCCESS;
    }

    if (range == (const open_cfw_cache_range *)0) {
        if ((unsigned char)b_clean != 0U) {
            open_cfw_cache_maintain_all(
                OPEN_CFW_CACHE_DCCISW_ADDRESS
            );
        } else {
            open_cfw_cache_maintain_all(OPEN_CFW_CACHE_DCISW_ADDRESS);
        }
    } else if ((unsigned char)b_clean != 0U) {
        open_cfw_cache_maintain_range(
            OPEN_CFW_CACHE_DCCIMVAC_ADDRESS,
            range
        );
    } else {
        open_cfw_cache_maintain_range(
            OPEN_CFW_CACHE_DCIMVAC_ADDRESS,
            range
        );
    }

    return OPEN_CFW_CACHE_STATUS_SUCCESS;
}

/*
 * ABI-compatible source replacement for stock
 * 0x0047510E...0x00475193.
 */
__attribute__((used, noinline))
unsigned int open_cfw_cache_dcache_clean(
    const open_cfw_cache_range *range
)
{
    if ((OPEN_CFW_CACHE_READ(OPEN_CFW_CACHE_CCR_ADDRESS) &
         OPEN_CFW_CACHE_CCR_DC_MASK) == 0U) {
        OPEN_CFW_CACHE_DSB();
        OPEN_CFW_CACHE_ISB();
        return OPEN_CFW_CACHE_STATUS_SUCCESS;
    }

    if (range == (const open_cfw_cache_range *)0) {
        open_cfw_cache_maintain_all(OPEN_CFW_CACHE_DCCSW_ADDRESS);
    } else {
        open_cfw_cache_maintain_range(
            OPEN_CFW_CACHE_DCCMVAC_ADDRESS,
            range
        );
    }

    return OPEN_CFW_CACHE_STATUS_SUCCESS;
}
