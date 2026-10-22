/* Product GATT services OTA, EUS, ESS, EFS and NUS: attribute-group
 * registration helpers. These follow the Cordio svc_*.c template
 * (SvcXxxAddGroup / SvcXxxCbackRegister) but are first-party services; Cordio
 * has no such files.
 *
 * Native 0x5361bc..0x536233, written from the 2.2.6.10 disassembly:
 *   0x5361bc add OTA  / 0x5361c6 cback OTA   (literal 0x5361d0 -> RAM 0x20003bb8)
 *   0x5361d4 add EUS  / 0x5361de cback EUS   (literal 0x5361e8 -> RAM 0x20003b4c)
 *   0x5361ec add ESS  / 0x5361f6 cback ESS   (literal 0x536200 -> RAM 0x20003b38)
 *   0x536204 add EFS  / 0x53620e cback EFS   (literal 0x536218 -> RAM 0x20003b24)
 *   0x53621c add NUS  / 0x536226 cback NUS   (literal 0x536230 -> RAM 0x20003ba4)
 * Each add is `push {r7,lr}; ldr r0,=group; bl AttsAddGroup (0x5353ae)`;
 * each register stores read/write callbacks at group +0x8/+0xc.
 *
 * The groups are Cordio attsGroup_t records (20 bytes) in initialised .data;
 * they are defined by the storage pass, not here. */
#include <stdint.h>

typedef struct {
    void *pNext;          /* +0x00 */
    const void *pAttr;    /* +0x04 */
    void *readCback;      /* +0x08 */
    void *writeCback;     /* +0x0c */
    uint16_t startHandle; /* +0x10 */
    uint16_t endHandle;   /* +0x12 */
} g2_atts_group_t;
_Static_assert(sizeof(g2_atts_group_t) == 20, "Cordio attsGroup_t is 20 bytes");

extern g2_atts_group_t svc_ota_group_20003bb8; /* RAM 0x20003bb8 */
extern g2_atts_group_t svc_eus_group_20003b4c; /* RAM 0x20003b4c */
extern g2_atts_group_t svc_ess_group_20003b38; /* RAM 0x20003b38 */
extern g2_atts_group_t svc_efs_group_20003b24; /* RAM 0x20003b24 */
extern g2_atts_group_t svc_nus_group_20003ba4; /* RAM 0x20003ba4 */

extern void AttsAddGroup(g2_atts_group_t *group); /* 0x5353ae */

void svc_ota_add_group_5361bc(void);
void svc_ota_cback_register_5361c6(void *read_cback, void *write_cback);
void svc_eus_add_group_5361d4(void);
void svc_eus_cback_register_5361de(void *read_cback, void *write_cback);
void svc_ess_add_group_5361ec(void);
void svc_ess_cback_register_5361f6(void *read_cback, void *write_cback);
void svc_efs_add_group_536204(void);
void svc_efs_cback_register_53620e(void *read_cback, void *write_cback);
void svc_nus_add_group_53621c(void);
void svc_nus_cback_register_536226(void *read_cback, void *write_cback);

/* Stock 0x5361BC */
void svc_ota_add_group_5361bc(void) { AttsAddGroup(&svc_ota_group_20003bb8); }

/* Stock 0x5361C6 */
void svc_ota_cback_register_5361c6(void *read_cback, void *write_cback) {
    svc_ota_group_20003bb8.readCback = read_cback;
    svc_ota_group_20003bb8.writeCback = write_cback;
}

/* Stock 0x5361D4 */
void svc_eus_add_group_5361d4(void) { AttsAddGroup(&svc_eus_group_20003b4c); }

/* Stock 0x5361DE */
void svc_eus_cback_register_5361de(void *read_cback, void *write_cback) {
    svc_eus_group_20003b4c.readCback = read_cback;
    svc_eus_group_20003b4c.writeCback = write_cback;
}

/* Stock 0x5361EC */
void svc_ess_add_group_5361ec(void) { AttsAddGroup(&svc_ess_group_20003b38); }

/* Stock 0x5361F6 */
void svc_ess_cback_register_5361f6(void *read_cback, void *write_cback) {
    svc_ess_group_20003b38.readCback = read_cback;
    svc_ess_group_20003b38.writeCback = write_cback;
}

/* Stock 0x536204 */
void svc_efs_add_group_536204(void) { AttsAddGroup(&svc_efs_group_20003b24); }

/* Stock 0x53620E */
void svc_efs_cback_register_53620e(void *read_cback, void *write_cback) {
    svc_efs_group_20003b24.readCback = read_cback;
    svc_efs_group_20003b24.writeCback = write_cback;
}

/* Stock 0x53621C */
void svc_nus_add_group_53621c(void) { AttsAddGroup(&svc_nus_group_20003ba4); }

/* Stock 0x536226 */
void svc_nus_cback_register_536226(void *read_cback, void *write_cback) {
    svc_nus_group_20003ba4.readCback = read_cback;
    svc_nus_group_20003ba4.writeCback = write_cback;
}
