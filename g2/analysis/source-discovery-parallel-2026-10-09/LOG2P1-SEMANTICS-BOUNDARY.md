# log2p1 semantics boundary — 2026-10-09

Static local SDK/source and bounded public official-source search only. No simulator, compiler, instruction execution or new downloads.

Available v4.6 arc.tcf identifies **LOG2_Extension.1_0** at939–961 and lists **UniPHY_ARC_ExtensionLibrary v1.0.0** at47. It enables log2_extension and declares the same7/0 log2p1 and7/1 log2p0 opcode bindings at1970+ and2142+. This supplies a concrete versioned hardware-extension component/library request for vendor follow-up, beyond a bare intrinsic name. Both user-extension and translated-Verilog nSIM model compilation switches are false at303–307; no matching C/RTL operation model or result truth table was found among the available SDK files. Configuration naming is not operation semantics or simulator implementation availability.

`apexextensions.s` FLAGS_NONE and stockF=0 support a no-flag-suffix encoding declaration. They do not independently specify architectural hidden effects or hardware condition-code behavior. Zero-input, negative/sign-bit input, exceptions and exact result arithmetic remain **unresolved** for the hardware operation.

Official pinned QPC qf_act.c:154–188 supplies an explicit **software fallback**, selected when QF_LOG2 is not overridden. Its lookup result forzero is0 and forpositive configured-width ready bits is floor(log2(x))+1. Vendor qf_port.h disables the intrinsic override when USE_SW_LOG2P1 is defined. These facts establish software comparator behavior and selection mechanism, not equality of the EM hardware intrinsic. No equivalence was inferred from the QPC expectation, macro name or scheduler downstream conditions.

Searches for log2p1 ARC/EM9305, exact LOG2_Extension and UniPHY_ARC_ExtensionLibrary names, and official emdeveloper mentions returned no applicable public operation specification or implementation. Unrelated C23 floating-point log2p1 results were excluded. Public product/guest portal boundary remains documented in EM9305-OFFICIAL-VERSION-BOUNDARY.md; no vendor-specific specification was obtained through it.

Concrete missing input: vendor **LOG2_Extension.1_0 / UniPHY_ARC_ExtensionLibrary1.0.0** operation specification, C nSIM model or RTL, with explicit zero/sign/flags truth table, plus original stock4.2 design/TCF or release evidence authenticating the same component and mapping. A v4.6 TCF alone cannot prove4.2 compatibility, even though the stock encoding fits the v4.6 declaration. No currently available official source closes this arithmetic-semantic gap. Keep the exact0x31163E word/name/operand binding and downstream scheduler guards while preserving this stop boundary.

Input SHA-256 receipts are saved in log2p1-semantics-search.json. Canonical artifacts and failed receipts remain untouched.
