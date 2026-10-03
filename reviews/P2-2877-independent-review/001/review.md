# Independent review 2877

Status: **PASS_SCOPED** (`accepted: false`).

The bootloader source and decoded ITCM hashes match inventory. The initializer body `[0x42AC54, 0x42ACA4)` matches the receipt digest, as do the candidate's listed artifacts. The isolated replay passed all 48 fixtures.

The fixture matrix crosses the three gate states, two controlled power-helper returns, two controlled slot-callback returns, two poll values, and both PRIMASK states. The initializer, output wrapper, callback dispatcher, polling helper, delay helper, and ITCM delay loop execute their original instructions; only the power helper and installed callback are controlled. The call order and arguments, `-40.0f` input, poll arguments `(2500, 0x400083E0, 1, 0)`, mapped statuses, and timeout delay/ITCM iteration counts agree with the decoded flow. The output callback writes into the initializer's stack-passed output area, so the epilogue returns the resulting bound words in R1/R2 while R3 receives the saved incoming R7 value; the assertions also check the other preserved registers, SP, and PRIMASK.

This evidence uses modeled status memory and controlled callees. It does not establish power-helper or installed-callback behavior, changing poll status, or physical hardware behavior. No canonical admission is claimed.
