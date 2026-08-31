# Security policy

## Supported scope

Security reports are accepted for the current `main` branch, the G2 community
source workflow, and current R1 source. Historical research artifacts and
vendor firmware are retained as evidence but are not maintained upstream
products.

## Private reporting

Use GitHub's private vulnerability-reporting or draft security-advisory feature
for this repository when it is available. If it is unavailable, contact the
repository owner privately through GitHub before sending exploit details. Do
not disclose a vulnerability, credential, signing material, private firmware,
or identifying device data in a public issue.

Include the affected commit, component, impact, minimal reproduction, and any
suggested mitigation. State whether testing used only software fixtures or
involved hardware. Do not perform destructive, remote, or directed hardware
testing without the device owner's authorization and explicit project
coordination.

Maintainers will acknowledge a report when it is received, validate it without
expanding its scope, and coordinate remediation and disclosure with the
reporter. No response-time or bounty commitment is implied.

## Release boundary

The public G2 source archive excludes official firmware, retained vendor bytes,
credentials, and signing keys. A report that such material appears in a public
artifact should be treated as a security and licensing incident and reported
privately immediately.

