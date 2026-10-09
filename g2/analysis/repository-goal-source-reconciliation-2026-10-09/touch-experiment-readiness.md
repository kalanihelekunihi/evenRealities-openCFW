# Touch compiler experiment readiness

The proposed unchanged-source GNU 10.3/11.3/12.2 Configure matrix is useful and
not shown as completed by the inspected Configure receipts. No new compilation
was run in this follow-up.

The existing ReadArray experiment matches all four GNU releases, but that does
not constitute a Configure matrix. Configure's prior 13.3 `-Og/-O1/-O2/-Os`
and loop-option tests are already recorded and must not be repeated without a
new discriminator. Configure remains 424 bytes with a 24-byte difference under
13.3 `-Og`; Capture and ConfigureScan are exact peers.

The checked local availability is bounded:

- `/tmp/opencfw-arm-gnu` contains only the documented 13.3 Darwin-arm64 tree.
- `/Users/kalani/.local/share/opencfw` contains the environment and Python venv,
  with no `toolchains` directory.
- bootstrap's documented `/opt/opencfw-tools` location is absent.
- `build/toolchains.local.json` is absent and `arm-none-eabi-gcc` is not on
  the current PATH.
- inspected matching and Configure receipts do not supply current executable
  paths for 10.3, 11.3 or 12.2.

This does not prove those releases are absent elsewhere. No broad filesystem or
temporary-directory inventory was performed. The denied daemon path was not
accessed. No access denial occurred during these bounded checks.

The audit identifies experiment/source owner
`01a0f4a0-6c2a-70e7-8394-b1e0c936f028`. Parent coordination with that owner and
exact paths to usable authenticated older compiler executables are the next
inputs. If installation is needed, use official release archives with recorded
archive/tool hashes and host architecture, isolated from firmware sources.

Once available, compile unchanged pinned `cy_msclp.c` at the recorded flags
with each compiler into an isolated directory. Preserve dependencies,
preprocessed translation unit, object/assembly, compiler version/hash, section
bytes and relocations. Compare all 424 Configure bytes and the 48-byte Capture
and 160-byte ConfigureScan peers. Require no unhandled relocations. A candidate
matching all three is stronger attribution evidence, not a unique producer or
whole-payload equality receipt.

IAR 10.10.2 support headers and Nema reference headers/archives are present as
documented by the audit. They do not establish matching IAR 9.60.2 runtime
implementation source or Nema implementation source for the linked IAR objects.
