/* EFS file import/export service, stock
 * D:\01_workspace\s200_ap510b_iar_git\platform\protocols\efs_service\efs_service.c
 * (native object 0x456722..0x458df0). */
#ifndef G2_EFS_SERVICE_H
#define G2_EFS_SERVICE_H

#include <stdint.h>

/* 0xAA-transport command bytes owned by the EFS service. */
#define G2_EFS_CMD_IMPORT_CONTROL 0xC4u /* subcommand 0 start, 1 data begin, 2 result check */
#define G2_EFS_CMD_IMPORT_DATA    0xC5u /* raw chunk, acknowledged {1,status} */
#define G2_EFS_CMD_EXPORT_CONTROL 0xC6u /* subcommand 0 start, 1 next chunk, 2 result, 3 cancel */
#define G2_EFS_CMD_EXPORT_DATA    0xC7u /* export chunk, same parser as 0xC6 */

/* eEvenFileServiceType_* values carried in the start header. */
enum {
    G2_EFS_TYPE_NOTIFICATION_JSON_WHITELIST = 0u,
    G2_EFS_TYPE_ANDROID_MSG_JSON_NOTIFICATION = 1u,
    G2_EFS_TYPE_LOGGER_FILE = 2u,     /* export only */
    G2_EFS_TYPE_TRACEPOINT_FILE = 3u, /* export only */
    G2_EFS_TYPE_OTHER_FILE = 0xAAu,
};

/* Frame entry registered for service 0x400; always returns 0. */
int32_t semantic_EfsFrameDispatch(uint8_t command, const uint8_t *payload, uint16_t length);
/* Fixed {1,status} acknowledgements for 0xC5 frames (status 4, 2, 5). */
void semantic_EfsNotifyStatus4(uint8_t command);
void semantic_EfsNotifyStatus2(uint8_t command);
void semantic_EfsNotifyStatus5(uint8_t command);
/* Non-zero while an import/export transfer is armed (isStart == 1). */
uint8_t semantic_EfsTransferActive(void);
/* Device-side abort of an active export: notifies 0xC6 {3,8} and clears state. */
void EFS_CancelExport(void);

#endif
