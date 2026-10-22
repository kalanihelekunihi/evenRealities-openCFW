/* Health data manager API (stock app\gui\health\health_data_manager.c, native
 * 0x5597f0..0x55a2af) and the decoded pb_service_health message layouts it
 * consumes. Implemented in ui/a-55-health-data-manager; called by
 * app/a-55-pb-health. */
#ifndef G2_HEALTH_DATA_MANAGER_H
#define G2_HEALTH_DATA_MANAGER_H

#include <stdint.h>
#include <stddef.h>

#define HEALTH_TYPE_UNKNOWN       0u
#define HEALTH_TYPE_ALL           1u
#define HEALTH_TYPE_STEPS         2u
#define HEALTH_TYPE_CALORIES      3u
#define HEALTH_TYPE_SLEEP         4u
#define HEALTH_TYPE_HEART_RATE    5u
#define HEALTH_TYPE_BLOOD_OXYGEN  6u
#define HEALTH_TYPE_TEMPERATURE   7u
#define HEALTH_TYPE_HRV           8u
#define HEALTH_TYPE_PRODUCTIVITY  9u

/* Decoded pb single data sample (0x18 bytes; mult data entries use the same layout). */
typedef struct {
    uint8_t type;       /* +0x00 */
    uint8_t pad1[3];
    uint32_t goal;      /* +0x04 */
    float value;        /* +0x08 */
    float avg_value;    /* +0x0c */
    uint32_t duration;  /* +0x10 */
    uint8_t flag14;     /* +0x14 not copied */
    uint8_t trend;      /* +0x15 */
    uint8_t pad16[2];
} g2_health_pb_data_t;
_Static_assert(sizeof(g2_health_pb_data_t) == 0x18u, "pb health data");

/* Decoded pb mult data. */
typedef struct {
    uint8_t type;                    /* +0x00 */
    uint8_t pad1;
    uint16_t count;                  /* +0x02 */
    g2_health_pb_data_t data[8];     /* +0x04 */
} g2_health_pb_mult_data_t;

/* Decoded pb highlight (0x106 bytes; mult highlight entries use the same layout). */
typedef struct {
    uint8_t type;         /* +0x000 */
    uint8_t pad1;
    uint16_t text_size;   /* +0x002 */
    uint8_t text[0x100];  /* +0x004 */
    uint8_t flag104;      /* +0x104 */
    uint8_t pad105;
} g2_health_pb_highlight_t;
_Static_assert(sizeof(g2_health_pb_highlight_t) == 0x106u, "pb health highlight");

/* Decoded pb mult highlight. */
typedef struct {
    uint16_t count;                       /* +0x000 */
    g2_health_pb_highlight_t item[3];     /* +0x002 */
} g2_health_pb_mult_highlight_t;
_Static_assert(offsetof(g2_health_pb_mult_highlight_t, item) == 2u, "mult highlight items");

uint8_t health_data_save_single_5598cc(const g2_health_pb_data_t *pb);                 /* 0x5598cc */
uint8_t health_data_save_mult_559ad2(const g2_health_pb_mult_data_t *pb);               /* 0x559ad2 */
uint8_t health_data_save_single_highlight_559dfc(const g2_health_pb_highlight_t *pb);   /* 0x559dfc */
uint8_t health_data_save_mult_highlight_559fb8(const g2_health_pb_mult_highlight_t *pb); /* 0x559fb8 */
int32_t health_data_reset_5598ae(void);                                                  /* 0x5598ae */

#endif /* G2_HEALTH_DATA_MANAGER_H */
