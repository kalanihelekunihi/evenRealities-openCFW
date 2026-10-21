/* Native 0x52f99e: assign parsed image record pointers to their four live
 * address slots and the 12-byte per-record table.  These cells are runtime
 * storage; their initial values are supplied by the product image/runtime. */
#include <stdint.h>
extern uint32_t audio_log_flags(void);
extern void audio_log_extended(uint8_t,const char *,const char *,const char *,
                               uint32_t,const char *,...);
extern uint32_t compressed_log_output(uint32_t,const char *,const char *,...);
static const char module[]="srv.em9305";
static const char source_path[]="D:\\01_workspace\\s200_ap510b_iar_git\\platform\\service\\DFU\\service_em9305_dfu.c";
static const char function[]="_readImageData";
static const char bad[]="Unknown address 0x%08X for record[%d]";
static const char bad_compact[]="[srv.em9305]Unknown address 0x%08X for record[%d]";
static const char records_message[]="image_records = 0x%08X";
static const char records_compact[]="[srv.em9305]image_records = 0x%08X";
static const char entry_message[]="Image data[%d]=0x%08X, length=%d, address=0x%08X";
static const char entry_compact[]="[srv.em9305]Image data[%d]=0x%08X, length=%d, address=0x%08X";
#define W(a) (*(volatile uint32_t *)(uintptr_t)(a))
static uint32_t read32(const volatile uint8_t *p) {
    uint32_t v=0u;for(uint32_t i=0;i<4u;i++)v|=(uint32_t)p[i]<<(i*8u);return v;
}
static void write32(volatile uint8_t *p,uint32_t v) {
    for(uint32_t i=0;i<4u;i++)p[i]=(uint8_t)(v>>(i*8u));
}
uint32_t audio_ble_radio_record_data_52f99e(const void *image,uint32_t count) {
    volatile uint8_t *const records=(volatile uint8_t *)(uintptr_t)0x200731f0u;
    volatile uint8_t *const image_data=(volatile uint8_t *)(uintptr_t)0x2007348cu;
    for(uint32_t i=0;i<count;i++) {
        volatile uint8_t *row=records+i*16u;
        uint32_t address=read32(row+8u);
        if(address==0u)continue;
        uintptr_t slot;
        switch(address) {
        case 0x00300000u:slot=0x20074958u;break;
        case 0x00300400u:slot=0x2007495cu;break;
        case 0x00302000u:slot=0x20074960u;break;
        case 0x00302400u:slot=0x20074964u;break;
        default:
            if(audio_log_flags()&2u)
                audio_log_extended(1u,module,source_path,function,0x132u,bad,address,i);
            if((audio_log_flags()&1u)||(audio_log_flags()&4u))
                (void)compressed_log_output(0x04800000u,bad_compact,bad_compact,address,i);
            return 0u;
        }
        uint32_t pointer=(uint32_t)(uintptr_t)image+read32(row);
        W(slot)=pointer;
        write32(row+12u,pointer);
        volatile uint8_t *entry=image_data+i*12u;
        write32(entry,pointer);
        write32(entry+4u,read32(row+4u));
        write32(entry+8u,address);
        if(audio_log_flags()&2u)
            audio_log_extended(4u,module,source_path,function,0x13eu,records_message,0x200036dcu);
        if((audio_log_flags()&1u)||(audio_log_flags()&4u))
            (void)compressed_log_output(0x10400000u,records_compact,records_compact,0x200036dcu);
        if(audio_log_flags()&2u) {
            uint32_t entry_pointer=W(0x200036dcu+i*4u);
            const volatile uint8_t *log_entry=(const volatile uint8_t *)(uintptr_t)entry_pointer;
            uint32_t x=read32(log_entry),y=read32(log_entry+4u),z=read32(log_entry+8u);
            audio_log_extended(4u,module,source_path,function,0x13fu,entry_message,i,x,y,z);
        }
        if((audio_log_flags()&1u)||(audio_log_flags()&4u)) {
            uint32_t entry_pointer=W(0x200036dcu+i*4u);
            const volatile uint8_t *log_entry=(const volatile uint8_t *)(uintptr_t)entry_pointer;
            uint32_t x=read32(log_entry),y=read32(log_entry+4u),z=read32(log_entry+8u);
            (void)compressed_log_output(0x11000000u,entry_compact,entry_compact,i,x,y,z);
        }
    }
    return 1u;
}
