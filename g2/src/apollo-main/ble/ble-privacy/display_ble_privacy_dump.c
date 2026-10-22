/* Native PrintSmpDbRecord 0x4789b0, authenticated app_db.c log fields. */
#include <stdint.h>
extern uint8_t audio_ble_privacy_nvm_records[10u*256u];
extern uint32_t audio_log_level(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
extern void audio_dump_hex(const char *,uint32_t,const uint8_t *,uint32_t);
static const char module[]="ble.smpdb";
static const char source[]="D:\\01_workspace\\s200_ap510b_iar_git\\third_party\\cordio\\ble-profiles\\sources\\apps\\app\\common\\app_db.c";
static const char function[]="PrintSmpDbRecord";
#define E0(level,line,msg) do { if(audio_log_level()&2u) audio_log_extended(level,module,source,function,line,msg); } while(0)
#define E(level,line,msg,...) do { if(audio_log_level()&2u) audio_log_extended(level,module,source,function,line,msg,__VA_ARGS__); } while(0)
#define C0(flags,msg) do { if((audio_log_level()&1u)||(audio_log_level()&4u)) (void)compressed_log_output(flags,msg,msg); } while(0)
#define C(flags,msg,...) do { if((audio_log_level()&1u)||(audio_log_level()&4u)) (void)compressed_log_output(flags,msg,msg,__VA_ARGS__); } while(0)
static uint16_t half(const uint8_t *p) { return *(const uint16_t *)(const void *)p; }
static uint32_t word(const uint8_t *p) { return *(const uint32_t *)(const void *)p; }
/* Stock 0x4789B0 (PrintSmpDbRecord; TSV FUN_004789b0) */
void audio_ble_privacy_dump_row(uint8_t *ignored,uint8_t index) {
    (void)ignored;
    const uint8_t *row=audio_ble_privacy_nvm_records+(uint32_t)index*256u;
    E(4u,0xb9u,"===== Device Database Record[%d] =====",index);
    C(0x10400000u,"[ble.smpdb]===== Device Database Record[%d] =====",index);
    E(4u,0xbdu,"Peer Address  : %02X:%02X:%02X:%02X:%02X:%02X",row[5],row[4],row[3],row[2],row[1],row[0]);
    C(0x11800000u,"[ble.smpdb]Peer Address  : %02X:%02X:%02X:%02X:%02X:%02X",row[5],row[4],row[3],row[2],row[1],row[0]);
    const char *type=row[6]==0u?"Public":(row[6]==1u?"Random":"Unknown");
    E(4u,0xc1u,"Address Type  : %s (%d)",type,row[6]);
    C(0x10800000u,"[ble.smpdb]Address Type  : %s (%d)",type,row[6]);
    const char *in_use=row[0x2fu]?"TRUE":"FALSE";
    E(4u,0xc2u,"Record In Use : %s",in_use);
    C(0x10400000u,"[ble.smpdb]Record In Use : %s",in_use);
    const char *valid=row[0x30u]?"TRUE":"FALSE";
    E(4u,0xc3u,"Record Valid  : %s",valid);
    C(0x10400000u,"[ble.smpdb]Record Valid  : %s",valid);
    E(4u,0xc4u,"Record Timestamp=%lu",word(row+0xc4u));
    C(0x10400000u,"[ble.smpdb]Record Timestamp=%lu",word(row+0xc4u));
    E(4u,0xc5u,"Key Valid Mask: 0x%02X",row[0x2eu]);
    C(0x10400000u,"[ble.smpdb]Key Valid Mask: 0x%02X",row[0x2eu]);
    const char *added=row[0x31u]?"TRUE":"FALSE";
    E(4u,0xc6u,"Peer Added to Resolving List: %s",added);
    C(0x10400000u,"[ble.smpdb]Peer Added to Resolving List: %s",added);
    const char *rpa=row[0x32u]?"TRUE":"FALSE";
    E(4u,0xc7u,"Peer RPA Only : %s",rpa);
    C(0x10400000u,"[ble.smpdb]Peer RPA Only : %s",rpa);
    E(4u,0xc8u,"keyValidMask : 0x%02X",row[0x2eu]);
    C(0x10400000u,"[ble.smpdb]keyValidMask : 0x%02X",row[0x2eu]);
    audio_dump_hex("Peer IRK",16u,row+7u,16u);
    audio_dump_hex("Peer CSRK",16u,row+0x1eu,16u);
    E0(4u,0xd0u,"--- Slave Role Fields ---");
    C0(0x10000000u,"[ble.smpdb]--- Slave Role Fields ---");
    audio_dump_hex("Slave Local LTK",16u,row+0x34u,16u);
    E(4u,0xd3u,"Local LTK Security Level: %d",row[0x4eu]);
    C(0x10400000u,"[ble.smpdb]Local LTK Security Level: %d",row[0x4eu]);
    const char *resolution=row[0x4fu]?"Supported":"Not Supported";
    E(4u,0xd4u,"Peer Address Resolution: %s",resolution);
    C(0x10400000u,"[ble.smpdb]Peer Address Resolution: %s",resolution);
    E0(4u,0xd7u,"--- Master Role Fields ---");
    C0(0x10000000u,"[ble.smpdb]--- Master Role Fields ---");
    audio_dump_hex("Master Peer LTK",16u,row+0x50u,16u);
    E(4u,0xd9u,"Peer LTK Security Level: %d",row[0x6au]);
    C(0x10400000u,"[ble.smpdb]Peer LTK Security Level: %d",row[0x6au]);
    E0(4u,0xdcu,"--- ATT Server Fields ---");
    C0(0x10000000u,"[ble.smpdb]--- ATT Server Fields ---");
    E(4u,0xddu,"Peer Sign Counter: %u",word(row+0x80u));
    C(0x10400000u,"[ble.smpdb]Peer Sign Counter: %u",word(row+0x80u));
    E(4u,0xdeu,"Change Aware State: %d",row[0x84u]);
    C(0x10400000u,"[ble.smpdb]Change Aware State: %d",row[0x84u]);
    E0(4u,0xe0u,"CCCD Table: ");
    C0(0x10000000u,"[ble.smpdb]CCCD Table: ");
    for(uint32_t i=0;i<10u;i++) {
        uint16_t value=half(row+0x6cu+i*2u);
        if(value!=0u) {
            E(4u,0xe3u,"[%d]=0x%04X ",i,value);
            C(0x10800000u,"[ble.smpdb][%d]=0x%04X ",i,value);
        }
    }
    E0(4u,0xe7u,"Client Supported Features: ");
    C0(0x10000000u,"[ble.smpdb]Client Supported Features: ");
    E(4u,0xe9u,"%02X",row[0x85u]);
    C(0x10400000u,"[ble.smpdb]%02X",row[0x85u]);
    E0(4u,0xedu,"--- ATT Client Fields ---");
    C0(0x10000000u,"[ble.smpdb]--- ATT Client Fields ---");
    const char *hash=row[0x86u]?"TRUE":"FALSE";
    E(4u,0xeeu,"Cache by Hash: %s",hash);
    C(0x10400000u,"[ble.smpdb]Cache by Hash: %s",hash);
    E0(4u,0xf2u,"Handle List: ");
    C0(0x10000000u,"[ble.smpdb]Handle List: ");
    for(uint32_t i=0;i<21u;i++) {
        uint16_t value=half(row+0x98u+i*2u);
        if(value!=0u) {
            E(4u,0xf5u,"0x%04X ",value);
            C(0x10400000u,"[ble.smpdb]0x%04X ",value);
        }
    }
    E(4u,0xf9u,"Discovery Status: 0x%02X",row[0xc2u]);
    C(0x10400000u,"[ble.smpdb]Discovery Status: 0x%02X",row[0xc2u]);
    const char *master=row[0xc3u]?"TRUE":"FALSE";
    E(4u,0xfau,"Master Role: %s",master);
    C(0x10400000u,"[ble.smpdb]Master Role: %s",master);
    E0(4u,0xfbu,"===============================");
    C0(0x10000000u,"[ble.smpdb]===============================");
}
