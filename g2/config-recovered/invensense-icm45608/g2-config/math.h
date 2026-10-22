/* openCFW compatibility header for the TDK ICM-45608 driver 1.1.2 (b79ae575).
 *
 * src/imu/sif_classifier_ir.h includes <math.h>, which the freestanding
 * arm-none-eabi clang build does not provide. Nothing in the driver files the
 * G2 image links (inv_imu_driver*.c, inv_imu_edmp*.c, inv_imu_transport.c,
 * inv_imu_i2cm.c, Ict1531x.c, invn_mag.c) uses a math.h declaration, so this
 * header is intentionally empty. Confidence: Compat (no code effect). */
#ifndef G2_INVENSENSE_MATH_H
#define G2_INVENSENSE_MATH_H
#endif
