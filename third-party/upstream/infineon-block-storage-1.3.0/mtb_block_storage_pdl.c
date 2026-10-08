/***********************************************************************************************//**
 * \file mtb_block_storage_pdl.c
 *
 * \brief
 * Utility library for for defining storage to NVM for PSOC 4 that is not supported by HAL NVM.
 *
 ***************************************************************************************************
 * \copyright
 * Copyright 2023 Cypress Semiconductor Corporation (an Infineon company) or
 * an affiliate of Cypress Semiconductor Corporation
 *
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
 **************************************************************************************************/
#if defined(COMPONENT_CAT2)

#include "mtb_block_storage.h"
#include "cy_flash.h"

#include <string.h>

#define MTB_BLOCK_STORAGE_PDL_ERASE_VALUE   (0x00)


//--------------------------------------------------------------------------------------------------
// mtb_block_storage_pdl_read_size
//--------------------------------------------------------------------------------------------------
static uint32_t mtb_block_storage_pdl_read_size(void* context, uint32_t addr)
{
    CY_UNUSED_PARAMETER(context);
    CY_UNUSED_PARAMETER(addr);
    //Read operation is based on direct memory access so read size is always one 32-bit word.
    return 1;
}


//--------------------------------------------------------------------------------------------------
// mtb_block_storage_pdl_program_size
//--------------------------------------------------------------------------------------------------
static uint32_t mtb_block_storage_pdl_program_size(void* context, uint32_t addr)
{
    CY_UNUSED_PARAMETER(context);
    CY_UNUSED_PARAMETER(addr);
    return CY_FLASH_SIZEOF_ROW;
}


//--------------------------------------------------------------------------------------------------
// mtb_block_storage_pdl_erase_size
//--------------------------------------------------------------------------------------------------
static uint32_t mtb_block_storage_pdl_erase_size(void* context, uint32_t addr)
{
    CY_UNUSED_PARAMETER(context);
    CY_UNUSED_PARAMETER(addr);
    return CY_FLASH_SIZEOF_ROW;
}


//--------------------------------------------------------------------------------------------------
// mtb_block_storage_pdl_erase_value
//--------------------------------------------------------------------------------------------------
static uint8_t mtb_block_storage_pdl_erase_value(void* context, uint32_t addr)
{
    CY_UNUSED_PARAMETER(context);
    CY_UNUSED_PARAMETER(addr);
    return MTB_BLOCK_STORAGE_PDL_ERASE_VALUE;
}


//--------------------------------------------------------------------------------------------------
// mtb_block_storage_pdl_read
//--------------------------------------------------------------------------------------------------
static cy_rslt_t mtb_block_storage_pdl_read(void* context, uint32_t addr, uint32_t length,
                                            uint8_t* buf)
{
    CY_UNUSED_PARAMETER(context);
    (void)memcpy((uint8_t*)buf, (const uint8_t*)(addr), length);
    return CY_RSLT_SUCCESS;
}


//--------------------------------------------------------------------------------------------------
// mtb_block_storage_pdl_program
//--------------------------------------------------------------------------------------------------
static cy_rslt_t mtb_block_storage_pdl_program(void* context, uint32_t addr, uint32_t length,
                                               const uint8_t* buf)
{
    cy_rslt_t result = CY_RSLT_SUCCESS;
    uint32_t prog_size = mtb_block_storage_pdl_program_size(context, addr);


    if ((0 != (length % prog_size)))
    {
        result = MTB_BLOCK_STORAGE_INVALID_SIZE_ERROR;
    }

    if (result == CY_RSLT_SUCCESS)
    {
        for (uint32_t loc = addr; result == CY_RSLT_SUCCESS && loc < addr + length;
             loc += prog_size, buf += prog_size)
        {
            if (CY_FLASH_DRV_SUCCESS == Cy_Flash_WriteRow((uint32_t)loc, (uint32_t*)buf))
            {
                result = CY_RSLT_SUCCESS;
            }
        }
    }

    return result;
}


//--------------------------------------------------------------------------------------------------
// mtb_block_storage_pdl_erase
//--------------------------------------------------------------------------------------------------
static cy_rslt_t mtb_block_storage_pdl_erase(void* context, uint32_t addr, uint32_t length)
{
    cy_rslt_t result = CY_RSLT_SUCCESS;
    uint32_t erase_size = mtb_block_storage_pdl_erase_size(context, addr);
    uint32_t buffer[CY_FLASH_SIZEOF_ROW] = { 0u };

    if ((0 != (length % erase_size)))
    {
        result = MTB_BLOCK_STORAGE_INVALID_SIZE_ERROR;
    }

    if (result == CY_RSLT_SUCCESS)
    {
        for (uint32_t loc = addr; result == CY_RSLT_SUCCESS && loc < addr + length;
             loc += erase_size)
        {
            if (CY_FLASH_DRV_SUCCESS == Cy_Flash_WriteRow((uint32_t)loc, &buffer[0]))
            {
                result = CY_RSLT_SUCCESS;
            }
        }
    }
    return result;
}


//--------------------------------------------------------------------------------------------------
// mtb_block_storage_pdl_is_in_range
//--------------------------------------------------------------------------------------------------
static bool mtb_block_storage_pdl_is_in_range(void* context, uint32_t addr, uint32_t length)
{
    CY_UNUSED_PARAMETER(context);
    bool result = false;
    if ((((addr) > CY_FLASH_BASE) && ((addr+length) <= (CY_FLASH_BASE + CY_FLASH_SIZE))))
    {
        result = true;
    }
    return result;
}


//--------------------------------------------------------------------------------------------------
// mtb_block_storage_pdl_is_in_erase_Required
//--------------------------------------------------------------------------------------------------
static bool mtb_block_storage_pdl_is_erase_required(void* context, uint32_t addr, uint32_t length)
{
    CY_UNUSED_PARAMETER(context);
    CY_UNUSED_PARAMETER(addr);
    CY_UNUSED_PARAMETER(length);
    return false;
}


//--------------------------------------------------------------------------------------------------
// mtb_block_storage_create_pdl
//--------------------------------------------------------------------------------------------------
cy_rslt_t mtb_block_storage_create_pdl(mtb_block_storage_t* bsd)
{
    cy_rslt_t result = CY_RSLT_SUCCESS;

    if (NULL == bsd)
    {
        result = MTB_BLOCK_STORAGE_INVALID_INPUT_ERROR;
    }

    if (result == CY_RSLT_SUCCESS)
    {
        bsd->read = mtb_block_storage_pdl_read;
        bsd->program = mtb_block_storage_pdl_program;
        bsd->erase = mtb_block_storage_pdl_erase;
        bsd->program_nb = NULL; //Setting NULL, as program_nb is not supported
        bsd->erase_nb = NULL; //Setting NULL, as erase_nb is not supported
        bsd->get_read_size = mtb_block_storage_pdl_read_size;
        bsd->get_program_size = mtb_block_storage_pdl_program_size;
        bsd->get_erase_size = mtb_block_storage_pdl_erase_size;
        bsd->get_erase_value = mtb_block_storage_pdl_erase_value;
        bsd->is_in_range = mtb_block_storage_pdl_is_in_range;
        bsd->is_erase_required = mtb_block_storage_pdl_is_erase_required;
        bsd->context = NULL;
    }
    return result;
}


#endif // if defined(COMPONENT_CAT2)
