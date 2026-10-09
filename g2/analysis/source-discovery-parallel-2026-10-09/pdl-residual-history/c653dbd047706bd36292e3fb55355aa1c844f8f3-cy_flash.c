/***************************************************************************//**
* \file cy_flash.c
* \version 1.0
*
* \brief
* Provides the public functions for the API for the Flash driver.
*
********************************************************************************
* \copyright
* Copyright 2016-2020 Cypress Semiconductor Corporation
* SPDX-License-Identifier: Apache-2.0
*
* Licensed under the Apache License, Version 2.0 (the "License");
* you may not use this file except in compliance with the License.
* You may obtain a copy of the License at
*
*     http://www.apache.org/licenses/LICENSE-2.0
*
* Unless required by applicable law or agreed to in writing, software
* distributed under the License is distributed on an "AS IS" BASIS,
* WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
* See the License for the specific language governing permissions and
* limitations under the License.
*******************************************************************************/
#include "cy_flash.h"
#include "cy_sysclk.h"
#include "cy_sysint.h"
#include "cy_device.h"
#include "cy_syslib.h"

#include <string.h>

/***************************************
* Macro definitions
***************************************/

/** \cond INTERNAL */

/** Command completed with no errors */
#define SROMCODE_SUCCESS                        (0xA0000000UL)
/** Command completed with error flag */
#define SROMCODE_ERROR_FLAG                     (0xF0000000UL)
/** Invalid device protection state */
#define SROMCODE_INVALID_PROTECTION             (0xF0000001UL)
/** Invalid flash page latch address */
#define SROMCODE_INVALID_FM_PL                  (0xF0000003UL)
/** Invalid flash address */
#define SROMCODE_INVALID_FLASH_ADDR             (0xF0000004UL)
/** Row is write protected */
#define SROMCODE_ROW_PROTECTED                  (0xF0000005UL)
/** All non-blocking API have completed */
#define SROMCODE_RESUME_COMPLETE                (0xF0000007UL)
/** A resume or non-blocking is still in progress. */
#define SROMCODE_PENDING_RESUME                 (0xF0000008UL)
/** Command in progress; no error */
#define SROMCODE_SYSCALL_IN_PROGRESS            (0xF0000009UL)
/** API not instantiated */
#define SROMCODE_API_NOT_INSTANTIATED           (0xF0000011UL)
/** Invalid Flash Clock */
#define SROMCODE_INVALID_CLOCK                  (0xF0000012UL)
/** Command invalid for SPCIF_SYNCHRONOUS=0. */
#define SROMCODE_INVALID_FLASH_IP               (0xF0000013UL)
/** Command Not Available in DEAD Mode */
#define SROMCODE_NA_IN_DEAD_MODE                (0xF0000014UL)
/** SROM return status mask for ERROR/SUCCESS */
#define SROMCODE_STATUS_MASK                    (0xF0000000UL)
/** \endcond */

#define CY_FLASH_SRAM_ROM_KEY1                          (0U)
#define CY_FLASH_SRAM_ROM_DATA                          (CY_FLASH_SRAM_ROM_KEY1 + 0x08U)

/* SROM API parameters offsets */
#define CY_FLASH_PARAM_KEY_TWO_OFFSET                   (8U)
#define CY_FLASH_PARAM_ADDR_OFFSET                      (16U)
#define CY_FLASH_PARAM_MACRO_SEL_OFFSET                 (24U)
#define CY_FLASH_PAGE_LATCH_START_ADDR                  (0UL)

/* Opcodes */
#define CY_FLASH_API_OPCODE_LOAD                        (0x04U)
#define CY_FLASH_API_OPCODE_WRITE_ROW                   (0x05U)
#define CY_FLASH_API_OPCODE_NON_BLOCKING_WRITE_ROW      (0x07U)
#define CY_FLASH_API_OPCODE_RESUME_NON_BLOCKING         (0x09U)

#define CY_FLASH_API_OPCODE_PROGRAM_ROW                 (0x06U)
#define CY_FLASH_API_OPCODE_WRITE_SFLASH_ROW            (0x18U)

#define CY_FLASH_API_OPCODE_CHECKSUM                    (0x0BU)
#define CY_FLASH_API_OPCODE_ERASE_SECTOR                (0x14U)

#define CY_FLASH_API_OPCODE_CLK_CONFIG                  (0x15U)
#define CY_FLASH_API_OPCODE_CLK_BACKUP                  (0x16U)
#define CY_FLASH_API_OPCODE_CLK_RESTORE                 (0x17U)


#define CY_FLASH_CPUSS_REQ_START                        ((uint32_t) ((uint32_t) 0x1U << 31U))
#define CY_FLASH_CPUSS_SYSARG_CHECKSUM_MASK             (0x00FFFFFFUL)

#define CY_FLASH_KEY_ONE                                (0xB6U)
#define CY_FLASH_KEY_TWO(x)                             ((uint32_t) (((uint16_t) 0xD3U) + ((uint16_t) (x))))

/*  Macro #0: rows 0x00-0x1ff, Macro #1: rows 0x200-0x3ff, macro # 2: rows 0x400-0x5ff  */
#define CY_FLASH_GET_MACRO_FROM_ROW(row)                ((row) / CY_FLASH_SIZEOF_MACRO)

#define CY_FLASH_CLOCK_BACKUP_SIZE      (6U)
typedef struct Cy_Flash_ClockBackupStruct
{
    uint32_t clockSettings[CY_FLASH_CLOCK_BACKUP_SIZE];       /* FM-Lite Clock Backup */
} CY_SYS_FLASH_CLOCK_BACKUP_STRUCT;
static CY_SYS_FLASH_CLOCK_BACKUP_STRUCT cySysFlashBackup;

static uint32_t Cy_Flash_GetRowNum(uint32_t flashAddr);
static cy_en_flashdrv_status_t ProcessStatusCode(void);
static cy_en_flashdrv_status_t Cy_Flash_ClockBackup(void);
static cy_en_flashdrv_status_t Cy_Flash_ClockConfig(void);
static cy_en_flashdrv_status_t Cy_Flash_ClockRestore(void);
static bool Cy_Flash_ValidAddr(uint32_t flashAddr);
#if (CY_FLASH_NON_BLOCKING_SUPPORTED)
    static bool Cy_Flash_ValidFlashAddr(uint32_t flashAddr);
#endif /* (CY_FLASH_NON_BLOCKING_SUPPORTED) */


/*******************************************************************************
* Function Name: Cy_Flash_WriteRow
****************************************************************************//**
*
* \brief Erases a row of Flash or Supervisory Flash and programs it with the
* new data. Does not return until the write operation is complete. Refer to the
* device datasheet for the details.
*
* This API will automatically enable IMO and modify the clock settings for the
* device. Writing to Flash requires 48 MHz IMO and changes be made to the HFCLK
* settings. The configuration is restored before returning. HFCLK will have
* several frequency changes during the operation of this API between a minimum
* frequency of the current IMO frequency divided by 8 and a maximum frequency of
* 12 MHz. This will impact the operation of most of the hardware in the device.
*
* \param rowAddr Address of the Flash or Supervisory Flash row to which the data
* needs to be written. The address shall be aligned to the beginning of the row.
*
* \param data Array of bytes to write. The size of the array must be equal to
* the Flash row size defined by \ref CY_FLASH_SIZEOF_ROW.
*
* \return \ref group_flash_enumerated_types
*
* \funcusage
* \snippet flash_snippet.c SNIPPET_FLASH_INIT
* \snippet flash_snippet.c SNIPPET_FLASH_WRITE
*
*******************************************************************************/
cy_en_flashdrv_status_t Cy_Flash_WriteRow(uint32_t rowAddr, const uint32_t* data)
{
    cy_en_flashdrv_status_t result = CY_FLASH_DRV_DEV_NOT_SUPPORTED;

    volatile uint32_t parameters[(CY_FLASH_SIZEOF_ROW + CY_FLASH_SRAM_ROM_DATA) / sizeof(uint32_t)];
    uint32_t interruptState;
    uint32_t rowNum = Cy_Flash_GetRowNum(rowAddr);

    if ((Cy_Flash_ValidAddr(rowAddr)) && (NULL != data))
    {
        /* Copy data to be written into internal variable */
        (void) memcpy((void *) &parameters[2U], (const void *) data, CY_FLASH_SIZEOF_ROW);

        parameters[0U] = (uint32_t) (CY_FLASH_GET_MACRO_FROM_ROW(rowNum)        << CY_FLASH_PARAM_MACRO_SEL_OFFSET) |
                         (uint32_t) (CY_FLASH_PAGE_LATCH_START_ADDR             << CY_FLASH_PARAM_ADDR_OFFSET     ) |
                         (uint32_t) (CY_FLASH_KEY_TWO(CY_FLASH_API_OPCODE_LOAD) << CY_FLASH_PARAM_KEY_TWO_OFFSET  ) |
                         CY_FLASH_KEY_ONE;
        parameters[1U] = CY_FLASH_SIZEOF_ROW - 1U;

        CPUSS_SYSARG = (uint32_t) &parameters[0U];
        CPUSS_SYSREQ = CY_FLASH_CPUSS_REQ_START | CY_FLASH_API_OPCODE_LOAD;
        __NOP();

        result = ProcessStatusCode();
        if(CY_FLASH_DRV_SUCCESS == result)
        {
            interruptState = Cy_SysLib_EnterCriticalSection();
            result = Cy_Flash_ClockBackup();
            if (CY_FLASH_DRV_SUCCESS == result)
            {
                result = Cy_Flash_ClockConfig();
                if (CY_FLASH_DRV_SUCCESS == result)
                {
                    cy_en_flashdrv_status_t resultClockRestore;

                    /* Write Row */
                    CPUSS_SYSARG = (uint32_t) &parameters[0U];
                    if (rowAddr >= CY_SFLASH_BASE)
                    {
                        /* Supervisory Flash */
                        parameters[0U] = (uint32_t) (((uint32_t) CY_FLASH_KEY_TWO(CY_FLASH_API_OPCODE_WRITE_SFLASH_ROW) <<  CY_FLASH_PARAM_KEY_TWO_OFFSET) | CY_FLASH_KEY_ONE);
                        parameters[1U] = (uint32_t) rowNum;
                        CPUSS_SYSREQ = CY_FLASH_CPUSS_REQ_START | CY_FLASH_API_OPCODE_WRITE_SFLASH_ROW;
                    }
                    else
                    {
                        /* Flash */
                        parameters[0U]  = (uint32_t) (((uint32_t) CY_FLASH_KEY_TWO(CY_FLASH_API_OPCODE_WRITE_ROW) <<  CY_FLASH_PARAM_KEY_TWO_OFFSET) | CY_FLASH_KEY_ONE);
                        parameters[0U] |= (uint32_t)(rowNum << 16U);
                        CPUSS_SYSREQ = CY_FLASH_CPUSS_REQ_START | CY_FLASH_API_OPCODE_WRITE_ROW;
                    }
                    __NOP();

                    result = ProcessStatusCode();
                    resultClockRestore = Cy_Flash_ClockRestore();
                    if (CY_FLASH_DRV_SUCCESS == result)
                    {
                        result = resultClockRestore;
                    }
                }
            }
            Cy_SysLib_ExitCriticalSection(interruptState);
        }
    }
    return (result);
}


#if (CY_FLASH_NON_BLOCKING_SUPPORTED) || defined (CY_DOXYGEN)
/*******************************************************************************
* Function Name: Cy_Flash_StartWrite
****************************************************************************//**
*
* Initiates a write to a row of Flash. A call to this API is non-blocking.
* Use \ref Cy_Flash_ResumeWrite() to resume Flash writes and
* \ref Cy_Flash_IsOperationComplete() to ascertain status of the write
* operation. Supervisory Flash does not support non-blocking write.
*
* This API will automatically enable IMO and modify the clock settings for the
* device. Writing to Flash requires 48 MHz IMO and changes be made to the HFCLK
* settings. The configuration is restored to original configuration by calling
* \ref Cy_Flash_IsOperationComplete(). HFCLK will have several frequency changes
* during the operation of these API between a minimum frequency of the current
* IMO frequency divided by 8 and a maximum frequency of 12 MHz. This will impact
* the operation of most of the hardware in the device.
*
* This API will automatically enable IMO and modify the clock settings for the
* device. Writing to Flash requires 48 MHz IMO and changes be made to the HFCLK
* settings. The configuration is restored to original configuration by calling
* \ref Cy_Flash_IsOperationComplete(). HFCLK will have several frequency
* changes during the operation of this API and \ref Cy_Flash_IsOperationComplete()
* API between a minimum frequency of the current IMO frequency divided by 8 and
* a maximum frequency of 12 MHz. This will impact the operation of most of the
* hardware in the device.
*
* The devices require HFCLK to be sourced by 48 MHz IMO during Flash write.
* The IMO must be enabled before calling this function. This API will modify
* IMO configuration; it can be later restored to original configuration by
* calling \ref Cy_Flash_IsOperationComplete().
*
* The non-blocking write row API \ref Cy_Flash_StartWrite() requires
* \ref Cy_Flash_ResumeWrite() to be called 3 times to complete the write. This
* can be done by configuring SPCIF interrupt and placing a call to this API.
*
* For Cortex-M0+ based devices, if the user wants to keep the vector table in
* Flash when performing non-blocking Flash write then they need to make sure the
* vector table is placed in the Flash macro which is not getting programmed by
* configuring the VTOR register.
*
* \param rowAddr Address of the Flash row to which the data needs to be written.
* The address shall be aligned to the beginning of the row. Supervisory Flash is
* not supported.
*
* \param data Array of bytes to write. The size of the array must be equal to
* the Flash row size. The Flash row size for the selected device is defined by
* the \ref CY_FLASH_SIZEOF_ROW macro. Refer to the device datasheet for the
* details.
*
* \return \ref group_flash_enumerated_types.
* Returns \ref CY_FLASH_DRV_OPERATION_STARTED in case of successful start.
*
* \note The non-blocking operation does not return success status
* CY_FLASH_DRV_SUCCESS until the last \ref Cy_Flash_ResumeWrite() API
* is complete. The CPUSS_SYSARG register will be reflecting the SRAM address
* during an ongoing non-blocking operation.
*
* \funcusage
* \snippet flash_snippet.c SNIPPET_FLASH_INIT
* \snippet flash_snippet.c SNIPPET_FLASH_NONBLOCKING_INIT
* \snippet flash_snippet.c SNIPPET_FLASH_NONBLOCKING
*
*******************************************************************************/
cy_en_flashdrv_status_t Cy_Flash_StartWrite(uint32_t rowAddr, const uint32_t* data)
{
    cy_en_flashdrv_status_t result = CY_FLASH_DRV_SUCCESS;
    volatile uint32_t parameters[(CY_FLASH_SIZEOF_ROW + CY_FLASH_SRAM_ROM_DATA) / sizeof(uint32_t)];
    uint32_t interruptState;
    uint32_t rowNum = Cy_Flash_GetRowNum(rowAddr);

    if ((Cy_Flash_ValidFlashAddr(rowAddr)) && (NULL != data))
    {
        /* Copy data to be written into internal variable */
        (void) memcpy((void *) &parameters[2U], (const void *) data, CY_FLASH_SIZEOF_ROW);

        /* Load Flash Bytes */
        parameters[0U] = (uint32_t) (CY_FLASH_GET_MACRO_FROM_ROW(rowNum)        << CY_FLASH_PARAM_MACRO_SEL_OFFSET) |
                         (uint32_t) (CY_FLASH_PAGE_LATCH_START_ADDR             << CY_FLASH_PARAM_ADDR_OFFSET     ) |
                         (uint32_t) (CY_FLASH_KEY_TWO(CY_FLASH_API_OPCODE_LOAD) << CY_FLASH_PARAM_KEY_TWO_OFFSET  ) |
                         CY_FLASH_KEY_ONE;
        parameters[1U] = CY_FLASH_SIZEOF_ROW - 1U;

        CPUSS_SYSARG = (uint32_t) &parameters[0U];
        CPUSS_SYSREQ = CY_FLASH_CPUSS_REQ_START | CY_FLASH_API_OPCODE_LOAD;
        __NOP();
        result = ProcessStatusCode();

        if(result == CY_FLASH_DRV_SUCCESS)
        {
            /***************************************************************
            * Mask all the exceptions to guarantee that Flash write will
            * occur in the atomic way. It will not affect system call
            * execution (flash row write) since it is executed in the NMI
            * context.
            ***************************************************************/
            interruptState = Cy_SysLib_EnterCriticalSection();

            result = Cy_Flash_ClockBackup();
        #if(CPUSS_SPCIF_SYNCHRONOUS)
            if(result == CY_FLASH_DRV_SUCCESS)
            {
                result = Cy_Flash_ClockConfig();
            }
        #endif  /* (CPUSS_SPCIF_SYNCHRONOUS) */
            if(result == CY_FLASH_DRV_SUCCESS)
            {
                /* Non-blocking Write Row */
                parameters[0U]  = (uint32_t) (((uint32_t) CY_FLASH_KEY_TWO(CY_FLASH_API_OPCODE_NON_BLOCKING_WRITE_ROW) <<
                                                        CY_FLASH_PARAM_KEY_TWO_OFFSET) | CY_FLASH_KEY_ONE);
                parameters[0U] |= (uint32_t)(rowNum << 16U);

                CPUSS_SYSARG = (uint32_t) &parameters[0U];
                CPUSS_SYSREQ = CY_FLASH_CPUSS_REQ_START | CY_FLASH_API_OPCODE_NON_BLOCKING_WRITE_ROW;
                __NOP();
                result = ProcessStatusCode();
            }

            Cy_SysLib_ExitCriticalSection(interruptState);
        }
    }
    else
    {
        result = CY_FLASH_DRV_INVALID_INPUT_PARAMETERS;
    }

    return result;
}


/*******************************************************************************
* Function Name: Cy_Flash_ResumeWrite
****************************************************************************//**
*
* The non-blocking write row API \ref Cy_Flash_StartWrite() requires that
* this function be called 3 times to complete the write. This can be done by
* configuring SPCIF interrupt and placing a call to this API.
*
* It is advised not to prolong calling this API for more than 25 ms.
*
* \note The non-blocking operation does not return success status
* CY_FLASH_DRV_SUCCESS until the last Resume API is complete.
* The CPUSS_SYSARG register will be reflecting the SRAM address during an
* ongoing non-blocking operation.
*
* \return \ref group_flash_enumerated_types
*
*******************************************************************************/
cy_en_flashdrv_status_t Cy_Flash_ResumeWrite(void)
{
    cy_en_flashdrv_status_t result = CY_FLASH_DRV_SUCCESS;
    static volatile uint32_t parameters[1U];

    /* Resume */
    parameters[0U] = (uint32_t) (((uint32_t) CY_FLASH_KEY_TWO(CY_FLASH_API_OPCODE_RESUME_NON_BLOCKING) <<
                                         CY_FLASH_PARAM_KEY_TWO_OFFSET) | CY_FLASH_KEY_ONE);
    CPUSS_SYSARG = (uint32_t) &parameters[0U];
    CPUSS_SYSREQ = CY_FLASH_CPUSS_REQ_START | CY_FLASH_API_OPCODE_RESUME_NON_BLOCKING;

    __NOP();
    result = ProcessStatusCode();

    return (result);
}


/*******************************************************************************
* Function Name: Cy_Flash_IsOperationComplete
****************************************************************************//**
*
* Returns the current status of the Flash write operation.
*
* \note The non-blocking operation does not return success status
* \ref CY_FLASH_DRV_SUCCESS until the last \ref Cy_Flash_ResumeWrite() is
* complete. The CPUSS_SYSARG register will be reflecting the SRAM address
* during an ongoing non-blocking operation.
*
* Calling this API before starting a non-blocking write row operation
* using the \ref Cy_Flash_StartWrite API will cause improper operation.
*
* \return \ref cy_en_flashdrv_status_t
*
*******************************************************************************/
cy_en_flashdrv_status_t Cy_Flash_IsOperationComplete(void)
{
    cy_en_flashdrv_status_t result;
    volatile cy_en_flashdrv_status_t resultClockRestore;
    bool operationCompleted;

    result = ProcessStatusCode();
    operationCompleted =    (CY_FLASH_DRV_OPERATION_STARTED != result) &&
                            (CY_FLASH_DRV_PROGRESS_NO_ERROR != result) &&
                            (CY_FLASH_DRV_PENDING_RESUME    != result);
    if (operationCompleted)
    {
        /* Operation completed with success or error. Clock should be restored
         * in any case. */
        resultClockRestore = Cy_Flash_ClockRestore();
        /* Return result of clock restore operation, only in case of
         * operation success. Operation error has a return priority. */
        if (CY_FLASH_DRV_SUCCESS == result)
        {
            result = resultClockRestore;
        }
    }

    return (result);
}


/*******************************************************************************
* Function Name: Cy_Flash_ValidFlashAddr
********************************************************************************
*
* Checks if the specified address is valid Flash address.
*
* \return Returns True if the specified address is valid.
*
*******************************************************************************/
static bool Cy_Flash_ValidFlashAddr(uint32_t flashAddr)
{
    bool valid = false;

    if (flashAddr < (CY_FLASH_BASE + CY_FLASH_SIZEOF_FLASH))
    {
        if ((flashAddr % CY_FLASH_SIZEOF_ROW) == 0UL)
        {
            valid = true;
        }
    }

    return (valid);
}

#endif /* (CY_FLASH_NON_BLOCKING_SUPPORTED) || defined (CY_DOXYGEN) */


/*******************************************************************************
* Function Name: Cy_Flash_RowChecksum
****************************************************************************//**
*
* Returns a checksum value of the specified Flash or Supervisory Flash row.
*
* \param rowAddr The address of the row. The address shall be aligned to the
* beginning of the row.
*
* \param checksumPtr The pointer to the address where checksum is to be stored.
*
* \return \ref cy_en_flashdrv_status_t
*
* \funcusage
* \snippet flash_snippet.c SNIPPET_FLASH_CHECKSUM
*
*******************************************************************************/
cy_en_flashdrv_status_t Cy_Flash_RowChecksum(uint32_t rowAddr, uint32_t* checksumPtr)
{
    cy_en_flashdrv_status_t result = CY_FLASH_DRV_DEV_NOT_SUPPORTED;
    volatile uint32_t parameters[1U];
    uint32_t rowNum = Cy_Flash_GetRowNum(rowAddr);

    if (Cy_Flash_ValidAddr(rowAddr))
    {
        /* Checksum */
        parameters[0U]  = (uint32_t) (((uint32_t) CY_FLASH_KEY_TWO(CY_FLASH_API_OPCODE_CHECKSUM) <<  CY_FLASH_PARAM_KEY_TWO_OFFSET) | CY_FLASH_KEY_ONE);
        parameters[0U] |= (uint32_t)(rowNum << 16U);

        CPUSS_SYSARG = (uint32_t) parameters[0U];
        CPUSS_SYSREQ = CY_FLASH_CPUSS_REQ_START | CY_FLASH_API_OPCODE_CHECKSUM;
        __NOP();
        result = ProcessStatusCode();
        if (CY_FLASH_DRV_SUCCESS == result)
        {
            *checksumPtr = CPUSS_SYSARG & CY_FLASH_CPUSS_SYSARG_CHECKSUM_MASK;
        }
    }

    return (result);
}


/*******************************************************************************
* Function Name: ProcessStatusCode
****************************************************************************//**
*
* Converts System Call returns to the Flash driver return defines.
*
* \return \ref cy_en_flashdrv_status_t
*
*******************************************************************************/
static cy_en_flashdrv_status_t ProcessStatusCode(void)
{
    cy_en_flashdrv_status_t result;
    uint32_t statuscode = CPUSS_SYSARG;

    if ((statuscode & SROMCODE_STATUS_MASK) == SROMCODE_SUCCESS)
    {
        result = CY_FLASH_DRV_SUCCESS;
    }
    else if ((statuscode & SROMCODE_STATUS_MASK) == SROMCODE_ERROR_FLAG)
    {
        /* Process error code */
        switch (statuscode)
        {
            case SROMCODE_INVALID_PROTECTION:
            {
                result = CY_FLASH_DRV_INVALID_PROT;
                break;
            }
            case SROMCODE_INVALID_FM_PL:
            case SROMCODE_INVALID_FLASH_ADDR:
            {
                result = CY_FLASH_DRV_INVALID_FLASH_ADDR;
                break;
            }
            case SROMCODE_ROW_PROTECTED:
            {
                result = CY_FLASH_DRV_ROW_PROTECTED;
                break;
            }
            case SROMCODE_RESUME_COMPLETE:
            {
                result = CY_FLASH_DRV_SUCCESS;
                break;
            }
            case SROMCODE_PENDING_RESUME:
            {
                result = CY_FLASH_DRV_PENDING_RESUME;
                break;
            }
            case SROMCODE_SYSCALL_IN_PROGRESS:
            {
                result = CY_FLASH_DRV_PROGRESS_NO_ERROR;
                break;
            }
            case SROMCODE_API_NOT_INSTANTIATED:
            case SROMCODE_INVALID_FLASH_IP:
            case SROMCODE_NA_IN_DEAD_MODE:
            {
                result = CY_FLASH_DRV_DEV_NOT_SUPPORTED;
                break;
            }
            default:
            {
                result = CY_FLASH_DRV_ERROR_UNKNOWN;
                break;
            }
        }
    }
    else
    {
        /* Not an error or success - the operation in not finished */
        result = CY_FLASH_DRV_OPERATION_STARTED;
    }

    return (result);
}


/*******************************************************************************
* Function Name: Cy_Flash_ValidAddr
********************************************************************************
*
* Checks if the specified Flash address is valid.
*
* \param flashAddr Flash row address.
*
* \return Returns true if the specified address is valid.
*
*******************************************************************************/
static bool Cy_Flash_ValidAddr(uint32_t flashAddr)
{
    bool valid = false;

    if (flashAddr < (CY_FLASH_BASE + CY_FLASH_SIZEOF_FLASH))
    {
        if ((flashAddr % CY_FLASH_SIZEOF_ROW) == 0UL)
        {
            valid = true;
        }
    }
    else
    #if (SFLASH_FLASH_M0_XTRA_ROWS == 1U)
        if ((flashAddr >= CY_FLASH_SFLASH_USERBASE) && (flashAddr < (CY_FLASH_SFLASH_USERBASE + CY_FLASH_SIZEOF_USERSFLASH)))
        {
            if ((flashAddr % CY_FLASH_SIZEOF_ROW) == 0UL)
            {
                valid = true;
            }
        }
        else
    #endif /* (SFLASH_FLASH_M0_XTRA_ROWS == 1U) */
    {
        valid = false;
    }

    return (valid);
}


/*******************************************************************************
* Function Name: Cy_Flash_GetRowNum
********************************************************************************
*
* Gets the (supervisory) Flash row number out of the absolute address.
*
* \param flashAddr Flash row address.
*
* \return Row number. Returns zero for invalid address.
*
*******************************************************************************/
static uint32_t Cy_Flash_GetRowNum(uint32_t flashAddr)
{
    uint32_t result = 0U;

    if (flashAddr < (CY_FLASH_BASE + CY_FLASH_SIZEOF_FLASH))
    {
        result = (flashAddr - CY_FLASH_BASE) / CY_FLASH_SIZEOF_ROW;
    }
    #if (SFLASH_FLASH_M0_XTRA_ROWS == 1U)
        else /* Assume SFLASH */
        {
            result = (flashAddr - CY_FLASH_SFLASH_USERBASE) / CY_FLASH_SIZEOF_ROW;
        }
    #endif /* (SFLASH_FLASH_M0_XTRA_ROWS == 1U) */

    return (result);
}


/*******************************************************************************
 * Function Name: Cy_Flash_ClockBackup
********************************************************************************
*
* Backups the device clock configuration.
*
* \return \ref cy_en_flashdrv_status_t
*
*******************************************************************************/
static cy_en_flashdrv_status_t Cy_Flash_ClockBackup(void)
{
    cy_en_flashdrv_status_t result = CY_FLASH_DRV_SUCCESS;
    volatile uint32_t   parameters[2U];

    parameters[0U] =(uint32_t) ((CY_FLASH_KEY_TWO(CY_FLASH_API_OPCODE_CLK_BACKUP) <<  CY_FLASH_PARAM_KEY_TWO_OFFSET) |
                            CY_FLASH_KEY_ONE);
    parameters[1U] = (uint32_t) &cySysFlashBackup.clockSettings[0U];
    CPUSS_SYSARG = (uint32_t) &parameters[0U];
    CPUSS_SYSREQ = CY_FLASH_CPUSS_REQ_START | CY_FLASH_API_OPCODE_CLK_BACKUP;
    __NOP();
    result = ProcessStatusCode();

    /* Enabling IMO after backup completion as required by hardware.
    *  The Cy_Flash_ClockRestore() restores original state of the system.
    */
    Cy_SysClk_ImoEnable();

    return (result);
}


/*******************************************************************************
 * Function Name: Cy_Flash_ClockConfig
********************************************************************************
*
* \brief Configures the device clocks for the Flash writing.
*
* \return \ref cy_en_flashdrv_status_t
*
*******************************************************************************/
static cy_en_flashdrv_status_t Cy_Flash_ClockConfig(void)
{
    cy_en_flashdrv_status_t result = CY_FLASH_DRV_SUCCESS;

    /* FM-Lite Clock Configuration */
    CPUSS_SYSARG =(uint32_t) ((CY_FLASH_KEY_TWO(CY_FLASH_API_OPCODE_CLK_CONFIG) <<  CY_FLASH_PARAM_KEY_TWO_OFFSET) |
                    CY_FLASH_KEY_ONE);
    CPUSS_SYSREQ = CY_FLASH_CPUSS_REQ_START | CY_FLASH_API_OPCODE_CLK_CONFIG;
    __NOP();
    result = ProcessStatusCode();

    return (result);
}


/*******************************************************************************
 * Function Name: Cy_Flash_ClockRestore
********************************************************************************
*
* \brief Restores the device clock configuration previously saved with
* \ref Cy_Flash_ClockBackup.
*
* \return \ref cy_en_flashdrv_status_t
*
********************************************************************************/
static cy_en_flashdrv_status_t Cy_Flash_ClockRestore(void)
{
    cy_en_flashdrv_status_t result = CY_FLASH_DRV_SUCCESS;
    volatile uint32_t   parameters[2U];

    /* FM-Lite Clock Restore */
    parameters[0U] = (uint32_t) ((CY_FLASH_KEY_TWO(CY_FLASH_API_OPCODE_CLK_RESTORE) <<  CY_FLASH_PARAM_KEY_TWO_OFFSET) |
                    CY_FLASH_KEY_ONE);
    parameters[1U] = (uint32_t) &cySysFlashBackup.clockSettings[0U];
    CPUSS_SYSARG = (uint32_t) &parameters[0U];
    CPUSS_SYSREQ = CY_FLASH_CPUSS_REQ_START | CY_FLASH_API_OPCODE_CLK_RESTORE;

    __NOP();
    result = ProcessStatusCode();

    return (result);
}


/* [] END OF FILE */
