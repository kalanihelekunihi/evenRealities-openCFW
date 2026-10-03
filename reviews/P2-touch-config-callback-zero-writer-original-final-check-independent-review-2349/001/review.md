# Independent review 2349

**Result:** PASS_SCOPED.

Receipt 96c4d2cd607e51c7800a7c1b4b88ad580930abb5155c73185981cf77fbb71a96 pins the source and body [0x4C7C,0x4DA8), with evidence hashes matching. Independent execution passes all 288 fixtures.

Original 4C7C runs through 6AC0(0,ctx), 4C72 and 4C44 with no function interception. For allowed modes 0/1/2/5/6/7, a nonzero supplied version byte reaches the final helper and actual 4C44 returns 128; unsupported modes 3/255 return 1 and skip 4C72. All test cases observe exactly one zero store to cfg.word20, final zero, parameter flags, helper call sequence, final status, R4-R7 and SP.

The corrected literal is independently confirmed: LDR at 0x4CB6 resolves to 0x4DA8, containing 0x0000028F; that value is stored in cfg.word44. This corrects the preserved 2342 prose error.

**Limits:** Zero-version success path is not covered; only rejection bytes 1, 2 and 255 are tested. This does not prove callback persistence against other callers, intervening writers, changing pointers or aliasing, and does not close dynamic target resolution. Physical behavior and canonical admission are not claimed; accepted:false.
