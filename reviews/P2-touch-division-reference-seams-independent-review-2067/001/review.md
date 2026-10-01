# Independent review 2067

**Result:** PASS_STATIC_SCOPED.

- Candidate receipt SHA-256 b97ced88db1ed1851218fbc516eddb1a758992a6f84f727b38828272067d97ae; source SHA-256 371d8a61b659a33b4cad4a7d892e144aba8263ae59497b4f658afc5b0c430f87. All declared artifact pins match.
- All candidate pins and source SHA match. Independently swept every halfword offset with Capstone over the authenticated image; the 59 listed branch/call candidates targeting A6C0/A7C0/A7CC/A9A8 match exactly, including addresses, offsets, instruction bytes and targets. The pointer-candidate list is empty as reported.
- The seam listing correctly distinguishes A7BE -> shared zero tail, wrapper entry A7CC, the A7C4 call to A9A8, and a second A99A call from neighboring signed division. It excludes A7D2 and A9AA from those owned spans.

**Limits:** This is a syntactic sweep that can include data or second halfwords; it is not a code-ownership proof or complete indirect-reference denominator. No canonical admission.
