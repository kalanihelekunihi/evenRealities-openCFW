# Logger module policy rows

`module_policy.c` source-defines the non-null branch of `0x43d4b0..0x43d574`: default level five when policy is disabled or no row matches; otherwise it scans five RAM rows of stride 33, checks active byte `+81`, compares 30 name bytes at `+50`, and returns level byte `+49` for the first match. Guard enter/exit remain explicit callbacks; bounded compare uses the separately validated `g2_smp_candidate_compare` source. Null module enters the stock fatal callback/recursion path and is outside this API.

The fixed main image is official G2 2.2.6.10 OTA stripped 32 bytes at base `0x438000`, SHA-256 `19044a72bdfeb04c6b1b104d87da7b98e13cc18928528d84d999b6bcc0ba9701`. `verify.py` compiles M55/M4 and runs **360** original/source Unicorn comparisons across disabled/enabled policy, each active and matching row, mismatches, absent rows and five policy levels. Return and ordered guard calls match. Production row initialization is not established.
