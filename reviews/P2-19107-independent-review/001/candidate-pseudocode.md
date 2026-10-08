# Embedded strings

0x469576..0x469578 is two zero alignment bytes; 0x469578..0x46957C is ON NUL plus a zero pad byte; 0x46957C..0x469580 is OFF NUL. ADR consumers in map19496 select addresses 0x469578 and 0x46957C. These ten bytes are data, preceding next PUSH at 0x469580. Partial/unaccepted; preserve exact bytes.
