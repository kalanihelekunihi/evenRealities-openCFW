# Floating literals, strings and library padding

Partial/unaccepted; 64 exact data bytes in four intervals. Zero halfwords 482AB2..482AB4,482F72..482F74,48334E..483350 follow previously recovered returns. 483612..483614 is zero padding after floating formatter return. 483614 ASCII nan plus NUL;483628 ASCII fni plus NUL, deliberately retain byte order used by reverse-output helper.

Full eight-byte little-endian binary64 literals:483618 FFFFFFFFFFFFEFFF = negative maximum finite;483620 000000000000F07F = positive infinity;48362C 0100000065CDCD41 = next representable value above 1000000000;483634 0000000065CDCDC1 = -1000000000;48363C 0000000000000000 = positive zero;483644 010000000000E03F = next representable value above 0.5. Exact bytes authoritative, including low-order one bits. These resolve full-width VLDR reads previously represented by four-byte reference prefixes in maps21728..21734. Candidate ends before code48364C. No C, freeze, whole coverage or equality claim.
