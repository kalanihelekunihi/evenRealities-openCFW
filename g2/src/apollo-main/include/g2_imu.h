/* G2 IMU driver API (stock D:\01_workspace\s200_ap510b_iar_git\driver\sensor\imu\imu_icm45608.c,
 * native 0x4a35b0..0x4a656e; log tag "sensor_imu").
 *
 * TDK InvenSense ICM-45608 on product I2C bus 4, 7-bit address 0x69
 * (WHO_AM_I 0x81), with a TDK ICT1531x magnetometer behind the IMU's I2C
 * master (aux address 0x1E, WHO_AM_I 0x45). The glue drives the vendored TDK
 * driver (inv_imu_*, edmp, invn_mag) and keeps a 20-entry sample ring.
 *
 * Names prefixed semantic_ are inventory anchors, not stock symbols. Functions
 * taking or returning float use the stock hard-float convention (aapcs-vfp). */
#ifndef G2_IMU_H
#define G2_IMU_H

#include <stdint.h>

#define G2_IMU_VFP __attribute__((pcs("aapcs-vfp")))

/* Work modes (semantic_imu_init argument, row of the mode table at RAM
 * 0x20000db0). The sensor hub uses 0 head-up/type 5, 1 display, 2 compass. */
#define G2_IMU_MODE_COUNT 5u

/* Events sent through semantic_emit_imu_event -> master input event. */
enum {
    G2_IMU_EVENT_HEAD_UP = 6u,
    G2_IMU_EVENT_HEAD_DOWN = 7u,
    G2_IMU_EVENT_COMPASS_ANGLE = 9u,   /* value = heading in degrees */
    G2_IMU_EVENT_COMPASS_CAL = 0x10u,  /* value = 1, calibration reached */
};

/* Bring-up and configuration. */
int32_t semantic_imu_init(uint8_t mode);
void semantic_sensor_power_cycle(void);
void semantic_sensor_reset_line(void); /* IMU power rail off */
int32_t semantic_set_orientation_matrix(const float accel[3], const float gyro[3],
                                        const float matrix[9]);

/* Sensor hub tick: interrupt status, FIFO drain and EDMP events. */
uint32_t DRV_IMUReadData(uint32_t tick);
uint32_t DRV_IMUCheckHeadUpEvent(void);
void DRV_IMUCheckCompassEvent(void);

/* Latest orientation results. */
G2_IMU_VFP float semantic_get_heading_float(void);  /* pitch, degrees */
int32_t semantic_get_heading_degrees(void);
const float *semantic_get_magnetic_vector(void);    /* {roll, pitch, yaw} degrees */
const float *semantic_get_orientation_vector(void); /* {0, pitch, roll} from accel */
const uint8_t *semantic_get_latest_complete_sample(void); /* gyro, accel, mag floats */
uint32_t semantic_get_flag_20074fdc(void);           /* compass calibrated */

/* IMU users opened by the sensor hub (1 = open). */
uint32_t semantic_get_state_20074674(void); /* head-up */
uint32_t semantic_get_state_20074678(void); /* compass */
uint32_t semantic_get_state_2007467c(void); /* display */
uint32_t semantic_get_state_20074680(void); /* fifth user, periodic accel report */
void semantic_set_state_20074674(uint32_t open);
void semantic_set_state_20074678(uint32_t open);
void semantic_set_state_2007467c(uint32_t open);
void semantic_set_state_20074680(uint32_t open);

/* Raw-data capture to /log/imu_rawdata_HHMMSS.csv (2 minute limit). */
void DRV_IMUStartRawDataCollection(void);
void DRV_IMUStopRawDataCollection(void);

/* Chip identification: 0 ok and *id written, -1 for NULL, else driver error. */
int32_t DRV_IMUReadWhoAmI(uint32_t *id);
int32_t DRV_MAGReadWhoAmI(uint32_t *id);

#endif
