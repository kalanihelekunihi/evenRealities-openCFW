#include "ess_audio.h"
#include <assert.h>
#include <string.h>
int main(void) {
 /* Same normal packet bytes as stock original-instruction test: synthetic LC3
  * marker bytes, not real encoded sound. */
 uint8_t pdu[208]={0x1b,0x64,0x08};
 memset(pdu+3,0x55,200);
 pdu[203]=0x12;pdu[204]=0;pdu[205]=0xd3;pdu[206]=0xff;pdu[207]=7;
 G2EssAudio a;
 assert(g2_ess_audio_att(pdu,sizeof(pdu),&a));
 assert(a.lc3_frames==pdu+3 && a.energy_ratio==18 && a.angle_degrees==-45 && a.sequence==7);
 assert(g2_ess_audio_value(pdu+3,205,&a));
 assert(!g2_ess_audio_att(pdu,207,&a));
 assert(!g2_ess_audio_att(NULL,208,&a));
 assert(!g2_ess_audio_value(pdu+3,204,&a));
 assert(!g2_ess_audio_value(pdu+3,205,NULL));
 pdu[0]=0x1d;assert(!g2_ess_audio_att(pdu,208,&a));
 pdu[0]=0x1b;pdu[1]=0x65;assert(!g2_ess_audio_att(pdu,208,&a));
 assert(g2_audio_sequence_distance(255,0)==1);
 return 0;
}
