# Conditional board audit integration

Independent BOARD-REVIEW.md passes the bounded board packet: 240 bytes of data, target-consumer field offsets, and seven-word by-value I2S interface. Initial mask enables PCM1/LOGFBANK and excludes I2S. KWS DMIC initializer fits; unchanged acquired AIoT initializer differs under the selected layout. Physical IRAM/DRAM visibility, active routing, exact producer and configuration remain unproved. Zero new executable or source-produced bytes are admitted.

The subsequent csky-queue-placement-binding-2026-10-09 result is separate and pending independent review. It constrains SRAM Put / XIP Get against acquired source section contracts; it does not inherit board audit approval. Neither result proves a unique source revision, whole-component completion or live behavior. Existing sealed packets and canonical ledger were not edited.

No additional static inference can establish physical aliasing from these packets. Exact placement attribution needs the producing source/configuration/link manifest; active routing needs the actual enable transition and provider evidence. Discovery owns the separate in-image ARC investigation. Closed mode and application-event bindings were checked and left unchanged rather than repeated.
