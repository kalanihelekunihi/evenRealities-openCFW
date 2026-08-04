/*
 * SPDX-License-Identifier: BSD-3-Clause
 *
 * Copyright (c) 2025, Ambiq Micro, Inc.
 * All rights reserved.
 *
 * Bounded Apollo510 SPOT-manager initializer adaptation from AmbiqSuite SDK
 * 5.1.0 and the reviewed G2 2.2.6.10 stock function at
 * 0x00480434...0x004806CF.
 */

typedef __UINTPTR_TYPE__ open_cfw_spotmgr_init_uintptr;

#define OPEN_CFW_SPOTMGR_INIT_STATE_ADDRESS 0x20073270U
#define OPEN_CFW_SPOTMGR_INIT_CHIP_REVISION_ADDRESS 0x4002000CU
#define OPEN_CFW_SPOTMGR_INIT_TRIM_VERSION_ADDRESS 0x200001E8U
#define OPEN_CFW_SPOTMGR_INIT_INFO1_CACHE_ADDRESS 0x20071948U
#define OPEN_CFW_SPOTMGR_INIT_INFO1_PATCH_TRACKER0_OFFSET 0x34U
#define OPEN_CFW_SPOTMGR_INIT_ACRG_ADDRESS 0x40020028U
#define OPEN_CFW_SPOTMGR_INIT_VRCTRL_ADDRESS 0x40020060U

#define OPEN_CFW_SPOTMGR_INIT_IS_PCM2P1_ADDRESS 0x20074F64U
#define OPEN_CFW_SPOTMGR_INIT_IS_PCM1P0_OR_PCM1P1_ADDRESS 0x20074F65U
#define OPEN_CFW_SPOTMGR_INIT_IS_B0_PCM1P1_OR_NEWER_ADDRESS 0x20074F66U
#define OPEN_CFW_SPOTMGR_INIT_IS_PCM2P0_ADDRESS 0x20074F67U
#define OPEN_CFW_SPOTMGR_INIT_IS_PCM2P2_OR_NEWER_ADDRESS 0x20074F68U
#define OPEN_CFW_SPOTMGR_INIT_IS_PCM2P1_WITHOUT_PATCH_ADDRESS 0x20074F69U

#define OPEN_CFW_SPOTMGR_INIT_SLOT_INIT 0x00U
#define OPEN_CFW_SPOTMGR_INIT_SLOT_POWER_UPDATE 0x04U
#define OPEN_CFW_SPOTMGR_INIT_SLOT_DEFAULT_RESET 0x08U
#define OPEN_CFW_SPOTMGR_INIT_SLOT_TEMPCO_POSTPONE 0x0CU
#define OPEN_CFW_SPOTMGR_INIT_SLOT_TEMPCO_PENDING 0x10U
#define OPEN_CFW_SPOTMGR_INIT_SLOT_SIMOBUCK_BFR_OVR 0x14U
#define OPEN_CFW_SPOTMGR_INIT_SLOT_SIMOBUCK_BFR_ENABLE 0x18U
#define OPEN_CFW_SPOTMGR_INIT_SLOT_SIMOBUCK_AFT_ENABLE 0x1CU
#define OPEN_CFW_SPOTMGR_INIT_SLOT_TON_INIT 0x20U
#define OPEN_CFW_SPOTMGR_INIT_SLOT_TON_UPDATE 0x24U
#define OPEN_CFW_SPOTMGR_INIT_SLOT_POST_LPTOHP 0x28U
#define OPEN_CFW_SPOTMGR_INIT_SLOT_TIMER_SERVICE 0x2CU
#define OPEN_CFW_SPOTMGR_INIT_SLOT_AUTOSW_INIT 0x30U
#define OPEN_CFW_SPOTMGR_INIT_SLOT_AUTOSW_ENABLE 0x34U
#define OPEN_CFW_SPOTMGR_INIT_SLOT_AUTOSW_DISABLE 0x38U
#define OPEN_CFW_SPOTMGR_INIT_STATE_SIZE 0x3CU

#define OPEN_CFW_SPOTMGR_INIT_REVISION_B0 0x21U
#define OPEN_CFW_SPOTMGR_INIT_REVISION_B1 0x22U
#define OPEN_CFW_SPOTMGR_INIT_REVISION_B2 0x23U

#define OPEN_CFW_SPOTMGR_INIT_ACRG_POWER_DOWN 0x00000002U
#define OPEN_CFW_SPOTMGR_INIT_ACRG_SOFTWARE_ENABLE 0x00000001U
#define OPEN_CFW_SPOTMGR_INIT_ANALDO_OVERRIDE 0x00002000U
#define OPEN_CFW_SPOTMGR_INIT_ANALDO_POWER_ENABLE 0x00004000U
#define OPEN_CFW_SPOTMGR_INIT_ANALDO_ACTIVE 0x00008000U

#define OPEN_CFW_SPOTMGR_INIT_PCM2P2_INIT 0x005A4D49U
#define OPEN_CFW_SPOTMGR_INIT_PCM2P2_POWER_UPDATE 0x005A490DU
#define OPEN_CFW_SPOTMGR_INIT_PCM2P2_DEFAULT_RESET 0x005A4E0DU
#define OPEN_CFW_SPOTMGR_INIT_PCM2P2_SIMOBUCK_AFT_ENABLE 0x005A4D01U
#define OPEN_CFW_SPOTMGR_INIT_PCM2P2_POST_LPTOHP 0x005A40B7U
#define OPEN_CFW_SPOTMGR_INIT_PCM2P2_TIMER_SERVICE 0x005A40CBU

#define OPEN_CFW_SPOTMGR_INIT_PCM2P1_INIT 0x005A1C19U
#define OPEN_CFW_SPOTMGR_INIT_PCM2P1_POWER_UPDATE 0x005A1739U
#define OPEN_CFW_SPOTMGR_INIT_PCM2P1_DEFAULT_RESET 0x005A1DA5U
#define OPEN_CFW_SPOTMGR_INIT_PCM2P1_SIMOBUCK_BFR_OVR 0x005A1BBDU
#define OPEN_CFW_SPOTMGR_INIT_PCM2P1_SIMOBUCK_BFR_ENABLE 0x005A1BCDU
#define OPEN_CFW_SPOTMGR_INIT_PCM2P1_SIMOBUCK_AFT_ENABLE 0x005A1BEDU
#define OPEN_CFW_SPOTMGR_INIT_PCM2P1_TIMER_SERVICE 0x005A0BCDU

#define OPEN_CFW_SPOTMGR_INIT_PCM2P0_INIT 0x005A08E5U
#define OPEN_CFW_SPOTMGR_INIT_PCM2P0_POWER_UPDATE 0x005A0787U
#define OPEN_CFW_SPOTMGR_INIT_PCM2P0_DEFAULT_RESET 0x005A0A6DU
#define OPEN_CFW_SPOTMGR_INIT_PCM2P0_TEMPCO_POSTPONE 0x005A07E7U
#define OPEN_CFW_SPOTMGR_INIT_PCM2P0_TEMPCO_PENDING 0x005A07F1U
#define OPEN_CFW_SPOTMGR_INIT_PCM2P0_SIMOBUCK_BFR_ENABLE 0x005A081DU
#define OPEN_CFW_SPOTMGR_INIT_PCM2P0_SIMOBUCK_AFT_ENABLE 0x005A0843U
#define OPEN_CFW_SPOTMGR_INIT_PCM2P0_AUTOSW_INIT 0x005A085FU
#define OPEN_CFW_SPOTMGR_INIT_PCM2P0_AUTOSW_ENABLE 0x005A08B7U
#define OPEN_CFW_SPOTMGR_INIT_PCM2P0_AUTOSW_DISABLE 0x005A08CBU

#define OPEN_CFW_SPOTMGR_INIT_PCM0P7_INIT 0x005A0019U
#define OPEN_CFW_SPOTMGR_INIT_PCM0P7_POWER_UPDATE 0x0059FD37U
#define OPEN_CFW_SPOTMGR_INIT_PCM0P7_SIMOBUCK_BFR_ENABLE 0x0059FD83U
#define OPEN_CFW_SPOTMGR_INIT_PCM0P7_SIMOBUCK_AFT_ENABLE 0x0059FDA9U
#define OPEN_CFW_SPOTMGR_INIT_PCM0P7_TON_INIT 0x0059FDC3U
#define OPEN_CFW_SPOTMGR_INIT_PCM0P7_TON_UPDATE 0x0059FE5BU

#ifndef OPEN_CFW_SPOTMGR_INIT_READ32
#define OPEN_CFW_SPOTMGR_INIT_READ32(address) \
    (*(const volatile unsigned int *)( \
        open_cfw_spotmgr_init_uintptr)(address))
#endif

#ifndef OPEN_CFW_SPOTMGR_INIT_WRITE32
#define OPEN_CFW_SPOTMGR_INIT_WRITE32(address, value) \
    (*(volatile unsigned int *)( \
        open_cfw_spotmgr_init_uintptr)(address) = (value))
#endif

#ifndef OPEN_CFW_SPOTMGR_INIT_READ8
#define OPEN_CFW_SPOTMGR_INIT_READ8(address) \
    (*(const volatile unsigned char *)( \
        open_cfw_spotmgr_init_uintptr)(address))
#endif

#ifndef OPEN_CFW_SPOTMGR_INIT_WRITE8
#define OPEN_CFW_SPOTMGR_INIT_WRITE8(address, value) \
    (*(volatile unsigned char *)( \
        open_cfw_spotmgr_init_uintptr)(address) = \
            (unsigned char)(value))
#endif

#ifndef OPEN_CFW_SPOTMGR_INIT_READ_HANDLER
#define OPEN_CFW_SPOTMGR_INIT_READ_HANDLER(offset) \
    (*(const volatile unsigned int *)( \
        open_cfw_spotmgr_init_uintptr)( \
            OPEN_CFW_SPOTMGR_INIT_STATE_ADDRESS + (offset)))
#endif

#ifndef OPEN_CFW_SPOTMGR_INIT_WRITE_HANDLER
#define OPEN_CFW_SPOTMGR_INIT_WRITE_HANDLER(offset, value) \
    (*(volatile unsigned int *)( \
        open_cfw_spotmgr_init_uintptr)( \
            OPEN_CFW_SPOTMGR_INIT_STATE_ADDRESS + (offset)) = (value))
#endif

#ifndef OPEN_CFW_SPOTMGR_INIT_CALL_HANDLER
typedef unsigned int (*open_cfw_spotmgr_init_function)(void);
#define OPEN_CFW_SPOTMGR_INIT_CALL_HANDLER(handler) \
    (((open_cfw_spotmgr_init_function) \
        (open_cfw_spotmgr_init_uintptr)(handler))())
#endif

static __attribute__((always_inline)) inline unsigned int
open_cfw_spotmgr_init_revision(void)
{
    return OPEN_CFW_SPOTMGR_INIT_READ32(
        OPEN_CFW_SPOTMGR_INIT_CHIP_REVISION_ADDRESS
    ) & 0xFFU;
}

static __attribute__((always_inline)) inline unsigned int
open_cfw_spotmgr_init_trim_version(void)
{
    return OPEN_CFW_SPOTMGR_INIT_READ32(
        OPEN_CFW_SPOTMGR_INIT_TRIM_VERSION_ADDRESS
    );
}

static __attribute__((always_inline)) inline unsigned int
open_cfw_spotmgr_init_is_pcm2p1(void)
{
    return (
        (
            open_cfw_spotmgr_init_revision()
            == OPEN_CFW_SPOTMGR_INIT_REVISION_B1
            && open_cfw_spotmgr_init_trim_version() == 2U
        )
        || (
            open_cfw_spotmgr_init_revision()
            == OPEN_CFW_SPOTMGR_INIT_REVISION_B2
            && open_cfw_spotmgr_init_trim_version() == 1U
        )
    );
}

static __attribute__((always_inline)) inline void
open_cfw_spotmgr_init_write_handler(
    unsigned int offset,
    unsigned int handler
)
{
    OPEN_CFW_SPOTMGR_INIT_WRITE_HANDLER(offset, handler);
}

/*
 * ABI-compatible source replacement for AmbiqSuite's public
 * am_hal_spotmgr_init at 0x00480434...0x004806CF.
 */
__attribute__((used, noinline))
unsigned int open_cfw_spotmgr_init(void)
{
    unsigned int offset;
    unsigned int value;
    unsigned int handler;
    unsigned int is_pcm2p2_or_newer;
    unsigned int is_pcm2p1;
    unsigned int is_pcm1p0_or_pcm1p1;
    unsigned int is_b0_pcm1p1_or_newer;
    unsigned int is_pcm2p0;
    unsigned int is_pcm2p1_without_patch;

    for (
        offset = 0U;
        offset < OPEN_CFW_SPOTMGR_INIT_STATE_SIZE;
        offset += 4U
    ) {
        open_cfw_spotmgr_init_write_handler(offset, 0U);
    }

    is_pcm2p2_or_newer = (
        (
            open_cfw_spotmgr_init_revision()
            == OPEN_CFW_SPOTMGR_INIT_REVISION_B2
            && open_cfw_spotmgr_init_trim_version() >= 2U
        )
        || open_cfw_spotmgr_init_revision()
            > OPEN_CFW_SPOTMGR_INIT_REVISION_B2
    );
    OPEN_CFW_SPOTMGR_INIT_WRITE8(
        OPEN_CFW_SPOTMGR_INIT_IS_PCM2P2_OR_NEWER_ADDRESS,
        is_pcm2p2_or_newer
    );

    is_pcm2p1 = open_cfw_spotmgr_init_is_pcm2p1();
    OPEN_CFW_SPOTMGR_INIT_WRITE8(
        OPEN_CFW_SPOTMGR_INIT_IS_PCM2P1_ADDRESS,
        is_pcm2p1
    );

    is_pcm1p0_or_pcm1p1 = (
        (
            open_cfw_spotmgr_init_revision()
            == OPEN_CFW_SPOTMGR_INIT_REVISION_B0
            && (
                open_cfw_spotmgr_init_trim_version() == 2U
                || open_cfw_spotmgr_init_trim_version() == 3U
            )
        )
        || (
            open_cfw_spotmgr_init_revision()
            == OPEN_CFW_SPOTMGR_INIT_REVISION_B1
            && open_cfw_spotmgr_init_trim_version() == 0U
        )
    );
    OPEN_CFW_SPOTMGR_INIT_WRITE8(
        OPEN_CFW_SPOTMGR_INIT_IS_PCM1P0_OR_PCM1P1_ADDRESS,
        is_pcm1p0_or_pcm1p1
    );

    is_b0_pcm1p1_or_newer = (
        open_cfw_spotmgr_init_revision()
            == OPEN_CFW_SPOTMGR_INIT_REVISION_B0
        && open_cfw_spotmgr_init_trim_version() >= 3U
    );
    OPEN_CFW_SPOTMGR_INIT_WRITE8(
        OPEN_CFW_SPOTMGR_INIT_IS_B0_PCM1P1_OR_NEWER_ADDRESS,
        is_b0_pcm1p1_or_newer
    );

    is_pcm2p0 = (
        (
            open_cfw_spotmgr_init_revision()
            == OPEN_CFW_SPOTMGR_INIT_REVISION_B1
            && open_cfw_spotmgr_init_trim_version() == 1U
        )
        || (
            open_cfw_spotmgr_init_revision()
            == OPEN_CFW_SPOTMGR_INIT_REVISION_B2
            && open_cfw_spotmgr_init_trim_version() == 0U
        )
    );
    OPEN_CFW_SPOTMGR_INIT_WRITE8(
        OPEN_CFW_SPOTMGR_INIT_IS_PCM2P0_ADDRESS,
        is_pcm2p0
    );

    is_pcm2p1_without_patch = (
        open_cfw_spotmgr_init_is_pcm2p1()
        && (
            OPEN_CFW_SPOTMGR_INIT_READ8(
                OPEN_CFW_SPOTMGR_INIT_INFO1_CACHE_ADDRESS
                + OPEN_CFW_SPOTMGR_INIT_INFO1_PATCH_TRACKER0_OFFSET
            ) & 1U
        ) == 0U
    );
    OPEN_CFW_SPOTMGR_INIT_WRITE8(
        OPEN_CFW_SPOTMGR_INIT_IS_PCM2P1_WITHOUT_PATCH_ADDRESS,
        is_pcm2p1_without_patch
    );

    if (
        is_pcm1p0_or_pcm1p1 != 0U
        || is_pcm2p0 != 0U
        || is_pcm2p1_without_patch != 0U
    ) {
        value = OPEN_CFW_SPOTMGR_INIT_READ32(
            OPEN_CFW_SPOTMGR_INIT_ACRG_ADDRESS
        );
        OPEN_CFW_SPOTMGR_INIT_WRITE32(
            OPEN_CFW_SPOTMGR_INIT_ACRG_ADDRESS,
            value & ~OPEN_CFW_SPOTMGR_INIT_ACRG_POWER_DOWN
        );
        value = OPEN_CFW_SPOTMGR_INIT_READ32(
            OPEN_CFW_SPOTMGR_INIT_ACRG_ADDRESS
        );
        OPEN_CFW_SPOTMGR_INIT_WRITE32(
            OPEN_CFW_SPOTMGR_INIT_ACRG_ADDRESS,
            value | OPEN_CFW_SPOTMGR_INIT_ACRG_SOFTWARE_ENABLE
        );

        value = OPEN_CFW_SPOTMGR_INIT_READ32(
            OPEN_CFW_SPOTMGR_INIT_VRCTRL_ADDRESS
        );
        OPEN_CFW_SPOTMGR_INIT_WRITE32(
            OPEN_CFW_SPOTMGR_INIT_VRCTRL_ADDRESS,
            value | OPEN_CFW_SPOTMGR_INIT_ANALDO_ACTIVE
        );
        value = OPEN_CFW_SPOTMGR_INIT_READ32(
            OPEN_CFW_SPOTMGR_INIT_VRCTRL_ADDRESS
        );
        OPEN_CFW_SPOTMGR_INIT_WRITE32(
            OPEN_CFW_SPOTMGR_INIT_VRCTRL_ADDRESS,
            value | OPEN_CFW_SPOTMGR_INIT_ANALDO_POWER_ENABLE
        );
        value = OPEN_CFW_SPOTMGR_INIT_READ32(
            OPEN_CFW_SPOTMGR_INIT_VRCTRL_ADDRESS
        );
        OPEN_CFW_SPOTMGR_INIT_WRITE32(
            OPEN_CFW_SPOTMGR_INIT_VRCTRL_ADDRESS,
            value | OPEN_CFW_SPOTMGR_INIT_ANALDO_OVERRIDE
        );
    }

    if (is_pcm2p2_or_newer != 0U) {
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_INIT,
            OPEN_CFW_SPOTMGR_INIT_PCM2P2_INIT
        );
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_POWER_UPDATE,
            OPEN_CFW_SPOTMGR_INIT_PCM2P2_POWER_UPDATE
        );
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_DEFAULT_RESET,
            OPEN_CFW_SPOTMGR_INIT_PCM2P2_DEFAULT_RESET
        );
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_SIMOBUCK_AFT_ENABLE,
            OPEN_CFW_SPOTMGR_INIT_PCM2P2_SIMOBUCK_AFT_ENABLE
        );
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_POST_LPTOHP,
            OPEN_CFW_SPOTMGR_INIT_PCM2P2_POST_LPTOHP
        );
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_TIMER_SERVICE,
            OPEN_CFW_SPOTMGR_INIT_PCM2P2_TIMER_SERVICE
        );
    }
    else if (is_pcm2p1 != 0U) {
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_INIT,
            OPEN_CFW_SPOTMGR_INIT_PCM2P1_INIT
        );
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_POWER_UPDATE,
            OPEN_CFW_SPOTMGR_INIT_PCM2P1_POWER_UPDATE
        );
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_DEFAULT_RESET,
            OPEN_CFW_SPOTMGR_INIT_PCM2P1_DEFAULT_RESET
        );
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_SIMOBUCK_BFR_OVR,
            OPEN_CFW_SPOTMGR_INIT_PCM2P1_SIMOBUCK_BFR_OVR
        );
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_SIMOBUCK_BFR_ENABLE,
            OPEN_CFW_SPOTMGR_INIT_PCM2P1_SIMOBUCK_BFR_ENABLE
        );
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_SIMOBUCK_AFT_ENABLE,
            OPEN_CFW_SPOTMGR_INIT_PCM2P1_SIMOBUCK_AFT_ENABLE
        );
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_TIMER_SERVICE,
            OPEN_CFW_SPOTMGR_INIT_PCM2P1_TIMER_SERVICE
        );
    }
    else if (
        (
            open_cfw_spotmgr_init_revision()
            == OPEN_CFW_SPOTMGR_INIT_REVISION_B0
            && open_cfw_spotmgr_init_trim_version() >= 2U
        )
        || (
            open_cfw_spotmgr_init_revision()
            == OPEN_CFW_SPOTMGR_INIT_REVISION_B1
            && open_cfw_spotmgr_init_trim_version() < 2U
        )
        || (
            open_cfw_spotmgr_init_revision()
            == OPEN_CFW_SPOTMGR_INIT_REVISION_B2
            && open_cfw_spotmgr_init_trim_version() == 0U
        )
    ) {
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_INIT,
            OPEN_CFW_SPOTMGR_INIT_PCM2P0_INIT
        );
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_POWER_UPDATE,
            OPEN_CFW_SPOTMGR_INIT_PCM2P0_POWER_UPDATE
        );
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_DEFAULT_RESET,
            OPEN_CFW_SPOTMGR_INIT_PCM2P0_DEFAULT_RESET
        );
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_TEMPCO_POSTPONE,
            OPEN_CFW_SPOTMGR_INIT_PCM2P0_TEMPCO_POSTPONE
        );
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_TEMPCO_PENDING,
            OPEN_CFW_SPOTMGR_INIT_PCM2P0_TEMPCO_PENDING
        );
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_AUTOSW_INIT,
            OPEN_CFW_SPOTMGR_INIT_PCM2P0_AUTOSW_INIT
        );
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_AUTOSW_ENABLE,
            OPEN_CFW_SPOTMGR_INIT_PCM2P0_AUTOSW_ENABLE
        );
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_AUTOSW_DISABLE,
            OPEN_CFW_SPOTMGR_INIT_PCM2P0_AUTOSW_DISABLE
        );

        if (
            open_cfw_spotmgr_init_revision()
                == OPEN_CFW_SPOTMGR_INIT_REVISION_B0
            && open_cfw_spotmgr_init_trim_version() == 2U
        ) {
            open_cfw_spotmgr_init_write_handler(
                OPEN_CFW_SPOTMGR_INIT_SLOT_SIMOBUCK_BFR_ENABLE,
                OPEN_CFW_SPOTMGR_INIT_PCM0P7_SIMOBUCK_BFR_ENABLE
            );
            open_cfw_spotmgr_init_write_handler(
                OPEN_CFW_SPOTMGR_INIT_SLOT_SIMOBUCK_AFT_ENABLE,
                OPEN_CFW_SPOTMGR_INIT_PCM0P7_SIMOBUCK_AFT_ENABLE
            );
        }
        else {
            open_cfw_spotmgr_init_write_handler(
                OPEN_CFW_SPOTMGR_INIT_SLOT_SIMOBUCK_BFR_ENABLE,
                OPEN_CFW_SPOTMGR_INIT_PCM2P0_SIMOBUCK_BFR_ENABLE
            );
            open_cfw_spotmgr_init_write_handler(
                OPEN_CFW_SPOTMGR_INIT_SLOT_SIMOBUCK_AFT_ENABLE,
                OPEN_CFW_SPOTMGR_INIT_PCM2P0_SIMOBUCK_AFT_ENABLE
            );
        }
    }
    else if (
        open_cfw_spotmgr_init_revision()
            == OPEN_CFW_SPOTMGR_INIT_REVISION_B0
        && open_cfw_spotmgr_init_trim_version() == 1U
    ) {
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_INIT,
            OPEN_CFW_SPOTMGR_INIT_PCM0P7_INIT
        );
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_POWER_UPDATE,
            OPEN_CFW_SPOTMGR_INIT_PCM0P7_POWER_UPDATE
        );
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_SIMOBUCK_BFR_ENABLE,
            OPEN_CFW_SPOTMGR_INIT_PCM0P7_SIMOBUCK_BFR_ENABLE
        );
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_SIMOBUCK_AFT_ENABLE,
            OPEN_CFW_SPOTMGR_INIT_PCM0P7_SIMOBUCK_AFT_ENABLE
        );
    }

    if (
        open_cfw_spotmgr_init_revision()
            == OPEN_CFW_SPOTMGR_INIT_REVISION_B0
        && open_cfw_spotmgr_init_trim_version() < 2U
    ) {
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_TON_INIT,
            OPEN_CFW_SPOTMGR_INIT_PCM0P7_TON_INIT
        );
        open_cfw_spotmgr_init_write_handler(
            OPEN_CFW_SPOTMGR_INIT_SLOT_TON_UPDATE,
            OPEN_CFW_SPOTMGR_INIT_PCM0P7_TON_UPDATE
        );
    }

    handler = OPEN_CFW_SPOTMGR_INIT_READ_HANDLER(
        OPEN_CFW_SPOTMGR_INIT_SLOT_INIT
    );
    if (handler != 0U) {
        handler = OPEN_CFW_SPOTMGR_INIT_READ_HANDLER(
            OPEN_CFW_SPOTMGR_INIT_SLOT_INIT
        );
        return OPEN_CFW_SPOTMGR_INIT_CALL_HANDLER(handler);
    }

    return 0U;
}

