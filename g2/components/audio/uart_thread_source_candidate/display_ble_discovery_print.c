/* Native appDiscPrintCharInfo 0x5322f6 and appDiscPrintDescInfo 0x532644.
 * The caller supplies a Cordio ATT message. The payload length/format is
 * trusted exactly as in the native logging routines. */
#include <stdint.h>
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern void audio_dump_hex(const char *,uint32_t,const void *,uint32_t);
static const char module[]="app.disc";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\app_disc.c";
static uint16_t rd16(const uint8_t *p){return (uint16_t)p[0]|((uint16_t)p[1]<<8);}
static uint32_t rd32(const uint8_t *p){return (uint32_t)p[0]|((uint32_t)p[1]<<8)|((uint32_t)p[2]<<16)|((uint32_t)p[3]<<24);}
static void simple(uint32_t line,const char *fn,const char *plain,const char *short_text){
    if((audio_log_flags()&2u)!=0u)audio_log_extended(4,module,source,fn,line,plain);
    if((audio_log_flags()&5u)!=0u)(void)compressed_log_output(0x10000000u,short_text,short_text);
}
static void one(uint32_t line,uint32_t mask,const char *fn,const char *plain,const char *short_text,uint32_t a){
    if((audio_log_flags()&2u)!=0u)audio_log_extended(4,module,source,fn,line,plain,a);
    if((audio_log_flags()&5u)!=0u)(void)compressed_log_output(mask,short_text,short_text,a);
}
static void two(uint32_t line,const char *fn,const char *plain,const char *short_text,uint32_t a,uint32_t b){
    if((audio_log_flags()&2u)!=0u)audio_log_extended(4,module,source,fn,line,plain,a,b);
    if((audio_log_flags()&5u)!=0u)(void)compressed_log_output(0x10800000u,short_text,short_text,a,b);
}
void audio_ble_discovery_print_characteristics_5322f6(uint8_t *context,const uint8_t *message){
    (void)context;
    const uint8_t *p=(const uint8_t *)(uintptr_t)rd32(message+4);
    const uint8_t properties=p[3];
    const uint16_t handle=rd16(p+4);
    static const char fn[]="appDiscPrintCharInfo";
    if(p[0]==7u){
        two(0x210u,fn,"   -CharacteristicDeclaration, UUID:0x%04X, handle=0x%04X",
            "[app.disc]   -CharacteristicDeclaration, UUID:0x%04X, handle=0x%04X",rd16(p+6),handle);
    }else{
        one(0x214u,0x10400000u,fn,"   -CharacteristicDeclaration, handle=0x%04X",
            "[app.disc]   -CharacteristicDeclaration, handle=0x%04X",handle);
        audio_dump_hex("          - appDiscPrint UUID128:",16u,p+6,16u);
    }
    one(0x223u,0x10400000u,fn,"     -Properties: = 0x%X",
        "[app.disc]     -Properties: = 0x%X",properties);
    static const char *const plain[]={"           broadcast","           read","           write_no_resp",
        "           write","           notify","           indicate","           auth_signed_wr"};
    static const char *const compact[]={"[app.disc]           broadcast","[app.disc]           read",
        "[app.disc]           write_no_resp","[app.disc]           write","[app.disc]           notify",
        "[app.disc]           indicate","[app.disc]           auth_signed_wr"};
    for(uint32_t bit=0;bit<7u;bit++)if((properties&(1u<<bit))!=0u)
        simple(0x224u+bit,fn,plain[bit],compact[bit]);
}
void audio_ble_discovery_print_descriptors_532644(uint8_t *context,const uint8_t *message){
    (void)context;
    const uint8_t *const payload=(const uint8_t *)(uintptr_t)rd32(message+4);
    const uint8_t format=payload[0];
    const uint8_t *item=payload+1;
    const uint8_t *const end=payload+rd16(message+8);
    static const char fn[]="appDiscPrintDescInfo";
    while(item<end){
        const uint16_t handle=rd16(item);
        if(format==1u){
            const uint16_t uuid=rd16(item+2);
            item+=4;
            switch(uuid){
            case 0x2900u:two(0x253u,fn,"     -Descriptor: Extended, UUID:0x%04X, handle=0x%04X",
                "[app.disc]     -Descriptor: Extended, UUID:0x%04X, handle=0x%04X",uuid,handle);break;
            case 0x2901u:two(600u,fn,"     -Descriptor: User Desc, UUID:0x%04X, handle=0x%04X",
                "[app.disc]     -Descriptor: User Desc, UUID:0x%04X, handle=0x%04X",uuid,handle);break;
            case 0x2902u:two(0x24eu,fn,"     -Descriptor: CCCD, UUID:0x%04X, handle=0x%04X",
                "[app.disc]     -Descriptor: CCCD, UUID:0x%04X, handle=0x%04X",uuid,handle);break;
            case 0x2908u:two(0x25du,fn,"     -Descriptor: Report Ref, UUID:0x%04X, handle=0x%04X",
                "[app.disc]     -Descriptor: Report Ref, UUID:0x%04X, handle=0x%04X",uuid,handle);break;
            default:two(0x262u,fn,"     -Descriptor: Unknown, UUID:0x%04X, handle=0x%04X",
                "[app.disc]     -Descriptor: Unknown, UUID:0x%04X, handle=0x%04X",uuid,handle);break;
            }
        }else{
            one(0x268u,0x10400000u,fn,"     -Descriptor: handle=0x%04X",
                "[app.disc]     -Descriptor: handle=0x%04X",handle);
            audio_dump_hex("UUID128:",16u,item+2,16u);
            item+=0x12;
            simple(0x26bu,fn," ","[app.disc] ");
        }
    }
}
