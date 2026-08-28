# G2 hardware-validation policy

Hardware testing is deliberately deferred during the current firmware-development
phase. No build, analyzer, test, or source-admission result in this repository
authorizes signing, flashing, resetting, erasing, or exercising a G2 device.

Earlier recovery notes sometimes described the authorized right temple as
"nonresponsive" or unavailable. That premise is superseded. The observed
disconnect came from the charging case being bumped during an unattended test,
which interrupted the connection; it is not evidence of a temple fault, a failed
flash, or unusable hardware.

Accordingly:

- current software reports must describe live qualification as **deferred by project direction**,
  not as blocked by a presumed device failure;
- offline source, ABI, provenance, build, and host/target-compile evidence may
  continue, but it must not be presented as physical validation;
- hardware acceptance requirements remain useful future gates, but they are not
  to be executed until the project owner explicitly starts the qualification
  phase; and
- historical per-closure audit records are retained as an evidence chronology.
  Any hardware-availability statement in those records is superseded by this
  policy and must not be treated as current device status.

This policy does not weaken fail-closed release, licensing, or compatibility
gates. It only corrects the reason physical evidence is absent and prevents an
accidental case disconnect from being propagated as a firmware diagnosis.
