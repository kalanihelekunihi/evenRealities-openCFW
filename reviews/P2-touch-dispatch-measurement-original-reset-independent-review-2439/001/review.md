# Independent review 2439

**Result:** PASS_SCOPED.

Candidate receipt SHA-256 59cb08f39c0713c67a148f0d60b214923d838b281847956ddb01f37a471ae4ff; source hash 371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87 matches. Eight pinned body ranges (dispatcher, measurement, budget, poll, scaler, start helper, register loader and reset 685C) match receipt hashes; evidence files validate.

Independent isolated replay passes all 64 cases with output hash matching pinned replays.json. Original dispatcher/measurement/budget/poll/scaler/divider/start/loader and reset 685C execute; 6AC0 and 6608 remain controlled.

The reset clears control bit31 and offset128, branches on the freshly read status bit, conditionally writes offset324 and calls controlled 6608(315,0,ctx), then sets bit31, zeros offsets116/296, performs command stores/readbacks, clears cfg byte113, applies FFFCFFFF, and sets control offset8 bit28. Measurement ignores reset return, then performs start/poll/sample cleanup. Exact ordered writes, helper arguments, both reset branches, countdown/status/item effects, and R4-R11/SP pass.

**Limits:** MMIO/status/sample accesses are synthetic; no physical reset, readiness or delay behavior is established. Mode helper and delay helper remain controlled. The tested countdown/readiness patterns are bounded; wider timing behavior is unresolved. Private evidence only; accepted:false. Prior literal/seam ownership limits remain unchanged.
