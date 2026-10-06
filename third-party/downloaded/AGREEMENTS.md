# Agreement and acceptance evidence

**Update 15:26 UTC:** user confirmed the downloaded IAR/EM licenses were already
accepted. The manifest records this once; no repeated question is needed.
Earlier unresolved statements below are superseded by this confirmation.
Entitlement, secure activation and usage restrictions remain separate facts.

No private license key, account, browser history or credential was inspected.
Existing files do not establish whether the responsible licensee accepted
agreements during download. They also do not establish that no agreement applies.
If acceptance is already established for the applicable product/contract, record
that confirmation once; do not require accepting the same agreement again.

## IAR

Exact local agreement from `iar-lmsc-tools_1.14_amd64.deb`:
`third-party/local-vendor/IAR_EndUserLicenseAgreement.pdf`, September 2025,
SHA-256 `8351c09200a37728cc60abc92a052268a6dbef32a2c8ba3a91e00504b89f8a4c`.
It was obtained by data-only `dpkg-deb --fsys-tarfile` plus selective tar output;
no installer scripts or license tools executed. Offline OCR is saved beside it
as `IAR_EndUserLicenseAgreement.ocr.txt`; read the PDF for exact wording because
OCR ordering/spelling can be imperfect.

Official [agreement selector](https://www.iar.com/support/software-license-agreement)
provides distinct [subscription SLA](https://www.iar.com/hubfs/Software%20License%20Agreement%20(SLA)_Subscription%20-%20202503.pdf)
and [perpetual SLA](https://www.iar.com/hubfs/Software%20License%20Agreement%20(SLA)_Perpetual%20-%20202503.pdf).
The actual contract determines which applies. [CXARM download instructions](https://updates.iar.com/?product=CXARM)
require a valid subscription for the Linux compiler; a Windows license key's
existence does not prove that entitlement. [LMSC Tools](https://updates.iar.com/?product=LMSCDAEMON)
publishes the hash that matches the local DEB.

Material terms identified in the local EULA: opening a package, installation or
use binds the user; use requires the organization to hold a valid license or
accepted evaluation. License type follows the contract. Personal-license sharing,
unauthorized redistribution, and compiler executable reverse engineering are
restricted. Included proprietary source is subject to confidentiality and
IAR-only compilation restrictions unless a stated exception applies; do not
import IAR runtime source into the open clang reconstruction on that basis.
Third-party software has supplemental terms. Download automation may not be
made part of CI/CD; this setup does no automatic IAR downloads.

The public subscription SLA also treats covered licensee download/use as an
effective-date trigger. Consequently inspection/extraction is technically distinct
from installation/execution, but **no categorical contractual inspection exemption
was established**. The extraction described above is evidence of what was done,
not a declaration that terms cannot apply. The compiler DEB is still missing,
and its own included agreement has not been inspected.

Decision needed: confirm whether the applicable terms were already accepted,
or accept them now with authority for the organization and applicable entitlement.
Only then run the installation script's `--apply --license-accepted` path after
the completed compiler DEB is checksum-registered. Activation is a separate
secure user handoff; no key goes into files, build layers, arguments or logs.

## EM9305 SDK v4.6

The supplied original is `~/Downloads/T9305_EMB_SDK_installer.sh.zip`. Exact
embedded agreement path is `License/em_sdk_sla.txt` in its Makeself tar payload.
The already inspected local agreement is
`g2/analysis/bootloader-completion-2026-10-06/upstream-worker/downloaded-sdks/em9305-v4.6-docs/em_sdk_sla.txt`.
The SDK documentation links its agreement as `doc/app_notes/EM_SDK_SLA.pdf`
(relative link `../app_notes/EM_SDK_SLA.pdf` from its license page); that PDF
was not separately extracted. No verified public URL for this exact agreement
was established, so use the supplied local agreement rather than guessing one.

Material terms: access/install/copy/use or affirmative acceptance binds the
individual and employer, subject to any pre-existing commercial agreement.
Materials must be obtained directly from EM. Evaluation is one year and for
EM9305-based products; commercial rights depend on production-chip purchases
from EM and are bounded by the shipment-based term. Transfer/sublicensing,
independent use, and reverse engineering of SDK binary/object code are restricted.
Confidentiality applies to materials/documentation. These provisions matter for
library matching and open-source redistribution even if installation is accepted.

SDK docs describe acceptance during installation; they do not prove that this
particular user's download or earlier installation accepted it. The shell installer
has not been executed. No broad SDK source/library extraction or copying was
performed. Static archive listing and selective agreement/docs inspection were
done; the broad access language means those are not categorically exempt either.

A single EM acceptance/previous-acceptance question was pending and is now
resolved by the 15:26 UTC confirmation. Acceptance alone
does not establish that restricted binary reverse engineering or redistribution
is authorized for OpenCFW. Permitted Apollo510 BSD source work continues.
