/***********************************************************************************************//**
 * \file mtb_block_storage.h
 *
 * \brief
 * Utility library for defining storage to NVM.
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
#pragma once


#include "cy_result.h"
#include <stdbool.h>
#if defined(COMPONENT_MTB_HAL)
#include "mtb_hal.h"
#endif
#if defined(CY_USING_HAL) || defined(CY_USING_HAL_LITE)
#include "cyhal.h"
#endif
#if defined(COMPONENT_MW_SERIAL_MEMORY)
#include "mtb_serial_memory.h"
#endif

#if defined(COMPONENT_SERIAL_FLASH)
#include "cy_serial_flash_qspi.h"
#endif

/** A not supported operation is called. */
#define MTB_BLOCK_STORAGE_NOT_SUPPORTED_ERROR                 \
    CY_RSLT_CREATE(CY_RSLT_TYPE_ERROR, CY_RSLT_MODULE_ABSTRACTION_BLOCK_STORAGE, 0)
#define MTB_BLOCK_STORAGE_NOT_IN_RANGE_ERROR                  \
    CY_RSLT_CREATE(CY_RSLT_TYPE_ERROR, CY_RSLT_MODULE_ABSTRACTION_BLOCK_STORAGE, 1)
#define MTB_BLOCK_STORAGE_INVALID_SIZE_ERROR                  \
    CY_RSLT_CREATE(CY_RSLT_TYPE_ERROR, CY_RSLT_MODULE_ABSTRACTION_BLOCK_STORAGE, 2)
#define MTB_BLOCK_STORAGE_INVALID_INPUT_ERROR                  \
    CY_RSLT_CREATE(CY_RSLT_TYPE_ERROR, CY_RSLT_MODULE_ABSTRACTION_BLOCK_STORAGE, 3)

//Only limit support for non blocking functionality to PSoC6 for the moment
#if (defined(COMPONENT_CAT1A) && !defined(CY_DEVICE_TVIIBE)) && \
    !(MTB_HAL_DRIVER_AVAILABLE_NVM)
#define MTB_BLOCK_STORAGE_NON_BLOCKING_SUPPORTED
#endif
/**
 * \addtogroup group_block_storage Block Storage Library
 * \{
 * This library provides a convenient way to abstract an underlying memory by abstracting it and
 * definining APIs to interact with the device.
 *
 * \section section_block_storage_getting_started Getting Started
 * This section provides steps for getting started with this library using the two implemented
 * abstraction supported already.
 *
 * -# Include the block-storage library header in the application
 *      \snippet block_storage.c snippet_mtb_block_storage_include
 *
 * -# Initialize the block storage device
 * Example initialization using the pre implemented device built on top of HAL NVM
 *      \snippet block_storage.c snippet_mtb_block_storage_init_nvm
 * Example initialization using the pre implemented device built on top of Serial Memory
 *      \snippet block_storage.c snippet_mtb_block_storage_init_serial_memory
 * Example initialization using the pre implemented device built on top of Serial Flash
 *      \snippet block_storage.c snippet_mtb_block_storage_init_serial_flash
 * -# The library should now be ready to perform operations.
 *      - Program operation.
 *        \snippet block_storage.c snippet_mtb_block_storage_program
 *      - Read operation.
 *        \snippet block_storage.c snippet_mtb_block_storage_read
 *      - Erase operation.
 *        \snippet block_storage.c snippet_mtb_block_storage_erase
 *
 * Users can create their own implementation of other block devices by following the implementation
 * done for mtb_block_storage_create_hal_nvm and mtb_block_storage_create_pdl
 */

/** Function prototype to get the read size of the block device for a specific address.
 *
 * @param[in]  context  Context object that is passed into mtb_block_storage_*_create
 * @param[in]  addr     Address for which the read size is queried. This address
 *                      is passed in as start_addr + offset.
 * @return Read size of the memory device.
 */
typedef uint32_t (* mtb_block_storage_read_size_t)(void* context, uint32_t addr);

/** Function prototype to get the program size of the block device for a specific address
 *
 * @param[in]  context  Context object that is passed into mtb_block_storage_*_create
 * @param[in]  addr     Address for which the program size is queried. This address
 *                      is passed in as start_addr + offset.
 * @return Program size of the memory device.
 */
typedef uint32_t (* mtb_block_storage_program_size_t)(void* context, uint32_t addr);

/** Function prototype to get the erase size of the block device for a specific address
 *
 * @param[in]  context  Context object that is passed into mtb_block_storage_*_create
 * @param[in]  addr     Address for which the erase size is queried. This address is passed in a
 *                      start_addr + offset.
 * @return Erase size of the memory device.
 */
typedef uint32_t (* mtb_block_storage_erase_size_t)(void* context, uint32_t addr);

/** Function prototype to get the erase value of the block device for a specific memory
 *
 * @param[in]  context  Context object that is passed into mtb_block_storage_*_create
 * @param[in]  addr     Address for which the erase value is queried.
 * @return Erase value of the memory device.
 */
typedef uint8_t (* mtb_block_storage_erase_value_t)(void* context, uint32_t addr);

/** Function prototype for reading data from the block device.
 *
 * @param[in]  context  Context object that is passed into mtb_block_storage_*_create
 * @param[in]  addr     Address to read the data from the block device. This address
 *                      is passed in as start_addr + offset.
 * @param[in]  length   Length of the data that needs to be read.
 * @param[out] buf      Buffer to read the data.
 * @return Result of the read operation.
 */
typedef cy_rslt_t (* mtb_block_storage_read_t)(void* context, uint32_t addr, uint32_t length,
                                               uint8_t* buf);

/** Function prototype for writing data to the block device.
 *
 * @param[in]  context  Context object that is passed into mtb_block_storage_*_create
 * @param[in]  addr     Address to program the data into the block device. This address
 *                      is passed in as start_addr + offset.
 * @param[in]  length   Length of the data that needs to be written
 * @param[in]  buf      Data that needs to be written (size = length)
 * @return Result of the program operation.
 */
typedef cy_rslt_t (* mtb_block_storage_program_t)(void* context, uint32_t addr, uint32_t length,
                                                  const uint8_t* buf);

/** Function prototype for erasing the block device.
 *
 * @param[in]  context  Context object that is passed into mtb_block_storage_*_create
 * @param[in]  addr     Address to read the data from the device. This address
 *                      is passed in as start_addr + offset.
 * @param[in]  length   Length of the data that needs to be erased.
 * @return Result of the erase operation.
 */
typedef cy_rslt_t (* mtb_block_storage_erase_t)(void* context, uint32_t addr, uint32_t length);

/** Function prototype for writing data to the block device in a non blocking way.
 *
 * @param[in]  context  Context object that is passed into mtb_block_storage_*_create
 * @param[in]  addr     Address to program the data into the block device. This address
 *                      is passed in as start_addr + offset.
 * @param[in]  length   Length of the data that needs to be written
 * @param[in]  buf      Data that needs to be written (size = length)
 * @return Result of the program operation.
 */
typedef cy_rslt_t (* mtb_block_storage_program_nb_t)(void* context, uint32_t addr, uint32_t length,
                                                     const uint8_t* buf);

/** Function prototype for erasing the block device in a non blocking way.
 *
 * @param[in]  context  Context object that is passed into mtb_block_storage_*_create
 * @param[in]  addr     Address to read the data from the device. This address
 *                      is passed in as start_addr + offset.
 * @param[in]  length   Length of the data that needs to be erased.
 * @return Result of the erase operation.
 */
typedef cy_rslt_t (* mtb_block_storage_erase_nb_t)(void* context, uint32_t addr, uint32_t length);

/** Function prototype for checking if an address is in range from the block device.
 *
 * @param[in]  context  Context object that is passed into mtb_block_storage_*_create
 * @param[in]  addr     Starting address to perform the check on
 * @param[in]  length   Size of the area from the given address to perform the check on
 * @return Result of the is in range check.
 */
typedef bool (* mtb_block_storage_is_in_range_t)(void* context, uint32_t addr, uint32_t length);

/** Function prototype for checking if the memory type does require erase operation.
 *
 * @param[in]  context  Context object that is passed into mtb_block_storage_*_create
 * @param[in]  addr     Address of the memory area to perform the check on
 * @param[in]  length   Size of the area from the given address to perform the check on
 * @return Result of the is erase required check.
 */
typedef bool (* mtb_block_storage_is_erase_required_t)(void* context, uint32_t addr,
                                                       uint32_t length);

/** Block device interface */
typedef struct
{
    void*                               context;           /**< Context object that can be used in
                                                              the
                                                              block
                                                              device implementation */
    mtb_block_storage_read_size_t       get_read_size;         /**< Function to get read size for an
                                                                  address
                                                                */
    mtb_block_storage_program_size_t    get_program_size;      /**< Function to get program size for
                                                                  an
                                                                  address */
    mtb_block_storage_erase_size_t      get_erase_size;        /**< Function to get erase size for
                                                                  an
                                                                  address
                                                                */
    mtb_block_storage_erase_value_t     get_erase_value;    /**< Function to determine the erase
                                                               value
                                                                for the memory used */
    mtb_block_storage_read_t            read;              /**< Function to read from device */
    mtb_block_storage_program_t         program;           /**< Function to program to device */
    mtb_block_storage_erase_t           erase;             /**< Function to erase device */
    mtb_block_storage_program_nb_t      program_nb;     /**< Function to program to device in a
                                                           non blocking way*/
    mtb_block_storage_erase_nb_t        erase_nb;       /**< Function to erase device in a non
                                                           blocking way*/
    mtb_block_storage_is_in_range_t     is_in_range;        /**< Function to check whether and
                                                               memory
                                                               area
                                                               is in the memory range*/
    mtb_block_storage_is_erase_required_t     is_erase_required;        /**< Function to check
                                                                           whether the memory
                                                                           type does require erase
                                                                              operation */
} mtb_block_storage_t;

#if !defined(COMPONENT_CAT2)
#if (CYHAL_DRIVER_AVAILABLE_NVM) || (CYHAL_DRIVER_AVAILABLE_FLASH) || (MTB_HAL_DRIVER_AVAILABLE_NVM)
/** Function to create the block storage elements for devices that have HAL support.
 *
 * @param[in]  bsd  Block storage element to be initialized
 * @param[in]  obj  Preinitialized HAL NVM object that is to used for block storage
 *                  operations
 * @return Result of the create function
 */
#if (MTB_HAL_DRIVER_AVAILABLE_NVM)
cy_rslt_t mtb_block_storage_create_hal_nvm(mtb_block_storage_t* bsd, mtb_hal_nvm_t* obj);
#else
/** For backwards compatibility with the classic HAL*/
cy_rslt_t mtb_block_storage_create_hal_nvm(mtb_block_storage_t* bsd, void* obj);
#endif

/** Deprecated, for backwards compatibility */
#define mtb_block_storage_nvm_create(bsd) mtb_block_storage_create_hal_nvm(bsd, NULL)
#endif \
    //(CYHAL_DRIVER_AVAILABLE_NVM) || (CYHAL_DRIVER_AVAILABLE_FLASH) ||
    // (MTB_HAL_DRIVER_AVAILABLE_NVM)
#else // if !defined(COMPONENT_CAT2)
/** Function to create the block storage elements for CAT2 that does not have HAL NVM support.
 *  It is built directly on top of the PDL layer.
 *
 * @param[in]  bsd  Block storage element to be initialized
 * @return Result of the create function
 */
cy_rslt_t mtb_block_storage_create_pdl(mtb_block_storage_t* bsd);

/** Deprecated, for backwards compatibility */
#define mtb_block_storage_cat2_create mtb_block_storage_create_pdl
#endif // if !defined(COMPONENT_CAT2)

#if defined(COMPONENT_MW_SERIAL_MEMORY)
/** Function to create the block storage elements for devices that has serial memory
 * support.
 *
 * @param[in]  bsd  Block storage element to be initialized
 * @param[in]  obj  Preinitialized serial memory object that can be used for
 *                  block storage operations
 * @return Result of the create function
 */
cy_rslt_t mtb_block_storage_create_serial_memory(mtb_block_storage_t* bsd,
                                                 mtb_serial_memory_t* obj);
#endif // defined(COMPONENT_MW_SERIAL_MEMORY)

#if defined(COMPONENT_SERIAL_FLASH)
/** Function to create the block storage elements for devices that has serial flash
 * support.
 *
 * @param[in]  bsd  Block storage element to be initialized
 * @return Result of the create function
 */
cy_rslt_t mtb_block_storage_create_serial_flash(mtb_block_storage_t* bsd);
#endif // defined(COMPONENT_SERIAL_FLASH)

/** \} group_block_storage */
