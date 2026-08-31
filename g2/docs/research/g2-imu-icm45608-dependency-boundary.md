# G2 ICM45608 production dependency boundary

Status: the public/canonical profile retains the authenticated stock G2
ICM45608 object byte-for-byte. This preserves the released device behavior
without compiling or redistributing the unsupported InvenSense/EDMP source
closure. Hardware qualification remains blocked by unavailable physical evidence.

## Retained production object

The stock object occupies `[0x004A35B0,0x004A6644)`: 53 linked functions,
11,674 body bytes, and 762 alignment/literal bytes. Its complete 12,436-byte
SHA-256 is
`d4946b892b0fcb6e45a3cb2f4dadd452e737712815577d6780c26ff7e1185e22`.
The canonical overlay has no patch whose interval overlaps this span.

Twenty-nine authenticated relocations from 11 source-owned caller functions
continue to target 20 exact stock entries. Their canonical row SHA-256 is
`e8cad0ba615a9a793e8f31f21c81db34ec749c9682be8d2236940030fbb3f9b0`.
No compatibility shim or behavioral substitute sits between those callers
and the donor implementation.

This is an explicit retained-donor boundary, not a source-ownership claim.
The historical Even Realities source inventory and its license remain
unavailable. Exact functionality is preserved by retaining the authenticated
released bytes, while the surrounding source-owned callers remain auditable.

## Retired research route

The repository retains a research candidate and a TDK InvenSense
`motion.arduino.ICM45608` tag-`1.1.2` snapshot for analysis. They are not
canonical compiler inputs and are not community-bundle inputs.

The snapshot's root license does not govern every file uniformly. Five headers
carry file-level language that prohibits use, reproduction, disclosure, or
distribution without an express license, and ten headers contain dense EDMP
program or RAM images. The previously selected transitive build closure reached
four restricted-notice headers and five dense payload headers. The exact
dispatch, B2S, AID, and MRM sequences do not occur in the official donor image;
only the selected calibration patch occurs there once. Donor extraction
therefore could not reproduce the retired source overlay.

The canonical migration removes:

- eight ICM45608/TDK translation-unit records;
- the InvenSense include route from both compiler profiles;
- 54 clean-room wrapper leaves and 52 redirects;
- 143 primary TDK/port function identities; and
- all five formerly selected EDMP payload sequences from the generated overlay.

The community selector admits none of the five restricted-notice files, ten
dense-payload files, research candidate, or TDK port. It may retain the upstream
license text as notice material; that does not make the snapshot release input.

## Acceptance gates

`tools/analyze_g2_imu_icm45608.py` fails closed unless:

- the donor image and complete stock object match their pinned identities;
- no configured or built patch overlaps the stock interval;
- the 29 external caller relocations retain their exact source/function/offset/
  target topology and every target is a known stock entry;
- the canonical compiler and community-bundle closures contain no restricted,
  dense-payload, candidate, or port implementation file;
- the built component's stock object equals the donor bytes; and
- the generated overlay contains none of the five retired payload sequences.

The analyzer's artifact gate intentionally fails against stale pre-migration
build output. Canonical artifacts must be recorded only after all concurrently
changing source hashes converge. No signing, flashing, device access, or network
operation is part of this audit.

Run the software-only checks with:

```sh
python3 -m unittest -v tests.test_analyze_g2_imu_icm45608
python3 tools/analyze_g2_imu_icm45608.py
```
