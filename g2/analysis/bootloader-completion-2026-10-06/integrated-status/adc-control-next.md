# Next ADC control/getter boundary42ec0c

Static original-instruction finding; not implemented by the context8ec1fa candidate. Locked bootloader f89a4c4657537cec6bfc572bdb8318866309b90a5d180c4307680d39824167b5. Body42ec0c..42ed60=340 bytes; stock430000 calls it with request3 and a16-byte array whose last word is sentinelc2f6e979 (-123.456f), corroborated by downloaded Apollo510 ADC request declarations.

Request is truncated to a byte. After context-prefix validation, request0 programs window registers from a struct with first-byte enable and two20-bit bounds; requests1/2/3 are temperature conversion/temperature trims/correction trims. Null output is rejected with6 only for1/2/3; invalid sentinel produces7. A read ofhandle+4 occurs before the NULL guard in the original entry, so a future C implementation must not quietly claim the whole raw-entry pointer behavior is null-safe.

Request2 checks output+12 sentinel, copies three raw temperature-trim words from20026fc0..fc8, then stores measured/default byte20026fcc as a **raw32-bit0/1 word** at output+12. It does not store IEEE float1.0 bits. Preserve actual bytes despite simplified SDK prose calling the argument an array of floats.

Request3 checks output+12 sentinel, copies raw offset20026fe0 tooutput0 and gain20026fe4 tooutput4, then stores literal0 tooutput8 andoutput12. It does **not read correction-valid marker20027199**. Thus the getter itself cannot distinguish a stale/invalid correction pair left by initialization failure. The sampling consumer's validity handling must be traced before treating this pair as an applied correction or adding a second correction in an app. This is a static call/data-flow result, not a demonstrated hardware failure.

Request1 computes a temperature using native single-precision operations and a lazy calibration-derived cache; exact constants, update order, NaN/sentinel behavior and byte-rounding require direct original/source tests in the next implementation batch. Request0 MMIO and unsupported-selector paths can be closed independently within this same340-byte family. No source integration or all-input/hardware claim is made here.
