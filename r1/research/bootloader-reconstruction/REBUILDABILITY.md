# Rebuildability and fidelity assessment

## Current status

Five distinct outputs now exist, with deliberately separate fidelity claims.

| Output | Builds | Fidelity |
| --- | --- | --- |
| mechanical Ghidra C corpus | analysis only | complete address-indexed pseudocode for 304 recovered functions; zero decompiler failures |
| [`firmware-project`](firmware-project) | yes, Cortex-M4 ELF/HEX/BIN | complete source-constructed target using a hash-pinned minimal SDK/library closure plus recovered R1 configuration and trust anchor |
| [`functional-model`](functional-model) | yes, host C11 with tests | clean behavioral model of boot selection, settings, signature policy, DATA bounds, postvalidation, ACL, and malformed-input handling |
| [`sdk-overlay`](sdk-overlay) + Nordic SDK 17.1.0 reference | yes, Cortex-M4 | closest on-device source reconstruction; correct layout/public key/configuration family, but not byte-identical |
| [`../r1-firmware-decompilation/rebuild`](../r1-firmware-decompilation/rebuild) | yes, host emitter | exact supplied raw bytes, without pretending the byte arrays are recovered source |

The firmware project is the buildable on-device answer to “functionally equivalent based on
available evidence.” The functional model remains its clean executable specification for
audit-derived behavior. Neither is claimed to be the vendor's original C or expected to reproduce
the original hash.

## Verified claims

| Claim | Status | Evidence |
| --- | --- | --- |
| input bytes preserved and hash-pinned | yes | live dump and generated hash manifests |
| every recovered function has an address/body/name | yes | 304 rows in `functions.csv` and `function-names.csv` |
| every recovered function has C-like output | yes | zero failures in `summary.json` |
| every name records provenance | yes | 304 recovered entries with confidence and evidence; zero synthetic residuals |
| official SDK/library correlation performed | yes | 3,576 BSim rows against a 321-function symbol-bearing ELF |
| clean functional C compiles and passes tests | yes | `functional-model/Makefile` and `tests/test_model.c` |
| Cortex-M reference build demonstrated | yes | official SDK 17.1.0 secure-bootloader target and Arm GCC 9.3.1 |
| complete repository-local target source/dependency closure | yes | 316 hash-pinned upstream files, 74 compiled source objects, 321 flash function addresses |
| deterministic ELF/HEX/BIN rebuild demonstrated | yes | captured and hardened profiles each match across two clean rebuilds and a relocated-tree build |
| original source identifiers recovered universally | no | stripped/optimized images do not encode them uniquely |
| byte-identical source rebuild demonstrated | no | vendor ArmCC version, product sources/configuration, and exact link decisions remain absent |

## Why byte identity remains underdetermined

Native compilation is many-to-one. A stripped executable omits local names, comments, inactive
source, macro expansions, exact types, file boundaries, inline decisions, compiler revision,
optimization choices, and scatter/linker inputs. The live image also contains vendor changes—the
retail 36-page cache delta is one confirmed example—and appears to use ArmCC-specific assembly and
runtime routines while the reproducible reference uses GCC.

The symbol-rich official reference is nevertheless very close: it uses the same `0xf8000`/`0x6000`
flash layout and `0x20005978` RAM origin, and links the same Nordic bootloader, nanopb, fstorage,
atomic FIFO, nrf_crypto, and CC310 families. That makes functional reconstruction and name recovery
well supported without making an impossible source-identity claim.

## Intentional hardening differences

For valid inputs, the functional model follows recovered behavior. For malformed inputs, it repairs
three audit findings instead of reproducing memory-unsafety:

- BLE control-point packets must satisfy operation-specific minimum lengths;
- nanopb varints must terminate within the supplied buffer and 64-bit width; and
- advertising-name length must be at most the 20-byte record capacity.

The model and SDK overlay leave captured `NRF_DFU_DEBUG_VERSION` behavior off by default because
the audit showed that it weakens installed-application CRC validation. The complete firmware
project exposes the captured behavior as its fidelity profile and a separate hardened profile;
both always retain package-signature verification.

## Signing boundary

The public key at `0x000fd868` is non-secret and required by a verifier. A private key is required
only to sign update packages accepted by the installed bootloader. No private key, signing service,
or secure-boot bypass is included.
