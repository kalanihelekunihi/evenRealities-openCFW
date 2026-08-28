# Apollo opacity wave 6 admission record

This research-only record closes the complete actionable call graph rooted at
`0x0051C5EC`. Seven SHA-pinned positive-byte rows total 4,386 bytes. Seven
terminal targets were already typed in waves 1–3 and contribute no new wave-6
bytes.

The closure includes an authenticated non-call continuation: the six-byte
Thumb guard at `0x00523A34` transfers into the separately counted body at
`0x00523A3A`. The analyzer pins the guard bytes and follows that edge rather
than trusting the incomplete static-callee list.

The bodies remain `typed-external-provider-unavailable`. Checked-in evidence
supports vector-path family context but not an exact maintained implementation,
provider, or license. Nothing is routed into production or hardware tooling.
