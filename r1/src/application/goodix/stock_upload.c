/* Stock 0x2d66c, called by GH3x2xGetFrameDataAndProcess at 0x2c5ce.
 * The stock PC-tool upload hook is disabled. Match the pinned public
 * gh_uprotocol.c disabled branch; do not infer an upload transport here. */
#include "gh_drv.h"
void Gh2x2xUploadDataToMaster(const STGh3x2xFrameInfo *const frame,
                            GU16 frame_count, GU16 frame_number, GU8 *tags)
{
    (void)frame;
    (void)frame_count;
    (void)frame_number;
    (void)tags;
}
