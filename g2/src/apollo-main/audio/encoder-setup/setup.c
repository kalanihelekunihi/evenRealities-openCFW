/* Bounded independent reconstruction of 0x59123A and wrappers; no LC3 encode body. */
#include <stdint.h>
#include <stddef.h>
static int dt_index(int dt,int hr){return dt==2500?0:dt==5000?1:(!hr&&dt==7500)?2:dt==10000?3:4;}
static int rate_index(int sr,int hr){
 if(hr)return sr==48000?5:sr==96000?6:7;
 return sr==8000?0:sr==16000?1:sr==24000?2:sr==32000?3:sr==48000?4:7;
}
void *audio_encoder_setup_selected(int hr,int dt,int sr,int pcm_sr,void *memory){
 int pcm=pcm_sr>0?pcm_sr:sr;int d=dt_index(dt,hr),s=rate_index(sr,hr),p=rate_index(pcm,hr);
 if(d>=4||p>=7||p<s||!memory)return 0;
 static const uint32_t geometry[]={20,40,60,80,120,120,240};
 uint8_t *m=memory;for(uint32_t i=0;i<0x4b0;i++)m[i]=0;
 m[0]=d;m[1]=s;m[2]=p;
 uint32_t n=(d+1)*geometry[p],half=geometry[p]/2,overlap=(n+half)/2;
 *(uint32_t*)(m+0x4a0)=half;*(uint32_t*)(m+0x4a4)=overlap;*(uint32_t*)(m+0x4a8)=n+overlap;
 /* Supported positive selectors constrain products below signed-overflow bounds. */
 uint32_t samples=(uint32_t)(pcm*dt)/1000000,delay=(uint32_t)(pcm*1250)/1000000;
 uint32_t lookback=(uint32_t)(pcm*(dt==7500?2000:1250))/1000000;
 uint32_t history=samples+(delay+samples)/2+samples/2+lookback;
 for(uint32_t i=0;i<4*history;i++)m[0x4ac+i]=0;
 return memory;
}
void *audio_encoder_setup_standard(int dt,int sr,int pcm_sr,void *memory){return audio_encoder_setup_selected(0,dt,sr,pcm_sr,memory);}
void audio_encoder_reset_config(uint32_t *config){
 if(config)config[6]=(uintptr_t)audio_encoder_setup_standard((int)config[1],(int)config[2],0,config+7);
}
