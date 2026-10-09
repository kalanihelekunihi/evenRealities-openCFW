# Delay/poll/IRQ flow

```
save_irq():
  saved = PRIMASK; disable_IRQ(); return saved

delay_us(us):
  iterations = VCVT_unsigned_fixed5(float_from_uint(us))
  if MCU_PERFSTATUS == 2:
    iterations = VCVT_unsigned(float(iterations)*250/96)
    overhead =24
  else: overhead =15
  if iterations > overhead:
    spin(iterations-overhead)    // guaranteed positive

spin(count):
  do: count = uint32(count-1)
  while count !=0

wait4(budget,address,mask,expected):
  repeat:
    if (read(address)&mask) == expected: return0
    if old_budget_before_decrement ==0: return4
    budget-- ; delay_us(1)

wait5(...,equal):
  condition = uint8(equal) !=0
  repeat:
    matched = (read(address)&mask) == expected
    if condition ? matched : !matched: return0
    if old_budget_before_decrement ==0: return4
    budget-- ; delay_us(1)
```

Delay source uses explicit namedVFP conversions and multiply/divide to preserveFPSCR/saturation; see timing.c. Register status values,software commands andmeasured readiness are different. The timed status argument specifies an iteration/delay budget; physical elapsed time has not been measured. Large-input tests stop before spin,not after a synthetic return. OriginalITCM spin provenance is separate from the following copy utility.
