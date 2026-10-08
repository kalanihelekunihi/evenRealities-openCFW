/* Reconstructed initializer token semantics; source/destination bounds are caller contracts. */
#include <stdint.h>
uint8_t *audio_startup_unpack(const uint8_t *src,uint32_t compressed_bytes,uint8_t *dst){
 const uint8_t *end=src+compressed_bytes;
 while(src!=end){uint8_t token=*src++;uint32_t literals=token&3,match=token>>4;
  if(!literals)literals=(uint32_t)(*src++) + 3;
  if(match==15)match=(uint32_t)(*src++) + 15;
  for(uint32_t i=1;i<literals;i++)*dst++=*src++;
  if(match){uint32_t offset=*src++,high=(token>>2)&3;if(high==3)high=*src++;offset+=high<<8;
   uint8_t *back=dst-offset;for(uint32_t i=0;i<match+2;i++)*dst++=*back++;
  }
 }
 return dst;
}
