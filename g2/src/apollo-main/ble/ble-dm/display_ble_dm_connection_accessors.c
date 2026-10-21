/* Packetcraft Cordio DmConnPeerAddr 0x4b6eea and DmConnRole 0x4b73c4. */
#include <stdint.h>
extern uint8_t audio_dm_connection_records[]; /* live dmCb.conn[0], RAM 0x200712a4; 3 records x 48 */
const uint8_t *audio_dm_conn_peer_address(uint8_t connection) {
    /* Native accessor does not validate the connection identifier. */
    return audio_dm_connection_records+((uint32_t)connection*48u)-48u;
}
uint8_t audio_dm_conn_role(uint8_t connection) {
    if(connection==0u || connection>3u) return 0xffu;
    return audio_dm_connection_records[((uint32_t)connection*48u)-0x17u];
}
