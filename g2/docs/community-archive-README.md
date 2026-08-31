# openCFW G2 community source archive

SPDX-License-Identifier: MIT

This is the deterministic, official-payload-free source distribution for the Even
Realities G2 firmware work. It contains openCFW source, reproducible build
recipes, selected software tests, exact dependency licenses, and authenticated
metadata. It contains no complete official package or component and no
unreviewed raw or encoded retained executable-byte transcript. It also excludes
signing keys, private canonical observations, and hardware-validation claims;
exact hashes and reviewed semantic source tables are not payload bodies.

This verified ZIP is the history-free public artifact. Do not substitute a
hosting service's automatic archive of the private development repository: its
existing Git history retains 52 `g2/.tmp-*` paths and descendants totaling
108,601,986 bytes, including official-derived firmware variants. That set
contains the now-deleted exact official-payload copies
`g2/.tmp-pt-working-base.bin` and
`g2/.tmp-pt-working-base-linux.bin` (SHA-256
`36c5b0e499a68ac2493a497bdab9740fd3e7027730c26a9094eca47268a27863`).
Publishing that history requires a separately audited clean-history export or
a separately authorized history rewrite.

The current G2 image is a hybrid compatibility build, not a source-complete
clean-room replacement. Codec, BLE-controller, Touch, case, Apollo bootloader,
and Apollo-main compatibility inputs remain locally supplied boundaries. The
project does not authorize redistribution of a stock-bearing image assembled
from those inputs. See the [licensing boundary](g2/docs/release-licensing-and-redistribution.md)
and [community workflow](g2/docs/community-source-distribution.md).

## Local workflow

Python 3.9+, GNU `make`, and a reviewed Clang profile are required. Run the
software-only dependency preflight from the extracted archive root before
hydrating anything:

```sh
./make.sh g2-community-preflight
```

The preflight resolves the selected compiler, requires its version to match the
recorded `apple-clang` or `linux-clang` profile, checks its builtin-resource
include directory, and reports the exact Python and GNU Make versions. Override
the automatic choice by exporting `OPENCFW_CLANG=/path/to/clang` and
`OPENCFW_TOOLCHAIN_PROFILE=linux-clang` (or `apple-clang`) before both preflight
and build. If GNU Make is installed as `gmake`, export `OPENCFW_MAKE=gmake`
too. Preflight reports but does not persist these environment selections.

Obtain the official `s200_v2.2.6.10` package through a channel available to you; possession
does not grant redistribution rights. Authenticate and hydrate this extracted
tree without network, signing, flashing, or hardware access:

```sh
python3 g2/tools/community_distribution.py prepare-local \
  path/to/s200_v2.2.6.10.evenota g2
```

Then run the exact extracted-tree software gate from the archive root. It uses
the same compiler/profile resolution and any still-exported overrides:

```sh
./make.sh g2-community-local-build
```

Only G2 targets are present in this archive. The minimal root entrypoint exposes
only `help` and `g2-community-local-build`; cross-target, R1,
archive-regeneration, and maintainer-only canonical-publication targets require
the full private checkout.
No command here authorizes signing, flashing, resetting, or exercising hardware.

## What to inspect first

- [Community distribution and hydration guide](g2/docs/community-source-distribution.md)
- [Mixed-license and redistribution inventory](g2/docs/release-licensing-and-redistribution.md)
- [Contributing rules](CONTRIBUTING.md)
- [Security policy](SECURITY.md)
- [Support policy](SUPPORT.md)
- [Project license](LICENSE) and [mixed-license notice](NOTICE)

The archive manifest authenticates every member and records its license basis.
The archive verifier also rejects any dangling local Markdown link, so each
local target named by the included documentation is present in the same archive.
