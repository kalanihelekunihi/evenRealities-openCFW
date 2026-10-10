# User-downloaded AmbiqSuite5.2 IAR Nema acquisition

Authenticated completed package `/Users/kalani/Downloads/AmbiqSuite_5.2.0.zip`,907382158bytes, SHA256d9751350ef593b306838792a64a5620e4912c84ddf32dc9ff6aacd5cca049cad matches emulator inventory. Full ZIP testzip CRC verification passes all30485members. A second same-size filename `(1).zip` exists but was not used/copied; the verified original-name archive is the selected input. Release notes identify July24,2026 release_sdk5p2p0_66487dd10, base edition without CEVA. Neither ZIP nor SDK executable was run.

Only licenses/release notes and selected IAR Nema archive were safely extracted into this new isolated analysis directory. ZIP names were checked for absolute/traversal paths; originals remain untouched. EXTRACTON metadata is in EXTRACTION.json, package identity in package-hash.json.

Verified comparator path:
`/Users/kalani/Repo/evenRealities-openCFW/g2/analysis/ambiq-520-iar-nema-acquisition-2026-10-09-source-track/extracted/third_party/ThinkSi/config/apollo510_nemagfx/iar/bin/lib_nema_apollo510_nemagfx.a`

SHA2568c6204496ab53860241db9236487a0eb93badf9627be4eea55249847813827e7 exactly matches emulator inventory. Static ar-member parsing finds ELF members including nema_blender.o and nema_cmdlist.o with .iar.rtmodel/.iar.stackusage/.iar.debug_* metadata. Embedded producer strings identify **IAR ANSI C/C++ Compiler V9.70.1.475/W64 for ARM** (COMPILER-STRINGS.txt). Compiler-family/version candidate is therefore established from archive content, not inferred solely from its iar directory. No stock byte equality/ABI compatibility follows; owner can perform the finite member comparison previously proposed.

License inspection: top-level AM-BSD-EULA.txt grants BSD3-style source/binary redistribution subject to notices and directs third-party licensing to docs/licenses. ThinkSi-license.txt specifically grants rights for headers/associated documentation, not a blanket proprietary implementation/binary grant. Both PDF license files and the RTF alternative are retained with hashes. Automated PDF text extraction stopped because this parser lacks the AES cryptography backend; this is a local extraction dependency, not a request for a password or permission to bypass document protections. Full PDF-specific component terms have not been certified by this source track. No new agreement was accepted; no binary redistribution, execution or public submodule registration occurred. Source availability and permitted binary-comparator use remain distinct.

No registered pin, root index, production source, seal or firmware/device state was changed. User download was not repeated.
