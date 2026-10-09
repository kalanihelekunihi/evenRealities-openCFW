# Low-speed/public ownership flow

```
LFRC_request(user):
  if clock0.user_bit(user): return0
  saved = IRQ_mask()
  discard clock0.set(user,true) status
  restore(saved); return0

XTAL_LS_request(user):
  if board.ls_hz == 0: return7   // even when already owned
  if clock1.user_bit(user): return0
  saved = IRQ_mask()
  discard clock1.set(user,true) status
  restore(saved); return0

LFRC/XTAL_LS_release(user):
  if corresponding user bit is absent: return0
  saved = IRQ_mask()
  discard corresponding clock.set(user,false) status
  restore(saved); return0

public request/release(clock,user):
  clock = uint8(clock); user = uint8(user)
  if user >=57: return6
  switch clock:
    0 LFRC; 1 XTAL_LS; 2 XTAL_HS; 3 external
    4 HFRC; 5 HFRC2; 6 SYSPLL
    otherwise return6
  return corresponding child(user)
```

Seven two-word rows start0x20073324; each user0..56 is an ownership bit. No optional SDK XTAL-LS hardware control occurs in these stock handlers. Public guard is required because query helpers and children lack equivalent bounds checks. `dispatch.h` supplies typed offline interfaces; scheduler/IRQ interleaving and hardware readiness remain outside this profile.
