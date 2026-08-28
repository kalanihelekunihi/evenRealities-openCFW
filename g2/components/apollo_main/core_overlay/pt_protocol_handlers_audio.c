/* SPDX-License-Identifier: MIT */
#include "pt_protocol_handlers_audio.h"
static int valid(const uint8_t*r,uint8_t n,uint8_t m){return r!=NULL&&n>=m;}
static int mode(const struct open_cfw_pt_audio_providers*x){uint8_t v;if(x==NULL||x->get_product_mode==NULL||x->get_product_mode(&v,x->context)!=0)return-1;return v==1U;}
static int header(uint8_t c,uint8_t n,uint8_t*p,uint8_t*l){if(p==NULL||l==NULL)return-1;p[0]=c;p[1]=1U;p[2]=3U;p[3]=n;*l=(uint8_t)(4U+n);return 0;}
static void put32be(uint8_t*p,uint32_t v){p[0]=(uint8_t)(v>>24U);p[1]=(uint8_t)(v>>16U);p[2]=(uint8_t)(v>>8U);p[3]=(uint8_t)v;}

static int control(const uint8_t*r,uint8_t n,uint8_t*p,uint8_t*l,void*c,uint8_t channel,uint8_t response){const struct open_cfw_pt_audio_providers*x=c;uint8_t result=5U;int m;if(!valid(r,n,6U))return OPEN_CFW_PT_INVALID_ARGUMENT;m=mode(x);if(m<0)return OPEN_CFW_PT_HANDLER_FAILED;if(m){if(r[4]>3U)result=3U;else if(x->control_channel==NULL)return OPEN_CFW_PT_HANDLER_FAILED;else result=x->control_channel(channel,r[4],r[5],x->context)==0?0U:1U;}if(header(response,2U,p,l)!=0)return OPEN_CFW_PT_INVALID_ARGUMENT;p[4]=result;p[5]=r[4];return 0;}
static int handler_18(const uint8_t*r,uint8_t n,uint8_t*p,uint8_t*l,void*c){return control(r,n,p,l,c,0U,0x19U);}
static int handler_19(const uint8_t*r,uint8_t n,uint8_t*p,uint8_t*l,void*c){return control(r,n,p,l,c,1U,0x1AU);}

static int handler_1a(const uint8_t*r,uint8_t n,uint8_t*p,uint8_t*l,void*c){const struct open_cfw_pt_audio_providers*x=c;uint8_t data[210];uint16_t bytes=0U;int done=0;int m;size_t i;uint32_t sum=0U;if(!valid(r,n,6U)||p==NULL||l==NULL)return OPEN_CFW_PT_INVALID_ARGUMENT;m=mode(x);if(m<0)return OPEN_CFW_PT_HANDLER_FAILED;if(!m){p[0]=0x1BU;p[1]=1U;p[2]=3U;p[3]=2U;p[4]=5U;p[5]=r[5];*l=6U;return 0;}if(x->read_test_file_chunk==NULL||x->read_test_file_chunk(r[5],r[4]==1U,data,&bytes,&done,x->context)!=0||bytes>210U){p[0]=0x1BU;p[1]=1U;p[2]=3U;p[3]=2U;p[4]=3U;p[5]=r[5];*l=6U;return 0;}p[0]=0x1BU;p[1]=1U;p[2]=3U;p[3]=216U;p[4]=r[5];for(i=0U;i<210U;++i){p[10U+i]=i<bytes?data[i]:0U;sum+=p[10U+i];}put32be(p+5U,sum);p[9]=done?1U:0U;*l=220U;return 0;}

static int handler_1b(const uint8_t*r,uint8_t n,uint8_t*p,uint8_t*l,void*c){const struct open_cfw_pt_audio_providers*x=c;if(!valid(r,n,4U)||x==NULL||x->read_metrics_32==NULL||header(0x20U,32U,p,l)!=0)return OPEN_CFW_PT_INVALID_ARGUMENT;return x->read_metrics_32(p+4U,32U,x->context)==0?0:OPEN_CFW_PT_HANDLER_FAILED;}
static int handler_1c(const uint8_t*r,uint8_t n,uint8_t*p,uint8_t*l,void*c){const struct open_cfw_pt_audio_providers*x=c;if(!valid(r,n,4U)||x==NULL||x->read_version_status_5==NULL||header(0x24U,5U,p,l)!=0)return OPEN_CFW_PT_INVALID_ARGUMENT;return x->read_version_status_5(p+4U,5U,x->context)==0?0:OPEN_CFW_PT_HANDLER_FAILED;}

int open_cfw_pt_bind_audio_handlers(struct open_cfw_pt_protocol *protocol,const struct open_cfw_pt_audio_providers *providers){static const struct{uint8_t command;open_cfw_pt_handler_fn handler;}bindings[]={
{0x18U,handler_18},{0x19U,handler_19},{0x1AU,handler_1a},{0x1BU,handler_1b},{0x1CU,handler_1c},};size_t i;if(protocol==NULL||providers==NULL)return OPEN_CFW_PT_INVALID_ARGUMENT;for(i=0U;i<sizeof(bindings)/sizeof(bindings[0]);++i)if(open_cfw_pt_protocol_bind(protocol,bindings[i].command,bindings[i].handler,(void*)providers)!=0)return OPEN_CFW_PT_HANDLER_FAILED;return 0;}
