# Calibration acquisition branch at 7BC0

Extend1503 with a zero state-helper result. Original7BC0 calls6928(scratch,descriptor), then7288(rowIndex,packetIndex,descriptor), then6980(previous R0,descriptor). Controlled returns99 and88 from the first two helpers demonstrate their flow: the first is discarded before7288; the second remains R0 entering6980. Nonzero6980 result leaves retained status0; zero adds errorbit4. The subsequent original hardware-read/output arithmetic and cleanup still execute for both results.

The486 original-instruction fixtures check the exact acquisition call order and arguments, retained status, output word, control-bit clear and restored frame. Helpers6AC0/6928/7288/6980 are controlled; MMIO is synthetic. Scratch/helper effects, record mode123==7 and physical behavior remain unresolved. No canonical admission or C implementation.
