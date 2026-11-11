// GATT layout of the stock G2 firmware (2.2.6.10 attsAttr_t table 0x6de974..0x6deb44,
// UUID constants 0x7894a0..0x789580; 2.3.2.14 constants at 0x7e96b8).
const BASE = (suffix: string) => `00002760-08c2-11e1-9073-0e8ac72e${suffix}`;

export const G2Gatt = {
  /** EUS: carries the 0xAA TPL protocol (eusWriteCallback 0x4bdf3c -> TPL_ReceivePacket pipe 0). */
  eus: { service: BASE('5450'), write: BASE('5401'), notify: BASE('5402') },
  /** ESS data service. */
  ess: { service: BASE('6450'), write: BASE('6401'), notify: BASE('6402') },
  /** EFS: file transport (efs_transport_receive). */
  efs: { service: BASE('7450'), write: BASE('7401'), notify: BASE('7402') },
  ota: { service: BASE('1001'), write: BASE('0001'), notify: BASE('0002') },
  /** Nordic UART, production test only. */
  nus: { service: '6e400001-b5a3-f393-e0a9-e50e24dcca9e', write: '6e400002-b5a3-f393-e0a9-e50e24dcca9e', notify: '6e400003-b5a3-f393-e0a9-e50e24dcca9e' },
} as const;

/** Advertised name template "0Even G2_**_#_A" (file offset 0x359a70). */
export const G2_NAME_PREFIX = 'Even G2';
