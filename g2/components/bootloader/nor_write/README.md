# NOR write and sector erase

Readable source candidates for the pinned Apollo bootloader routines at
`0x420B0C` (page program), `0x420A08` (4 KiB sector erase), `0x420984`
(WREN), and `0x4209C4` (WRDI). Source entry names retain the corresponding
stock address in `nor_write.h`.

The code uses the existing `nor_commands` provider `opencfw_provider_42069e`
for individual PIO commands and the `nor_read/runtime_helpers.h` helpers for
setup synchronization, raw delay/wait behavior, restore configuration, and
the end-of-operation unlock. Write-mode selection is provided by the existing
`opencfw_provider_420f10`; `opencfw_bl_nor_read_configure` is the separate
stock restore call at `0x420E8C`.

Build this isolated source candidate with `make -C g2/components/bootloader/nor_write`.
The default Cortex-M4 code-generation profile is a Thumb-2 subset accepted by
the current Unicorn differential runner and remains valid on the target
Cortex-M55. No device or flash operation is performed by the build or fixture.
