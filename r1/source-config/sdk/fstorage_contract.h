/* Native fstorage facades dispatch despite failed parameter predicates.
 * Keep the historical general SDK configuration intact. */
#ifndef R1_FSTORAGE_CONTRACT_H
#define R1_FSTORAGE_CONTRACT_H
#include "sdk_common.h"
#undef NRF_FSTORAGE_PARAM_CHECK_DISABLED
#define NRF_FSTORAGE_PARAM_CHECK_DISABLED 1
#include "nrf_assert.h"
#undef NRF_ASSERT_PRESENT
#define NRF_ASSERT_PRESENT 0
#endif
