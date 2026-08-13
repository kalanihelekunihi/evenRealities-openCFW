/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 low-power initialization adaptation from AmbiqSuite SDK
 * 5.1.0. Reviewed stock and SDK evidence is recorded in EVIDENCE.md.
 */

typedef __UINTPTR_TYPE__ open_cfw_pwrctrl_low_power_uintptr;

#define OPEN_CFW_PWRCTRL_LOW_POWER_RSTGEN_STATUS 0x4000885CU
#define OPEN_CFW_PWRCTRL_LOW_POWER_CHIP_REVISION 0x4002000CU
#define OPEN_CFW_PWRCTRL_LOW_POWER_DEBUG_CONTROL 0x40020250U
#define OPEN_CFW_PWRCTRL_LOW_POWER_SHADOW_VALID 0x400201BCU
#define OPEN_CFW_PWRCTRL_LOW_POWER_WIC_CONTROL 0x4002021CU
#define OPEN_CFW_PWRCTRL_LOW_POWER_CLOCK_MISC 0x40004044U
#define OPEN_CFW_PWRCTRL_LOW_POWER_CLOCK_CONTROL 0x40004120U
#define OPEN_CFW_PWRCTRL_LOW_POWER_AUDADC_DELAY 0x40020448U
#define OPEN_CFW_PWRCTRL_LOW_POWER_VR_STATUS 0x40021108U
#define OPEN_CFW_PWRCTRL_LOW_POWER_POWER_SWITCH_0 0x4002037CU
#define OPEN_CFW_PWRCTRL_LOW_POWER_POWER_SWITCH_1 0x40020380U
#define OPEN_CFW_PWRCTRL_LOW_POWER_MRAM_EXT_CONTROL 0x400211C8U

#define OPEN_CFW_PWRCTRL_LOW_POWER_TRACE_COUNT 0x20074F5EU
#define OPEN_CFW_PWRCTRL_LOW_POWER_ORIG_TRIMS_STORED 0x20074F63U
#define OPEN_CFW_PWRCTRL_LOW_POWER_CURRENT_GPU_MODE 0x20074F60U
#define OPEN_CFW_PWRCTRL_LOW_POWER_INFO1_CACHE 0x20071948U
#define OPEN_CFW_PWRCTRL_LOW_POWER_TRIM_VERSION_CACHE 0x200001E8U
#define OPEN_CFW_PWRCTRL_LOW_POWER_DEFAULT_MEMORY_CONFIG 0x200001ECU

#define OPEN_CFW_PWRCTRL_LOW_POWER_DEFAULT_CPDLP_CONFIG 0x0078EE50U
#define OPEN_CFW_PWRCTRL_LOW_POWER_DEFAULT_SRAM_CONFIG 0x0078C984U

#define OPEN_CFW_PWRCTRL_LOW_POWER_ACTTRIMVDDF_SOURCE 0x4002036CU
#define OPEN_CFW_PWRCTRL_LOW_POWER_MEMLDO_SOURCE 0x40020088U
#define OPEN_CFW_PWRCTRL_LOW_POWER_TVRGCVREF_SOURCE 0x40020044U
#define OPEN_CFW_PWRCTRL_LOW_POWER_TVRGFVREF_SOURCE 0x4002004CU
#define OPEN_CFW_PWRCTRL_LOW_POWER_VDDCLKG_SOURCE 0x40020374U
#define OPEN_CFW_PWRCTRL_LOW_POWER_CORELDO_SOURCE 0x40020080U
#define OPEN_CFW_PWRCTRL_LOW_POWER_D2ASPARE_SOURCE 0x400201B0U
#define OPEN_CFW_PWRCTRL_LOW_POWER_VDDC_SOURCE 0x40020344U
#define OPEN_CFW_PWRCTRL_LOW_POWER_VDDCLV_SOURCE 0x4002034CU
#define OPEN_CFW_PWRCTRL_LOW_POWER_VDDF_LOW_SOURCE 0x40020358U
#define OPEN_CFW_PWRCTRL_LOW_POWER_VDDF_HIGH_SOURCE 0x40020354U

#define OPEN_CFW_PWRCTRL_LOW_POWER_TVRGCVREF_DEST 0x2007426CU
#define OPEN_CFW_PWRCTRL_LOW_POWER_TVRGFVREF_DEST 0x20074270U
#define OPEN_CFW_PWRCTRL_LOW_POWER_VDDCLKG_DEST 0x20074274U
#define OPEN_CFW_PWRCTRL_LOW_POWER_CORELDO_ACTIVE_DEST 0x2007427CU
#define OPEN_CFW_PWRCTRL_LOW_POWER_ACTTRIMVDDF_DEST 0x20074280U
#define OPEN_CFW_PWRCTRL_LOW_POWER_MEMLDO_ACTIVE_DEST 0x20074284U
#define OPEN_CFW_PWRCTRL_LOW_POWER_LPTRIMVDDF_DEST 0x20074288U
#define OPEN_CFW_PWRCTRL_LOW_POWER_MEMLDO_LP_DEST 0x2007428CU
#define OPEN_CFW_PWRCTRL_LOW_POWER_D2ASPARE_DEST 0x20074290U
#define OPEN_CFW_PWRCTRL_LOW_POWER_VDDC_LOW_DEST 0x20074294U
#define OPEN_CFW_PWRCTRL_LOW_POWER_VDDC_HIGH_DEST 0x20074298U
#define OPEN_CFW_PWRCTRL_LOW_POWER_VDDCLV_LOW_DEST 0x2007429CU
#define OPEN_CFW_PWRCTRL_LOW_POWER_VDDCLV_HIGH_DEST 0x200742A0U
#define OPEN_CFW_PWRCTRL_LOW_POWER_VDDF_LOW_DEST 0x200742A4U
#define OPEN_CFW_PWRCTRL_LOW_POWER_VDDF_HIGH_DEST 0x200742A8U

#define OPEN_CFW_PWRCTRL_LOW_POWER_STATUS_SUCCESS 0U
#define OPEN_CFW_PWRCTRL_LOW_POWER_INFO1_VALID 0x1F01600DU
#define OPEN_CFW_PWRCTRL_LOW_POWER_PERIPH_CRYPTO 0x17U
#define OPEN_CFW_PWRCTRL_LOW_POWER_PERIPH_DEBUG 0x1CU
#define OPEN_CFW_PWRCTRL_LOW_POWER_PERIPH_OTP 0x1DU

#define OPEN_CFW_PWRCTRL_LOW_POWER_DEBUG_DISABLE_ENTRY 0x004D403FU
#define OPEN_CFW_PWRCTRL_LOW_POWER_INFO1_READ_ENTRY 0x004D3F3DU
#define OPEN_CFW_PWRCTRL_LOW_POWER_SPOT_INIT_ENTRY 0x00480435U
#define OPEN_CFW_PWRCTRL_LOW_POWER_SPOT_TON_INIT_ENTRY 0x004803ADU
#define OPEN_CFW_PWRCTRL_LOW_POWER_SPOT_TON_UPDATE_ENTRY 0x004803C3U
#define OPEN_CFW_PWRCTRL_LOW_POWER_SIMOBUCK_AUTOSW_INIT_ENTRY 0x004803F3U
#define OPEN_CFW_PWRCTRL_LOW_POWER_CLKMUX_INIT_ENTRY 0x0044B159U

#ifndef OPEN_CFW_PWRCTRL_LOW_POWER_READ32
#define OPEN_CFW_PWRCTRL_LOW_POWER_READ32(address) \
    (*(const volatile unsigned int *)( \
        open_cfw_pwrctrl_low_power_uintptr)(address))
#endif

#ifndef OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32
#define OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(address, value) \
    (*(volatile unsigned int *)( \
        open_cfw_pwrctrl_low_power_uintptr)(address) = (value))
#endif

#ifndef OPEN_CFW_PWRCTRL_LOW_POWER_READ8
#define OPEN_CFW_PWRCTRL_LOW_POWER_READ8(address) \
    (*(const volatile unsigned char *)( \
        open_cfw_pwrctrl_low_power_uintptr)(address))
#endif

#ifndef OPEN_CFW_PWRCTRL_LOW_POWER_WRITE8
#define OPEN_CFW_PWRCTRL_LOW_POWER_WRITE8(address, value) \
    (*(volatile unsigned char *)( \
        open_cfw_pwrctrl_low_power_uintptr)(address) = \
            (unsigned char)(value))
#endif

#ifndef OPEN_CFW_PWRCTRL_LOW_POWER_DEBUG_DISABLE
typedef void (*open_cfw_pwrctrl_low_power_void_function)(void);
#define OPEN_CFW_PWRCTRL_LOW_POWER_DEBUG_DISABLE() \
    (((open_cfw_pwrctrl_low_power_void_function) \
        OPEN_CFW_PWRCTRL_LOW_POWER_DEBUG_DISABLE_ENTRY)())
#endif

#ifndef OPEN_CFW_PWRCTRL_LOW_POWER_PERIPH_DISABLE
unsigned int open_cfw_pwrctrl_periph_disable(unsigned int);
#define OPEN_CFW_PWRCTRL_LOW_POWER_PERIPH_DISABLE(peripheral) \
    open_cfw_pwrctrl_periph_disable(peripheral)
#endif

#ifndef OPEN_CFW_PWRCTRL_LOW_POWER_CPDLP_CONFIG
unsigned int open_cfw_pwrctrl_cpdlp_config(unsigned int);
#define OPEN_CFW_PWRCTRL_LOW_POWER_CPDLP_CONFIG(configuration) \
    open_cfw_pwrctrl_cpdlp_config(configuration)
#endif

#ifndef OPEN_CFW_PWRCTRL_LOW_POWER_PERIPH_ENABLED
unsigned int open_cfw_pwrctrl_periph_enabled(
    unsigned int,
    unsigned char *
);
#define OPEN_CFW_PWRCTRL_LOW_POWER_PERIPH_ENABLED(peripheral, enabled) \
    open_cfw_pwrctrl_periph_enabled((peripheral), (enabled))
#endif

#ifndef OPEN_CFW_PWRCTRL_LOW_POWER_PERIPH_ENABLE
unsigned int open_cfw_pwrctrl_periph_enable(unsigned int);
#define OPEN_CFW_PWRCTRL_LOW_POWER_PERIPH_ENABLE(peripheral) \
    open_cfw_pwrctrl_periph_enable(peripheral)
#endif

#ifndef OPEN_CFW_PWRCTRL_LOW_POWER_TRIM_GET
unsigned int open_cfw_pwrctrl_trim_version_get(unsigned int *);
#define OPEN_CFW_PWRCTRL_LOW_POWER_TRIM_GET(output) \
    open_cfw_pwrctrl_trim_version_get(output)
#endif

#ifndef OPEN_CFW_PWRCTRL_LOW_POWER_INFO1_POPULATE
unsigned int open_cfw_pwrctrl_info1_populate(void);
#define OPEN_CFW_PWRCTRL_LOW_POWER_INFO1_POPULATE() \
    open_cfw_pwrctrl_info1_populate()
#endif

#ifndef OPEN_CFW_PWRCTRL_LOW_POWER_INFO1_READ
typedef unsigned int (*open_cfw_pwrctrl_low_power_info1_read_function)(
    unsigned int,
    unsigned int,
    unsigned int,
    unsigned int *
);
#define OPEN_CFW_PWRCTRL_LOW_POWER_INFO1_READ( \
    info_space, word_offset, word_count, destination_address \
) \
    (((open_cfw_pwrctrl_low_power_info1_read_function) \
        OPEN_CFW_PWRCTRL_LOW_POWER_INFO1_READ_ENTRY)( \
            (info_space), \
            (word_offset), \
            (word_count), \
            (unsigned int *)(open_cfw_pwrctrl_low_power_uintptr) \
                (destination_address) \
        ))
#endif

#ifndef OPEN_CFW_PWRCTRL_LOW_POWER_SPOT_INIT
#define OPEN_CFW_PWRCTRL_LOW_POWER_SPOT_INIT() \
    (((open_cfw_pwrctrl_low_power_void_function) \
        OPEN_CFW_PWRCTRL_LOW_POWER_SPOT_INIT_ENTRY)())
#endif

#ifndef OPEN_CFW_PWRCTRL_LOW_POWER_MCU_MEMORY_CONFIG
unsigned int open_cfw_pwrctrl_mcu_memory_config(const void *);
#define OPEN_CFW_PWRCTRL_LOW_POWER_MCU_MEMORY_CONFIG(configuration) \
    open_cfw_pwrctrl_mcu_memory_config( \
        (const void *)(open_cfw_pwrctrl_low_power_uintptr)(configuration) \
    )
#endif

#ifndef OPEN_CFW_PWRCTRL_LOW_POWER_SRAM_CONFIG
unsigned int open_cfw_pwrctrl_sram_config(const void *);
#define OPEN_CFW_PWRCTRL_LOW_POWER_SRAM_CONFIG(configuration) \
    open_cfw_pwrctrl_sram_config( \
        (const void *)(open_cfw_pwrctrl_low_power_uintptr)(configuration) \
    )
#endif

#ifndef OPEN_CFW_PWRCTRL_LOW_POWER_IRQ_DISABLE
unsigned int open_cfw_lv_irq_disable(void);
#define OPEN_CFW_PWRCTRL_LOW_POWER_IRQ_DISABLE() \
    open_cfw_lv_irq_disable()
#endif

#ifndef OPEN_CFW_PWRCTRL_LOW_POWER_SPOT_TON_INIT
#define OPEN_CFW_PWRCTRL_LOW_POWER_SPOT_TON_INIT() \
    (((open_cfw_pwrctrl_low_power_void_function) \
        OPEN_CFW_PWRCTRL_LOW_POWER_SPOT_TON_INIT_ENTRY)())
#endif

#ifndef OPEN_CFW_PWRCTRL_LOW_POWER_SPOT_TON_UPDATE
typedef unsigned int (*open_cfw_pwrctrl_low_power_two_word_function)(
    unsigned int,
    unsigned int
);
#define OPEN_CFW_PWRCTRL_LOW_POWER_SPOT_TON_UPDATE(enabled, gpu_mode) \
    (((open_cfw_pwrctrl_low_power_two_word_function) \
        OPEN_CFW_PWRCTRL_LOW_POWER_SPOT_TON_UPDATE_ENTRY)( \
            (enabled), (gpu_mode) \
        ))
#endif

#ifndef OPEN_CFW_PWRCTRL_LOW_POWER_IRQ_RESTORE
static void
open_cfw_pwrctrl_low_power_irq_restore(unsigned int primask)
{
    __asm__ volatile (
        "msr primask, %0"
        :
        : "r" (primask)
        : "memory"
    );
}
#define OPEN_CFW_PWRCTRL_LOW_POWER_IRQ_RESTORE(primask) \
    open_cfw_pwrctrl_low_power_irq_restore(primask)
#endif

#ifndef OPEN_CFW_PWRCTRL_LOW_POWER_SIMOBUCK_AUTOSW_INIT
#define OPEN_CFW_PWRCTRL_LOW_POWER_SIMOBUCK_AUTOSW_INIT() \
    (((open_cfw_pwrctrl_low_power_void_function) \
        OPEN_CFW_PWRCTRL_LOW_POWER_SIMOBUCK_AUTOSW_INIT_ENTRY)())
#endif

#ifndef OPEN_CFW_PWRCTRL_LOW_POWER_CLKMUX_INIT
#define OPEN_CFW_PWRCTRL_LOW_POWER_CLKMUX_INIT() \
    (((open_cfw_pwrctrl_low_power_void_function) \
        OPEN_CFW_PWRCTRL_LOW_POWER_CLKMUX_INIT_ENTRY)())
#endif

static unsigned int
open_cfw_pwrctrl_low_power_extract(
    unsigned int value,
    unsigned int shift,
    unsigned int mask
)
{
    return (value >> shift) & mask;
}

/*
 * ABI-compatible source replacement for AmbiqSuite's public
 * am_hal_pwrctrl_low_power_init at 0x0047FAE8...0x0047FE11.
 */
__attribute__((used, noinline))
unsigned int open_cfw_pwrctrl_low_power_init(void)
{
    unsigned int value;
    unsigned int revision;
    unsigned int trim_version = 0U;
    unsigned int primask;
    unsigned int core_ldo_active;
    unsigned int status;
    unsigned char enabled = 0U;

    value = OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
        OPEN_CFW_PWRCTRL_LOW_POWER_RSTGEN_STATUS
    );
    if ((value & (1U << 1)) != 0U) {
        value = OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
            OPEN_CFW_PWRCTRL_LOW_POWER_RSTGEN_STATUS
        );
        OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
            OPEN_CFW_PWRCTRL_LOW_POWER_RSTGEN_STATUS,
            value & ~(1U << 2)
        );
    }

    if (
        OPEN_CFW_PWRCTRL_LOW_POWER_READ8(
            OPEN_CFW_PWRCTRL_LOW_POWER_TRACE_COUNT
        ) == 0U
    ) {
        (void)OPEN_CFW_PWRCTRL_LOW_POWER_DEBUG_DISABLE();
        (void)OPEN_CFW_PWRCTRL_LOW_POWER_PERIPH_DISABLE(
            OPEN_CFW_PWRCTRL_LOW_POWER_PERIPH_DEBUG
        );
        value = OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
            OPEN_CFW_PWRCTRL_LOW_POWER_DEBUG_CONTROL
        );
        OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
            OPEN_CFW_PWRCTRL_LOW_POWER_DEBUG_CONTROL,
            value & ~0x1U
        );
        value = OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
            OPEN_CFW_PWRCTRL_LOW_POWER_DEBUG_CONTROL
        );
        OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
            OPEN_CFW_PWRCTRL_LOW_POWER_DEBUG_CONTROL,
            value & ~0xEU
        );
    }

    (void)OPEN_CFW_PWRCTRL_LOW_POWER_CPDLP_CONFIG(
        OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
            OPEN_CFW_PWRCTRL_LOW_POWER_DEFAULT_CPDLP_CONFIG
        )
    );

    value = OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
        OPEN_CFW_PWRCTRL_LOW_POWER_WIC_CONTROL
    );
    OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
        OPEN_CFW_PWRCTRL_LOW_POWER_WIC_CONTROL,
        value | 1U
    );

    if (
        (
            OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
                OPEN_CFW_PWRCTRL_LOW_POWER_SHADOW_VALID
            ) & (1U << 3)
        ) != 0U
    ) {
        (void)OPEN_CFW_PWRCTRL_LOW_POWER_PERIPH_ENABLED(
            OPEN_CFW_PWRCTRL_LOW_POWER_PERIPH_OTP,
            &enabled
        );
        if (enabled == 0U) {
            (void)OPEN_CFW_PWRCTRL_LOW_POWER_PERIPH_ENABLE(
                OPEN_CFW_PWRCTRL_LOW_POWER_PERIPH_OTP
            );
        }
    }

    (void)OPEN_CFW_PWRCTRL_LOW_POWER_TRIM_GET(&trim_version);
    (void)OPEN_CFW_PWRCTRL_LOW_POWER_INFO1_POPULATE();

    if (
        OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
            OPEN_CFW_PWRCTRL_LOW_POWER_INFO1_CACHE
        ) != OPEN_CFW_PWRCTRL_LOW_POWER_INFO1_VALID
    ) {
        status = OPEN_CFW_PWRCTRL_LOW_POWER_INFO1_READ(
            1U,
            0x210U,
            1U,
            OPEN_CFW_PWRCTRL_LOW_POWER_INFO1_CACHE + 0x34U
        );
        if (status != OPEN_CFW_PWRCTRL_LOW_POWER_STATUS_SUCCESS) {
            return status;
        }
        status = OPEN_CFW_PWRCTRL_LOW_POWER_INFO1_READ(
            1U,
            0x245U,
            1U,
            OPEN_CFW_PWRCTRL_LOW_POWER_INFO1_CACHE + 0x44U
        );
        if (status != OPEN_CFW_PWRCTRL_LOW_POWER_STATUS_SUCCESS) {
            return status;
        }
    }

    (void)OPEN_CFW_PWRCTRL_LOW_POWER_SPOT_INIT();
    (void)OPEN_CFW_PWRCTRL_LOW_POWER_PERIPH_DISABLE(
        OPEN_CFW_PWRCTRL_LOW_POWER_PERIPH_CRYPTO
    );
    (void)OPEN_CFW_PWRCTRL_LOW_POWER_PERIPH_DISABLE(
        OPEN_CFW_PWRCTRL_LOW_POWER_PERIPH_OTP
    );

    revision = OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
        OPEN_CFW_PWRCTRL_LOW_POWER_CHIP_REVISION
    ) & 0xFFU;
    if (revision >= 0x22U) {
        OPEN_CFW_PWRCTRL_LOW_POWER_WRITE8(
            OPEN_CFW_PWRCTRL_LOW_POWER_DEFAULT_MEMORY_CONFIG,
            1U
        );
    }
    (void)OPEN_CFW_PWRCTRL_LOW_POWER_MCU_MEMORY_CONFIG(
        OPEN_CFW_PWRCTRL_LOW_POWER_DEFAULT_MEMORY_CONFIG
    );
    (void)OPEN_CFW_PWRCTRL_LOW_POWER_SRAM_CONFIG(
        OPEN_CFW_PWRCTRL_LOW_POWER_DEFAULT_SRAM_CONFIG
    );

    value = OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
        OPEN_CFW_PWRCTRL_LOW_POWER_CLOCK_MISC
    );
    value |= 0x000F80000U | 0x0003BFC0U;
    value &= ~0x00004000U;
    OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
        OPEN_CFW_PWRCTRL_LOW_POWER_CLOCK_MISC,
        value
    );
    OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
        OPEN_CFW_PWRCTRL_LOW_POWER_CLOCK_CONTROL,
        0U
    );

    value = OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
        OPEN_CFW_PWRCTRL_LOW_POWER_AUDADC_DELAY
    );
    value = (value & ~0x0000FF00U) | 0x00000400U;
    OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
        OPEN_CFW_PWRCTRL_LOW_POWER_AUDADC_DELAY,
        value
    );

    if (
        OPEN_CFW_PWRCTRL_LOW_POWER_READ8(
            OPEN_CFW_PWRCTRL_LOW_POWER_ORIG_TRIMS_STORED
        ) == 0U
    ) {
        value = OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
            OPEN_CFW_PWRCTRL_LOW_POWER_ACTTRIMVDDF_SOURCE
        );
        OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
            OPEN_CFW_PWRCTRL_LOW_POWER_ACTTRIMVDDF_DEST,
            open_cfw_pwrctrl_low_power_extract(value, 20U, 0x3FU)
        );
        OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
            OPEN_CFW_PWRCTRL_LOW_POWER_LPTRIMVDDF_DEST,
            open_cfw_pwrctrl_low_power_extract(value, 26U, 0x3FU)
        );

        value = OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
            OPEN_CFW_PWRCTRL_LOW_POWER_MEMLDO_SOURCE
        );
        OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
            OPEN_CFW_PWRCTRL_LOW_POWER_MEMLDO_ACTIVE_DEST,
            value & 0x3FU
        );
        OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
            OPEN_CFW_PWRCTRL_LOW_POWER_MEMLDO_LP_DEST,
            open_cfw_pwrctrl_low_power_extract(value, 18U, 0x3FU)
        );

        value = OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
            OPEN_CFW_PWRCTRL_LOW_POWER_TVRGCVREF_SOURCE
        );
        OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
            OPEN_CFW_PWRCTRL_LOW_POWER_TVRGCVREF_DEST,
            value & 0x7FU
        );
        value = OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
            OPEN_CFW_PWRCTRL_LOW_POWER_TVRGFVREF_SOURCE
        );
        OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
            OPEN_CFW_PWRCTRL_LOW_POWER_TVRGFVREF_DEST,
            value & 0x7FU
        );
        value = OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
            OPEN_CFW_PWRCTRL_LOW_POWER_VDDCLKG_SOURCE
        );
        OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
            OPEN_CFW_PWRCTRL_LOW_POWER_VDDCLKG_DEST,
            open_cfw_pwrctrl_low_power_extract(value, 29U, 0x3U)
        );

        value = OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
            OPEN_CFW_PWRCTRL_LOW_POWER_CORELDO_SOURCE
        );
        core_ldo_active = value & 0x3FFU;
        if (
            open_cfw_pwrctrl_low_power_extract(
                OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
                    OPEN_CFW_PWRCTRL_LOW_POWER_VR_STATUS
                ),
                4U,
                0x3U
            ) == 3U
            && (
                (
                    revision == 0x21U
                    && OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
                        OPEN_CFW_PWRCTRL_LOW_POWER_TRIM_VERSION_CACHE
                    ) != 0U
                )
                || revision >= 0x22U
            )
        ) {
            trim_version = OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
                OPEN_CFW_PWRCTRL_LOW_POWER_TRIM_VERSION_CACHE
            );
            if (
                (revision == 0x21U && trim_version >= 3U)
                || (revision == 0x22U && trim_version == 1U)
                || (revision == 0x23U && trim_version == 0U)
            ) {
                core_ldo_active += 7U;
            }
            else if (
                (revision == 0x21U && trim_version < 3U)
                || (revision == 0x22U && trim_version == 0U)
            ) {
                core_ldo_active += 6U;
            }
        }
        OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
            OPEN_CFW_PWRCTRL_LOW_POWER_CORELDO_ACTIVE_DEST,
            core_ldo_active
        );

        OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
            OPEN_CFW_PWRCTRL_LOW_POWER_D2ASPARE_DEST,
            OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
                OPEN_CFW_PWRCTRL_LOW_POWER_D2ASPARE_SOURCE
            )
        );

        value = OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
            OPEN_CFW_PWRCTRL_LOW_POWER_VDDC_SOURCE
        );
        OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
            OPEN_CFW_PWRCTRL_LOW_POWER_VDDC_LOW_DEST,
            open_cfw_pwrctrl_low_power_extract(value, 25U, 0x1FU)
        );
        OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
            OPEN_CFW_PWRCTRL_LOW_POWER_VDDC_HIGH_DEST,
            open_cfw_pwrctrl_low_power_extract(value, 11U, 0x1FU)
        );
        value = OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
            OPEN_CFW_PWRCTRL_LOW_POWER_VDDCLV_SOURCE
        );
        OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
            OPEN_CFW_PWRCTRL_LOW_POWER_VDDCLV_LOW_DEST,
            open_cfw_pwrctrl_low_power_extract(value, 25U, 0x1FU)
        );
        OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
            OPEN_CFW_PWRCTRL_LOW_POWER_VDDCLV_HIGH_DEST,
            open_cfw_pwrctrl_low_power_extract(value, 11U, 0x1FU)
        );
        value = OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
            OPEN_CFW_PWRCTRL_LOW_POWER_VDDF_LOW_SOURCE
        );
        OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
            OPEN_CFW_PWRCTRL_LOW_POWER_VDDF_LOW_DEST,
            open_cfw_pwrctrl_low_power_extract(value, 8U, 0x1FU)
        );
        value = OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
            OPEN_CFW_PWRCTRL_LOW_POWER_VDDF_HIGH_SOURCE
        );
        OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
            OPEN_CFW_PWRCTRL_LOW_POWER_VDDF_HIGH_DEST,
            open_cfw_pwrctrl_low_power_extract(value, 17U, 0x1FU)
        );
        OPEN_CFW_PWRCTRL_LOW_POWER_WRITE8(
            OPEN_CFW_PWRCTRL_LOW_POWER_ORIG_TRIMS_STORED,
            1U
        );
    }

    value = OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
        OPEN_CFW_PWRCTRL_LOW_POWER_POWER_SWITCH_0
    );
    OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
        OPEN_CFW_PWRCTRL_LOW_POWER_POWER_SWITCH_0,
        value | 0x40000000U
    );
    value = OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
        OPEN_CFW_PWRCTRL_LOW_POWER_POWER_SWITCH_1
    );
    OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
        OPEN_CFW_PWRCTRL_LOW_POWER_POWER_SWITCH_1,
        value | 0x00010000U
    );
    value = OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
        OPEN_CFW_PWRCTRL_LOW_POWER_POWER_SWITCH_1
    );
    OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
        OPEN_CFW_PWRCTRL_LOW_POWER_POWER_SWITCH_1,
        value | 0x00001000U
    );

    primask = OPEN_CFW_PWRCTRL_LOW_POWER_IRQ_DISABLE();
    (void)OPEN_CFW_PWRCTRL_LOW_POWER_SPOT_TON_INIT();
    (void)OPEN_CFW_PWRCTRL_LOW_POWER_SPOT_TON_UPDATE(
        0U,
        OPEN_CFW_PWRCTRL_LOW_POWER_READ8(
            OPEN_CFW_PWRCTRL_LOW_POWER_CURRENT_GPU_MODE
        )
    );
    OPEN_CFW_PWRCTRL_LOW_POWER_IRQ_RESTORE(primask);
    (void)OPEN_CFW_PWRCTRL_LOW_POWER_SIMOBUCK_AUTOSW_INIT();
    (void)OPEN_CFW_PWRCTRL_LOW_POWER_CLKMUX_INIT();

    if (revision >= 0x22U) {
        value = OPEN_CFW_PWRCTRL_LOW_POWER_READ32(
            OPEN_CFW_PWRCTRL_LOW_POWER_MRAM_EXT_CONTROL
        );
        OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32(
            OPEN_CFW_PWRCTRL_LOW_POWER_MRAM_EXT_CONTROL,
            value | 0x6U
        );
    }

    return OPEN_CFW_PWRCTRL_LOW_POWER_STATUS_SUCCESS;
}

#undef OPEN_CFW_PWRCTRL_LOW_POWER_CLKMUX_INIT
#undef OPEN_CFW_PWRCTRL_LOW_POWER_SIMOBUCK_AUTOSW_INIT
#undef OPEN_CFW_PWRCTRL_LOW_POWER_IRQ_RESTORE
#undef OPEN_CFW_PWRCTRL_LOW_POWER_SPOT_TON_UPDATE
#undef OPEN_CFW_PWRCTRL_LOW_POWER_SPOT_TON_INIT
#undef OPEN_CFW_PWRCTRL_LOW_POWER_IRQ_DISABLE
#undef OPEN_CFW_PWRCTRL_LOW_POWER_SRAM_CONFIG
#undef OPEN_CFW_PWRCTRL_LOW_POWER_MCU_MEMORY_CONFIG
#undef OPEN_CFW_PWRCTRL_LOW_POWER_SPOT_INIT
#undef OPEN_CFW_PWRCTRL_LOW_POWER_INFO1_READ
#undef OPEN_CFW_PWRCTRL_LOW_POWER_INFO1_POPULATE
#undef OPEN_CFW_PWRCTRL_LOW_POWER_TRIM_GET
#undef OPEN_CFW_PWRCTRL_LOW_POWER_PERIPH_ENABLE
#undef OPEN_CFW_PWRCTRL_LOW_POWER_PERIPH_ENABLED
#undef OPEN_CFW_PWRCTRL_LOW_POWER_CPDLP_CONFIG
#undef OPEN_CFW_PWRCTRL_LOW_POWER_PERIPH_DISABLE
#undef OPEN_CFW_PWRCTRL_LOW_POWER_DEBUG_DISABLE
#undef OPEN_CFW_PWRCTRL_LOW_POWER_WRITE8
#undef OPEN_CFW_PWRCTRL_LOW_POWER_READ8
#undef OPEN_CFW_PWRCTRL_LOW_POWER_WRITE32
#undef OPEN_CFW_PWRCTRL_LOW_POWER_READ32
