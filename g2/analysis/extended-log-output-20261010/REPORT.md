# Logger output wrapper

`output.c` owns the complete local wrapper `0x44aa80..0x44aa98`. It truncates the level to eight bits, calls the lower transport submitter as `(buffer, length, 0, level)`, then reads the handle cell at `0x20074570` and calls the lower signal provider as `(handle, 1)`. The fixed OTA literal at `0x44ab04` confirms the handle cell. It does not claim transport delivery.

`verify.py` compiles Cortex-M55 and M4 with warnings as errors. **126 original/source Unicorn comparisons pass** across zero/nonzero buffer, three lengths, seven levels including 256 and `UINT32_MAX`, and three handle values. Ordered lower call arguments and stack restoration agree. Stock image SHA-256 is `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`; base is `0x438000`. This wrapper is a lower call of the still-open extended logger.
