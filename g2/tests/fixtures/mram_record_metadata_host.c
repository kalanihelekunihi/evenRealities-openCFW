/*
 * SPDX-License-Identifier: MIT
 *
 * Native host oracle for the bounded Cordio record-metadata cluster.
 */

unsigned char open_cfw_test_mram_metadata_records[10U * 200U];
unsigned char open_cfw_test_mram_metadata_device_hash[16U];

unsigned int open_cfw_test_mram_metadata_update_calls;
unsigned int open_cfw_test_mram_metadata_verify_calls;
unsigned int open_cfw_test_mram_metadata_connection_id_calls;
unsigned int open_cfw_test_mram_metadata_connection_active_calls;
unsigned int open_cfw_test_mram_metadata_connection_id;
int open_cfw_test_mram_metadata_connection_active_result;
unsigned int open_cfw_test_mram_metadata_connection_active_argument;
const unsigned char *open_cfw_test_mram_metadata_update_record;
const unsigned char *open_cfw_test_mram_metadata_verify_record;
unsigned int open_cfw_test_mram_metadata_trace[16U];
unsigned int open_cfw_test_mram_metadata_trace_count;

static unsigned int
open_cfw_test_mram_metadata_update(const unsigned char *record)
{
    open_cfw_test_mram_metadata_update_record = record;
    ++open_cfw_test_mram_metadata_update_calls;
    open_cfw_test_mram_metadata_trace[
        open_cfw_test_mram_metadata_trace_count++
    ] = 3U;
    return 0U;
}

static unsigned int
open_cfw_test_mram_metadata_verify(const unsigned char *record)
{
    open_cfw_test_mram_metadata_verify_record = record;
    ++open_cfw_test_mram_metadata_verify_calls;
    open_cfw_test_mram_metadata_trace[
        open_cfw_test_mram_metadata_trace_count++
    ] = 4U;
    return 0U;
}

static unsigned int open_cfw_test_mram_metadata_get_connection_id(void)
{
    ++open_cfw_test_mram_metadata_connection_id_calls;
    open_cfw_test_mram_metadata_trace[
        open_cfw_test_mram_metadata_trace_count++
    ] = 1U;
    return open_cfw_test_mram_metadata_connection_id;
}

static int open_cfw_test_mram_metadata_is_connection_active(
    unsigned int connection_id
)
{
    open_cfw_test_mram_metadata_connection_active_argument =
        connection_id;
    ++open_cfw_test_mram_metadata_connection_active_calls;
    open_cfw_test_mram_metadata_trace[
        open_cfw_test_mram_metadata_trace_count++
    ] = 2U;
    return open_cfw_test_mram_metadata_connection_active_result;
}

#define OPEN_CFW_MRAM_METADATA_UPDATE(record) \
    open_cfw_test_mram_metadata_update(record)
#define OPEN_CFW_MRAM_METADATA_VERIFY(record) \
    open_cfw_test_mram_metadata_verify(record)
#define OPEN_CFW_MRAM_METADATA_CONNECTION_ID() \
    open_cfw_test_mram_metadata_get_connection_id()
#define OPEN_CFW_MRAM_METADATA_CONNECTION_ACTIVE(connection_id) \
    open_cfw_test_mram_metadata_is_connection_active(connection_id)
#define OPEN_CFW_MRAM_METADATA_RECORDS \
    open_cfw_test_mram_metadata_records
#define OPEN_CFW_MRAM_METADATA_DEVICE_DB_HASH \
    open_cfw_test_mram_metadata_device_hash

#include "../../components/apollo_main/core_overlay/mram_record_metadata.c"
