/* SPDX-License-Identifier: MIT */
/* Backup LvpAudioInUpdateReadIndex: unsigned wrapping sum and comparison.
 * Only the two consumed audio-control fields are described here. */
#include <stdint.h>
struct audio_indices { uint32_t read_index, write_index; };
extern volatile struct audio_indices backup_audio_indices;
int open_cfw_gx8002_backup_audio_read_index(uint32_t offset)
{
    uint32_t next=backup_audio_indices.read_index+offset;
    if(next>backup_audio_indices.write_index)return -1;
    backup_audio_indices.read_index=next;
    return 0;
}
