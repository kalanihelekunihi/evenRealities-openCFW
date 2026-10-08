# Independent review — P2-21387

Status: partial; accepted: false.

Fresh extraction passed for the 100-byte disjoint data range, and regenerated raw bytes match. I checked the reversed four-byte `fni-` and `fni+` strings with NUL/zero padding, the Thumb callback word at 0x484010, and the ten ascending little-endian binary64 power-of-ten entries from 1 through 1,000,000,000. The table pointer literal and consumer references align with the listed use sites in maps 21728, 21730, 21732, and 21734; the callback word is consumed by map 21784.

This confirms bytes and referenced consumer roles, not exclusive ownership of pointer targets or the full surrounding image. Review remains partial/unaccepted.
