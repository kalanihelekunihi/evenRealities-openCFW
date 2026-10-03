# Independent review 2897

**PASS_SCOPED** — accepted remains false.

Reviewed candidate analysis/apollo-boot-spot-trim-helpers-map-2896/001. Source SHA-256 and all three body hashes match; isolated Capstone decode replay into a fresh destination passed and emitted 89 Thumb instructions spanning 228 bytes. Independently checked all PC-relative literal targets and control flow. ADB8 conditionally ORs bits 15–16 at 400201B0 for nonzero low-byte input, updates 40020088 from profile word104, then computes/stores a bounded delta and updates the low 10 control bits at 40020080 with fresh reads. AE24 performs both profile-derived RMW stores before its input gate; nonzero input subtracts the stored delta from control low10, while zero skips that subtraction; R4 is saved/restored. AE6C skips stores when byte 200271AE is nonzero; otherwise two fresh RAM words feed low-seven-bit RMWs at 40020044 and 4002004C. Literal pools are separately resolved and the three exact body intervals tile [42ADB8,42AE9C). This is static instruction-backed pseudocode, not dynamic validation: volatile changes, aliasing, flags/caller ownership and physical hardware behavior remain unresolved. accepted:false; no canonical admission.

Candidate receipt SHA-256: `822ae938eab71f241a819626b14d44a8e1883c09533c3f33cdf95e10b6b04ff0`.
