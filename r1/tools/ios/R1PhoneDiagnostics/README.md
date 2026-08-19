# R1 iPhone diagnostics

This source-only iOS application performs the same bounded, non-mutating BLE
campaign as the macOS probe on an owner-authorized R1 whose advertised name
contains `B56EE2`. It discovers the exact four-lane BAE8 service, subscribes to
both notification lanes, selects the ephemeral phone role, reads device
identity, and interleaves twenty status requests with twenty channel-1 opcode
`0x89` frames whose command-valid byte is zero.

The application has no DFU, ACE, generic GATT write, flash, storage, factory,
sensor-control, advertising-control, NFC, or power-control path. Its four
outbound frame vectors are checked at startup against the C-generated reference
bytes before Bluetooth scanning begins.

Generate the Xcode project with XcodeGen when `project.yml` changes:

```sh
xcodegen generate --spec r1/tools/ios/R1PhoneDiagnostics/project.yml
```

Compile without requiring an Apple signing identity:

```sh
xcodebuild \
  -project r1/tools/ios/R1PhoneDiagnostics/R1PhoneDiagnostics.xcodeproj \
  -scheme R1PhoneDiagnostics \
  -configuration Debug \
  -destination 'generic/platform=iOS' \
  CODE_SIGNING_ALLOWED=NO build
```

Installing on a physical iPhone additionally requires a locally configured
Apple development team and provisioning profile for
`org.openr1.phone-diagnostics`. The project does not contain credentials or a
provisioning profile.

