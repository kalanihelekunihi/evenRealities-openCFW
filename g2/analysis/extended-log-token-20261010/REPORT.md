# Logger config token search

`token.c` source-defines `0x44b63a..0x44b666` for the non-null NUL-terminated domain used by the logger: it returns the first substring occurrence or zero, including the haystack address for an empty needle. Its stock helper `0x481818` is a character finder. This domain is bounded; no initialized config string is asserted.

The fixed main image is official G2 2.2.6.10 OTA stripped 32 bytes, mapped at `0x438000`, SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`. `verify.py` compiles M55 and M4 with warnings as errors and compares original/source Unicorn return and stack behavior across **169** string pairs including empty, overlapping and absent matches. All pass. The 19-unit main source archive includes the source; its build receipt has four unchanged direct FlashDB undefined symbols.

This closes the config-token comparison lower contract. The direct logger `0x43d574..0x43d976` remains 10/11 SMP bodies. Three larger contracts remain before full source comparison: timestamp formatting `0x44b728`, variadic formatting `0x44b76c`/`0x481836`, and shared-buffer/lock output state.
