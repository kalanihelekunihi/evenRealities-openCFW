//*****************************************************************************
//
//! @file am_hal_iom.c
//!
//! @brief Functions for interfacing with IO Master serial (SPI/I2C) modules.
//!
//! @addtogroup iom4_ap510 IOM - IO Master (SPI/I2C)
//! @ingroup apollo510_hal
//! @{
//!
//! Purpose: This module provides comprehensive functions for interfacing with
//! IO Master (IOM) modules on Apollo5 devices. It supports SPI and
//! I2C master communication, DMA transfers, command queue operations,
//! and interrupt handling for flexible serial master operations.
//!
//! @section iom_features Key Features
//!
//! 1. @b SPI @b Master: Full SPI master communication with configurable modes.
//! 2. @b I2C @b Master: I2C master communication with multiple clock speeds.
//! 3. @b DMA @b Transfers: High-speed DMA-based data transfer operations.
//! 4. @b Command @b Queue: Advanced command queue for complex transaction sequences.
//! 5. @b Interrupt @b Handling: Comprehensive interrupt management and status monitoring.
//! 6. @b Power @b Management: Power state control and state retention capabilities.
//!
//! @section iom_functionality Functionality
//!
//! - Initialize and configure IOM modules for SPI and I2C communication
//! - Perform blocking and non-blocking data transfers
//! - Manage DMA transfers with callback support
//! - Handle command queue operations and sequencing
//! - Support high-priority transaction processing
//! - Provide interrupt-driven operation with status monitoring
//! - Enable power management and state retention
//! - Support full-duplex SPI communication
//!
//! @section iom_usage Usage
//!
//! 1. Initialize IOM using am_hal_iom_initialize()
//! 2. Configure interface settings with am_hal_iom_configure()
//! 3. Enable IOM module with am_hal_iom_enable()
//! 4. Perform transfers using blocking or non-blocking functions
//! 5. Handle interrupts and manage power states as needed
//!
//! @section iom_configuration Configuration
//!
//! - @b Interface @b Modes: SPI and I2C master mode configurations
//! - @b Clock @b Management: Configurable clock sources and frequencies
//! - @b DMA @b Settings: Transfer control buffer and threshold configuration
//! - @b Command @b Queue: Configurable queue depth and entry management
//! - @b Interrupt @b Masking: Selective interrupt enable/disable control
//*****************************************************************************

//*****************************************************************************
//
// Copyright (c) 2026, Ambiq Micro, Inc.
// All rights reserved.
//
// Redistribution and use in source and binary forms, with or without
// modification, are permitted provided that the following conditions are met:
//
// 1. Redistributions of source code must retain the above copyright notice,
// this list of conditions and the following disclaimer.
//
// 2. Redistributions in binary form must reproduce the above copyright
// notice, this list of conditions and the following disclaimer in the
// documentation and/or other materials provided with the distribution.
//
// 3. Neither the name of the copyright holder nor the names of its
// contributors may be used to endorse or promote products derived from this
// software without specific prior written permission.
//
// THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
// AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
// IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
// ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
// LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
// CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
// SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
// INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
// CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
// ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
// POSSIBILITY OF SUCH DAMAGE.
//
// This is part of revision stable-add55ed0181 of the AmbiqSuite Development Package.
//
//*****************************************************************************

#include <stdint.h>
#include <stdbool.h>
#include "am_mcu_apollo.h"

#ifdef __IAR_SYSTEMS_ICC__
#define AM_INSTR_CLZ(n)                     __CLZ(n)
#else
#define AM_INSTR_CLZ(n)                     __builtin_clz(n)
#endif

#define MANUAL_POP  0

#define AM_HAL_MAGIC_IOM            0x123456
#define AM_HAL_IOM_CHK_HANDLE(h)    ((h) && ((am_hal_handle_prefix_t *)(h))->s.bInit && (((am_hal_handle_prefix_t *)(h))->s.magic == AM_HAL_MAGIC_IOM))

//*****************************************************************************
//
//! @name IOM Un/Pausing Selections
//! @{
//! For IOM - Need to clear the flag for unpausing
//
//*****************************************************************************
#define AM_HAL_IOM_SC_PAUSE_CQ         AM_HAL_IOM_SC_PAUSE(AM_HAL_IOM_PAUSE_FLAG_CQ)
#define AM_HAL_IOM_SC_PAUSE_SEQLOOP    AM_HAL_IOM_SC_PAUSE(AM_HAL_IOM_PAUSE_FLAG_SEQLOOP)
#define AM_HAL_IOM_SC_UNPAUSE_CQ       AM_HAL_IOM_SC_UNPAUSE(AM_HAL_IOM_PAUSE_FLAG_CQ)
#define AM_HAL_IOM_SC_UNPAUSE_SEQLOOP  AM_HAL_IOM_SC_UNPAUSE(AM_HAL_IOM_PAUSE_FLAG_SEQLOOP)
#define AM_HAL_IOM_SC_PAUSE_BLOCK      AM_HAL_IOM_SC_PAUSE(AM_HAL_IOM_PAUSE_FLAG_BLOCK)
#define AM_HAL_IOM_SC_UNPAUSE_BLOCK    AM_HAL_IOM_SC_UNPAUSE(AM_HAL_IOM_PAUSE_FLAG_BLOCK)
//! @}

//
//! Max time to wait when attempting to pause the command queue
//
#define AM_HAL_IOM_MAX_PAUSE_DELAY     (100*1000) // 100ms

//*****************************************************************************
//
//! @name IOM interface clock selections
//! @{
//
//*****************************************************************************
#define AM_REG_IOM_CLKCFG_FSEL_MIN_PWR               0x00000000
#define AM_REG_IOM_CLKCFG_FSEL_HFRC                  0x00000100
#define AM_REG_IOM_CLKCFG_FSEL_HFRC_DIV2             0x00000200
#define AM_REG_IOM_CLKCFG_FSEL_HFRC_DIV4             0x00000300
#define AM_REG_IOM_CLKCFG_FSEL_HFRC_DIV8             0x00000400
#define AM_REG_IOM_CLKCFG_FSEL_HFRC_DIV16            0x00000500
#define AM_REG_IOM_CLKCFG_FSEL_HFRC_DIV32            0x00000600
#define AM_REG_IOM_CLKCFG_FSEL_HFRC_DIV64            0x00000700
//! @}

//
// Only keep IOM interrupts we're interested in
//
// Necessary interrupts for respective modes
//! For CQ - we rely only on the CQUPD interrupt
#define AM_HAL_IOM_INT_CQMODE   (AM_HAL_IOM_INT_CQUPD | AM_HAL_IOM_INT_ERR)

//
//! Need both CMDCMP & DCMP, as for Read we need to wait for DCMP after CMDCMP
//
#define AM_HAL_IOM_INT_DMAMODE  (AM_HAL_IOM_INT_CMDCMP | AM_HAL_IOM_INT_DCMP | AM_HAL_IOM_INT_ERR)
#define AM_HAL_IOM_INT_FDNBMODE (AM_HAL_IOM_INT_THR    | AM_HAL_IOM_INT_DMAMODE)

//
//! Configures the interrupts to provided coniguration - clearing all pending interrupts
//
#define IOM_SET_INTEN(ui32Module, intCfg)                               \
    do                                                                  \
    {                                                                   \
        IOMn(ui32Module)->INTEN = 0;                                    \
        IOMn(ui32Module)->INTCLR = AM_HAL_IOM_INT_ALL;                  \
        IOMn(ui32Module)->INTEN = (intCfg);                             \
    } while (0);

//*****************************************************************************
//
// Private Types.
//
//*****************************************************************************

//
//! This is the max number of pins used per module
//
#define IOM_RESET_NUM_LW 3

//
//! This value is used to disable pin toggle
//
#define IOM_RESET_DO_NOT_TOGGLE 0xFFFF

//
//! struct used for passing in i2c pin numbers for AM_HAL_IOM_REQ_RESET
//! case in am_hal_iom_control()
//
typedef struct
{
    //
    //! The scl or sda pin number, used in I2C and SPI mode
    //
    uint32_t scl_sck_pin_number;

    //
    //! The sda or mosi pin number, used in I2C and SPI mode
    //
    uint32_t mosi_sda_pin_number;

    //
    //! The miso pin, this is used in SPI mode
    //
    uint32_t miso_pin_number;

}
am_hal_iom_pin_reset_t;

//
//! Command Queue entry structure.
//
typedef struct
{
    uint32_t    ui32PAUSENAddr;
    uint32_t    ui32PAUSEENVal;
    uint32_t    ui32PAUSEN2Addr;
    uint32_t    ui32PAUSEEN2Val;
    uint32_t    ui32OFFSETHIAddr;
    uint32_t    ui32OFFSETHIVal;
    uint32_t    ui32DEVCFGAddr;
    uint32_t    ui32DEVCFGVal;
    uint32_t    ui32DMACFGdis1Addr;
    uint32_t    ui32DMACFGdis1Val;
    uint32_t    ui32DMATOTCOUNTAddr;
    uint32_t    ui32DMATOTCOUNTVal;
    uint32_t    ui32DMATARGADDRAddr;
    uint32_t    ui32DMATARGADDRVal;
    uint32_t    ui32DMACFGAddr;
    uint32_t    ui32DMACFGVal;
    uint32_t    ui32DCXAddr;
    uint32_t    ui32DCXVal;
    uint32_t    ui32CMDAddr;
    uint32_t    ui32CMDVal;
    uint32_t    ui32SETCLRAddr;
    uint32_t    ui32SETCLRVal;
} am_hal_iom_txn_cmdlist_t;

//
//! Command Queue entry structure for Sequence Repeat
//
typedef struct
{
    uint32_t                    ui32PAUSENAddr;
    uint32_t                    ui32PAUSEENVal;
    uint32_t                    ui32PAUSEN2Addr;
    uint32_t                    ui32PAUSEEN2Val;
    uint32_t                    ui32SETCLRAddr;
    uint32_t                    ui32SETCLRVal;
} am_hal_iom_cq_loop_entry_t;

#ifndef AM_HAL_IOM_MAX_PENDING_TRANSACTIONS
#define AM_HAL_IOM_MAX_PENDING_TRANSACTIONS      (256) // Must be power of 2 for the implementation below
#endif
#define AM_HAL_IOM_CQUPD_INT_FLAG                (0x00000001)

//
//! IOM register State
//
typedef struct
{
    bool        bValid;
    uint32_t    regFIFOTHR;
    uint32_t    regDMATRIGEN;
    uint32_t    regCLKCFG;
    uint32_t    regSUBMODCTRL;
    uint32_t    regCQCFG;
    uint32_t    regCQADDR;
    uint32_t    regCQFLAGS;
    uint32_t    regCQPAUSEEN;
    uint32_t    regCQCURIDX;
    uint32_t    regCQENDIDX;
    uint32_t    regMSPICFG;
    uint32_t    regMI2CCFG;
    uint32_t    regINTEN;
} am_hal_iom_register_state_t;

//
//! IOM Sequence State
//
typedef enum
{
    AM_HAL_IOM_SEQ_NONE,
    AM_HAL_IOM_SEQ_UNDER_CONSTRUCTION,
    AM_HAL_IOM_SEQ_RUNNING,
} am_hal_iom_seq_e;

//
//! IOM DMA Entry Info
//
typedef struct
{
    uint32_t                    ui32OFFSETHIVal;
    uint32_t                    ui32DEVCFGVal;
    uint32_t                    ui32DMATOTCOUNTVal;
    uint32_t                    ui32DMATARGADDRVal;
    uint32_t                    ui32DMACFGVal;
    uint32_t                    ui32CMDVal;
    am_hal_iom_callback_t       pfnCallback;
    void                        *pCallbackCtxt;
} am_hal_iom_dma_entry_t;

typedef struct
{
    bool                        bActive;
    uint8_t                     *pui8RxBuf;
    uint32_t                    ui32RxBytesLeft;
    uint32_t                    ui32SavedIntCfg;
    uint32_t                    ui32SavedDmaTrigEn;
    am_hal_iom_callback_t       pfnCallback;
    void                        *pCallbackCtxt;
} am_hal_iom_fdnb_state_t;

//
//! IOM State
//
typedef struct
{
    am_hal_handle_prefix_t  prefix;

    //
    //! Physical module number.
    //
    uint32_t                ui32Module;

    //
    //! Interface mode (SPI or I2C).
    //
    am_hal_iom_mode_e       eInterfaceMode;

    //
    //! Non-Blocking transaction Tranfer Control Buffer.
    //
    uint32_t                *pNBTxnBuf;
    uint32_t                ui32NBTxnBufLength;

    //
    //! Saves the user application defined interrupt configuration.
    //
    uint32_t                ui32UserIntCfg;

    //
    //! Saves the transaction interrupt state for non-blocking interrupt service.
    //
    uint32_t                ui32TxnInt;

    //
    //! Index of last non-blocking transaction processed in CQ.
    //
    uint32_t                ui32LastIdxProcessed;

    //
    //! Maximum number of transactions allowed in the CQ.
    //
    uint32_t                ui32MaxTransactions;

    //
    //! Number of pending transactions in the CQ.
    //
    volatile uint32_t       ui32NumPendTransactions;

    //
    //! Stores the CQ callbacks and contexts.
    //
    am_hal_iom_callback_t   pfnCallback[AM_HAL_IOM_MAX_PENDING_TRANSACTIONS];
    void                    *pCallbackCtxt[AM_HAL_IOM_MAX_PENDING_TRANSACTIONS];

    //
    //! Handle to the CQ.
    //
    void                    *pCmdQHdl;

    //
    //! To support sequence.
    //
    am_hal_iom_seq_e        eSeq;
    bool                    bAutonomous;

    //
    //! This is used to track the number of transactions in a sequence.
    //
    uint32_t                ui32NumSeqTransactions;
    volatile bool           bRestart;
    uint32_t                block;

    //
    //! To support high priority transactions - out of band
    //! High Priority DMA transactions
    //
    volatile bool           bHP;

    uint32_t                ui32NumHPEntries;
    uint32_t                ui32NumHPPendingEntries;
    uint32_t                ui32MaxHPTransactions;
    uint32_t                ui32NextHPIdx;
    uint32_t                ui32LastHPIdxProcessed;
    am_hal_iom_dma_entry_t  *pHPTransactions;

    //
    //! Max pending transactions based on NB Buffer size
    //
    uint32_t                ui32MaxPending;

    //
    //! Number of back to back transactions with no callbacks
    //
    uint32_t                ui32NumUnSolicited;

    //
    //! Delay timeout value.
    //
    uint32_t                waitTimeout;

    //
    //! Configured clock time.
    //
    uint32_t                ui32BitTimeUs;

    //
    //! IOM register state for power down save/restore.
    //
    am_hal_iom_register_state_t registerState;

    //
    //! DCX state.
    //
    uint8_t                 dcx[AM_HAL_IOM_MAX_CS_SPI];

    //
    //! Full-duplex non-blocking SPI (TX DMA + RX FIFO/IRQ) state.
    //
    am_hal_iom_fdnb_state_t sFdNb;

    bool                    bCmdQInTCM;

} am_hal_iom_state_t;

//*****************************************************************************
//
// pin locator utilities
//
//*****************************************************************************

typedef struct
{
    uint16_t pn_scl;
    uint16_t pn_sck;
    uint16_t pn_sda;
    uint16_t pn_mosi;
    uint16_t pn_miso;
}
am_hal_iom_pin_allocations_t;

//*****************************************************************************
//
// This will map the IOM channel with the pins that can be assigned.
// For apollo4p there is only one pin that can be assigned
// for each IOM function.
//
//*****************************************************************************
static const am_hal_iom_pin_allocations_t tIomPinAlloc[] =
{
    [0] =
    {
        .pn_scl  = (5 << 4) | AM_HAL_PIN_5_M0SCL,
        .pn_sck  = (5 << 4) | AM_HAL_PIN_5_M0SCK,
        .pn_sda  = (6 << 4) | AM_HAL_PIN_6_M0SDAWIR3,
        .pn_mosi = (6 << 4) | AM_HAL_PIN_6_M0MOSI,
        .pn_miso = (7 << 4) | AM_HAL_PIN_7_M0MISO,
    },
    [1] =
    {
        .pn_scl  = (8 << 4)  | AM_HAL_PIN_8_M1SCL,
        .pn_sck  = (8 << 4)  | AM_HAL_PIN_8_M1SCK,
        .pn_sda  = (9 << 4)  | AM_HAL_PIN_9_M1SDAWIR3,
        .pn_mosi = (9 << 4)  | AM_HAL_PIN_9_M1MOSI,
        .pn_miso = (10 << 4) | AM_HAL_PIN_10_M1MISO,
    },
    [2] =
    {
        .pn_scl  = (25 << 4) | AM_HAL_PIN_25_M2SCL,
        .pn_sck  = (25 << 4) | AM_HAL_PIN_25_M2SCK,
        .pn_sda  = (26 << 4) | AM_HAL_PIN_26_M2SDAWIR3,
        .pn_mosi = (26 << 4) | AM_HAL_PIN_26_M2MOSI,
        .pn_miso = (27 << 4) | AM_HAL_PIN_27_M2MISO
    },
    [3] =
    {
        .pn_scl  = (31 << 4) | AM_HAL_PIN_31_M3SCL,
        .pn_sck  = (31 << 4) | AM_HAL_PIN_31_M3SCK,
        .pn_sda  = (32 << 4) | AM_HAL_PIN_32_M3SDAWIR3,
        .pn_mosi = (32 << 4) | AM_HAL_PIN_32_M3MOSI,
        .pn_miso = (33 << 4) | AM_HAL_PIN_33_M3MISO,
    },
    [4] =
    {
        .pn_scl  = (34 << 4) | AM_HAL_PIN_34_M4SCL,
        .pn_sck  = (34 << 4) | AM_HAL_PIN_34_M4SCK,
        .pn_sda  = (35 << 4) | AM_HAL_PIN_35_M4SDAWIR3,
        .pn_mosi = (35 << 4) | AM_HAL_PIN_35_M4MOSI,
        .pn_miso = (36 << 4) | AM_HAL_PIN_36_M4MISO,
    },
    [5] =
    {
        .pn_scl  = (47 << 4) | AM_HAL_PIN_47_M5SCL,
        .pn_sck  = (47 << 4) | AM_HAL_PIN_47_M5SCK,
        .pn_sda  = (48 << 4) | AM_HAL_PIN_48_M5SDAWIR3,
        .pn_mosi = (48 << 4) | AM_HAL_PIN_48_M5MOSI,
        .pn_miso = (49 << 4) | AM_HAL_PIN_49_M5MISO,
    },
    [6] =
    {
        .pn_scl  = (61 << 4) | AM_HAL_PIN_61_M6SCL,
        .pn_sck  = (61 << 4) | AM_HAL_PIN_61_M6SCK,
        .pn_sda  = (62 << 4) | AM_HAL_PIN_62_M6SDAWIR3,
        .pn_mosi = (62 << 4) | AM_HAL_PIN_62_M6MOSI,
        .pn_miso = (63 << 4) | AM_HAL_PIN_63_M6MISO,
    },
    [7] =
    {
        .pn_scl  = (22 << 4) | AM_HAL_PIN_22_M7SCL,
        .pn_sck  = (22 << 4) | AM_HAL_PIN_22_M7SCK,
        .pn_sda  = (23 << 4) | AM_HAL_PIN_23_M7SDAWIR3,
        .pn_mosi = (23 << 4) | AM_HAL_PIN_23_M7MOSI,
        .pn_miso = (24 << 4) | AM_HAL_PIN_24_M7MISO,
    },
};

#define FSELMAX 10  // This is used freq divider computation the highest value that can be used is 8
#define FSEL_MAX_REGISTER_VAL 8

//
//! Clock divider table
//
static const uint32_t ui32FselClockLookup[FSELMAX] = {
    375000,  // this is actally the location of 375,000
    0,  // this is off
    48000000,  // 2
    24000000,
    12000000,
    6000000,
    3000000,
    1500000,  // 7
    750000,  // 8
    375000,  // 9, this is used in the divider selection loop, entry 9 doesn't exist in the actual register
};

//
//! return value from clock comparator
//
typedef enum
{
    eLEFT,
    eRIGHT,
}
iom_ab_chooser_e;

//
//! frequency calc return codes
//
typedef enum
{
    eFREQ_ERROR_NO_ERROR,
    eUSE_LOWER_BASE_FREQ_WARNING,
    eREQ_FREQ_TOO_HIGH_WARNING,

} iom_freq_calc_errors;
//
//! define fixed-point duty cycle scaling at 1024 , so 512 is 50%
//
#define DUTY_CYCLE_SCALING 1024

//
//! Parameters use din clock divider search
//
typedef struct
{
    uint32_t ui32Phase;          //!< Phase bias when exact 50% duty is not achievable (0 = longer low, 1 = longer high)

    uint32_t ui32Fsel;           //!< FSEL (2 - 7): base clock selector (e.g., FSEL=2 for 48MHz)
    uint32_t ui32Div3;           //!< Set to 1 to divide base clock by 3 before TOTPER logic
    uint32_t ui32DivEn;          //!< Set to 1 to enable TOTPER-based division; 0 = bypass (simple divide by 1 or 3)

    uint32_t ui32TotPer;         //!< TOTPER register value (TOTPER + 1) = total waveform period in cycles)
    uint32_t ui32LowPer;         //!< Lower +1 is the low cycle count, must be less than TOTPER
    uint32_t ui32OutClock;       //!< Output frequency in Hz, based on the current parameters

    int32_t  ui32DC_1024;        //!< Duty cycle scaled by 1024 (e.g., 512 = 50%, 768 = 75%)
    int32_t  ui32DC_deviation;   //!< Absolute deviation from 50% duty cycle (in 1/1024 units)

    uint32_t ui32DesiredFreq;    //!< User-requested target frequency in Hz
    int32_t  i32Diff;            //!< Signed difference between actual and desired frequency (Hz)
    uint32_t ui32AbsDiff;        //!< Absolute frequency error (Hz)

    iom_freq_calc_errors  eErrors; //!< Errors encountered during Freq computations

    am_hal_iom_clock_sel_priority_e eClockSelPriority; //!< Selection strategy (freq match, symmetry, or hybrid)
}
iom_clock_comp_parms_t;

static void iom_compute_freq_helper(iom_clock_comp_parms_t* pcp);
static iom_ab_chooser_e compare_lr(iom_clock_comp_parms_t *left, iom_clock_comp_parms_t *right);
static iom_clock_comp_parms_t *compare_div1_3(iom_clock_comp_parms_t *psDiv1L, iom_clock_comp_parms_t *psDiv3R);
static uint32_t iom_compute_freq_cp( iom_clock_comp_parms_t *pcp);
static int32_t iom_clock_selector(iom_clock_comp_parms_t *psClockL);

//*****************************************************************************
//
// Globals
//
//*****************************************************************************
am_hal_iom_state_t          g_IOMhandles[AM_REG_IOM_NUM_MODULES];

//*****************************************************************************
//
// Internal Functions.
//
//*****************************************************************************

//*****************************************************************************
//
//! @brief Get IOM pause value based on current block state.
//!
//! @param pIOMState - Pointer to IOM state structure.
//! @param pause - Pause value to process.
//!
//! @return Returns the processed pause value.
//!
//*****************************************************************************
static uint32_t
get_pause_val(am_hal_iom_state_t *pIOMState, uint32_t pause)
{
    uint32_t retval;
    switch (pIOMState->block)
    {
        case 1:
            //
            // Pause the CQ till the whole block is built
            //
            retval = pause | AM_HAL_IOM_CQP_PAUSE_DEFAULT | AM_HAL_IOM_PAUSE_FLAG_BLOCK;
            pIOMState->block = 2;
            break;
        case 2:
            //
            // No pausing allowed
            //
            retval = AM_HAL_IOM_PAUSE_DEFAULT;
            break;
        default: // case 0
            retval = pause | AM_HAL_IOM_CQP_PAUSE_DEFAULT;
    }
    return retval;
}

//*****************************************************************************
//
//! @brief Build the IOM CMD value.
//!
//! @param ui32CS - Chip select value.
//! @param ui32Dir - Transfer direction.
//! @param ui32Cont - Continue flag.
//! @param ui64Offset - Offset value.
//! @param ui32OffsetCnt - Offset count.
//! @param ui32nBytes - Number of bytes to transfer.
//!
//! @return Returns the built CMD value.
//!
//! @note The OFFSETHI register must still be handled by the caller, e.g.
//!       AM_REGn(IOM, ui32Module, OFFSETHI) = (uint32_t)(ui32Offset >> 8);
//!
//*****************************************************************************
static uint32_t
build_cmd(uint32_t ui32CS,     uint32_t ui32Dir, uint32_t ui32Cont,
          uint64_t ui64Offset, uint32_t ui32OffsetCnt,
          uint32_t ui32nBytes)
{
    //
    // Initialize the CMD variable
    //
    uint32_t ui32Cmd = 0;

    //
    // If SPI, we'll need the chip select
    //
    ui32Cmd |= _VAL2FLD(IOM0_CMD_CMDSEL, ui32CS);

    //
    // Build the CMD with number of bytes and direction.
    //
    ui32Cmd |= _VAL2FLD(IOM0_CMD_TSIZE, ui32nBytes);

    if (ui32Dir == AM_HAL_IOM_RX)
    {
        ui32Cmd |= _VAL2FLD(IOM0_CMD_CMD, IOM0_CMD_CMD_READ);
    }
    else
    {
        ui32Cmd |= _VAL2FLD(IOM0_CMD_CMD, IOM0_CMD_CMD_WRITE);
    }

    ui32Cmd |= _VAL2FLD(IOM0_CMD_CONT, ui32Cont);

    //
    // Now add the OFFSETLO and OFFSETCNT information.
    //
    ui32Cmd |= _VAL2FLD(IOM0_CMD_OFFSETLO, (uint8_t)ui64Offset);
    ui32Cmd |= _VAL2FLD(IOM0_CMD_OFFSETCNT, ui32OffsetCnt);

    return ui32Cmd;
} // build_cmd()

//*****************************************************************************
//
//! @brief Build command list for IOM transaction.
//!
//! @param pIOMState - Pointer to IOM state structure.
//! @param pCQEntry - Pointer to command queue entry.
//! @param psTransaction - Pointer to transaction structure.
//!
//*****************************************************************************
static void
build_txn_cmdlist(am_hal_iom_state_t       *pIOMState,
                  am_hal_iom_txn_cmdlist_t *pCQEntry,
                  am_hal_iom_transfer_t    *psTransaction)
{
    uint32_t                ui32Cmd;
    uint32_t                ui32Module = pIOMState->ui32Module;
    uint32_t                ui32Dir = psTransaction->eDirection;
    uint32_t                ui32SRAMAddress;

    //
    // Command for OFFSETHI
    //
    pCQEntry->ui32OFFSETHIAddr  = (uint32_t)&IOMn(ui32Module)->OFFSETHI;

    pCQEntry->ui32OFFSETHIVal   = (uint32_t)(psTransaction->ui64Instr >> 8);

    //
    // Command for I2C DEVADDR field in DEVCFG
    //
    pCQEntry->ui32DEVCFGAddr    = (uint32_t)&IOMn(ui32Module)->DEVCFG;
    pCQEntry->ui32DEVCFGVal     = _VAL2FLD(IOM0_DEVCFG_DEVADDR, psTransaction->uPeerInfo.ui32I2CDevAddr);

    //
    // Command to disable DMA before writing TOTCOUNT.
    //
    pCQEntry->ui32DMACFGdis1Addr   = (uint32_t)&IOMn(ui32Module)->DMACFG;
    pCQEntry->ui32DMACFGdis1Val    = 0x0;

    //
    // Command to set DMATOTALCOUNT
    //
    pCQEntry->ui32DMATOTCOUNTAddr = (uint32_t)&IOMn(ui32Module)->DMATOTCOUNT;
    pCQEntry->ui32DMATOTCOUNTVal  = psTransaction->ui32NumBytes;

    //
    // Command to set DMATARGADDR
    //
    pCQEntry->ui32DMATARGADDRAddr = (uint32_t)&IOMn(ui32Module)->DMATARGADDR;
    ui32SRAMAddress = (ui32Dir == AM_HAL_IOM_TX) ? (uint32_t)psTransaction->pui32TxBuffer : (uint32_t)psTransaction->pui32RxBuffer;
    pCQEntry->ui32DMATARGADDRVal  = ui32SRAMAddress;

    //
    // Command to set DMACFG to start the DMA operation
    //
    pCQEntry->ui32DMACFGAddr    = (uint32_t)&IOMn(ui32Module)->DMACFG;
    pCQEntry->ui32DMACFGVal     =
        _VAL2FLD(IOM0_DMACFG_DMAPRI, psTransaction->ui8Priority)     |
        _VAL2FLD(IOM0_DMACFG_DMADIR, ui32Dir == AM_HAL_IOM_TX ? 1 : 0);

    if (psTransaction->ui32NumBytes)
    {
        pCQEntry->ui32DMACFGVal |= IOM0_DMACFG_DMAEN_Msk;
    }

    pCQEntry->ui32DCXAddr = (uint32_t)&IOMn(ui32Module)->DCXCTRL;
    pCQEntry->ui32DCXVal = (pIOMState->eInterfaceMode == AM_HAL_IOM_SPI_MODE)  ? pIOMState->dcx[psTransaction->uPeerInfo.ui32SpiChipSelect] : 0;

    //
    // Command to start the transfer.
    //
    ui32Cmd = pIOMState->eInterfaceMode == AM_HAL_IOM_SPI_MODE  ?
              psTransaction->uPeerInfo.ui32SpiChipSelect : 0;
    ui32Cmd = build_cmd(ui32Cmd,                            // ChipSelect
                        ui32Dir,          // ui32Dir
                        psTransaction->bContinue,           // ui32Cont
                        psTransaction->ui64Instr,           // ui64Offset
                        psTransaction->ui32InstrLen,        // ui32OffsetCnt
                        psTransaction->ui32NumBytes);  // ui32Bytes

    pCQEntry->ui32CMDAddr  = (uint32_t)&IOMn(ui32Module)->CMD;
    pCQEntry->ui32CMDVal   = ui32Cmd;

    pCQEntry->ui32PAUSENAddr = pCQEntry->ui32PAUSEN2Addr = (uint32_t)&IOMn(ui32Module)->CQPAUSEEN;
    pCQEntry->ui32PAUSEEN2Val = AM_HAL_IOM_PAUSE_DEFAULT;
    pCQEntry->ui32PAUSEENVal = get_pause_val(pIOMState, psTransaction->ui32PauseCondition);
    pCQEntry->ui32SETCLRVal = psTransaction->ui32StatusSetClr;
    pCQEntry->ui32SETCLRAddr = (uint32_t)&IOMn(ui32Module)->CQSETCLEAR;

} // build_txn_cmdlist()

static bool
disable_submodule(uint32_t ui32Module, uint32_t ui32Type)
{
    if ( IOMn(ui32Module)->SUBMODCTRL_b.SMOD0TYPE == ui32Type )
    {
        IOMn(ui32Module)->SUBMODCTRL = _VAL2FLD(IOM0_SUBMODCTRL_SMOD0EN, 0);
    }
    else if ( IOMn(ui32Module)->SUBMODCTRL_b.SMOD1TYPE == ui32Type )
    {
        IOMn(ui32Module)->SUBMODCTRL = _VAL2FLD(IOM0_SUBMODCTRL_SMOD1EN, 0);
    }
    else
    {
        return false;
    }

    return true;
} // disable_submodule()

//*****************************************************************************
//
//! @brief Enable IOM submodule.
//!
//! @param ui32Module - IOM module number.
//! @param ui32Type - Submodule type (0 for SPI, 1 for I2C).
//!
//! @return Returns true if the submodule was enabled or false otherwise.
//!
//*****************************************************************************
static bool
enable_submodule(uint32_t ui32Module, uint32_t ui32Type)
{
    if ( IOMn(ui32Module)->SUBMODCTRL_b.SMOD0TYPE == ui32Type )
    {
        IOMn(ui32Module)->SUBMODCTRL = _VAL2FLD(IOM0_SUBMODCTRL_SMOD0EN, 1);
    }
    else if ( IOMn(ui32Module)->SUBMODCTRL_b.SMOD1TYPE == ui32Type )
    {
        IOMn(ui32Module)->SUBMODCTRL = _VAL2FLD(IOM0_SUBMODCTRL_SMOD1EN, 1);
    }
    else
    {
        return false;
    }

    return true;
} // enable_submodule()

//*****************************************************************************
//
//! @brief Given a pin number/assignment value
//!
//! @param pinVal - This will determine if a pin is allocated to the
//!   associated IOM if a pin is not allocated as expected,
//!   it is disabled with 0xFFFF
//!
//! @return pinVal - will return the pin-number or 0xFFFF (if pin is not in use)
//
//*****************************************************************************
static uint32_t
internal_iom_lookup_function(uint16_t pinVal)
{
    uint32_t ui32PinNumRef = pinVal >> 4;
    uint32_t ui32FcnSel    = pinVal & 0xF;
    volatile uint32_t *pui32Config = &GPIO->PINCFG0;

    am_hal_gpio_pincfg_t sGpioCfg;

    sGpioCfg.GP.cfg = pui32Config[ui32PinNumRef];

    if (sGpioCfg.GP.cfg_b.uFuncSel == ui32FcnSel)
    {
        //
        // found it
        //
        return ui32PinNumRef;
    }

    return IOM_RESET_DO_NOT_TOGGLE;
}

//*****************************************************************************
//
//! @brief this will find all pins associated with the given IOM
//!
//! @param ui32IomNumber iom number
//! @param pIomPinMap    returns pin map here, allocate at least three
//! @param bIsSPI        true if in SPI mode
//
//*****************************************************************************
static void
internal_iom_find_pins(uint32_t ui32IomNumber, am_hal_iom_pin_reset_t *pIomPinMap, bool bIsSPI)
{
    const am_hal_iom_pin_allocations_t *pPinMap = &tIomPinAlloc[ui32IomNumber];

    if (bIsSPI)
    {
        //
        // spi mode
        //
        pIomPinMap->scl_sck_pin_number  = internal_iom_lookup_function(pPinMap->pn_sck);
        pIomPinMap->mosi_sda_pin_number = internal_iom_lookup_function(pPinMap->pn_mosi);
        pIomPinMap->miso_pin_number     = internal_iom_lookup_function(pPinMap->pn_miso);
    }
    else
    {
        //
        // i2c mode
        //
        // miso is not used, so it is disabled
        //
        pIomPinMap->miso_pin_number     = IOM_RESET_DO_NOT_TOGGLE;
        pIomPinMap->scl_sck_pin_number  = internal_iom_lookup_function(pPinMap->pn_scl);
        pIomPinMap->mosi_sda_pin_number = internal_iom_lookup_function(pPinMap->pn_sda);
    }
}

//*****************************************************************************
//
//! @brief Error handling., push write
//! @note will write remaining tx bytes (dummy bytes) into IOM tx fifo so transfer
//!       will complete
//!
//! @param pIOMState pointer to handle
//! @param i32NumBytesRemaining number of bytes remaining.
//!                             If this is less than one nothing will happen
//!
//! @return AM_HAL_STATUS_SUCCESS
//! @return AM_HAL_STATUS_TIMEOUT
//
//*****************************************************************************
static void
internal_iom_reset_iom_pins(am_hal_iom_state_t *pIOMState)
{
    struct sSavedPcfg
    {
        am_hal_gpio_pincfg_t tPinCfg;
        bool bPinValid;
    }
    sSavedPinCfg[IOM_RESET_NUM_LW];

    am_hal_iom_pin_reset_t tIomPinMap = { 0 };
    uint32_t *pui32_PinNum = 0;
    uint32_t ui32UsToWait = 6 * (pIOMState->ui32BitTimeUs ? pIOMState->ui32BitTimeUs : 1); // effectively > 6 clocks
    uint32_t ui32Module = pIOMState->ui32Module;

    //
    // This will toggle the pins to release the hang, then reset the module
    // if not, will only try to reset the module
    //
    // clear this error with a pin function toggle to and back from GPIO with pullups enabled
    //

    internal_iom_find_pins(ui32Module, &tIomPinMap, pIOMState->eInterfaceMode == AM_HAL_IOM_SPI_MODE);

    //
    // clear this error with a pin function toggle to and back from GPIO with pullups enabled
    //
    if (pIOMState->eInterfaceMode != AM_HAL_IOM_I2C_MODE)
    {
        //
        // in i2c mode there is no miso pin, so deactivate it
        //
        tIomPinMap.miso_pin_number = IOM_RESET_DO_NOT_TOGGLE;
    }

    pui32_PinNum = (uint32_t *)&tIomPinMap;

    for (uint32_t i = 0; i < IOM_RESET_NUM_LW; i++)
    {
        uint32_t ui32pn = pui32_PinNum[i];

        //
        // for Apollo4, the IOM does not use PIN 0
        //
        sSavedPinCfg[i].bPinValid = (ui32pn > 0) && (ui32pn < AM_HAL_GPIO_MAX_PADS);

        if (sSavedPinCfg[i].bPinValid)
        {
            //
            // this pin is being used, save current pin config
            //
            am_hal_gpio_pinconfig_get(ui32pn, &sSavedPinCfg[i].tPinCfg);

            //
            // disable pin (I2C) mode, leave pullups on
            //
            am_hal_gpio_pinconfig(ui32pn, am_hal_gpio_pincfg_pulledup_disabled);
        }
    }

    //
    // Wait for few IO clock cycles
    //
    am_hal_delay_us(ui32UsToWait);

    //
    // Restore pin config
    //
    for (uint32_t i = 0; i < IOM_RESET_NUM_LW; i++)
    {
        if (sSavedPinCfg[i].bPinValid)
        {
            am_hal_gpio_pinconfig(pui32_PinNum[i], sSavedPinCfg[i].tPinCfg);
        }
    }
}

//*****************************************************************************
//
//! @brief Compute I2C transfer delay based on bit rate and number of bytes
//!
//! @param pIOMState
//! @param ui32NumBytes
//!
//! @return  delay time in microseconds
//
// *****************************************************************************
static uint32_t
internal_iom_compute_transfer_delay(am_hal_iom_state_t *pIOMState,
                                    uint32_t ui32NumBytes)
{
    //
    // use 10 bits per byte of transfer
    //   and a factor of 2 for margin of safety
    //
    uint32_t ui32TransferTimeUs = pIOMState->ui32BitTimeUs * 2 * 10 * ui32NumBytes;

    if ( ui32TransferTimeUs < 1 )
    {
        ui32TransferTimeUs = 1;
    }

    return ui32TransferTimeUs;
}

//*****************************************************************************
//
//! @brief Error handling, push write
//! @note will write remaining tx bytes (dummy bytes) into IOM tx fifo so transfer
//!       will complete
//!
//! @param pIOMState pointer to handle
//! @param i32NumBytesRemaining number of bytes remaining. If this is less than one
//!                 nothing will happen
//!
//! @return AM_HAL_STATUS_SUCCESS
//! @return AM_HAL_STATUS_TIMEOUT
//
//*****************************************************************************
static uint32_t
internal_iom_finish_buffer_write(am_hal_iom_state_t *pIOMState,
                                 int32_t i32NumBytesRemaining)
{
    uint32_t ui32RetStat = AM_HAL_STATUS_SUCCESS;

    if (i32NumBytesRemaining > 0)
    {
        uint32_t ui32dummy      = 0xDEADBEEF;
        uint32_t ui32Module = pIOMState->ui32Module;
        uint32_t ui32TimeoutCount = 0;

        //
        // compute max time to wait for tx
        //
        uint32_t ui32WaitUs = internal_iom_compute_transfer_delay(pIOMState,
                                                       i32NumBytesRemaining);

        while (i32NumBytesRemaining > 0)
        {
            while (IOMn(ui32Module)->FIFOPTR_b.FIFO0REM >= 4)
            {
                //
                // Write one 4-byte word to FIFO
                //
                IOMn(ui32Module)->FIFOPUSH = ui32dummy;
                if (i32NumBytesRemaining <= 4)
                {
                    break;
                }
                i32NumBytesRemaining -= 4;
            }
            if (++ui32TimeoutCount > ui32WaitUs)
            {
                return AM_HAL_STATUS_TIMEOUT;
            }
            am_hal_delay_us(1);
        }

        //
        // wait for fifo to empty
        //
        ui32WaitUs = internal_iom_compute_transfer_delay(pIOMState, AM_HAL_IOM_FIFO_SIZE_MAX);
        ui32TimeoutCount = 0;

        while (IOMn(ui32Module)->FIFOPTR_b.FIFO0SIZ)
        {
            am_hal_delay_us(1);

            if (++ui32TimeoutCount > ui32WaitUs)
            {
                ui32RetStat = AM_HAL_STATUS_TIMEOUT;
                break;
            }
        }
    } // i32NumBytesRemaining

    return ui32RetStat;
}

//*****************************************************************************
//
// Error handling.
//
//*****************************************************************************
uint32_t
internal_iom_get_int_err(uint32_t ui32Module, uint32_t ui32IntStatus)
{
    //
    // Map the INTSTAT bits for transaction status
    //
    uint32_t ui32Status = AM_HAL_STATUS_SUCCESS;

    //
    // Let's accumulate the errors
    //
    ui32IntStatus |= IOMn(ui32Module)->INTSTAT;

    if (ui32IntStatus & AM_HAL_IOM_INT_SWERR)
    {
        //
        // Error in hardware command issued or illegal access by SW
        //
        ui32Status = AM_HAL_IOM_ERR_INVALID_OPER;
    }
    else if (ui32IntStatus & AM_HAL_IOM_INT_I2CARBERR)
    {
        //
        // Loss of I2C multi-master arbitration
        //
        ui32Status = AM_HAL_IOM_ERR_I2C_ARB;
    }
    else if (ui32IntStatus & AM_HAL_IOM_INT_NAK)
    {
        //
        // I2C NAK
        //
        ui32Status = AM_HAL_IOM_ERR_I2C_NAK;
    }
    else if (ui32IntStatus & AM_HAL_IOM_INT_INTERR)
    {
        //
        // Other Error
        //
        ui32Status = AM_HAL_STATUS_FAIL;
    }

    return ui32Status;
} // internal_iom_get_int_err()

static uint32_t
internal_iom_error_reset_disable_submodule(am_hal_iom_state_t  *pIOMState)
{
    struct sSavedPcfg
    {
        am_hal_gpio_pincfg_t tPinCfg;
        bool bPinValid;
    } sSavedPinCfg[IOM_RESET_NUM_LW];

    uint32_t ui32Module = pIOMState->ui32Module;
    am_hal_iom_pin_reset_t tIomPinMap = { 0 };
    uint32_t *pui32_PinNum = 0;

    //
    // Set to minimum 6+ clocks
    //
    uint32_t ui32UsToWait = 6 * (pIOMState->ui32BitTimeUs ? pIOMState->ui32BitTimeUs : 1);

    //
    // Save off IOMDBG
    //
    uint32_t ui32IomDbg = IOMn(ui32Module)->IOMDBG;

    //
    // Check for Idle
    //
    (void)am_hal_delay_us_status_check(AM_HAL_IOM_MAX_BLOCKING_WAIT,
                  (uint32_t) &IOMn(ui32Module)->STATUS,
                  (IOM0_STATUS_IDLEST_Msk | IOM0_STATUS_CMDACT_Msk),
                  IOM0_STATUS_IDLEST_Msk,
                  true);
    //
    // find pin map for this IOM channel
    //
    internal_iom_find_pins(ui32Module, &tIomPinMap, pIOMState->eInterfaceMode == AM_HAL_IOM_SPI_MODE);

    //
    // clear this error with a pin function toggle to and back from GPIO with pullups enabled
    //
    if (pIOMState->eInterfaceMode != AM_HAL_IOM_I2C_MODE)
    {
        //
        // in i2c mode there is no miso pin, so deactivate it
        //
        tIomPinMap.miso_pin_number = IOM_RESET_DO_NOT_TOGGLE;
    }

    pui32_PinNum = (uint32_t *)&tIomPinMap;

    for (uint32_t i = 0; i < IOM_RESET_NUM_LW; i++)
    {
        uint32_t ui32pn = pui32_PinNum[i];

        //
        // for Apollo4, the IOM does not use PIN 0
        //
        sSavedPinCfg[i].bPinValid = (ui32pn > 0) && (ui32pn < AM_HAL_GPIO_MAX_PADS);

        if (sSavedPinCfg[i].bPinValid)
        {
            //
            // this pin is being used, save current pin config
            //
            am_hal_gpio_pinconfig_get(ui32pn, &sSavedPinCfg[i].tPinCfg);

            //
            // disable pin (I2C) mode, leave pullups on
            //
            am_hal_gpio_pinconfig(ui32pn, am_hal_gpio_pincfg_pulledup_disabled);
        }
    }

    //
    // Reset Submodule & FIFO
    //
    // Disable the submodules
    //
    if (!disable_submodule(ui32Module, ((pIOMState->eInterfaceMode == AM_HAL_IOM_SPI_MODE) ? 0 : 1)))
    {
        return AM_HAL_STATUS_HW_ERR;
    }

    //
    // Reset Fifo
    //
    IOMn(ui32Module)->FIFOCTRL_b.FIFORSTN = 0;

    //
    // Disable Clock gating
    //
    IOMn(ui32Module)->IOMDBG |= IOM0_IOMDBG_IOCLKON_Msk;

    //
    // Wait for few IO clock cycles
    //
    am_hal_delay_us(ui32UsToWait);

    //
    // Restore pin config
    //
    for (uint32_t i = 0; i < IOM_RESET_NUM_LW; i++)
    {
        if (sSavedPinCfg[i].bPinValid)
        {
            am_hal_gpio_pinconfig(pui32_PinNum[i], sSavedPinCfg[i].tPinCfg);
        }
    }

    //
    // Revert IOMDBG
    //
    IOMn(ui32Module)->IOMDBG = ui32IomDbg;

    IOMn(ui32Module)->FIFOCTRL_b.FIFORSTN = 1;

    if (!enable_submodule(ui32Module, ((pIOMState->eInterfaceMode == AM_HAL_IOM_SPI_MODE) ? 0 : 1)))
    {
        return AM_HAL_STATUS_HW_ERR;
    }

    return AM_HAL_STATUS_SUCCESS;
}

#define READ_FIFO_TIMEOUT_RST1 50000

//*****************************************************************************
//
//! @brief Error handling., reset cmd busy error (i2c hung)
//! @note it is assumed IOM interrupts are disabled before calling this fcn.
//!
//! @param pIOMState iom handle
//!
//! @return AM_HAL_STATUS_INVALID_ARG when invalid input
//! @return AM_HAL_STATUS_SUCCESS when reset was successful
//! @return AM_HAL_STATUS_HW_ERR when reset was not successful
//
//*****************************************************************************
static uint32_t
internal_iom_reset_cmd_busy(am_hal_iom_state_t *pIOMState)
{
    uint32_t ui32Module = pIOMState->ui32Module;
    //
    // now the transfer should run to completion, wait for it to end
    // may need to help the transfer finish, by pushing tx bytes and/or
    // reading the rx fifo
    //
    uint32_t ui32TimeoutCount = 0;
    //
    // find if transmit or rx is pending
    //
    uint32_t ui32CmdStatLW = IOMn(ui32Module)->CMDSTAT;
    //
    // find num bytes left and tx/rx mode
    //
    uint32_t ui32CCmd = (ui32CmdStatLW & IOM0_CMDSTAT_CCMD_Msk) >> IOM0_CMDSTAT_CCMD_Pos;
    uint32_t ui32Status = AM_HAL_STATUS_SUCCESS;

    internal_iom_reset_iom_pins(pIOMState);

    if (ui32CCmd == IOM0_CMD_CMD_WRITE)
    {
        //
        // need to send some tx bytes to finish operation
        // return status is not used, if there is a problem
        // it will be detected later in this function
        //
        uint32_t numBytestLeft = (ui32CmdStatLW & IOM0_CMDSTAT_CTSIZE_Msk) >> IOM0_CMDSTAT_CTSIZE_Pos;
        ui32Status = internal_iom_finish_buffer_write(pIOMState, (int32_t) numBytestLeft);
    }
    else
    {
        //
        // read fifo until command finished
        // use 50 milliseconds for timeout
        // this is about 500bytes at 100Khz clock
        //
        while (IOMn(ui32Module)->STATUS_b.CMDACT)
        {
            uint32_t ui32FifoWrites = 0;
            while (IOMn(ui32Module)->FIFOPTR_b.FIFO1SIZ >= 4)
            {
                //
                // Read one 4-byte word from FIFO
                //
                (void) IOMn(ui32Module)->FIFOPOP;

                //
                // ensure the IOM hardware responds properly to the writes, use factor of 2
                //
                if (++ui32FifoWrites > (2 * AM_HAL_IOM_FIFO_SIZE_MAX / 4))
                {
                    //
                    // the fifo is not working properly,
                    // don't want to get stuck in this loop and never timeout
                    //
                    ui32Status = AM_HAL_STATUS_TIMEOUT;
                    break;
                }
            }

            am_hal_delay_us(1);
            if (++ui32TimeoutCount >= READ_FIFO_TIMEOUT_RST1)
            {
                //
                // a timeout, this error will be caught below
                //
                break;
            }

            //
            // there could be a few bytes left over: will reset fifo below
            //
        }
    }

    if (ui32Status == AM_HAL_STATUS_SUCCESS)
    {
        ui32Status = am_hal_delay_us_status_check(AM_HAL_IOM_MAX_BLOCKING_WAIT,
                                                  (uint32_t) &IOMn(ui32Module)->STATUS,
                                                  (IOM0_STATUS_IDLEST_Msk | IOM0_STATUS_CMDACT_Msk),
                                                  IOM0_STATUS_IDLEST_Msk,
                                                  true);
    }

    if (ui32Status == AM_HAL_STATUS_SUCCESS)
    {
        //
        // now, presumably, the transfer has finished, but the data is not trusted
        // reset the module and clear the fifo
        //
        internal_iom_error_reset_disable_submodule(pIOMState);
    }
    else
    {
        //
        // did not clear the cmd busy bit, return this error, for the application to handle
        //
        ui32Status = AM_HAL_STATUS_HW_ERR;
    }

    return ui32Status;
}


//*****************************************************************************
//
//! @brief Reset IOM on error.
//!
//! @param pIOMState - Pointer to IOM state structure.
//! @param ui32IntMask - Interrupt mask for error handling.
//
//*****************************************************************************
static void
internal_iom_reset_on_error(am_hal_iom_state_t  *pIOMState, uint32_t ui32IntMask)
{
    uint32_t ui32Module = pIOMState->ui32Module;
    uint32_t ui32CurIntCfg = IOMn(ui32Module)->INTEN;
    uint32_t ui32Status = AM_HAL_STATUS_SUCCESS;

    IOMn(ui32Module)->INTEN = 0;

    //
    // Disable interrupts temporarily
    //
    if (ui32IntMask & AM_HAL_IOM_INT_DERR)
    {
        if ((IOMn(ui32Module)->DMACFG & IOM0_DMACFG_DMADIR_Msk) == _VAL2FLD(IOM0_DMACFG_DMADIR, IOM0_DMACFG_DMADIR_M2P))
        {
            //
            // Write
            //
            uint32_t dummy = 0xDEADBEEF;
            uint32_t numBytesRemaining = IOMn(ui32Module)->DMATOTCOUNT;

            while (numBytesRemaining)
            {
                if (IOMn(ui32Module)->FIFOPTR_b.FIFO0REM >= 4)
                {
                    //
                    // Write one 4-byte word to FIFO
                    //
                    IOMn(ui32Module)->FIFOPUSH = dummy;
                    if (numBytesRemaining > 4)
                    {
                        numBytesRemaining -= 4;
                    }
                    else
                    {
                        break;
                    }
                }
            }

            //
            // Now wait for command to finish
            //
            (void)am_hal_delay_us_status_check(AM_HAL_IOM_MAX_BLOCKING_WAIT,
                                                      (uint32_t) &IOMn(ui32Module)->STATUS,
                                                      (IOM0_STATUS_IDLEST_Msk | IOM0_STATUS_CMDACT_Msk),
                                                      IOM0_STATUS_IDLEST_Msk,
                                                      true);
        }
        else
        {
            //
            // Read
            // Let command finish
            //
            while (IOMn(ui32Module)->STATUS_b.CMDACT)
            {
                while (IOMn(ui32Module)->FIFOPTR_b.FIFO1SIZ >= 4)
                {
                    //
                    // Read one 4-byte word from FIFO
                    //
                    (void)IOMn(ui32Module)->FIFOPOP;
#if MANUAL_POP
                    IOMn(ui32Module)->FIFOPOP = 0x11111111;
#endif
                }
            }

            ui32Status = am_hal_delay_us_status_check(AM_HAL_IOM_MAX_BLOCKING_WAIT,
                                                      (uint32_t) &IOMn(ui32Module)->STATUS,
                                                      (IOM0_STATUS_IDLEST_Msk | IOM0_STATUS_CMDACT_Msk),
                                                      IOM0_STATUS_IDLEST_Msk,
                                                      true);

            if (ui32Status == AM_HAL_STATUS_SUCCESS)
            {
                //
                // Flush any remaining data from FIFO
                // this should work, should not need to look for timeout here
                //
                while (IOMn(ui32Module)->FIFOPTR_b.FIFO1SIZ >= 4)
                {
                    //
                    // Read one 4-byte word from FIFO
                    //
                    (void)IOMn(ui32Module)->FIFOPOP;
#if MANUAL_POP
                    IOMn(ui32Module)->FIFOPOP = 0x11111111;
#endif
                }
            } // ui32Status == AM_HAL_STATUS_SUCCESS
        }
    } // DMA ERROR

    if (ui32IntMask & (AM_HAL_IOM_INT_NAK | AM_HAL_IOM_INT_ARB))
    {
        //
        // Disable IOM pins prior to disabling submodules
        // Reenable pins and then submodules
        //
        internal_iom_error_reset_disable_submodule(pIOMState);
    }

    if ((IOMn(ui32Module)->STATUS & IOM0_STATUS_CMDACT_Msk))
    {
        //
        // command is still active...
        // attempt to free the hung IOM hardware
        // pin map is needed to reset the IOM in this state
        //
        (void)internal_iom_reset_cmd_busy(pIOMState);
    }

    IOMn(ui32Module)->INTCLR = AM_HAL_IOM_INT_ALL;

    //
    // Restore interrupts
    //
    IOMn(ui32Module)->INTEN = ui32CurIntCfg;
}

//*****************************************************************************
//
//! @brief Finalize computed clock settings and derive output frequency.
//!
//! Given a fully populated clock profile (including FSEL, Div3, TOTPER, LOWPER),
//! this function calculates the actual output frequency and duty cycle. It assumes
//! the configuration is already valid and doesn't perform any searching or guessing.
//!
//! The computed fields include:
//!   - ui32OutClock         (actual frequency in Hz)
//!   - ui32DC_1024          (duty cycle, scaled to 1024 units)
//!   - ui32DC_deviation     (absolute deviation from 50% duty cycle)
//!   - i32Diff / ui32AbsDiff (error from desired frequency)
//!
//! Used internally for scoring and comparison between candidate configurations.
//!
//! @param pcp Pointer to a clock configuration struct with valid divider settings.
//!
//! @return The actual output frequency in Hz.
//
//*****************************************************************************
static uint32_t
iom_compute_freq_cp( iom_clock_comp_parms_t *pcp)
{
    //
    // get base frequency (start at the highest frequency for this module)
    //
    uint32_t ui32HFRCfreqHz = ui32FselClockLookup[pcp->ui32Fsel] ;

    //
    // divide input freq by 3 if feature is enabled
    //
    if ( pcp->ui32Div3 )
    {
        ui32HFRCfreqHz /= 3 ;
    }

    if ( pcp->ui32DivEn )
    {
        //
        // toper divider is enabled
        //
        uint32_t ui32Denomfinal = (1 + pcp->ui32TotPer);

        pcp->ui32OutClock = ui32HFRCfreqHz / ui32Denomfinal;

        // duty cycle is dc = (lowper+1)/(totPer+1) ==> (ui32DenomFinal/2) /ui32DenomFinal
        // when ui32Denomfinal is odd, dc != 50%

        uint32_t dc_1024  = ((1 + pcp->ui32LowPer) * DUTY_CYCLE_SCALING) / ui32Denomfinal;
        pcp->ui32DC_1024 = (int32_t) dc_1024;
    }
    else
    {
        //
        // no other dividers are enabled
        //
        pcp->ui32OutClock = ui32HFRCfreqHz ;
        pcp->ui32DC_1024 = DUTY_CYCLE_SCALING / 2;
    }

    int32_t dec_devo = pcp->ui32DC_1024 - (DUTY_CYCLE_SCALING / 2); // how far from 50% duty cycle
    pcp->ui32DC_deviation = (dec_devo < 0) ? -dec_devo : dec_devo;  // make positive

    //
    // compute difference from requested, this is used in to select best method
    // actual freq. should not be greater than requested
    //
    pcp->i32Diff = (int32_t) pcp->ui32DesiredFreq - (int32_t) pcp->ui32OutClock ;
    pcp->ui32AbsDiff = (uint32_t) ((pcp->i32Diff < 0) ? -pcp->i32Diff : pcp->i32Diff) ;

    return pcp->ui32OutClock;

} // iom_compute_freq_cp
//*****************************************************************************
//
//! @brief Compute divider values for a given base clock and mode.
//!
//! This function calculates the TOTPER and LOWPER divider settings that produce
//! the closest achievable frequency to the requested value. It assumes a fixed
//! base clock (FSEL) and divider mode (/1 or /3), and tries to find the best
//! divider settings that do not exceed the requested frequency.
//!
//! It also computes the resulting duty cycle, frequency error, and flags any
//! out-of-range conditions.
//!
//! If TOTPER is not needed (i.e., divide-by-1 with no division), it disables it.
//!
//! @param pcp  Pointer to the clock profile structure. Must have FSEL, Div3,
//!             and DesiredFreq already set. The function fills in the rest.
//
//*****************************************************************************
static void
iom_compute_freq_helper(iom_clock_comp_parms_t* pcp)
{
    //
    // first pull the clock speed out of the table
    //
    uint32_t ui32HFRCfreqHz = ui32FselClockLookup[pcp->ui32Fsel];
    //
    // divide by 3 if in that mode
    //
    if ( pcp->ui32Div3 )
    {
        ui32HFRCfreqHz /= 3;
    }

    uint32_t baseFreq = ui32HFRCfreqHz;  // this is the base freq

    // if this divides clean (like 24,000,000 / 3 mhz) or not,
    // looking for the divider that gets closest without going over
    uint32_t ui32bDiv = (baseFreq + pcp->ui32DesiredFreq - 1) / pcp->ui32DesiredFreq;

    // the largest divider TOTPER can be is 256

    pcp->eErrors = eFREQ_ERROR_NO_ERROR;
    if (ui32bDiv == 0)
    {
        pcp->eErrors = eREQ_FREQ_TOO_HIGH_WARNING;
        return;
    }

    if ( ui32bDiv == 1 )
    {
        //
        // there is no div used here
        //
        pcp->ui32DivEn = 0;
        pcp->ui32TotPer = 0;
        pcp->ui32LowPer = 0;
    }
    else
    {
        bool computeTotPer = true;
        if (ui32bDiv & 0x01)
        {
            //
            // non symmetrical dc
            //
            if ( pcp->eClockSelPriority == AM_HAL_IOM_FORCE_SYMMETRICAL_DC)
            {
                //
                // force DC symmetry by lowering output freq
                //
                ui32bDiv++;
                pcp->ui32TotPer = ui32bDiv - 1;
                pcp->ui32LowPer = (pcp->ui32TotPer - 1) / 2;
                computeTotPer = false;
            }
        }
        if (ui32bDiv > 256 )
        {
            pcp->eErrors = eUSE_LOWER_BASE_FREQ_WARNING;
            return;
        }
        if (computeTotPer)
        {
            pcp->ui32TotPer = ui32bDiv-1;
            pcp->ui32LowPer = pcp->ui32Phase ? (pcp->ui32TotPer - 1) / 2 : (pcp->ui32TotPer) / 2;
        }
        pcp->ui32DivEn = 1;
    }

    //
    // take the data just generated above and compute the output statistics
    //
    iom_compute_freq_cp( pcp );
} // iom_compute_freq_helper

//*****************************************************************************
//
//! @brief Compare clock profiles for divide-by-1 vs divide-by-3 paths.
//!
//! This function compares two completed clock configurations: one using a direct base
//! clock (divide-by-1), and the other using the divide-by-3 prescaler. The selection is
//! made based on the specified clock selection priority (accuracy, symmetry, or balance).
//!
//! The priority policy influences how much importance is given to frequency accuracy
//! vs. duty cycle symmetry.
//! In some cases, div3 may produce better frequency, symmetry, or power use.
//!
//! All else being equal, the divide-by-3 configuration is preferred to reduce power.
//!
//! @param psDiv1L   Pointer to divide-by-1 clock profile (typically from FSEL search).
//! @param psDiv3R   Pointer to divide-by-3 clock profile.
//!
//! @return Pointer to the preferred profile (either psDiv1L or psDiv3R).
//
//*****************************************************************************
static iom_clock_comp_parms_t *
compare_div1_3(iom_clock_comp_parms_t *psDiv1L, iom_clock_comp_parms_t *psDiv3R)
{
    //
    // left is intended to have a higher base freq. if right matches it, then right is better
    //
    switch (psDiv1L->eClockSelPriority)
    {
        case AM_HAL_IOM_FORCE_SYMMETRICAL_DC:
            // compare dc difference
            if (psDiv1L->ui32DC_deviation != psDiv3R->ui32DC_deviation)
            {
                if (psDiv1L->ui32DC_deviation < psDiv3R->ui32DC_deviation)
                {
                    return psDiv1L;
                }
                break;
            }
            if (psDiv1L->ui32AbsDiff != psDiv3R->ui32AbsDiff)
            {
                if (psDiv1L->ui32AbsDiff < psDiv3R->ui32AbsDiff)
                {
                    return psDiv1L;
                }
            }
            break ;
        case AM_HAL_IOM_PREFER_SYMMETRICAL_DC:
            // compare dc difference
            if ((psDiv1L->ui32DC_deviation > 10) || (psDiv3R->ui32DC_deviation > 10))
            {
                // if dc not in 1 % (1024 / 100)
                if (psDiv1L->ui32DC_deviation != psDiv3R->ui32DC_deviation)
                {
                    if (psDiv1L->ui32DC_deviation < psDiv3R->ui32DC_deviation)
                    {
                        return psDiv1L;
                    }
                    break ;
                }
            }
            if (psDiv1L->ui32AbsDiff != psDiv3R->ui32AbsDiff)
            {
                if (psDiv1L->ui32AbsDiff < psDiv3R->ui32AbsDiff)
                {
                    return psDiv1L;
                }
            }
            break;

        case AM_HAL_IOM_BALANCED_SELECTION:
        default:
            {
                bool preferD3 = true ;
                if (psDiv1L->ui32DC_deviation != psDiv3R->ui32DC_deviation)
                {
                    if ( (psDiv1L->ui32DC_deviation < 10) && psDiv3R->ui32DC_deviation < 10)
                    {
                        // if dc not in 1 % (1024 / 100)
                        if (psDiv1L->ui32DC_deviation < psDiv3R->ui32DC_deviation)
                        {
                            preferD3 = false ;
                        }
                    }
                    else if (psDiv1L->ui32DC_deviation < psDiv3R->ui32DC_deviation)
                    {
                        preferD3 = false ;
                    }
                }
                if (psDiv1L->ui32AbsDiff == psDiv3R->ui32AbsDiff)
                {
                    return preferD3 ? psDiv3R : psDiv1L ;
                }
            }

            return (psDiv1L->ui32AbsDiff < psDiv3R->ui32AbsDiff) ? psDiv1L : psDiv3R ;

        case AM_HAL_IOM_PREFER_FREQ_MATCH:
            if (psDiv1L->ui32AbsDiff != psDiv3R->ui32AbsDiff)
            {
                if (psDiv1L->ui32AbsDiff < psDiv3R->ui32AbsDiff)
                {
                    return psDiv1L;
                }
                break;
            }
            if (psDiv1L->ui32DC_deviation != psDiv3R->ui32DC_deviation)
            {
                if (psDiv1L->ui32DC_deviation < psDiv3R->ui32DC_deviation)
                {
                    return psDiv1L;
                }
            }
            break;
    } // switch
    return psDiv3R ;
} // compareDiv1_3

//*****************************************************************************
//
//! @brief Compare two clock profiles to decide which one is better.
//!
//! This function is used during the FSEL sweep when evaluating multiple base
//! clocks. It compares two fully computed clock configurations: a "left" (higher
//! base clock) and a "right" (lower base clock) candidate.
//!
//! The right-hand (lower clock) profile can't be better than the left
//! If the right-hand (lower clock) profile is as good as the left,
//! it becomes the new baseline. Otherwise, the search ends with the current higher freq profile.
//!
//! Comparison is based on the specified selection priority:
//!   - Frequency error
//!   - Duty cycle symmetry
//!   - Combined heuristics (if BALANCED_SELECTION is used)
//!
//! @param left   Pointer to the reference (higher base clock) profile.
//! @param right  Pointer to the candidate (lower base clock) profile.
//!
//! @return eLEFT if the left profile is as good as the right,
//!         eRIGHT if the right is better.
//
//************************************************************************
static iom_ab_chooser_e
compare_lr(iom_clock_comp_parms_t *left, iom_clock_comp_parms_t *right)
{
    // left is intended to have higher freq. is right matches it, then right is better
    switch (left->eClockSelPriority)
    {
        case AM_HAL_IOM_FORCE_SYMMETRICAL_DC:
            // compare dc difference
            if (left->ui32DC_deviation < right->ui32DC_deviation)
            {
                return eLEFT;
            }
            // compare freq difference
            if (left->ui32AbsDiff < right->ui32AbsDiff)
            {
                return eLEFT;
            }
            break;
        case AM_HAL_IOM_PREFER_SYMMETRICAL_DC:
            if (left->ui32DC_deviation < right->ui32DC_deviation)
            {
                return eLEFT;
            }
            // compare freq difference
            if (left->ui32AbsDiff < right->ui32AbsDiff)
            {
                return eLEFT;
            }
            break;
        case AM_HAL_IOM_BALANCED_SELECTION:
        default:
            if ((left->ui32DC_deviation > 10) || (right->ui32DC_deviation > 10))
            {
                // dc not within 1%, pick best dc
                if ( left->ui32DC_deviation < right->ui32DC_deviation)
                {
                    return eLEFT;
                }
            }
            // compare freq difference
            if (left->ui32AbsDiff < right->ui32AbsDiff)
            {
                return eLEFT;
            }
            break;
        case AM_HAL_IOM_PREFER_FREQ_MATCH:
            // compare freq difference
            if (left->ui32AbsDiff < right->ui32AbsDiff)
            {
                return eLEFT;
            }
            if (left->ui32DC_deviation < right->ui32DC_deviation)
            {
                return eLEFT;
            }
            break ;
    } // switch
    return eRIGHT;
} // compareLR

//*****************************************************************************
//
//! @brief Search for the best clock configuration for a single divider mode (/1 or /3).
//!
//! Given a starting clock profile (`psClockL`) with a base clock (FSEL) and divider mode
//! (either divide-by-1 or divide-by-3), this function iteratively searches from the highest
//! valid FSEL (starting at 48 MHz) downward. It finds the best clock divider settings to
//! match the requested output frequency as closely as possible.
//!
//! For each FSEL candidate, it computes divider settings (TOTPER, LOWPER) and evaluates
//! the resulting frequency and duty cycle. It stops when reducing the base clock begins to
//! degrade performance. The assumption is that higher base clocks will always be equal or
//! better when using the same divider path.
//!
//! The result is stored back into the provided `psClockL` structure.
//!
//! This function does not compare across modes (e.g. /1 vs /3): That is done in another function
//!
//! @param psClockL   Pointer to clock configuration struct with the desired frequency,
//!                   divider mode, and search preferences. Updated in-place with best match.
//!
//! @return
//!     - 0     : Success - valid configuration found.
//!     - -1    : Failure - frequency too low (no valid FSEL).
//!     - -2    : Failure - frequency too high (requires sub-1 divider).
//
//*****************************************************************************
static int32_t
iom_clock_selector(iom_clock_comp_parms_t *psClockL)
{
    //
    // first search for invalid frequencies for this entry
    //
    while (true)
    {
        //
        // computer divider for original freq.
        // if desired, freq is too low, or too high this exists with an error
        // first compute freq params for the base freq
        // this function will use the contents of psClockL to
        // compute additional parameters for this divider option
        //
        iom_compute_freq_helper(psClockL);
        if (psClockL->eErrors == eREQ_FREQ_TOO_HIGH_WARNING)
        {
            return -2;
        }
        if (psClockL->eErrors == eFREQ_ERROR_NO_ERROR)
        {
            //
            // found the first (highest) freq that can be divided to work
            // so continue with selection
            //
            break;
        }
        //
        // The previous base freq was too high, lower the base freq, by
        // increasing Fsel
        //

        if (++psClockL->ui32Fsel >= FSELMAX)
        {
            //
            // this is an error, freq too low
            //
            return -1;
        }
    }

    //
    // Establish the base right structure
    // This is where the current (left) base freq /2 is computed
    // Copy left (ref) struct to right,
    // from now on computations will be done into the right and
    // will be compared to the left. If the right is as good as the left,
    // it will become the reference (left), the lower freq(right) will never
    // be better than the higher freq (right)
    //
    iom_clock_comp_parms_t psClockpR = *psClockL;

    while (true)
    {

        //
        // prepare the second (right) for comparison
        // advance to the next slowest base clock
        //
        if (++psClockpR.ui32Fsel >= FSELMAX)
        {
            //
            // Done.
            // Ran out of clock dividers
            // whatever is in the L struct is the best
            //
            break;
        }

        //
        // Right side computation
        // Compute clock params using the new base clock
        //
        iom_compute_freq_helper( &psClockpR );

        //
        // compare left (higher freq) and right, if right is good enough to pass, use that
        //
        iom_ab_chooser_e lr = compare_lr(psClockL, &psClockpR);
        if (lr == eLEFT)
        {
            //
            // right is inferior to left, so that is the end of this search
            // nothing will improve with a lower base clock
            //
            break;
        }

        //
        // The lower freq was as good as higher freq so:
        // The lower freq now becomes the ref (higher freq).
        // Do another loop
        // Copy right into Left as right is the new reference
        //
        *psClockL = psClockpR;
    }

    return 0;  // success
} //iom_clockSelector()

//*****************************************************************************
//
//! @brief Compute the best IOM CLKCFG register settings for a desired output frequency.
//!
//! This function attempts to match the requested SPI clock frequency by evaluating
//! all valid base clocks (FSEL) with and without a divide-by-3 prescaler. It calculates
//! the best available divider settings (TOTPER, LOWPER) to achieve the requested frequency,
//! while balancing duty cycle symmetry and frequency accuracy based on the provided priority.
//!
//! The function evaluates two independent search paths:
//!   - One using direct division (no /3 prescaler)
//!   - One using the divide-by-3 prescaler before the TOTPER divider
//!
//! Each path searches from highest to lowest base clock, retaining the lowest FSEL that
//! produces an equivalent result. This favors lower power when performance is equal.
//!
//! The best of the two resulting profiles is chosen according to the specified priority mode
//! (frequency accuracy, duty cycle symmetry, or a balance).
//!
//! If no valid configuration is found, the function returns zero (0).
//!
//! @param ui32FreqHz            Desired output frequency in Hz (must be > 0).
//! @param ui32Phase             If odd divider, selects whether the extra clock cycle goes
//!                              to the high or low period. (0 = longer low, 1 = longer high).
//! @param eClockSelPriority     Selection policy from ::am_hal_iom_clock_sel_priority_e.
//!
//! @return 64-bit result:
//!     - Upper 32 bits = actual output frequency achieved (Hz)
//!     - Lower 32 bits = value to write to IOMx->CLKCFG register
//!
//! @note A return value of 0 (both halves) indicates failure to match any valid configuration.
//!       A nonzero result may still have some deviation from the requested frequency.
//!
//*****************************************************************************
uint64_t
iom_get_interface_clock_cfg(uint32_t ui32FreqHz,
                            uint32_t ui32Phase,
                            am_hal_iom_clock_sel_priority_e eClockSelPriority)
{

    if (ui32FreqHz == 0)
    {
        return 0;
    }

    if (eClockSelPriority >= AM_HAL_IOM_CLOCK_SEL_PRIO_MAX)
    {
        //
        // user probably allocating iom config struct on stack
        // choose default which will always be at zero
        //
        eClockSelPriority = (am_hal_iom_clock_sel_priority_e) 0;
    }

    //
    // Load up two utility structs
    // that are used to find the best div1 and best div3 options
    // After they are found, div1 and div3 solutions will be compared
    //
    iom_clock_comp_parms_t clockD1;
    iom_clock_comp_parms_t clockD3;
    clockD1.ui32Phase       = ui32Phase;
    clockD1.ui32DesiredFreq = ui32FreqHz;
    clockD1.eClockSelPriority    = eClockSelPriority;
    clockD1.ui32Fsel        = 2;   // first valid divider 48,000,000
    clockD1.ui32Div3        = 0;
    clockD3                  = clockD1; // copy one struct into the other
    clockD3.ui32Div3        = 1;        // this struct will be used for /3 tests

    int32_t div1Status = iom_clock_selector(&clockD1);
    int32_t div3Status = iom_clock_selector(&clockD3);

    //
    // This will hold a pointer to the winning clock profile (div1 or div3)
    //
    iom_clock_comp_parms_t *psChosenProfile = 0;

    if (div1Status >= 0)
    {
        //
        // divide by one trial found a valid solution
        //
        if (div3Status >= 0)
        {
            //
            // clock div3 will get priority when all else equal
            //
            psChosenProfile = compare_div1_3(&clockD1, &clockD3);
        }
        else
        {
            psChosenProfile = &clockD1;
        }
    }
    else if (div3Status >= 0)
    {
        psChosenProfile = &clockD3;
    }

    if (psChosenProfile == 0)
    {
        return 0 ; // failure
    }

    // if 375Khz base is selected, that needs a register value of 0, not 9
    if (psChosenProfile->ui32Fsel > FSEL_MAX_REGISTER_VAL)
    {
        psChosenProfile->ui32Fsel = 0;
    }

    uint32_t ui32ClkCfg = _VAL2FLD( IOM0_CLKCFG_FSEL, psChosenProfile->ui32Fsel);

    if (psChosenProfile->ui32DivEn)
    {
        ui32ClkCfg |= _VAL2FLD( IOM0_CLKCFG_DIVEN, 1) |
            _VAL2FLD( IOM0_CLKCFG_TOTPER, psChosenProfile->ui32TotPer) |
            _VAL2FLD( IOM0_CLKCFG_LOWPER, psChosenProfile->ui32LowPer);
    }
    if (psChosenProfile->ui32Div3)
    {
        ui32ClkCfg |=  _VAL2FLD( IOM0_CLKCFG_DIV3, 1);
    }

    uint64_t output = ((uint64_t)(psChosenProfile->ui32OutClock) << 32) | ui32ClkCfg;
    return output;
} // iom_get_interface_clock_cfg()

//*****************************************************************************
//
//! @brief Initializes the IOM Command Queue.
//!
//! @param pHandle      - handle for the interface.
//! @param ui32Length   - length of the SRAM Command Queue buffer in words.
//! @param pTCB         - pointer to the SRAM to use for the Command Queue.
//!
//! This function initializes the global command queue structure.
//!
//! @return HAL status of the operation.
//
//*****************************************************************************
uint32_t
am_hal_iom_CQInit(void *pHandle, uint32_t ui32Length,
                  uint32_t *pTCB)
{
    am_hal_cmdq_cfg_t cqCfg;
    am_hal_iom_state_t  *pIOMState = (am_hal_iom_state_t *)pHandle;
    uint32_t            ui32Module = pIOMState->ui32Module;
    uint32_t            ui32Status = AM_HAL_STATUS_SUCCESS;

    pIOMState->pCmdQHdl = NULL;
    pIOMState->ui32MaxTransactions = 0;
    pIOMState->ui32NumUnSolicited = 0;

    cqCfg.pCmdQBuf = pTCB;
    cqCfg.cmdQSize = ui32Length / 2;
    cqCfg.priority = AM_HAL_CMDQ_PRIO_HI;
    ui32Status = am_hal_cmdq_init((am_hal_cmdq_if_e)(AM_HAL_CMDQ_IF_IOM0 + ui32Module),
                      &cqCfg, &pIOMState->pCmdQHdl);
    if (ui32Status == AM_HAL_STATUS_SUCCESS)
    {
        pIOMState->ui32MaxTransactions = AM_HAL_IOM_MAX_PENDING_TRANSACTIONS;
    }
    return ui32Status;
} // am_hal_iom_CQInit()

//*****************************************************************************
//
//! @brief Resets the IOM Command Queue.
//!
//! @param pHandle - handle for the interface.
//!
//! This function resets the global command queue structure.
//!
//! @return HAL status of the operation.
//
//*****************************************************************************
uint32_t
am_hal_IOM_CQReset(void *pHandle)
{
    am_hal_iom_state_t  *pIOMState = (am_hal_iom_state_t *)pHandle;

    if (pIOMState->pCmdQHdl)
    {
        am_hal_cmdq_term(pIOMState->pCmdQHdl, true);
        pIOMState->pCmdQHdl = NULL;
    }

    //
    // Return the status.
    //
    return AM_HAL_STATUS_SUCCESS;
} // am_hal_IOM_CQReset()

//*****************************************************************************
//
// Adds a transaction the IOM Command Queue.
//
// This function copies data from the IOM FIFO into the array \e pui32Data.
// This is how input data from SPI or I2C transactions may be retrieved.
//
//*****************************************************************************
uint32_t
am_hal_iom_CQAddTransaction(void *pHandle,
                            am_hal_iom_transfer_t *psTransaction,
                            am_hal_iom_callback_t pfnCallback,
                            void *pCallbackCtxt)
{
    am_hal_iom_state_t      *pIOMState = (am_hal_iom_state_t *)pHandle;
    am_hal_iom_txn_cmdlist_t   *pCQEntry;
    am_hal_cmdq_entry_t     *pCQBlock;
    uint32_t                index;

    //
    // Check to see if there is enough room in the CQ
    //
    if ((pIOMState->ui32NumPendTransactions == AM_HAL_IOM_MAX_PENDING_TRANSACTIONS) ||
        (am_hal_cmdq_alloc_block(pIOMState->pCmdQHdl, sizeof(am_hal_iom_txn_cmdlist_t) / 8, &pCQBlock, &index)))
    {
        return AM_HAL_STATUS_OUT_OF_RANGE;
    }

    pCQEntry = (am_hal_iom_txn_cmdlist_t *)pCQBlock;

    build_txn_cmdlist(pIOMState, pCQEntry, psTransaction);

    //
    // Because we set AM_HAL_IOM_CQUPD_INT_FLAG, an interrupt will occur once
    // we reach this point in the Command Queue.  In the service routine, we'll
    // look for the appropriate callback.
    //
    // If ENDIDX has been reached, the CQ will pause here. Otherwise will
    // continue with the next CQ entry.
    //

    //
    // Store the callback function pointer.
    //
    pIOMState->pfnCallback[index & (AM_HAL_IOM_MAX_PENDING_TRANSACTIONS - 1)] = pfnCallback;
    pIOMState->pCallbackCtxt[index & (AM_HAL_IOM_MAX_PENDING_TRANSACTIONS - 1)] = pCallbackCtxt;

    return AM_HAL_STATUS_SUCCESS;
} // am_hal_iom_CQAddTransaction()

//*****************************************************************************
//
//! @ Enable the Command Queue operation.
//!
//! This function enables Command Queue operation.
//
//*****************************************************************************
uint32_t
am_hal_iom_CQEnable(void *pHandle)
{
    am_hal_iom_state_t  *pIOMState = (am_hal_iom_state_t *)pHandle;

    if (0 == pIOMState->ui32NumPendTransactions)
    {
        uint32_t *pCqAddr = (uint32_t *)IOMn(pIOMState->ui32Module)->CQADDR;
        // When CQ is enabled with nothing there - it always executes the first command
        // insert dummy command
        *pCqAddr = (uint32_t) &IOMn(pIOMState->ui32Module)->CQADDR;
        *(pCqAddr + 1) = (uint32_t)pCqAddr;
    }
    //
    // Enable the Command Queue operation
    //
    return am_hal_cmdq_enable(pIOMState->pCmdQHdl);

} // am_hal_iom_CQEnable()

//*****************************************************************************
//
//! @brief Disable the Command Queue operation.
//!
//! @param pHandle       - handle for the interface.
//!
//! This function disables the Command Queue operation.
//!
//!
//! @return HAL status of the operation.
//
//
//*****************************************************************************
uint32_t
am_hal_iom_CQDisable(void *pHandle)
{
    am_hal_iom_state_t  *pIOMState = (am_hal_iom_state_t *)pHandle;

    //
    // Disable the Command Queue operation
    //
    return am_hal_cmdq_disable(pIOMState->pCmdQHdl);
} // am_hal_iom_CQDisable()

//*****************************************************************************
//
//! @brief Abort the Command Queue operation.
//!
//! @param pHandle       - handle for the interface.
//!
//! This function aborts the Command Queue operation.
//!
//!
//! @return HAL status of the operation.
//
//
//*****************************************************************************
uint32_t
am_hal_iom_CQAbort(void *pHandle)
{
    am_hal_iom_state_t  *pIOMState = (am_hal_iom_state_t *)pHandle;

    //
    // Disable CQ
    //
    IOMn(pIOMState->ui32Module)->CQCFG_b.CQEN = 0;

    //
    // Disable DMA
    //
    IOMn(pIOMState->ui32Module)->DMACFG_b.DMAEN = 0;

    //
    // Clear DMAERR in DMASTAT
    //
    IOMn(pIOMState->ui32Module)->DMASTAT = 0;

    //
    // Reset Submodule & FIFO
    //
    internal_iom_reset_on_error(pIOMState, AM_HAL_IOM_INT_ERR);

    //
    // Reset the cmdq
    //
    am_hal_cmdq_reset(pIOMState->pCmdQHdl);
    pIOMState->ui32LastIdxProcessed = 0;
    pIOMState->ui32NumSeqTransactions = 0;
    pIOMState->ui32NumPendTransactions = 0;
    pIOMState->ui32NumUnSolicited = 0;
    pIOMState->pHPTransactions = NULL;
    pIOMState->bHP = false;
    pIOMState->block = 0;
    pIOMState->ui32NumHPPendingEntries = 0;
    pIOMState->ui32NumHPEntries = 0;
    pIOMState->eSeq = AM_HAL_IOM_SEQ_NONE;
    pIOMState->bAutonomous = true;

    return AM_HAL_STATUS_SUCCESS;
} // am_hal_iom_CQAbort()

//*****************************************************************************
//
//! @brief Dummy callback function.
//!
//! @param pCallbackCtxt - Callback context (unused).
//! @param status - Status value (unused).
//!
//*****************************************************************************
static void iom_dummy_callback(void *pCallbackCtxt, uint32_t status)
{
    // Dummy - Do nothing
}

//*****************************************************************************
//
//! @brief Callback when end of sequence is reached.
//!
//! @param pCallbackCtxt - Callback context containing IOM state.
//! @param status - Status value from the transaction.
//!
//*****************************************************************************
static void iom_seq_loopback(void *pCallbackCtxt, uint32_t status)
{
    // Reset the state to allow serving callbacks for next set
    am_hal_iom_state_t *pIOMState = (am_hal_iom_state_t *)pCallbackCtxt;
    pIOMState->ui32NumPendTransactions = pIOMState->ui32NumSeqTransactions + 1;
    pIOMState->ui32LastIdxProcessed = 0;
    pIOMState->bRestart = true;
    // Now resume the CQ - to finish loopback
    // Resume the CQ
    IOMn(pIOMState->ui32Module)->CQSETCLEAR = AM_HAL_IOM_SC_UNPAUSE_SEQLOOP;
}

//*****************************************************************************
//
//! @brief Pause the Command Queue.
//!
//! @param pIOMState       - pointer to the IOM internal state.
//!
//! This function pauses the Command Queue operation.
//!
//! @return HAL status of the operation.
//
//*****************************************************************************
static uint32_t iom_cq_pause(am_hal_iom_state_t *pIOMState)
{
    uint32_t status = AM_HAL_STATUS_SUCCESS;
    uint32_t ui32usMaxDelay = AM_HAL_IOM_MAX_PAUSE_DELAY;
    // Pause the CQ
    IOMn(pIOMState->ui32Module)->CQSETCLEAR = AM_HAL_IOM_SC_PAUSE_CQ;
    // It is possible that CQ is disabled once the last transaction is processed
    while ( IOMn(pIOMState->ui32Module)->CQCFG_b.CQEN )
    {
        // Need to make sure we're paused at a designated pause point
        if ( IOMn(pIOMState->ui32Module)->CQSTAT_b.CQPAUSED && (IOMn(pIOMState->ui32Module)->CQPAUSEEN & AM_HAL_IOM_PAUSE_FLAG_CQ) )
        {
            break;
        }
        if ( ui32usMaxDelay-- )
        {
            //
            // Call the BOOTROM cycle function to delay for about 1 microsecond.
            //
            am_hal_delay_us(1);
        }
        else
        {
            return AM_HAL_STATUS_TIMEOUT;
        }
    }
    if (status == AM_HAL_STATUS_SUCCESS)
    {
        // Now that CQ is guaranteed to not progress further - we need to still wait in case the current CQ entry
        // resulted in a DMA state....need to make sure we finish the current DMA
        status = am_hal_delay_us_status_check(AM_HAL_IOM_MAX_PAUSE_DELAY,
                                             (uint32_t)&IOMn(pIOMState->ui32Module)->DMASTAT,
                                             IOM0_DMASTAT_DMATIP_Msk,
                                             _VAL2FLD(IOM0_DMASTAT_DMATIP, 0),
                                             true);

    }
    return status;
}

//*****************************************************************************
//
//! @brief Program the DMA directly.
//!
//! @param pHandle - Pointer to the IOM instance handle.
//!
//*****************************************************************************
static void
program_dma(void *pHandle)
{
    am_hal_iom_state_t         *pIOMState = (am_hal_iom_state_t *)pHandle;
    uint32_t                    ui32Module = pIOMState->ui32Module;
    uint32_t                    index = (pIOMState->ui32LastHPIdxProcessed + 1) % pIOMState->ui32MaxHPTransactions;
    am_hal_iom_dma_entry_t     *pDMAEntry = &pIOMState->pHPTransactions[index];

    //
    // OFFSETHI
    //
    IOMn(ui32Module)->OFFSETHI = pDMAEntry->ui32OFFSETHIVal;

    //
    // I2C DEVADDR field in DEVCFG
    //
    IOMn(ui32Module)->DEVCFG = pDMAEntry->ui32DEVCFGVal;

    //
    // disable DMA before writing TOTCOUNT.
    //
    IOMn(ui32Module)->DMACFG = 0x0;

    //
    // set DMATOTALCOUNT
    //
    IOMn(ui32Module)->DMATOTCOUNT = pDMAEntry->ui32DMATOTCOUNTVal;

    //
    // set DMATARGADDR
    //
    IOMn(ui32Module)->DMATARGADDR = pDMAEntry->ui32DMATARGADDRVal;

    //
    // Command to set DMACFG to start the DMA operation
    //
    IOMn(ui32Module)->DMACFG = pDMAEntry->ui32DMACFGVal;
    //
    // Command to start the transfer.
    //
    IOMn(ui32Module)->CMD = pDMAEntry->ui32CMDVal;
}

//*****************************************************************************
//
//! @brief Schedule a high priority transaction.
//!
//! @param pIOMState - Pointer to the IOM internal state.
//! @param numTrans - Number of transactions to schedule in a block.
//!
//! @return HAL status of the operation.
//!
//*****************************************************************************
static uint32_t
sched_hiprio(am_hal_iom_state_t *pIOMState, uint32_t numTrans)
{
    uint32_t ui32NumPend;
    uint32_t ui32Status = AM_HAL_STATUS_SUCCESS;
    //
    // Start a critical section.
    //
    AM_CRITICAL_BEGIN

    ui32NumPend = pIOMState->ui32NumHPEntries;
    pIOMState->ui32NumHPEntries += numTrans;

    //
    // End the critical section.
    //
    AM_CRITICAL_END

    if (0 == ui32NumPend)
    {
        // Force CQ to Pause
        ui32Status = iom_cq_pause(pIOMState);
        if (ui32Status != AM_HAL_STATUS_SUCCESS)
        {
            return ui32Status;
        }
        pIOMState->ui32TxnInt = 0;
        // Clear & Enable DMACMP interrupt
        IOMn(pIOMState->ui32Module)->INTCLR = AM_HAL_IOM_INT_DCMP | AM_HAL_IOM_INT_CMDCMP;
        IOMn(pIOMState->ui32Module)->INTEN |= AM_HAL_IOM_INT_DCMP | AM_HAL_IOM_INT_CMDCMP;
        pIOMState->bHP = true;
        //
        // Program the DMA
        //
        program_dma(pIOMState);
    }
    return ui32Status;
} // sched_hiprio()

//*****************************************************************************
//
//! @brief Add a high priority transaction.
//!
//! @param pHandle       - pointer the IOM instance handle.
//! @param psTransaction - pointer to IOM transaction.
//! @param pfnCallback   - pointer to the callback for transaction (could be NULL)
//! @param pCallbackCtxt - pointer to the context to the callback (could be NULL)
//!
//! This function adds a function to the internal high priority transaction queue
//!
//! @return HAL status of the operation.
//
//*****************************************************************************
static uint32_t
iom_add_hp_transaction(void *pHandle,
                       am_hal_iom_transfer_t *psTransaction,
                       am_hal_iom_callback_t pfnCallback,
                       void *pCallbackCtxt)
{
    am_hal_iom_state_t      *pIOMState = (am_hal_iom_state_t *)pHandle;
    am_hal_iom_dma_entry_t  *pDMAEntry;
    uint32_t                ui32Dir = psTransaction->eDirection;
    uint32_t                ui32SRAMAddress;

    uint32_t  index = pIOMState->ui32NextHPIdx % pIOMState->ui32MaxHPTransactions;
    //
    // Check to see if there is enough room in the queue
    //
    if ( pIOMState->ui32NumHPEntries == pIOMState->ui32MaxHPTransactions )
    {
        return AM_HAL_STATUS_OUT_OF_RANGE;
    }

    ui32SRAMAddress = (ui32Dir == AM_HAL_IOM_TX) ? (uint32_t)psTransaction->pui32TxBuffer : (uint32_t)psTransaction->pui32RxBuffer;
    pDMAEntry = &pIOMState->pHPTransactions[index];
    pDMAEntry->ui32OFFSETHIVal   = (uint32_t)(psTransaction->ui64Instr >> 8);
    pDMAEntry->ui32DEVCFGVal     = _VAL2FLD(IOM0_DEVCFG_DEVADDR, psTransaction->uPeerInfo.ui32I2CDevAddr);
    pDMAEntry->ui32DMATARGADDRVal = ui32SRAMAddress;
    pDMAEntry->ui32DMATOTCOUNTVal  = psTransaction->ui32NumBytes;
    pDMAEntry->ui32DMACFGVal      =
        _VAL2FLD(IOM0_DMACFG_DMAPRI, psTransaction->ui8Priority)     |
        _VAL2FLD(IOM0_DMACFG_DMADIR, ui32Dir == AM_HAL_IOM_TX ? 1 : 0);

    if (psTransaction->ui32NumBytes)
    {
        pDMAEntry->ui32DMACFGVal |= IOM0_DMACFG_DMAEN_Msk;
    }
    //
    // Command to start the transfer.
    //
    pDMAEntry->ui32CMDVal =  build_cmd((pIOMState->eInterfaceMode == AM_HAL_IOM_SPI_MODE) ? psTransaction->uPeerInfo.ui32SpiChipSelect : 0, // ChipSelect
                                ui32Dir,          // ui32Dir
                                psTransaction->bContinue,           // ui32Cont
                                psTransaction->ui64Instr,           // ui64Offset
                                psTransaction->ui32InstrLen,        // ui32OffsetCnt
                                psTransaction->ui32NumBytes);  // ui32Bytes

    pDMAEntry->pfnCallback = pfnCallback;
    pDMAEntry->pCallbackCtxt = pCallbackCtxt;

    pIOMState->ui32NextHPIdx++;
    return AM_HAL_STATUS_SUCCESS;
} // iom_add_hp_transaction()

//*****************************************************************************
//
//! @brief Validate an IOM transaction.
//!
//! @param pIOMState     - pointer to the IOM internal state.
//! @param psTransaction - pointer to IOM transaction.
//! @param bBlocking     - is this a blocking transaction?
//!
//! This function validates.
//!
//! @return HAL status of the operation.
//
//*****************************************************************************
uint32_t
validate_transaction(am_hal_iom_state_t *pIOMState,
                     am_hal_iom_transfer_t *psTransaction,
                     bool bBlocking)
{
    uint32_t ui32OffsetCnt, ui32Dir, ui32Bytes;
    uint64_t ui64Offset;

    ui64Offset = psTransaction->ui64Instr;
    ui32OffsetCnt = psTransaction->ui32InstrLen;
    ui32Dir = psTransaction->eDirection;
    ui32Bytes = psTransaction->ui32NumBytes;

    //
    // Validate parameters
    //
    if ( (ui32OffsetCnt > AM_HAL_IOM_MAX_OFFSETSIZE)               ||
         (ui64Offset & (0xFFFFFFFFFFFFFFFF << (ui32OffsetCnt*8)))                       ||
         (ui32Bytes && (ui32Dir != AM_HAL_IOM_TX) && (psTransaction->pui32RxBuffer == NULL)) ||
         (ui32Bytes && (ui32Dir != AM_HAL_IOM_RX) && (psTransaction->pui32TxBuffer == NULL)) ||
         ((pIOMState->eInterfaceMode == AM_HAL_IOM_I2C_MODE) &&
          (psTransaction->ui32NumBytes > AM_HAL_IOM_MAX_TXNSIZE_I2C))           ||
         ((pIOMState->eInterfaceMode == AM_HAL_IOM_SPI_MODE) &&
          ((psTransaction->uPeerInfo.ui32SpiChipSelect > AM_HAL_IOM_MAX_CS_SPI) ||
           (psTransaction->ui32NumBytes > AM_HAL_IOM_MAX_TXNSIZE_SPI))) )
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }

    if (!bBlocking)
    {
        if (psTransaction->ui32PauseCondition & AM_HAL_IOM_PAUSE_FLAG_RESV)
        {
            return AM_HAL_STATUS_INVALID_ARG;
        }
        if (psTransaction->ui32StatusSetClr & AM_HAL_IOM_SC_RESV_MASK)
        {
            return AM_HAL_STATUS_INVALID_ARG;
        }
    }

    return AM_HAL_STATUS_SUCCESS;

} // validate_transaction()

//*****************************************************************************
//
// IOM uninitialize function
//
//*****************************************************************************
uint32_t
am_hal_iom_uninitialize(void *pHandle)
{
    uint32_t status = AM_HAL_STATUS_SUCCESS;
    am_hal_iom_state_t *pIOMState = (am_hal_iom_state_t*)pHandle;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    if (!AM_HAL_IOM_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    if (pIOMState->prefix.s.bEnable)
    {
        am_hal_iom_disable(pHandle);
    }

    pIOMState->prefix.s.bInit = false;

    //
    // Return the status.
    //
    return status;

} // am_hal_iom_uninitialize()

//*****************************************************************************
//
// IOM initialization function
//
//*****************************************************************************
uint32_t
am_hal_iom_initialize(uint32_t ui32Module, void **ppHandle)
{
    // Compile time check to ensure ENTRY_SIZE macros are defined correctly
    // incorrect definition will cause divide by 0 error at build time
    am_ct_assert((sizeof(am_hal_iom_txn_cmdlist_t) + 8) == AM_HAL_IOM_CQ_ENTRY_SIZE);
    am_ct_assert(sizeof(am_hal_iom_dma_entry_t) == AM_HAL_IOM_HIPRIO_ENTRY_SIZE);

#ifndef AM_HAL_DISABLE_API_VALIDATION
    //
    // Validate the module number
    //
    if ( ui32Module >= AM_REG_IOM_NUM_MODULES )
    {
        return AM_HAL_STATUS_OUT_OF_RANGE;
    }

    if (ppHandle == NULL)
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }

    if (g_IOMhandles[ui32Module].prefix.s.bInit)
    {
        return AM_HAL_STATUS_INVALID_OPERATION;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    g_IOMhandles[ui32Module].prefix.s.bInit = true;
    g_IOMhandles[ui32Module].prefix.s.bEnable = false;
    g_IOMhandles[ui32Module].prefix.s.magic = AM_HAL_MAGIC_IOM;

    //
    // Initialize the handle.
    //
    g_IOMhandles[ui32Module].ui32Module = ui32Module;

    //
    // Return the handle.
    //
    *ppHandle = (void *)&g_IOMhandles[ui32Module];

    //
    // Return the status
    //
    return AM_HAL_STATUS_SUCCESS;

} // am_hal_iom_initialize()

//*****************************************************************************
//
// IOM enable function
//
//*****************************************************************************
uint32_t
am_hal_iom_enable(void *pHandle)
{
    am_hal_iom_state_t *pIOMState = (am_hal_iom_state_t*)pHandle;
    uint32_t status = AM_HAL_STATUS_SUCCESS;
#ifndef AM_HAL_DISABLE_API_VALIDATION
    if (!AM_HAL_IOM_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }

    if (pIOMState->prefix.s.bEnable)
    {
        return AM_HAL_STATUS_SUCCESS;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    // Enable submodule
    if ( !enable_submodule(pIOMState->ui32Module, ((pIOMState->eInterfaceMode == AM_HAL_IOM_SPI_MODE) ? 0 : 1)) )
    {
        return AM_HAL_STATUS_HW_ERR;
    }

#if MANUAL_POP
    IOMn(pIOMState->ui32Module)->FIFOCTRL_b.POPWR = 1;
#endif

    //
    // If Enable the Command Queue
    //
    if ( pIOMState->pNBTxnBuf )
    {
        pIOMState->ui32NumPendTransactions = 0;
        pIOMState->ui32LastIdxProcessed = 0;
        // Initialize Flags used to force CQ Pause
        IOMn(pIOMState->ui32Module)->CQSETCLEAR = AM_HAL_IOM_SC_UNPAUSE_CQ | AM_HAL_IOM_SC_PAUSE_SEQLOOP;
        pIOMState->pHPTransactions = NULL;
        pIOMState->bHP = false;
        pIOMState->block = 0;
        pIOMState->ui32NumHPPendingEntries = 0;
        pIOMState->ui32NumHPEntries = 0;
        pIOMState->eSeq = AM_HAL_IOM_SEQ_NONE;
        pIOMState->ui32NumSeqTransactions = 0;
        pIOMState->bAutonomous = true;
        status = am_hal_iom_CQInit(pIOMState,
                                   pIOMState->ui32NBTxnBufLength,
                                   pIOMState->pNBTxnBuf);
        // Initialize the DMA Trigger Setting
        //
        // DMATRIG, set DTHREN and/or DCMDCMPEN.
        // Note - it is recommended that DTHREN always be set.
        //
        IOMn(pIOMState->ui32Module)->DMATRIGEN = _VAL2FLD(IOM0_DMATRIGEN_DTHREN, 1);
    }

    if (status == AM_HAL_STATUS_SUCCESS)
    {
        // Make sure IOM is fully enabled
        status = am_hal_delay_us_status_check(1000,
                                (uint32_t)&IOMn(pIOMState->ui32Module)->STATUS,
                                (IOM0_STATUS_IDLEST_Msk | IOM0_STATUS_CMDACT_Msk),
                                IOM0_STATUS_IDLEST_Msk,
                                true);
        if ( status == AM_HAL_STATUS_SUCCESS )
        {
            pIOMState->prefix.s.bEnable = true;
        }
        else
        {
            // Else abort enable session
            IOMn(pIOMState->ui32Module)->SUBMODCTRL_b.SMOD0EN = 0;
            IOMn(pIOMState->ui32Module)->SUBMODCTRL_b.SMOD1EN = 0;
        }
    }

    //
    // We're done, return the status.
    //
    return status;

} // am_hal_iom_enable()

//*****************************************************************************
//
// IOM disable function
//
//*****************************************************************************
uint32_t
am_hal_iom_disable(void *pHandle)
{
  am_hal_iom_state_t *pIOMState = (am_hal_iom_state_t*)pHandle;

#ifndef AM_HAL_DISABLE_API_VALIDATION
  if (!AM_HAL_IOM_CHK_HANDLE(pHandle))
  {
    return AM_HAL_STATUS_INVALID_HANDLE;
  }
#endif // AM_HAL_DISABLE_API_VALIDATION

  if (!pIOMState->prefix.s.bEnable)
  {
    return AM_HAL_STATUS_SUCCESS;
  }

  // Check if we have any pending transactions.
  if (pIOMState->ui32NumPendTransactions)
  {
    return AM_HAL_STATUS_IN_USE;
  }

  //
  // Disable the submodules
  //
  IOMn(pIOMState->ui32Module)->SUBMODCTRL_b.SMOD0EN = 0;
  IOMn(pIOMState->ui32Module)->SUBMODCTRL_b.SMOD1EN = 0;

  am_hal_IOM_CQReset(pHandle);

  pIOMState->prefix.s.bEnable = false;

  //
  // Return the status.
  //
  return AM_HAL_STATUS_SUCCESS;

} // am_hal_iom_disable()

//*****************************************************************************
//
// IOM get status function
//
//*****************************************************************************
uint32_t
am_hal_iom_status_get(void *pHandle, am_hal_iom_status_t *psStatus)
{
    uint32_t ui32Module, ui32IomStat;
    am_hal_iom_state_t *pIOMState = (am_hal_iom_state_t*)pHandle;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    if (!AM_HAL_IOM_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
    if (!psStatus)
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    ui32Module = pIOMState->ui32Module;

    //
    // Begin critical section while we gather status information.
    //
    AM_CRITICAL_BEGIN

    ui32IomStat = IOMn(ui32Module)->STATUS;
    psStatus->bStatIdle   = _FLD2VAL(IOM0_STATUS_IDLEST, ui32IomStat);
    psStatus->bStatErr    = _FLD2VAL(IOM0_STATUS_ERR,    ui32IomStat);
    psStatus->bStatCmdAct = _FLD2VAL(IOM0_STATUS_CMDACT, ui32IomStat);

    //
    // Return all the bitfields of DMASTAT.
    //
    psStatus->ui32DmaStat = IOMn(ui32Module)->DMASTAT;

    psStatus->ui32MaxTransactions = pIOMState->ui32MaxTransactions;
    psStatus->ui32NumPendTransactions = pIOMState->ui32NumPendTransactions;

    //
    // End the critical section.
    //
    AM_CRITICAL_END

    //
    // Return the status.
    //
    return AM_HAL_STATUS_SUCCESS;

} // am_hal_iom_status_get()

//*****************************************************************************
//
// IOM enable interrupts function
//
//*****************************************************************************
uint32_t
am_hal_iom_interrupt_enable(void *pHandle, uint32_t ui32IntMask)
{
    uint32_t ui32Module;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    if (!AM_HAL_IOM_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    ui32Module = ((am_hal_iom_state_t*)pHandle)->ui32Module;

    //
    // Set the interrupt enables according to the mask.
    //
    IOMn(ui32Module)->INTEN |= ui32IntMask;

    //
    // Return the status.
    //
    return AM_HAL_STATUS_SUCCESS;

} // am_hal_iom_interrupt_enable()

//*****************************************************************************
//
// IOM disable interrupts function
//
//*****************************************************************************
uint32_t
am_hal_iom_interrupt_disable(void *pHandle, uint32_t ui32IntMask)
{
    uint32_t ui32Module;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    if (!AM_HAL_IOM_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    ui32Module = ((am_hal_iom_state_t*)pHandle)->ui32Module;

    //
    // Clear the interrupt enables according to the mask.
    //
    IOMn(ui32Module)->INTEN &= ~ui32IntMask;

    //
    // Return the status.
    //
    return AM_HAL_STATUS_SUCCESS;

} // am_hal_iom_interrupt_disable()

//*****************************************************************************
//
// IOM get interrupt status
//
//*****************************************************************************
uint32_t
am_hal_iom_interrupt_status_get(void *pHandle, bool bEnabledOnly,
                                uint32_t *pui32IntStatus)
{
    uint32_t ui32IntStatus;
    uint32_t ui32Module;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    if ( !AM_HAL_IOM_CHK_HANDLE(pHandle) )
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }

    if ( !pui32IntStatus )
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    ui32Module = ((am_hal_iom_state_t*)pHandle)->ui32Module;

    ui32IntStatus = IOMn(ui32Module)->INTSTAT;

    if ( bEnabledOnly )
    {
        ui32IntStatus &= IOMn(ui32Module)->INTEN;
    }

    *pui32IntStatus = ui32IntStatus;

    //
    // Return the status.
    //
    return AM_HAL_STATUS_SUCCESS;

} // am_hal_iom_interrupt_status_get()

//*****************************************************************************
//
// IOM interrupt clear
//
//*****************************************************************************
uint32_t
am_hal_iom_interrupt_clear(void *pHandle, uint32_t ui32IntMask)
{
    uint32_t ui32Module;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    if (!AM_HAL_IOM_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION
    ui32Module = ((am_hal_iom_state_t*)pHandle)->ui32Module;

    //
    // Clear the requested interrupts.
    //
    IOMn(ui32Module)->INTCLR = ui32IntMask;
    *(volatile uint32_t*)(&IOMn(ui32Module)->INTSTAT);
    //
    // Return the status.
    //
    return AM_HAL_STATUS_SUCCESS;

} // am_hal_iom_interrupt_clear()

static void
iom_fdnb_drain_rx_fifo(am_hal_iom_state_t *pIOMState)
{
    uint32_t ui32Module = pIOMState->ui32Module;
    uint32_t i;
    while (pIOMState->sFdNb.ui32RxBytesLeft && (IOMn(ui32Module)->FIFOPTR_b.FIFO1SIZ >= 4))
    {
        uint32_t ui32Word = IOMn(ui32Module)->FIFOPOP;
        uint32_t ui32Chunk = (pIOMState->sFdNb.ui32RxBytesLeft >= 4) ? 4 : pIOMState->sFdNb.ui32RxBytesLeft;
        for (i = 0; i < ui32Chunk; i++)
        {
            *pIOMState->sFdNb.pui8RxBuf++ = (uint8_t)(ui32Word & 0xFF);
            ui32Word >>= 8;
        }
        pIOMState->sFdNb.ui32RxBytesLeft -= ui32Chunk;
    }
}

static void
iom_fdnb_finish(am_hal_iom_state_t *pIOMState, uint32_t ui32Status)
{
    uint32_t ui32Module = pIOMState->ui32Module;
    am_hal_iom_callback_t pfnCallback = pIOMState->sFdNb.pfnCallback;
    void *pCallbackCtxt = pIOMState->sFdNb.pCallbackCtxt;

    pIOMState->sFdNb.bActive = false;
    pIOMState->sFdNb.pui8RxBuf = NULL;
    pIOMState->sFdNb.ui32RxBytesLeft = 0;
    pIOMState->sFdNb.pfnCallback = NULL;
    pIOMState->sFdNb.pCallbackCtxt = NULL;
    pIOMState->ui32NumPendTransactions = 0;
    pIOMState->ui32TxnInt = 0;

    IOMn(ui32Module)->DMACFG_b.DMAEN = 0;
    IOMn(ui32Module)->DMATRIGEN = pIOMState->sFdNb.ui32SavedDmaTrigEn;
    IOMn(ui32Module)->MSPICFG_b.FULLDUP = 0;
    IOM_SET_INTEN(ui32Module, pIOMState->sFdNb.ui32SavedIntCfg);

    if (pfnCallback != NULL)
    {
        pfnCallback(pCallbackCtxt, ui32Status);
    }
}

//*****************************************************************************
//
// IOM interrupt service routine
//
//*****************************************************************************
uint32_t
am_hal_iom_interrupt_service(void *pHandle, uint32_t ui32IntMask)
{
    uint32_t ui32Module;
    uint32_t ui32Status = AM_HAL_STATUS_SUCCESS;
    am_hal_iom_state_t *pIOMState = (am_hal_iom_state_t*)pHandle;
    uint32_t index;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    if (!AM_HAL_IOM_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    ui32Module = pIOMState->ui32Module;

    if (pIOMState->sFdNb.bActive)
    {
        pIOMState->ui32TxnInt |= ui32IntMask;
        iom_fdnb_drain_rx_fifo(pIOMState);

        if (pIOMState->ui32TxnInt & AM_HAL_IOM_INT_ERR)
        {
            ui32Status = internal_iom_get_int_err(ui32Module, pIOMState->ui32TxnInt);
            internal_iom_reset_on_error(pIOMState, pIOMState->ui32TxnInt & AM_HAL_IOM_INT_ERR);
            iom_fdnb_finish(pIOMState, ui32Status);
            return ui32Status;
        }

        if (pIOMState->ui32TxnInt & AM_HAL_IOM_INT_CMDCMP)
        {
            iom_fdnb_drain_rx_fifo(pIOMState);

            if (pIOMState->sFdNb.ui32RxBytesLeft == 0)
            {
                iom_fdnb_finish(pIOMState, AM_HAL_STATUS_SUCCESS);
            }
            else if ((IOMn(ui32Module)->STATUS & (IOM0_STATUS_IDLEST_Msk | IOM0_STATUS_CMDACT_Msk)) == IOM0_STATUS_IDLEST_Msk)
            {
                iom_fdnb_finish(pIOMState, AM_HAL_STATUS_FAIL);
            }
        }
        return AM_HAL_STATUS_SUCCESS;
    }

    if (pIOMState->bHP)
    {
        //
        // Accumulate the INTSTAT for this transaction
        //
        pIOMState->ui32TxnInt |= ui32IntMask;

        //
        // Check for the command completion
        //
        if (pIOMState->ui32TxnInt & (AM_HAL_IOM_INT_CMDCMP | AM_HAL_IOM_INT_DERR))
        {
            //
            // We need to wait for the DMA complete as well
            // Special case for 0 length DMA - by checking the DMAEN register
            //
            if ((IOMn(ui32Module)->DMACFG_b.DMAEN == 0) || (pIOMState->ui32TxnInt & (AM_HAL_IOM_INT_DCMP | AM_HAL_IOM_INT_ERR)))
            {
                // Call the callback
                // Need to determine the error, call the callback with proper status
                pIOMState->ui32LastHPIdxProcessed++;
                pIOMState->ui32NumHPEntries--;
                index = pIOMState->ui32LastHPIdxProcessed % pIOMState->ui32MaxHPTransactions;
                am_hal_iom_dma_entry_t *pDMAEntry = &pIOMState->pHPTransactions[index];
                if ( pDMAEntry->pfnCallback != NULL )
                {
                    pDMAEntry->pfnCallback(pDMAEntry->pCallbackCtxt, internal_iom_get_int_err(ui32Module, pIOMState->ui32TxnInt));
                    pDMAEntry->pfnCallback = NULL;
                }

                if (pIOMState->ui32TxnInt & AM_HAL_IOM_INT_ERR)
                {
                    //
                    // Do Error recovery
                    // Disable DMA
                    //
                    IOMn(ui32Module)->DMACFG_b.DMAEN = 0;

                    //
                    // Clear DMAERR in DMASTAT
                    //
                    IOMn(ui32Module)->DMASTAT = 0;

                    //
                    // Reset Submodule & FIFO
                    //
                    internal_iom_reset_on_error(pIOMState, pIOMState->ui32TxnInt & AM_HAL_IOM_INT_ERR);
                }
                //
                // Post next transaction if queue is not empty
                //
                if (pIOMState->ui32NumHPEntries)
                {
                    //
                    // Initialize the DMA state machine (clear the DMACPL flag).
                    //
                    IOMn(ui32Module)->DMASTAT = 0;
                    //AM_REGn(IOM, ui32Module, INTCLR) = AM_HAL_IOM_INT_ALL;
                    pIOMState->ui32TxnInt = 0;
                    program_dma(pIOMState);
                }
                else
                {
                    pIOMState->bHP = false;
                    // Unpause the CQ
                    // Restore interrupts
                    IOMn(ui32Module)->INTEN &= ~(AM_HAL_IOM_INT_DCMP | AM_HAL_IOM_INT_CMDCMP);
                    // Resume the CQ
                    IOMn(ui32Module)->CQSETCLEAR = AM_HAL_IOM_SC_UNPAUSE_CQ;
                }
            }
        }
        return AM_HAL_STATUS_SUCCESS;
    }
    if (pIOMState->ui32NumPendTransactions)
    {
        am_hal_cmdq_status_t status;

        //
        // Get the current and last indexes.
        //
        if (pIOMState->pCmdQHdl && ((ui32Status = am_hal_cmdq_get_status(pIOMState->pCmdQHdl, &status)) == AM_HAL_STATUS_SUCCESS))
        {
            // For Sequence - this can be updated in the callback
            pIOMState->bRestart = false;
            //
            // Figure out which callbacks need to be handled.
            //
            while ((pIOMState->ui32LastIdxProcessed != status.lastIdxProcessed) && !(pIOMState->bRestart))
            {
                pIOMState->ui32LastIdxProcessed++;
                pIOMState->ui32NumPendTransactions--;
                index = pIOMState->ui32LastIdxProcessed & (AM_HAL_IOM_MAX_PENDING_TRANSACTIONS - 1);
                if ( pIOMState->pfnCallback[index] != NULL )
                {
                    pIOMState->pfnCallback[index](pIOMState->pCallbackCtxt[index], AM_HAL_STATUS_SUCCESS);
                    if (pIOMState->eSeq != AM_HAL_IOM_SEQ_RUNNING)
                    {
                        pIOMState->pfnCallback[index] = NULL;
                    }
                }
            }

            // For Sequence - this can be updated in the callback
            if (!pIOMState->bRestart)
            {
                //
                // Check the CQError - If set it indicates that the current transaction encountered an error
                //
                if (ui32IntMask & AM_HAL_IOM_INT_ERR)
                {
                    // Need to determine the error, call the callback with proper status
                    pIOMState->ui32LastIdxProcessed++;
                    pIOMState->ui32NumPendTransactions--;
                    index = pIOMState->ui32LastIdxProcessed & (AM_HAL_IOM_MAX_PENDING_TRANSACTIONS - 1);
                    if ( pIOMState->pfnCallback[index] != NULL )
                    {
                        pIOMState->pfnCallback[index](pIOMState->pCallbackCtxt[index], internal_iom_get_int_err(ui32Module, ui32IntMask));
                        if (pIOMState->eSeq != AM_HAL_IOM_SEQ_RUNNING)
                        {
                            pIOMState->pfnCallback[index] = NULL;
                        }
                    }

                    //
                    // Do Error recovery
                    // Disable CQ
                    //
                    IOMn(ui32Module)->CQCFG_b.CQEN = 0;

                    //
                    // Disable DMA
                    //
                    IOMn(ui32Module)->DMACFG_b.DMAEN = 0;

                    //
                    // Clear DMAERR in DMASTAT
                    //
                    IOMn(ui32Module)->DMASTAT = 0;

                    //
                    // Reset Submodule & FIFO
                    //
                    internal_iom_reset_on_error(pIOMState, ui32IntMask & AM_HAL_IOM_INT_ERR);

                    //
                    // Move the command queue at next transaction
                    //
                    am_hal_cmdq_error_resume(pIOMState->pCmdQHdl);
                    if (pIOMState->ui32NumPendTransactions)
                    {
                        // Re-enable the CQ
                        am_hal_iom_CQEnable(pIOMState);
                    }
                }
            }

            if (pIOMState->ui32NumPendTransactions == 0)
            {
                //
                // Disable the Command Queue
                //
                am_hal_iom_CQDisable(pHandle);
            }
        }

        if (pIOMState->ui32NumPendTransactions == 0)
        {
            //
            // Clear interrupts
            // Restore IOM interrupts.
            //
            IOM_SET_INTEN(ui32Module, pIOMState->ui32UserIntCfg);
        }
    }

    //
    // Return the status.
    //
    return ui32Status;

} // am_hal_iom_interrupt_service()

//*****************************************************************************
//
// IOM power control function
//
//*****************************************************************************
uint32_t
am_hal_iom_power_ctrl(void *pHandle,
                      am_hal_sysctrl_power_state_e ePowerState,
                      bool bRetainState)
{
    am_hal_iom_state_t *pIOMState = (am_hal_iom_state_t*)pHandle;
    uint32_t ui32Status = AM_HAL_STATUS_SUCCESS;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    if (!AM_HAL_IOM_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    //
    // Decode the requested power state and update IOM operation accordingly.
    //
    switch (ePowerState)
    {
        case AM_HAL_SYSCTRL_WAKE:
            if (bRetainState && !pIOMState->registerState.bValid)
            {
                return AM_HAL_STATUS_INVALID_OPERATION;
            }

            //
            // Enable power control.
            //
            am_hal_pwrctrl_periph_enable((am_hal_pwrctrl_periph_e)(AM_HAL_PWRCTRL_PERIPH_IOM0 + pIOMState->ui32Module));

            if (bRetainState)
            {
                //
                // Restore IOM registers
                IOMn(pIOMState->ui32Module)->FIFOTHR    = pIOMState->registerState.regFIFOTHR;
                IOMn(pIOMState->ui32Module)->CLKCFG     = pIOMState->registerState.regCLKCFG;
                IOMn(pIOMState->ui32Module)->CQADDR     = pIOMState->registerState.regCQADDR;
                IOMn(pIOMState->ui32Module)->CQFLAGS    = pIOMState->registerState.regCQFLAGS;
                IOMn(pIOMState->ui32Module)->CQPAUSEEN  = pIOMState->registerState.regCQPAUSEEN;
                IOMn(pIOMState->ui32Module)->CQCURIDX   = pIOMState->registerState.regCQCURIDX;
                IOMn(pIOMState->ui32Module)->CQENDIDX   = pIOMState->registerState.regCQENDIDX;
                IOMn(pIOMState->ui32Module)->MSPICFG    = pIOMState->registerState.regMSPICFG;
                IOMn(pIOMState->ui32Module)->MI2CCFG    = pIOMState->registerState.regMI2CCFG;
                IOMn(pIOMState->ui32Module)->INTEN      = pIOMState->registerState.regINTEN;
                IOMn(pIOMState->ui32Module)->DMATRIGEN  = pIOMState->registerState.regDMATRIGEN;

                //
                // Set CQCFG next to last - can not set the enable yet
                //
                IOMn(pIOMState->ui32Module)->CQCFG      = pIOMState->registerState.regCQCFG & ~_VAL2FLD(IOM0_CQCFG_CQEN, IOM0_CQCFG_CQEN_EN);
                // Restore SUBMOD last
                IOMn(pIOMState->ui32Module)->SUBMODCTRL = pIOMState->registerState.regSUBMODCTRL;

                if (pIOMState->registerState.regCQCFG & _VAL2FLD(IOM0_CQCFG_CQEN, IOM0_CQCFG_CQEN_EN))
                {
                    am_hal_iom_CQEnable(pIOMState);
                }
                if (pIOMState->prefix.s.bEnable)
                {
                    // Make sure IOM is fully enabled
                    am_hal_delay_us_status_check(1000,
                                (uint32_t)&IOMn(pIOMState->ui32Module)->STATUS,
                                (IOM0_STATUS_IDLEST_Msk | IOM0_STATUS_CMDACT_Msk),
                                IOM0_STATUS_IDLEST_Msk,
                                true);
                }

                pIOMState->registerState.bValid = false;
            }
            //
            // IOM Clock request.
            //
            ui32Status = am_hal_clkmgr_clock_request(AM_HAL_CLKMGR_CLK_ID_HFRC,
                                                        (am_hal_clkmgr_user_id_e)(AM_HAL_CLKMGR_USER_ID_IOM0 + pIOMState->ui32Module));
            if ( ui32Status != AM_HAL_STATUS_SUCCESS )
            {
                return ui32Status;
            }
            break;

        case AM_HAL_SYSCTRL_NORMALSLEEP:
        case AM_HAL_SYSCTRL_DEEPSLEEP:
            // Make sure IOM is not active currently
            if (pIOMState->prefix.s.bEnable &&
                (((IOMn(pIOMState->ui32Module)->STATUS & (IOM0_STATUS_IDLEST_Msk | IOM0_STATUS_CMDACT_Msk)) != IOM0_STATUS_IDLEST_Msk) ||
                   pIOMState->ui32NumPendTransactions))
            {
                return AM_HAL_STATUS_IN_USE;
            }
            if (bRetainState)
            {
                // Save IOM Registers
                pIOMState->registerState.regFIFOTHR    = IOMn(pIOMState->ui32Module)->FIFOTHR;
                pIOMState->registerState.regCLKCFG     = IOMn(pIOMState->ui32Module)->CLKCFG;
                pIOMState->registerState.regSUBMODCTRL = IOMn(pIOMState->ui32Module)->SUBMODCTRL;
                pIOMState->registerState.regCQCFG      = IOMn(pIOMState->ui32Module)->CQCFG;
                pIOMState->registerState.regCQADDR     = IOMn(pIOMState->ui32Module)->CQADDR;
                pIOMState->registerState.regCQFLAGS    = IOMn(pIOMState->ui32Module)->CQFLAGS;
                pIOMState->registerState.regCQPAUSEEN  = IOMn(pIOMState->ui32Module)->CQPAUSEEN;
                pIOMState->registerState.regCQCURIDX   = IOMn(pIOMState->ui32Module)->CQCURIDX;
                pIOMState->registerState.regCQENDIDX   = IOMn(pIOMState->ui32Module)->CQENDIDX;
                pIOMState->registerState.regMSPICFG    = IOMn(pIOMState->ui32Module)->MSPICFG;
                pIOMState->registerState.regMI2CCFG    = IOMn(pIOMState->ui32Module)->MI2CCFG;
                pIOMState->registerState.regINTEN      = IOMn(pIOMState->ui32Module)->INTEN;
                pIOMState->registerState.regDMATRIGEN  = IOMn(pIOMState->ui32Module)->DMATRIGEN;

                if (IOMn(pIOMState->ui32Module)->CQCFG & _VAL2FLD(IOM0_CQCFG_CQEN, IOM0_CQCFG_CQEN_EN))
                {
                    am_hal_iom_CQDisable(pIOMState);
                }

                pIOMState->registerState.bValid = true;
            }

            //
            // Disable the submodules first
            //
            IOMn(pIOMState->ui32Module)->SUBMODCTRL_b.SMOD0EN = 0;
            IOMn(pIOMState->ui32Module)->SUBMODCTRL_b.SMOD1EN = 0;
            //
            // Disable power control.
            //
            am_hal_pwrctrl_periph_disable((am_hal_pwrctrl_periph_e)(AM_HAL_PWRCTRL_PERIPH_IOM0 + pIOMState->ui32Module));

            //
            // IOM clock release
            //
            ui32Status = am_hal_clkmgr_clock_release(AM_HAL_CLKMGR_CLK_ID_HFRC,
                                                        (am_hal_clkmgr_user_id_e)(AM_HAL_CLKMGR_USER_ID_IOM0 + pIOMState->ui32Module));
            if ( ui32Status != AM_HAL_STATUS_SUCCESS )
            {
                return ui32Status;
            }
            break;

        default:
            return AM_HAL_STATUS_INVALID_ARG;
    }

    //
    // Return the status.
    //
    return AM_HAL_STATUS_SUCCESS;

} // am_hal_iom_power_ctrl()

//*****************************************************************************
//
// IOM configuration function.
//
//*****************************************************************************
uint32_t
am_hal_iom_configure(void *pHandle, const am_hal_iom_config_t *psConfig)
{
    uint32_t ui32ClkCfg;
    am_hal_iom_state_t *pIOMState = (am_hal_iom_state_t*)pHandle;
    uint32_t status = AM_HAL_STATUS_SUCCESS;
    uint32_t ui32Module;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    if (!AM_HAL_IOM_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }

    //
    // Validate the parameters
    //
    if ( (pHandle == NULL)      ||
         (psConfig == NULL)     ||
         (pIOMState->ui32Module >= AM_REG_IOM_NUM_MODULES) )
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }
    // Configure not allowed in Enabled state
    if (pIOMState->prefix.s.bEnable)
    {
        return AM_HAL_STATUS_INVALID_OPERATION;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    ui32Module = pIOMState->ui32Module;
    //
    // Save the interface mode and chip select in the global handle.
    //
    pIOMState->eInterfaceMode = psConfig->eInterfaceMode;

    //
    // Set the IOM read/write FIFO thresholds to default values.
    //
    IOMn(ui32Module)->FIFOTHR =
        _VAL2FLD(IOM0_FIFOTHR_FIFORTHR, 16) |
        _VAL2FLD(IOM0_FIFOTHR_FIFOWTHR, 16);

    if ( psConfig->eInterfaceMode == AM_HAL_IOM_SPI_MODE )
    {
#ifndef AM_HAL_DISABLE_API_VALIDATION
        //
        // Validate the SPI mode
        //
        if ( psConfig->eSpiMode > AM_HAL_IOM_SPI_MODE_3 )
        {
            return AM_HAL_STATUS_INVALID_ARG;
        }
        if (psConfig->ui32ClockFreq > AM_HAL_IOM_MAX_FREQ)
        {
            return AM_HAL_STATUS_INVALID_ARG;
        }
#endif // AM_HAL_DISABLE_API_VALIDATION

        //
        // Determine the CLKCFG value for SPI.
        //
        uint64_t ui64ClkCfgRet =
            iom_get_interface_clock_cfg( psConfig->ui32ClockFreq,
                (psConfig->eSpiMode & 2) >> 1,
                psConfig->eClockSelPriority);

        if ( ui64ClkCfgRet == 0)
        {
            return AM_HAL_STATUS_INVALID_OPERATION;
        }
        ui32ClkCfg = (uint32_t)ui64ClkCfgRet;

        //
        // Set the SPI configuration.
        //
        IOMn(ui32Module)->MSPICFG =
            ( ((psConfig->eSpiMode << IOM0_MSPICFG_SPOL_Pos) & (IOM0_MSPICFG_SPHA_Msk | IOM0_MSPICFG_SPOL_Msk))  |
             _VAL2FLD(IOM0_MSPICFG_FULLDUP, 0)                              |
             _VAL2FLD(IOM0_MSPICFG_WTFC,    IOM0_MSPICFG_WTFC_DIS)          |
             _VAL2FLD(IOM0_MSPICFG_RDFC,    IOM0_MSPICFG_RDFC_DIS)          |
             _VAL2FLD(IOM0_MSPICFG_MOSIINV, IOM0_MSPICFG_MOSIINV_NORMAL)    |
             _VAL2FLD(IOM0_MSPICFG_WTFCIRQ, IOM0_MSPICFG_WTFCIRQ_MISO)      |
             _VAL2FLD(IOM0_MSPICFG_WTFCPOL, IOM0_MSPICFG_WTFCPOL_HIGH)      |
             _VAL2FLD(IOM0_MSPICFG_RDFCPOL, IOM0_MSPICFG_RDFCPOL_HIGH)      |
             _VAL2FLD(IOM0_MSPICFG_SPILSB,  IOM0_MSPICFG_SPILSB_MSB)        |
             _VAL2FLD(IOM0_MSPICFG_DINDLY,  0)                              |
             _VAL2FLD(IOM0_MSPICFG_DOUTDLY, 0)                              |
             _VAL2FLD(IOM0_MSPICFG_MSPIRST, 0) );
    }
    else if ( psConfig->eInterfaceMode == AM_HAL_IOM_I2C_MODE )
    {
        switch (psConfig->ui32ClockFreq)
        {
            case AM_HAL_IOM_100KHZ:
                //
                // settings below should give ~100 kHz
                //
                ui32ClkCfg = _VAL2FLD(IOM0_CLKCFG_TOTPER, 0x77)                     |
                             _VAL2FLD(IOM0_CLKCFG_LOWPER, 0x3B)                     |
                             _VAL2FLD(IOM0_CLKCFG_DIVEN, IOM0_CLKCFG_DIVEN_EN)      |
                             _VAL2FLD(IOM0_CLKCFG_DIV3, IOM0_CLKCFG_DIV3_DIS)       |
                             _VAL2FLD(IOM0_CLKCFG_FSEL, IOM0_CLKCFG_FSEL_HFRC_24MHZ) |
                             _VAL2FLD(IOM0_CLKCFG_IOCLKEN, 1);
                IOMn(ui32Module)->MI2CCFG = _VAL2FLD(IOM0_MI2CCFG_STRDIS, 0)                            |
                                            _VAL2FLD(IOM0_MI2CCFG_SMPCNT, 3)                            |
                                            _VAL2FLD(IOM0_MI2CCFG_SDAENDLY, 15)                         |
                                            _VAL2FLD(IOM0_MI2CCFG_SCLENDLY, 0)                          |
                                            _VAL2FLD(IOM0_MI2CCFG_MI2CRST, 1)                           |
                                            _VAL2FLD(IOM0_MI2CCFG_SDADLY, 3)                            |
                                            _VAL2FLD(IOM0_MI2CCFG_ARBEN, IOM0_MI2CCFG_ARBEN_ARBDISABLE)     |
                                            _VAL2FLD(IOM0_MI2CCFG_I2CLSB, IOM0_MI2CCFG_I2CLSB_MSBFIRST) |
                                            _VAL2FLD(IOM0_MI2CCFG_ADDRSZ, IOM0_MI2CCFG_ADDRSZ_ADDRSZ7);
                break;
            case AM_HAL_IOM_400KHZ:
                //
                // settings below should give ~400 kHz
                //
                ui32ClkCfg = _VAL2FLD(IOM0_CLKCFG_TOTPER, 0x1D)                         |
                             _VAL2FLD(IOM0_CLKCFG_LOWPER, 0x0E)                         |
                             _VAL2FLD(IOM0_CLKCFG_DIVEN, IOM0_CLKCFG_DIVEN_EN)          |
                             _VAL2FLD(IOM0_CLKCFG_DIV3, IOM0_CLKCFG_DIV3_DIS)           |
                             _VAL2FLD(IOM0_CLKCFG_FSEL, IOM0_CLKCFG_FSEL_HFRC_24MHZ)    |
                             _VAL2FLD(IOM0_CLKCFG_IOCLKEN, 1);
                IOMn(ui32Module)->MI2CCFG = _VAL2FLD(IOM0_MI2CCFG_STRDIS, 0)                            |
                                            _VAL2FLD(IOM0_MI2CCFG_SMPCNT, 3)                            |
                                            _VAL2FLD(IOM0_MI2CCFG_SDAENDLY, 15)                         |
                                            _VAL2FLD(IOM0_MI2CCFG_SCLENDLY, 2)                          |
                                            _VAL2FLD(IOM0_MI2CCFG_MI2CRST, 1)                           |
                                            _VAL2FLD(IOM0_MI2CCFG_SDADLY, 3)                            |
                                            _VAL2FLD(IOM0_MI2CCFG_ARBEN, IOM0_MI2CCFG_ARBEN_ARBDISABLE)     |
                                            _VAL2FLD(IOM0_MI2CCFG_I2CLSB, IOM0_MI2CCFG_I2CLSB_MSBFIRST) |
                                            _VAL2FLD(IOM0_MI2CCFG_ADDRSZ, IOM0_MI2CCFG_ADDRSZ_ADDRSZ7);
                break;
            case AM_HAL_IOM_1MHZ:
                //
                // The settings below should give ~860 kHz
                //
                ui32ClkCfg = _VAL2FLD(IOM0_CLKCFG_TOTPER, 0x0B)                         |
                             _VAL2FLD(IOM0_CLKCFG_LOWPER, 0x05)                         |
                             _VAL2FLD(IOM0_CLKCFG_DIVEN, IOM0_CLKCFG_DIVEN_EN)          |
                             _VAL2FLD(IOM0_CLKCFG_DIV3, IOM0_CLKCFG_DIV3_DIS)           |
                             _VAL2FLD(IOM0_CLKCFG_FSEL, IOM0_CLKCFG_FSEL_HFRC_24MHZ)    |
                             _VAL2FLD(IOM0_CLKCFG_IOCLKEN, 1);
                IOMn(ui32Module)->MI2CCFG = _VAL2FLD(IOM0_MI2CCFG_STRDIS, 0)                            |
                                            _VAL2FLD(IOM0_MI2CCFG_SMPCNT, 0x2)                          |
                                            _VAL2FLD(IOM0_MI2CCFG_SDAENDLY, 3)                          |
                                            _VAL2FLD(IOM0_MI2CCFG_SCLENDLY, 0)                          |
                                            _VAL2FLD(IOM0_MI2CCFG_MI2CRST, 1)                           |
                                            _VAL2FLD(IOM0_MI2CCFG_SDADLY, 0)                            |
                                            _VAL2FLD(IOM0_MI2CCFG_ARBEN, IOM0_MI2CCFG_ARBEN_ARBDISABLE) |
                                            _VAL2FLD(IOM0_MI2CCFG_I2CLSB, IOM0_MI2CCFG_I2CLSB_MSBFIRST) |
                                            _VAL2FLD(IOM0_MI2CCFG_ADDRSZ, IOM0_MI2CCFG_ADDRSZ_ADDRSZ7);
                break;
            default:
                return AM_HAL_STATUS_INVALID_ARG;
        }
    }
    else
    {
        return AM_HAL_STATUS_OUT_OF_RANGE;
    }

    //
    // Enable and set the clock configuration.
    //
    ui32ClkCfg |= _VAL2FLD(IOM0_CLKCFG_IOCLKEN, 1);
    IOMn(ui32Module)->CLKCFG = ui32ClkCfg;

    //
    // Get the current clock frequency and calculate bit time based on it.
    // NOTE: This will work only if I2C freq <= 1MHz, as the case currently
    //
    pIOMState->ui32BitTimeUs = 1000000 / psConfig->ui32ClockFreq;

    //
    // Set the delay timeout value to the default maximum value.
    //
    pIOMState->waitTimeout = 1000;

    pIOMState->pNBTxnBuf = psConfig->pNBTxnBuf;
    pIOMState->ui32NBTxnBufLength = psConfig->ui32NBTxnBufLength;
    if (pIOMState->pNBTxnBuf)
    {
        pIOMState->bCmdQInTCM = (((uint32_t)pIOMState->pNBTxnBuf + pIOMState->ui32NBTxnBufLength * 4) < SSRAM_BASEADDR) ? true: false;
        //
        // Worst case minimum CQ entries that can be accomodated in provided buffer
        // Need to account for the wrap
        //
        pIOMState->ui32MaxPending = ((pIOMState->ui32NBTxnBufLength - 8) * 4 / AM_HAL_IOM_CQ_ENTRY_SIZE);
        if (pIOMState->ui32MaxPending > AM_HAL_IOM_MAX_PENDING_TRANSACTIONS)
        {
            pIOMState->ui32MaxPending = AM_HAL_IOM_MAX_PENDING_TRANSACTIONS;
        }
    }

    // Disable the DCX
    for (uint8_t i = 0; i < AM_HAL_IOM_MAX_CS_SPI; i++)
    {
        pIOMState->dcx[i] = 0;
    }

    //
    // Return the status.
    //
    return status;

} // am_hal_iom_configure()

//*****************************************************************************
//
// IOM blocking transfer function
//
//*****************************************************************************
uint32_t
am_hal_iom_blocking_transfer(void *pHandle,
                             am_hal_iom_transfer_t *psTransaction)
{
    uint32_t ui32Cmd, ui32OffsetCnt, ui32Dir, ui32Cont;
    uint64_t ui64Offset;
    uint32_t ui32FifoRem, ui32FifoSiz;
    uint32_t ui32Bytes;
    uint32_t ui32IntConfig;
    const uint32_t* pui32TxBuffer;
    uint32_t *pui32RxBuffer;
    am_hal_iom_state_t *pIOMState = (am_hal_iom_state_t*)pHandle;
    uint32_t ui32Module;
    uint32_t ui32Status = AM_HAL_STATUS_SUCCESS;
    bool     bCmdCmp = false;
    uint32_t numWait = 0;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    if ( !AM_HAL_IOM_CHK_HANDLE(pHandle) )
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }

    if ( !psTransaction )
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }

    if (psTransaction->eDirection > AM_HAL_IOM_RX)
    {
        return AM_HAL_STATUS_INVALID_OPERATION;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    ui32Bytes = psTransaction->ui32NumBytes;
    if ( ui32Bytes == 0 )
    {
        //
        // Only TX is supported for 0-length transactions. A 0-length
        // transfer presumes that only an offset value is being written.
        //
        psTransaction->eDirection = AM_HAL_IOM_TX;
    }

#ifndef AM_HAL_DISABLE_API_VALIDATION
    //
    // Validate parameters
    //
    ui32Status = validate_transaction(pIOMState, psTransaction, true);

    if (ui32Status != AM_HAL_STATUS_SUCCESS)
    {
        return ui32Status;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION
    if (pIOMState->eSeq == AM_HAL_IOM_SEQ_RUNNING)
    {
        // Dynamic additions to sequence not allowed
        return AM_HAL_STATUS_INVALID_OPERATION;
    }

    ui32Module = pIOMState->ui32Module;
    ui64Offset = psTransaction->ui64Instr;
    ui32OffsetCnt = psTransaction->ui32InstrLen;
    ui32Dir = psTransaction->eDirection;
    ui32Cont = psTransaction->bContinue ? 1 : 0;

    //
    // Make sure any previous non-blocking transfers have completed.
    //
    ui32Status = am_hal_delay_us_status_check(pIOMState->waitTimeout,
                                                 (uint32_t)&pIOMState->ui32NumPendTransactions,
                                                 0xFFFFFFFF,
                                                 0,
                                                 true);
    if ( ui32Status != AM_HAL_STATUS_SUCCESS )
    {
        return ui32Status;
    }

    //
    // Make sure any previous blocking transfer has been completed.
    // This check is required to make sure previous transaction has cleared if the blocking call
    // finished with a timeout
    //
    ui32Status = am_hal_delay_us_status_check(pIOMState->waitTimeout,
                            (uint32_t)&IOMn(ui32Module)->STATUS,
                            (IOM0_STATUS_IDLEST_Msk | IOM0_STATUS_CMDACT_Msk),
                            IOM0_STATUS_IDLEST_Msk,
                            true);

    if ( ui32Status != AM_HAL_STATUS_SUCCESS )
    {
        return ui32Status;
    }

    //
    // Disable interrupts so that we don't get any undesired interrupts.
    //
    ui32IntConfig = IOMn(ui32Module)->INTEN;
    //
    // Disable IOM interrupts as we'll be polling
    //
    IOMn(ui32Module)->INTEN = 0;
    //
    // Disable DMA - in case the last transaction was DMA
    // For CQ - we disable DMA only at the start of next transaction
    //
    IOMn(ui32Module)->DMACFG_b.DMAEN = 0;

    //
    // Clear interrupts
    //
    IOMn(ui32Module)->INTCLR = AM_HAL_IOM_INT_ALL;

    //
    // Set the dev addr (either 7 or 10 bit as configured in MI2CCFG).
    //
    IOMn(ui32Module)->DEVCFG = psTransaction->uPeerInfo.ui32I2CDevAddr;

    // Set the DCX.
    IOMn(ui32Module)->DCXCTRL = (pIOMState->eInterfaceMode == AM_HAL_IOM_SPI_MODE)  ? pIOMState->dcx[psTransaction->uPeerInfo.ui32SpiChipSelect] : 0;

    //
    // Build the CMD value
    //

    ui32Cmd = pIOMState->eInterfaceMode == AM_HAL_IOM_SPI_MODE ?
              psTransaction->uPeerInfo.ui32SpiChipSelect : 0;
    ui32Cmd = build_cmd(ui32Cmd, ui32Dir,  ui32Cont, ui64Offset, ui32OffsetCnt, ui32Bytes);

    //
    // Set the OFFSETHI register.
    //
    IOMn(ui32Module)->OFFSETHI = (uint32_t)(ui64Offset >> 8);

    ui32Bytes = psTransaction->ui32NumBytes;

    if ( ui32Dir == AM_HAL_IOM_RX )
    {
        pui32RxBuffer = psTransaction->pui32RxBuffer;
        //
        // Start the transfer
        //
        IOMn(ui32Module)->CMD = ui32Cmd;

        //
        // Start a loop to catch the Rx data.
        //
        while ( ui32Bytes )
        {
            //
            // Limit the wait to reasonable limit - instead of blocking forever
            //
            numWait = 0;
            while ((ui32FifoSiz = IOMn(ui32Module)->FIFOPTR_b.FIFO1SIZ) < 4)
            {
                if (numWait++ < AM_HAL_IOM_MAX_BLOCKING_WAIT)
                {
                    if (bCmdCmp && (ui32Bytes > ui32FifoSiz))
                    {
                        //
                        // No more data expected. Get out of the loop
                        //
                        break;
                    }
                    am_hal_delay_us(1);
                }
                else
                {
                    //
                    // We've waited long enough - get out!
                    //
                    break;
                }
                bCmdCmp = IOMn(ui32Module)->INTSTAT_b.CMDCMP;
            }
            if (ui32FifoSiz < 4)
            {
                //
                // Something went wrong - get out and report failure
                //
                break;
            }

            while ((ui32FifoSiz >= 4) && ui32Bytes)
            {
                //
                // Safe to read the FIFO, read 4 bytes
                //
                uint32_t ui32Read;
                ui32Read = IOMn(ui32Module)->FIFOPOP;
#if MANUAL_POP
                IOMn(ui32Module)->FIFOPOP = 0x11111111;
#endif
                ui32FifoSiz -= 4;
                if (ui32Bytes >= 4)
                {
                    *pui32RxBuffer++ = ui32Read;
                    ui32Bytes -= 4;
                }
                else
                {
                    // Copy byte by byte - so as to not corrupt the rest of the buffer
                    uint8_t *pui8Buffer = (uint8_t *)pui32RxBuffer;
                    do
                    {
                        *pui8Buffer++ = ui32Read & 0xFF;
                        ui32Read >>= 8;
                    } while (--ui32Bytes);

                }
            }
        }
    }
    else if ( ui32Dir == AM_HAL_IOM_TX )
    {
        pui32TxBuffer = psTransaction->pui32TxBuffer;
        // Write data to FIFO first - before starting the transfer

        ui32FifoRem = IOMn(ui32Module)->FIFOPTR_b.FIFO0REM;
        while ((ui32FifoRem >= 4) && ui32Bytes)
        {
            IOMn(ui32Module)->FIFOPUSH = *pui32TxBuffer++;
            ui32FifoRem -= 4;
            if (ui32Bytes >= 4)
            {
                ui32Bytes -= 4;
            }
            else
            {
                ui32Bytes = 0;
            }
        }

        //
        // Start the transfer
        //
        IOMn(ui32Module)->CMD = ui32Cmd;
        //
        // Keep looping until we're out of bytes to send or command complete (error).
        //
        while (ui32Bytes)
        {
            //
            // Limit the wait to reasonable limit - instead of blocking forever
            //
            numWait = 0;
            while ((ui32FifoRem = IOMn(ui32Module)->FIFOPTR_b.FIFO0REM) < 4)
            {
                bCmdCmp = IOMn(ui32Module)->INTSTAT_b.CMDCMP;
                if (bCmdCmp || (numWait++ >= AM_HAL_IOM_MAX_BLOCKING_WAIT))
                {
                    //
                    // FIFO not expected to change any more - get out
                    //
                    break;
                }
                else
                {
                    am_hal_delay_us(1);
                }
            }
            if (bCmdCmp || (ui32FifoRem < 4))
            {
                //
                // Something went wrong - bail out
                //
                break;
            }

            while ((ui32FifoRem >= 4) && ui32Bytes)
            {
                IOMn(ui32Module)->FIFOPUSH = *pui32TxBuffer++;
                ui32FifoRem -= 4;
                if (ui32Bytes >= 4)
                {
                    ui32Bytes -= 4;
                }
                else
                {
                    ui32Bytes = 0;
                }
            }
        }
    }

    //
    // Make sure transfer is completed.
    //
    ui32Status = am_hal_delay_us_status_check(AM_HAL_IOM_MAX_BLOCKING_WAIT,
                            (uint32_t)&IOMn(ui32Module)->STATUS,
                            (IOM0_STATUS_IDLEST_Msk | IOM0_STATUS_CMDACT_Msk),
                            IOM0_STATUS_IDLEST_Msk,
                            true);

    if ( ui32Status == AM_HAL_STATUS_SUCCESS )
    {
        ui32Status = internal_iom_get_int_err(ui32Module, 0);

        if (ui32Status == AM_HAL_STATUS_SUCCESS)
        {
            if (ui32Bytes)
            {
                // Indicates transaction did not finish for some reason
                ui32Status = AM_HAL_STATUS_FAIL;
            }
        }
    }

    if ( ui32Status != AM_HAL_STATUS_SUCCESS )
    {
        // Do Error recovery
        // Reset Submodule & FIFO
        internal_iom_reset_on_error(pIOMState, IOMn(ui32Module)->INTSTAT);
    }

    //
    // Clear interrupts
    // Re-enable IOM interrupts.
    //
    IOMn(ui32Module)->INTCLR = AM_HAL_IOM_INT_ALL;
    IOMn(ui32Module)->INTEN = ui32IntConfig;

    //
    // Return the status.
    //
    return ui32Status;

} // am_hal_iom_blocking_transfer()

//*****************************************************************************
//
// IOM non-blocking transfer function
//
//*****************************************************************************
uint32_t
am_hal_iom_nonblocking_transfer(void *pHandle,
                                am_hal_iom_transfer_t *psTransaction,
                                am_hal_iom_callback_t pfnCallback,
                                void *pCallbackCtxt)
{
    am_hal_iom_state_t *pIOMState = (am_hal_iom_state_t*)pHandle;
    uint32_t ui32Status = AM_HAL_STATUS_SUCCESS;
    uint32_t ui32NumPend;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    if ( !AM_HAL_IOM_CHK_HANDLE(pHandle) )
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }

    if ( !psTransaction )
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }

    if (psTransaction->eDirection > AM_HAL_IOM_RX)
    {
        return AM_HAL_STATUS_INVALID_OPERATION;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    if ( psTransaction->ui32NumBytes == 0 )
    {
        //
        // Only TX is supported for 0-length transactions. A 0-length
        // transfer presumes that only an offset value is being written.
        //
        psTransaction->eDirection = AM_HAL_IOM_TX;
    }

#ifndef AM_HAL_DISABLE_API_VALIDATION
    //
    // Validate parameters
    //
    ui32Status = validate_transaction(pIOMState, psTransaction, false);

    if (ui32Status != AM_HAL_STATUS_SUCCESS)
    {
        return ui32Status;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    am_hal_iom_callback_t pfnCallback1 = pfnCallback;
    if (!pIOMState->pCmdQHdl)
    {
        return AM_HAL_STATUS_INVALID_OPERATION;
    }
    if (pIOMState->eSeq == AM_HAL_IOM_SEQ_RUNNING)
    {
        // Dynamic additions to sequence not allowed
        return AM_HAL_STATUS_INVALID_OPERATION;
    }
    if (pIOMState->block && (psTransaction->ui32PauseCondition != 0))
    {
        // Paused operations not allowed in block mode
        return AM_HAL_STATUS_INVALID_OPERATION;
    }
    if (!pfnCallback1 && !pIOMState->block && (pIOMState->eSeq == AM_HAL_IOM_SEQ_NONE) &&
        (pIOMState->ui32NumUnSolicited >= (pIOMState->ui32MaxPending / 2)))
    {
        // Need to schedule a dummy callback, to ensure ui32NumPendTransactions get updated in ISR
        pfnCallback1 = iom_dummy_callback;
    }
    //
    // DMA defaults to using the Command Queue
    //
    ui32Status = am_hal_iom_CQAddTransaction(pHandle, psTransaction, pfnCallback1, pCallbackCtxt);

    if (ui32Status == AM_HAL_STATUS_SUCCESS)
    {
        uint32_t ui32Critical = 0;

        //
        // Need to protect access of ui32NumPendTransactions as it is accessed
        // from ISR as well
        //
        // Start a critical section.
        //
        ui32Critical = am_hal_interrupt_master_disable();

        //
        // Register for interrupt only if there is a callback
        //
        ui32Status = am_hal_cmdq_post_block(pIOMState->pCmdQHdl, pfnCallback1);
        if (ui32Status == AM_HAL_STATUS_SUCCESS)
        {
            ui32NumPend = pIOMState->ui32NumPendTransactions++;
            pIOMState->ui32NumSeqTransactions++;
            if (pfnCallback)
            {
                pIOMState->bAutonomous = false;
                pIOMState->ui32NumUnSolicited = 0;
            }
            else
            {
                if (pfnCallback1)
                {
                    // This implies we have already scheduled a dummy callback
                    pIOMState->ui32NumUnSolicited = 0;
                }
                else
                {
                    pIOMState->ui32NumUnSolicited++;
                }
            }
            if (0 == ui32NumPend)
            {
                pIOMState->ui32UserIntCfg = IOMn(pIOMState->ui32Module)->INTEN;
                IOM_SET_INTEN(pIOMState->ui32Module, AM_HAL_IOM_INT_CQMODE);
                am_hal_iom_CQEnable(pIOMState);
            }

        }
        else
        {
            am_hal_cmdq_release_block(pIOMState->pCmdQHdl);
        }
        //
        // End the critical section.
        //
        am_hal_interrupt_master_set(ui32Critical);
    }

    //
    // Return the status.
    //
    return ui32Status;

} // am_hal_iom_nonblocking_transfer()

//*****************************************************************************
//
// Perform a simple full-duplex transaction to the SPI interface.
// This function performs SPI full-duplex operation to a selected SPI device.
//
//*****************************************************************************
uint32_t
am_hal_iom_spi_blocking_fullduplex(void *pHandle,
                                   am_hal_iom_transfer_t *psTransaction)
{
    uint32_t ui32Cmd, ui32OffsetCnt, ui32Dir, ui32Cont;
    uint64_t ui64Offset;
    uint32_t ui32FifoRem, ui32FifoSiz;
    uint32_t ui32Bytes;
    uint32_t ui32RxBytes;
    uint32_t ui32IntConfig;
    const uint32_t *pui32TxBuffer;
    uint32_t *pui32RxBuffer;
    am_hal_iom_state_t *pIOMState = (am_hal_iom_state_t*)pHandle;
    uint32_t ui32Module;
    uint32_t ui32Status = AM_HAL_STATUS_SUCCESS;
    bool     bCmdCmp = false;
    uint32_t numWait = 0;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    if ( !AM_HAL_IOM_CHK_HANDLE(pHandle) )
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }

    if ( !psTransaction )
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }

    if ( psTransaction->eDirection != AM_HAL_IOM_FULLDUPLEX )
    {
        return AM_HAL_STATUS_INVALID_OPERATION;
    }

    //
    // Validate parameters
    //
    ui32Status = validate_transaction(pIOMState, psTransaction, true);

    if ( ui32Status != AM_HAL_STATUS_SUCCESS )
    {
        return ui32Status;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION
    if (pIOMState->eSeq == AM_HAL_IOM_SEQ_RUNNING)
    {
        // Dynamic additions to sequence not allowed
        return AM_HAL_STATUS_INVALID_OPERATION;
    }

    ui32Module = pIOMState->ui32Module;
    ui64Offset = psTransaction->ui64Instr;
    ui32OffsetCnt = psTransaction->ui32InstrLen;
    ui32Bytes = psTransaction->ui32NumBytes;
    ui32Dir = psTransaction->eDirection;
    ui32Cont = psTransaction->bContinue ? 1 : 0;
    pui32RxBuffer = psTransaction->pui32RxBuffer;
    pui32TxBuffer = psTransaction->pui32TxBuffer;

    //
    // Make sure any previous non-blocking transfers have completed.
    //
    ui32Status = am_hal_delay_us_status_check(pIOMState->waitTimeout,
                                                 (uint32_t)&pIOMState->ui32NumPendTransactions,
                                                 0xFFFFFFFF,
                                                 0,
                                                 true);
    if ( ui32Status != AM_HAL_STATUS_SUCCESS )
    {
        return ui32Status;
    }

    //
    // Make sure any previous blocking transfer has been completed.
    // This check is required to make sure previous transaction has cleared if the blocking call
    // finished with a timeout
    //
    ui32Status = am_hal_delay_us_status_check(pIOMState->waitTimeout,
                            (uint32_t)&IOMn(ui32Module)->STATUS,
                            (IOM0_STATUS_IDLEST_Msk | IOM0_STATUS_CMDACT_Msk),
                            IOM0_STATUS_IDLEST_Msk,
                            true);

    if ( ui32Status != AM_HAL_STATUS_SUCCESS )
    {
        return ui32Status;
    }

    //
    // Disable interrupts so that we don't get any undesired interrupts.
    //
    ui32IntConfig = IOMn(ui32Module)->INTEN;

    //
    // Disable IOM interrupts as we'll be polling
    //
    IOMn(ui32Module)->INTEN = 0;
    //
    // Disable DMA - in case the last transaction was DMA
    // For CQ - we disable DMA only at the start of next transaction
    //
    IOMn(ui32Module)->DMACFG_b.DMAEN = 0;

    //
    // Clear interrupts
    //
    IOMn(ui32Module)->INTCLR = AM_HAL_IOM_INT_ALL;

    //
    // Set the dev addr (either 7 or 10 bit as configured in MI2CCFG).
    //
    IOMn(ui32Module)->DEVCFG = psTransaction->uPeerInfo.ui32I2CDevAddr;

    // Set the DCX
    IOMn(ui32Module)->DCXCTRL_b.DCXSEL = pIOMState->dcx[psTransaction->uPeerInfo.ui32SpiChipSelect];
    IOMn(ui32Module)->DCXCTRL_b.DCXEN = 1;

    //
    // Build the CMD value
    //
    ui32Cmd = pIOMState->eInterfaceMode == AM_HAL_IOM_SPI_MODE ?
              psTransaction->uPeerInfo.ui32SpiChipSelect : 0;
    ui32Cmd = build_cmd(ui32Cmd, ui32Dir,  ui32Cont, ui64Offset, ui32OffsetCnt, ui32Bytes);

    //
    // Set the OFFSETHI register.
    //
    IOMn(ui32Module)->OFFSETHI = (uint32_t)(ui64Offset >> 8);

    //
    // Set FULLDUPLEX mode
    //
    IOMn(ui32Module)->MSPICFG |= _VAL2FLD(IOM0_MSPICFG_FULLDUP, 1);

    //
    // Start the transfer
    //
    IOMn(ui32Module)->CMD = ui32Cmd;

    ui32Bytes = psTransaction->ui32NumBytes;
    ui32RxBytes = ui32Bytes;

    //
    // Start a loop to catch the Rx data.
    //
    //
    // Keep looping until we're out of bytes to send or command complete (error).
    //
    while (!bCmdCmp && (ui32Bytes || ui32RxBytes))
    {
        //
        // Limit the wait to reasonable limit - instead of blocking forever
        //
        numWait = 0;
        ui32FifoRem = IOMn(ui32Module)->FIFOPTR_b.FIFO0REM;
        ui32FifoSiz = IOMn(ui32Module)->FIFOPTR_b.FIFO1SIZ;

        while ((ui32FifoRem < 4) &&
               (ui32FifoSiz < 4))
        {
            if (numWait++ < AM_HAL_IOM_MAX_BLOCKING_WAIT)
            {
                if (bCmdCmp && (ui32RxBytes > ui32FifoSiz))
                {
                    //
                    // No more data expected. Get out of the loop
                    //
                    break;
                }
                am_hal_delay_us(1);
            }
            else
            {
                //
                // We've waited long enough - get out!
                //
                break;
            }
            bCmdCmp     = IOMn(ui32Module)->INTSTAT_b.CMDCMP;
            ui32FifoRem = IOMn(ui32Module)->FIFOPTR_b.FIFO0REM;
            ui32FifoSiz = IOMn(ui32Module)->FIFOPTR_b.FIFO1SIZ;
        }
        if ((ui32FifoRem < 4) && (ui32FifoSiz < 4))
        {
            //
            // Something went wrong - bail out
            //
            break;
        }

        while ((ui32FifoRem >= 4) && ui32Bytes)
        {
            IOMn(ui32Module)->FIFOPUSH = *pui32TxBuffer++;
            ui32FifoRem -= 4;
            if (ui32Bytes >= 4)
            {
                ui32Bytes -= 4;
            }
            else
            {
                ui32Bytes = 0;
            }
        }
        while ((ui32FifoSiz >= 4) && ui32RxBytes)
        {
            //
            // Safe to read the FIFO, read 4 bytes
            //
            uint32_t ui32Read;
            ui32Read = IOMn(ui32Module)->FIFOPOP;
#if MANUAL_POP
            IOMn(ui32Module)->FIFOPOP = 0x11111111;
#endif
            ui32FifoSiz -= 4;
            if (ui32RxBytes >= 4)
            {
                *pui32RxBuffer++ = ui32Read;
                ui32RxBytes -= 4;
            }
            else
            {
                // Copy byte by byte - so as to not corrupt the rest of the buffer
                uint8_t *pui8Buffer = (uint8_t *)pui32RxBuffer;
                do
                {
                    *pui8Buffer++ = ui32Read & 0xFF;
                    ui32Read >>= 8;
                } while (--ui32RxBytes);
            }
        }
    }

    //
    // Make sure transfer is completed.
    //
    ui32Status = am_hal_delay_us_status_check(AM_HAL_IOM_MAX_BLOCKING_WAIT,
                            (uint32_t)&IOMn(ui32Module)->STATUS,
                            (IOM0_STATUS_IDLEST_Msk | IOM0_STATUS_CMDACT_Msk),
                            IOM0_STATUS_IDLEST_Msk,
                            true);

    if ( ui32Status != AM_HAL_STATUS_SUCCESS )
    {
        IOMn(ui32Module)->MSPICFG_b.FULLDUP = 0;
        return ui32Status;
    }

    ui32Status = internal_iom_get_int_err(ui32Module, 0);

    if (ui32Status == AM_HAL_STATUS_SUCCESS)
    {
            if (ui32Bytes || ui32RxBytes)
        {
            // Indicates transaction did not finish for some reason
            ui32Status = AM_HAL_STATUS_FAIL;
        }
    }
    else
    {
        // Do Error recovery
        // Reset Submodule & FIFO
        internal_iom_reset_on_error(pIOMState, IOMn(ui32Module)->INTSTAT);
    }

    //
    // Clear interrupts
    // Re-enable IOM interrupts.
    //
    IOMn(ui32Module)->INTCLR = AM_HAL_IOM_INT_ALL;
    IOMn(ui32Module)->INTEN = ui32IntConfig;

    //
    // Quit FULLDUPLEX mode
    //
    IOMn(ui32Module)->MSPICFG_b.FULLDUP = 0;

    //
    // Return the status.
    //
    return ui32Status;

}

//*****************************************************************************
//
//! Perform a non-blocking full-duplex transaction to the SPI interface.
//! TX uses DMA, RX is drained by FIFO interrupts.
//!
//*****************************************************************************
uint32_t
am_hal_iom_spi_nonblocking_fullduplex(void *pHandle,
                                      am_hal_iom_transfer_t *psTransaction,
                                      am_hal_iom_callback_t pfnCallback,
                                      void *pCallbackCtxt)
{
    am_hal_iom_state_t *pIOMState = (am_hal_iom_state_t *)pHandle;
    uint32_t ui32Module;
    uint32_t ui32Cmd;
    uint32_t ui32Critical;
    uint32_t ui32Status = AM_HAL_STATUS_SUCCESS;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    if (!AM_HAL_IOM_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }

    if (!psTransaction)
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }

    if (psTransaction->eDirection != AM_HAL_IOM_FULLDUPLEX)
    {
        return AM_HAL_STATUS_INVALID_OPERATION;
    }

    if (psTransaction->ui32NumBytes == 0)
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    if (pIOMState->eInterfaceMode != AM_HAL_IOM_SPI_MODE)
    {
        return AM_HAL_STATUS_INVALID_OPERATION;
    }

    if (pIOMState->eSeq == AM_HAL_IOM_SEQ_RUNNING)
    {
        return AM_HAL_STATUS_INVALID_OPERATION;
    }

#ifndef AM_HAL_DISABLE_API_VALIDATION
    ui32Status = validate_transaction(pIOMState, psTransaction, true);
    if (ui32Status != AM_HAL_STATUS_SUCCESS)
    {
        return ui32Status;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    ui32Module = pIOMState->ui32Module;
    ui32Critical = am_hal_interrupt_master_disable();

    if (pIOMState->sFdNb.bActive || pIOMState->bHP || pIOMState->ui32NumPendTransactions)
    {
        ui32Status = AM_HAL_STATUS_INVALID_OPERATION;
        goto fdnb_exit;
    }

    if ((IOMn(ui32Module)->STATUS & (IOM0_STATUS_IDLEST_Msk | IOM0_STATUS_CMDACT_Msk)) != IOM0_STATUS_IDLEST_Msk)
    {
        ui32Status = AM_HAL_STATUS_IN_USE;
        goto fdnb_exit;
    }

    pIOMState->sFdNb.ui32SavedIntCfg = IOMn(ui32Module)->INTEN;
    pIOMState->sFdNb.ui32SavedDmaTrigEn = IOMn(ui32Module)->DMATRIGEN;
    pIOMState->ui32TxnInt = 0;
    pIOMState->ui32NumPendTransactions = 1;

    IOMn(ui32Module)->DMACFG_b.DMAEN = 0;
    IOMn(ui32Module)->INTCLR = AM_HAL_IOM_INT_ALL;
    IOMn(ui32Module)->OFFSETHI = (uint32_t)(psTransaction->ui64Instr >> 8);
    IOMn(ui32Module)->DEVCFG = psTransaction->uPeerInfo.ui32I2CDevAddr;
    IOMn(ui32Module)->DCXCTRL_b.DCXSEL = pIOMState->dcx[psTransaction->uPeerInfo.ui32SpiChipSelect];
    IOMn(ui32Module)->DCXCTRL_b.DCXEN = 1;
    IOMn(ui32Module)->MSPICFG |= _VAL2FLD(IOM0_MSPICFG_FULLDUP, 1);

    pIOMState->sFdNb.bActive = true;
    pIOMState->sFdNb.pui8RxBuf = (uint8_t *)psTransaction->pui32RxBuffer;
    pIOMState->sFdNb.ui32RxBytesLeft = psTransaction->ui32NumBytes;
    pIOMState->sFdNb.pfnCallback = pfnCallback;
    pIOMState->sFdNb.pCallbackCtxt = pCallbackCtxt;

    IOMn(ui32Module)->DMATRIGEN = _VAL2FLD(IOM0_DMATRIGEN_DTHREN, 1);
    IOMn(ui32Module)->DMATOTCOUNT = psTransaction->ui32NumBytes;
    IOMn(ui32Module)->DMATARGADDR = (uint32_t)psTransaction->pui32TxBuffer;
    IOMn(ui32Module)->DMACFG =
        _VAL2FLD(IOM0_DMACFG_DMAPRI, psTransaction->ui8Priority)     |
        _VAL2FLD(IOM0_DMACFG_DMADIR, IOM0_DMACFG_DMADIR_M2P)        |
        _VAL2FLD(IOM0_DMACFG_DMAEN, 1);

    ui32Cmd = build_cmd(psTransaction->uPeerInfo.ui32SpiChipSelect,
                        psTransaction->eDirection,
                        psTransaction->bContinue ? 1 : 0,
                        psTransaction->ui64Instr,
                        psTransaction->ui32InstrLen,
                        psTransaction->ui32NumBytes);

    IOM_SET_INTEN(ui32Module, AM_HAL_IOM_INT_FDNBMODE);
    IOMn(ui32Module)->CMD = ui32Cmd;

fdnb_exit:
    am_hal_interrupt_master_set(ui32Critical);
    return ui32Status;
}

//*****************************************************************************
//
// IOM control function
// This function allows advanced settings
//
//*****************************************************************************
uint32_t
am_hal_iom_control(void *pHandle, am_hal_iom_request_e eReq, void *pArgs)
{
    am_hal_iom_state_t *pIOMState = (am_hal_iom_state_t*)pHandle;
    uint32_t status = AM_HAL_STATUS_SUCCESS;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    if (!AM_HAL_IOM_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }

    //
    // Validate the parameters
    //
    if (eReq >= AM_HAL_IOM_REQ_MAX)
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    uint32_t ui32Module = pIOMState->ui32Module;
    switch (eReq)
    {
        case AM_HAL_IOM_REQ_FLAG_SETCLR:
            if (pArgs)
            {
#ifndef AM_HAL_DISABLE_API_VALIDATION
                if (*((uint32_t *)pArgs) & AM_HAL_IOM_SC_RESV_MASK)
                {
                    return AM_HAL_STATUS_INVALID_ARG;
                }
#endif // AM_HAL_DISABLE_API_VALIDATION
                IOMn(ui32Module)->CQSETCLEAR = *((uint32_t *)pArgs);
            }
            else
            {
                status = AM_HAL_STATUS_INVALID_ARG;
            }
            break;
        case AM_HAL_IOM_REQ_SPI_LSB:
            if (pArgs)
            {
                IOMn(ui32Module)->MSPICFG_b.SPILSB = *((uint32_t *)pArgs);
            }
            else
            {
                status = AM_HAL_STATUS_INVALID_ARG;
            }
            break;
        case AM_HAL_IOM_REQ_SPI_RDTHRESH:
            if (pArgs)
            {
                IOMn(ui32Module)->FIFOTHR_b.FIFORTHR = *((uint32_t *)pArgs);
            }
            else
            {
                status = AM_HAL_STATUS_INVALID_ARG;
            }
            break;
        case AM_HAL_IOM_REQ_SPI_WRTHRESH:
            if (pArgs)
            {
                IOMn(ui32Module)->FIFOTHR_b.FIFOWTHR = *((uint32_t *)pArgs);
            }
            else
            {
                status = AM_HAL_STATUS_INVALID_ARG;
            }
            break;

    case AM_HAL_IOM_REQ_LINK_MSPI:
            if (pArgs)
            {
#ifndef AM_HAL_DISABLE_API_VALIDATION
                if (*((uint32_t *)pArgs) > AM_REG_MSPI_NUM_MODULES)
                {
                    return AM_HAL_STATUS_INVALID_ARG;
                }
#endif // AM_HAL_DISABLE_API_VALIDATION
                IOMn(ui32Module)->CQCFG_b.MSPIFLGSEL = *((uint32_t *)pArgs);
            }
            else
            {
                status = AM_HAL_STATUS_INVALID_ARG;
            }
            break;
        case AM_HAL_IOM_REQ_PAUSE:
            // Force CQ to Paused
            status = iom_cq_pause(pIOMState);
            break;

        case AM_HAL_IOM_REQ_UNPAUSE:
            // Resume the CQ
            if (!pIOMState->bCmdQInTCM)
            {
                // Need to ensure the CQ memory writes have been flushed before informing
                // hardware
                __DMB();
            }
            IOMn(ui32Module)->CQSETCLEAR = AM_HAL_IOM_SC_UNPAUSE_CQ;
            break;

        case AM_HAL_IOM_REQ_SET_SEQMODE:
        {
            am_hal_iom_seq_e eSeq;
#ifndef AM_HAL_DISABLE_API_VALIDATION
            if (!pArgs)
            {
                return AM_HAL_STATUS_INVALID_ARG;
            }
            if (!pIOMState->pNBTxnBuf)
            {
                // No space for CMDQ
                return AM_HAL_STATUS_INVALID_OPERATION;
            }
#endif // AM_HAL_DISABLE_API_VALIDATION
            eSeq = *((bool *)pArgs) ? AM_HAL_IOM_SEQ_UNDER_CONSTRUCTION: AM_HAL_IOM_SEQ_NONE;
            if (eSeq == pIOMState->eSeq)
            {
                // Nothing to do
                return AM_HAL_STATUS_SUCCESS;
            }

            switch (pIOMState->eSeq)
            {
                case AM_HAL_IOM_SEQ_RUNNING:
                {
                    // Force CQ to Pause
                    status = iom_cq_pause(pIOMState);
                    break;
                }
                case AM_HAL_IOM_SEQ_NONE:
                {
                    // Make sure there is no non-blocking transaction in progress
                    if (pIOMState->ui32NumPendTransactions)
                    {
                        status = AM_HAL_STATUS_INVALID_OPERATION;
                    }
                    break;
                }
                default:
                   ;
            }
            if (status == AM_HAL_STATUS_SUCCESS)
            {
                // Reset the cmdq
                am_hal_cmdq_reset(pIOMState->pCmdQHdl);
                pIOMState->ui32LastIdxProcessed = 0;
                pIOMState->ui32NumSeqTransactions = 0;
                pIOMState->ui32NumPendTransactions = 0;
                pIOMState->ui32NumUnSolicited = 0;
                pIOMState->eSeq = eSeq;
                pIOMState->bAutonomous = true;
            }
            break;
        }

        case AM_HAL_IOM_REQ_SEQ_END:
        {
            uint32_t ui32Status = AM_HAL_STATUS_SUCCESS;
            am_hal_cmdq_entry_t     *pCQBlock;
            uint32_t                index;
            am_hal_iom_seq_end_t *pLoop = (am_hal_iom_seq_end_t *)pArgs;
            uint32_t pause = 0;
            uint32_t scUnpause = 0;
            uint32_t ui32Critical = 0;
#ifndef AM_HAL_DISABLE_API_VALIDATION
            if (!pArgs)
            {
                return AM_HAL_STATUS_INVALID_ARG;
            }
            if (pLoop->ui32PauseCondition & AM_HAL_IOM_PAUSE_FLAG_RESV)
            {
                return AM_HAL_STATUS_INVALID_ARG;
            }
            if (pLoop->ui32StatusSetClr & AM_HAL_IOM_SC_RESV_MASK)
            {
                return AM_HAL_STATUS_INVALID_ARG;
            }
            if (pIOMState->eSeq != AM_HAL_IOM_SEQ_UNDER_CONSTRUCTION)
            {
                return AM_HAL_STATUS_INVALID_OPERATION;
            }
#endif // AM_HAL_DISABLE_API_VALIDATION
            if (pIOMState->block)
            {
                // End the block if the sequence is ending
                pIOMState->block = 0;
                // Unblock the whole batch of commands in this block
                if (!pIOMState->bCmdQInTCM)
                {
                    // Need to ensure the CQ memory writes have been flushed before informing
                    // hardware
                    __DMB();
                }
                IOMn(pIOMState->ui32Module)->CQSETCLEAR = AM_HAL_IOM_SC_UNPAUSE_BLOCK;
            }

            if ((pLoop->bLoop) && (!pIOMState->bAutonomous))
            {
                // Need to insert special element in CQ to cause a callback
                // This is to reset internal state
                ui32Status = am_hal_cmdq_alloc_block(pIOMState->pCmdQHdl, 1, &pCQBlock, &index);
                if (ui32Status != AM_HAL_STATUS_SUCCESS)
                {
                    return ui32Status;
                }
                else
                {
                    //
                    // Store the callback function pointer.
                    //
                    pIOMState->pfnCallback[index & (AM_HAL_IOM_MAX_PENDING_TRANSACTIONS - 1)] = iom_seq_loopback;
                    pIOMState->pCallbackCtxt[index & (AM_HAL_IOM_MAX_PENDING_TRANSACTIONS - 1)] = (void *)pIOMState;

                    // Dummy Entry
                    pCQBlock->address = (uint32_t)&IOMn(pIOMState->ui32Module)->CQSETCLEAR;
                    pCQBlock->value = 0;
                    //
                    // Need to protect access of ui32NumPendTransactions as it is accessed
                    // from ISR as well
                    //
                    // Start a critical section.
                    //
                    ui32Critical = am_hal_interrupt_master_disable();

                    //
                    // Post to the CQ.
                    //
                    ui32Status = am_hal_cmdq_post_block(pIOMState->pCmdQHdl, true);

                    if (AM_HAL_STATUS_SUCCESS != ui32Status)
                    {
                        am_hal_cmdq_release_block(pIOMState->pCmdQHdl);
                    }
                    else
                    {
                        uint32_t ui32NumPend = pIOMState->ui32NumPendTransactions++;
                        if (0 == ui32NumPend)
                        {
                            pIOMState->ui32UserIntCfg = IOMn(ui32Module)->INTEN;
                            IOM_SET_INTEN(ui32Module, AM_HAL_IOM_INT_CQMODE);
                            // Re-enable the CQ
                            am_hal_iom_CQEnable(pIOMState);
                        }
                    }
                    //
                    // End the critical section.
                    //
                    am_hal_interrupt_master_set(ui32Critical);
                    // Use SWFLAG6 to cause a pause
                    pause = AM_HAL_IOM_PAUSE_FLAG_SEQLOOP;
                    // Revert back the flag after SW callback unpauses it
                    scUnpause = AM_HAL_IOM_SC_PAUSE_SEQLOOP;
                }
            }

            // Insert the loopback
            ui32Status = am_hal_cmdq_alloc_block(pIOMState->pCmdQHdl, sizeof(am_hal_iom_cq_loop_entry_t) / 8, &pCQBlock, &index);
            if (ui32Status != AM_HAL_STATUS_SUCCESS)
            {
                return ui32Status;
            }
            else
            {
                am_hal_iom_cq_loop_entry_t *pLoopEntry = (am_hal_iom_cq_loop_entry_t *)pCQBlock;
                pLoopEntry->ui32PAUSENAddr = pLoopEntry->ui32PAUSEN2Addr = (uint32_t)&IOMn(ui32Module)->CQPAUSEEN;
                pLoopEntry->ui32SETCLRAddr = (uint32_t)&IOMn(ui32Module)->CQSETCLEAR;
                pLoopEntry->ui32PAUSEENVal = get_pause_val(pIOMState, pLoop->ui32PauseCondition | pause);
                pLoopEntry->ui32PAUSEEN2Val = AM_HAL_IOM_PAUSE_DEFAULT;
                pLoopEntry->ui32SETCLRVal = pLoop->ui32StatusSetClr | scUnpause;

                //
                // Need to protect access of ui32NumPendTransactions as it is accessed
                // from ISR as well
                //
                // Start a critical section.
                //
                ui32Critical = am_hal_interrupt_master_disable();

                //
                // Post to the CQ.
                //
                if (pLoop->bLoop)
                {
                    ui32Status = am_hal_cmdq_post_loop_block(pIOMState->pCmdQHdl, false);
                }
                else
                {
                    ui32Status = am_hal_cmdq_post_block(pIOMState->pCmdQHdl, false);
                }

                if (AM_HAL_STATUS_SUCCESS != ui32Status)
                {
                    am_hal_cmdq_release_block(pIOMState->pCmdQHdl);
                }
                else
                {
                    uint32_t ui32NumPend = pIOMState->ui32NumPendTransactions++;
                    pIOMState->eSeq = (pLoop->bLoop) ? AM_HAL_IOM_SEQ_RUNNING : AM_HAL_IOM_SEQ_NONE;
                    if (0 == ui32NumPend)
                    {
                        pIOMState->ui32UserIntCfg = IOMn(ui32Module)->INTEN;
                        IOM_SET_INTEN(ui32Module, AM_HAL_IOM_INT_CQMODE);
                        // Re-enable the CQ
                        am_hal_iom_CQEnable(pIOMState);
                    }
                }
                //
                // End the critical section.
                //
                am_hal_interrupt_master_set(ui32Critical);
            }
            return AM_HAL_STATUS_SUCCESS;
            //break;
        }
        case AM_HAL_IOM_REQ_INIT_HIPRIO:
        {
            am_hal_iom_hiprio_cfg_t *pHPCfg = (am_hal_iom_hiprio_cfg_t *)pArgs;
#ifndef AM_HAL_DISABLE_API_VALIDATION
            if (!pHPCfg)
            {
                return AM_HAL_STATUS_INVALID_ARG;
            }
#endif // AM_HAL_DISABLE_API_VALIDATION
            pIOMState->ui32NumHPEntries = pIOMState->ui32LastHPIdxProcessed = 0;
            pIOMState->ui32NextHPIdx = pIOMState->ui32LastHPIdxProcessed + 1;
            pIOMState->pHPTransactions = (am_hal_iom_dma_entry_t *)pHPCfg->pBuf;
            pIOMState->ui32MaxHPTransactions = pHPCfg->size / sizeof(am_hal_iom_dma_entry_t);
            break;
        }

        case AM_HAL_IOM_REQ_START_BLOCK:
            // Pause the next block from proceeding till whole block is finished
            IOMn(pIOMState->ui32Module)->CQSETCLEAR = AM_HAL_IOM_SC_PAUSE_BLOCK;
            pIOMState->block = 1;
            pIOMState->ui32NumHPPendingEntries = 0;
            break;

        case AM_HAL_IOM_REQ_END_BLOCK:
            // Unblock the whole batch of commands in this block
            if (!pIOMState->bCmdQInTCM)
            {
                // Need to ensure the CQ memory writes have been flushed before informing
                // hardware
                __DMB();
            }
            IOMn(pIOMState->ui32Module)->CQSETCLEAR = AM_HAL_IOM_SC_UNPAUSE_BLOCK;
            pIOMState->block = 0;
            if (pIOMState->ui32NumHPPendingEntries)
            {
                // Now it is okay to let go of the block of HiPrio transactions
                status = sched_hiprio(pIOMState, pIOMState->ui32NumHPPendingEntries);
                if (status == AM_HAL_STATUS_SUCCESS)
                {
                    pIOMState->ui32NumHPPendingEntries = 0;
                }
            }
            break;

        case AM_HAL_IOM_REQ_SET_DCX:
        {
            am_hal_iom_dcx_cfg_t *pDcxCfg = (am_hal_iom_dcx_cfg_t *)pArgs;
#ifndef AM_HAL_DISABLE_API_VALIDATION
            if (!pDcxCfg)
            {
                return AM_HAL_STATUS_INVALID_ARG;
            }
            if ((pIOMState->eInterfaceMode != AM_HAL_IOM_SPI_MODE) ||
                  (pDcxCfg->cs == pDcxCfg->dcx) ||
                  (pDcxCfg->cs > AM_HAL_IOM_MAX_CS_SPI) ||
                  ((pDcxCfg->dcx != AM_HAL_IOM_DCX_INVALID) && (pDcxCfg->dcx > AM_HAL_IOM_MAX_CS_SPI)))
            {
                return AM_HAL_STATUS_INVALID_ARG;
            }
#endif // AM_HAL_DISABLE_API_VALIDATION

            pIOMState->dcx[pDcxCfg->cs] =
              (pDcxCfg->dcx == AM_HAL_IOM_DCX_INVALID) ?
                0 : (IOM0_DCXCTRL_DCXEN_Msk | ((0x1 << pDcxCfg->dcx) << IOM0_DCXCTRL_DCXSEL_Pos));
            break;
        }

        case AM_HAL_IOM_REQ_CQ_RAW:
        {
            am_hal_iom_cq_raw_t *pCqRaw = (am_hal_iom_cq_raw_t *)pArgs;
            am_hal_cmdq_entry_t *pCQBlock;
            am_hal_iom_callback_t pfnCallback1;

            uint32_t            ui32Critical = 0;
            uint32_t            index;
#ifndef AM_HAL_DISABLE_API_VALIDATION
            if (!pCqRaw)
            {
                return AM_HAL_STATUS_INVALID_ARG;
            }
            if (!pIOMState->pCmdQHdl)
            {
                return AM_HAL_STATUS_INVALID_OPERATION;
            }
#endif // AM_HAL_DISABLE_API_VALIDATION
            //
            // Check to see if there is enough room in the CQ
            //
            if ((pIOMState->ui32NumPendTransactions == AM_HAL_IOM_MAX_PENDING_TRANSACTIONS) ||
                (am_hal_cmdq_alloc_block(pIOMState->pCmdQHdl, pCqRaw->numEntries + 3, &pCQBlock, &index)))
            {
                return AM_HAL_STATUS_OUT_OF_RANGE;
            }

            pCQBlock->address = (uint32_t)&IOMn(pIOMState->ui32Module)->CQPAUSEEN;
            pCQBlock->value = get_pause_val(pIOMState, pCqRaw->ui32PauseCondition);
            pCQBlock++;
            for (uint32_t i = 0; i < pCqRaw->numEntries; i++, pCQBlock++)
            {
                pCQBlock->address = pCqRaw->pCQEntry[i].address;
                pCQBlock->value = pCqRaw->pCQEntry[i].value;
            }
            // If there is a need - populate the jump back address
            if (pCqRaw->pJmpAddr)
            {
                *(pCqRaw->pJmpAddr) = (uint32_t)pCQBlock;
            }
            pCQBlock->address = (uint32_t)&IOMn(pIOMState->ui32Module)->CQPAUSEEN;
            pCQBlock->value = AM_HAL_IOM_PAUSE_DEFAULT;
            pCQBlock++;
            pCQBlock->address = (uint32_t)&IOMn(pIOMState->ui32Module)->CQSETCLEAR;
            pCQBlock->value = pCqRaw->ui32StatusSetClr;

            pfnCallback1 = pCqRaw->pfnCallback;
            if (!pfnCallback1 && !pIOMState->block && (pIOMState->eSeq == AM_HAL_IOM_SEQ_NONE) &&
                (pIOMState->ui32NumUnSolicited >= (pIOMState->ui32MaxPending / 2)))
            {
                // Need to schedule a dummy callback, to ensure ui32NumPendTransactions get updated in ISR
                pfnCallback1 = iom_dummy_callback;
            }
            //
            // Store the callback function pointer.
            //
            pIOMState->pfnCallback[index & (AM_HAL_IOM_MAX_PENDING_TRANSACTIONS - 1)] = pfnCallback1;
            pIOMState->pCallbackCtxt[index & (AM_HAL_IOM_MAX_PENDING_TRANSACTIONS - 1)] = pCqRaw->pCallbackCtxt;

            //
            // Need to protect access of ui32NumPendTransactions as it is accessed
            // from ISR as well
            //
            // Start a critical section.
            //
            ui32Critical = am_hal_interrupt_master_disable();

            //
            // Register for interrupt only if there is a callback
            //
            status = am_hal_cmdq_post_block(pIOMState->pCmdQHdl, pfnCallback1);

            if (status == AM_HAL_STATUS_SUCCESS)
            {
                uint32_t ui32NumPend = pIOMState->ui32NumPendTransactions++;
                pIOMState->ui32NumSeqTransactions++;
                if (pCqRaw->pfnCallback)
                {
                    pIOMState->bAutonomous = false;
                    pIOMState->ui32NumUnSolicited = 0;
                }
                else
                {
                    if (pfnCallback1)
                    {
                        // This implies we have already scheduled a dummy callback
                        pIOMState->ui32NumUnSolicited = 0;
                    }
                    else
                    {
                        pIOMState->ui32NumUnSolicited++;
                    }
                }
                if (0 == ui32NumPend)
                {
                    pIOMState->ui32UserIntCfg = IOMn(ui32Module)->INTEN;
                    IOM_SET_INTEN(ui32Module, AM_HAL_IOM_INT_CQMODE);
                    // Re-enable the CQ
                    am_hal_iom_CQEnable(pIOMState);
                }
            }
            else
            {
                am_hal_cmdq_release_block(pIOMState->pCmdQHdl);
            }
            //
            // End the critical section.
            //
            am_hal_interrupt_master_set(ui32Critical);
            break;
        }


        default:
            status = AM_HAL_STATUS_INVALID_ARG;
    }

    return status;
}

//*****************************************************************************
//
// IOM High Priority transfer function
//
//*****************************************************************************
uint32_t
am_hal_iom_highprio_transfer(void *pHandle,
                             am_hal_iom_transfer_t *psTransaction,
                             am_hal_iom_callback_t pfnCallback,
                             void *pCallbackCtxt)
{
    am_hal_iom_state_t           *pIOMState = (am_hal_iom_state_t *)pHandle;
    uint32_t                      ui32Status = AM_HAL_STATUS_SUCCESS;

#ifndef AM_HAL_DISABLE_API_VALIDATION
    //
    // Check the handle.
    //
    if (!AM_HAL_IOM_CHK_HANDLE(pHandle))
    {
        return AM_HAL_STATUS_INVALID_HANDLE;
    }
    if (!pIOMState->pNBTxnBuf)
    {
        return AM_HAL_STATUS_INVALID_OPERATION;
    }
    //
    // Validate parameters
    //
    ui32Status = validate_transaction(pIOMState, psTransaction, false);

    if (ui32Status != AM_HAL_STATUS_SUCCESS)
    {
        return ui32Status;
    }
    if (psTransaction->ui32PauseCondition != 0)
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }
    if (psTransaction->ui32StatusSetClr != 0)
    {
        return AM_HAL_STATUS_INVALID_ARG;
    }
    if (psTransaction->eDirection > AM_HAL_IOM_RX)
    {
        return AM_HAL_STATUS_INVALID_OPERATION;
    }
    if (!pIOMState->pHPTransactions)
    {
        return AM_HAL_STATUS_INVALID_OPERATION;
    }
#endif // AM_HAL_DISABLE_API_VALIDATION

    ui32Status = iom_add_hp_transaction(pHandle, psTransaction, pfnCallback, pCallbackCtxt);

    if (ui32Status == AM_HAL_STATUS_SUCCESS)
    {
        if (!(pIOMState->block))
        {
            ui32Status = sched_hiprio(pIOMState, 1);
        }
        else
        {
            pIOMState->ui32NumHPPendingEntries++;
        }
    }

    //
    // Return the status.
    //
    return ui32Status;
}

//*****************************************************************************
//
// End Doxygen group.
//! @}
//
//*****************************************************************************
