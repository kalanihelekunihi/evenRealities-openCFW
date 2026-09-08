# DesignWare SPI cleanup candidate

Authenticated spi_master_v3.o exactly matches stock cleanup at0xf6f0 and
IRQ handler at0xf6fc. The following setup routine matches only an instruction
prefix; do not assume the entire upstream object or adjacent layout matches.
SDKspi_flash_register_master prefix was not found in this image; no alternate
implementation absence claim is made.

Cleanup C loads device->master, master->driver_data at24, the private register
pointer at4, then writes zero to controller word2 (+8). Other private fields
remain unknown and are not assigned inferred meanings. Native macOS C
compilation gives12bytes identical to stock, SHA
7106625a18c7c6cd2c6b3da75c7b4641c5283be27d6481ab3601b09a8b399482.
Candidate is unqualified/unregistered; next structural pointer-load/store
proof and valid-pointer/ABI tests. Stock does not check null pointers here.

Structural qualification completed:all six executed instructions required,
three pointer loads followed by one zero store and leaf return. Four tests
pass including wrong private field, destination register and nonzero write
mutations. Valid initialized pointer chains are required; no null checks or
hardware electrical semantics are inferred. Candidate remains unregistered.

Adjacent IRQ handler exact upstream match has conditional absolute reads
at0x38 and0x3c after testing status bits2 and8 from data->word1 base+0x30.
Do not silently convert these to controller-relative offsets. Establish low
address mapping/intended behavior before any upstream bug-fix deviation.
