# SPI device-list initialization

Recovered package0xf674/runtime0x102060e8 initializes two empty circular lists:
SPI head at0x20027ad0 and SPI-flash head at0x20027ad8. The authenticated
SDK device.o provides the function and list identities; device.h declares
its void API. Local C defines the two-pointer layout and uses four explicit
volatile stores. No upstream object bytes are linked.

Native macOS compilation produces20 bytes identical to stock, SHA
4e7e5e95824bfc057f5be66b2f41e88cbc8c32e5d74c12e7d8ec2d03816b791b.
Structural proof checks all seven executed instructions, four ordered stores
and leaf ABI. Three tests pass, including wrong second-head address and
crosslinked-list mutations. Registry insertion/traversal and concurrent use
remain separate. Candidate is qualified but not registered.

Integrated with the GPIO initializer:637 tests pass and full macOS package
rebuild/verify succeeds. The combined44 C bytes are stock-identical, so the
codec and package payload hashes remain unchanged.
