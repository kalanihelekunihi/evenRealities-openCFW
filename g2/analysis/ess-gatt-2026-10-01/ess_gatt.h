#ifndef G2_ESS_GATT_H
#define G2_ESS_GATT_H
/* Recovered stock 2.2.6.10 identifiers; app discovery constants, not firmware. */
#define G2_ESS_SERVICE_UUID "00002760-08c2-11e1-9073-0e8ac72e6450"
#define G2_ESS_WRITE_UUID   "00002760-08c2-11e1-9073-0e8ac72e6401"
#define G2_ESS_NOTIFY_UUID  "00002760-08c2-11e1-9073-0e8ac72e6402"
/* Handles are image-specific. Discover UUIDs in applications. */
enum { G2_ESS_SERVICE_HANDLE=0x860, G2_ESS_WRITE_HANDLE=0x862,
       G2_ESS_NOTIFY_HANDLE=0x864, G2_ESS_CCC_HANDLE=0x865,
       G2_ESS_AUDIO_VALUE_BYTES=205, G2_ESS_AUDIO_ATT_BYTES=208 };
#endif
