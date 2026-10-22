/* Native ATTS CSF callback 0x53482c and children 0x4bb07c, 0x47b418. */
#include <stdint.h>
extern uint8_t audio_ble_atts_connection_rows[]; /* live 0x200717b0 */
extern void *audio_queue_copy_bytes(void *,const void *,uint32_t); /* selected 0x439be4 */

void audio_ble_atts_csf_copy(uint8_t *row,uint8_t value,const uint8_t *source) {
    if(source!=0 && row!=0) {
        row[0x84u]=value;
        (void)audio_queue_copy_bytes(row+0x85u,source,1u);
    }
}
