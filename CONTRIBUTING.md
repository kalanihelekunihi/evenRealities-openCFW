# Contributing to openCFW

Thanks for helping keep supported hardware useful. Contributions are welcome
when their origin, license, and verification boundary can be reviewed by the
community.

## Evidence and licensing rules

- Do not submit leaked or confidential source, signing keys, credentials,
  official firmware payloads, extracted vendor bytes, or material you are not
  permitted to share.
- Describe the public documentation, observable behavior, independently
  collected evidence, or licensed upstream source used for a change. Preserve
  exact upstream version, commit, license, and provenance records.
- New openCFW-authored code and documentation must be offered under the root
  MIT License. Adapted or vendored code keeps its upstream license and must
  include the applicable notice and license text.
- Consume upstream code from its pinned submodule under `third-party/`; do
  not re-implement or copy an upstream library. Record a new upstream as a
  submodule at the exact commit the firmware used, with the evidence.
- Never label a retained or inferred region as source-owned without evidence.
  Unknown boundaries must remain explicit and fail closed. Only source that
  compiles to identical bytes counts toward reconstruction.

By submitting an original contribution, you agree that it may be distributed
under the repository's MIT License. This does not relicense third-party work.

## Preparing a change

1. Keep the change scoped to one reviewable behavior, dependency, or evidence
   boundary.
2. Update the relevant manifest, provenance, notice, and documentation records.
3. Add positive, mutation, and failure-path tests where the change affects a
   build or release claim.
4. Run the narrow target first, then `./make.sh test` and the relevant gate in
   [g2/workflow/PROCEDURE.md](g2/workflow/PROCEDURE.md) or
   [docs/roadmap.md](docs/roadmap.md).
5. Explain any test that could not be run and why.

G2 software work must not require flashing or directed hardware testing during
the present software-development phase. Hardware experiments require explicit
coordination, a written safety procedure, and separate result reporting.

## Reporting problems

Use a GitHub issue for reproducible build, documentation, or behavior defects.
Do not attach proprietary firmware or secrets. Security-sensitive reports must
follow [SECURITY.md](SECURITY.md).
