# Recovered SYSPLL call flow and interface

```
clock_config(SYSPLL, requested_hz, explicit_config=NULL)
  -> SYSPLL configuration (0x4C3B44)
     -> postdiv(config, reference_hz, requested_hz) [0x539794]
        low = min_vco(..., 60 MHz)   [0x539674]
        high = min_vco(..., 240 MHz)
        choose valid minimum uint32 weighted score; equal chooses high
        preserve config.reference; copy remaining fields on success

min_vco(config, reference_hz, output_hz, minimum_hz):
  if gcd(float(output)/1e6, float(reference)/1e6) < 1:
    minimum = max(minimum, (reference/(reference/10e6))*10)
  post = (1,1) when output >= minimum
       = packed_table[ceil(minimum/output)] otherwise
  reject required table index >= 50
  vco = uint32(output * post.first * post.second)
  status = generate(config, float(reference)/1e6, float(vco)/1e6)
  if status != 0: return status
  if ceil(reference/config.refdiv) < (fractional ? 10e6 : 1e6):
    return 5                    // base fields already changed
  store postdiv1/2; return 0

generate(config, ref_mhz, vco_mhz) [0x5395A0]:
  NULL -> 6; finite vco outside [60,960] -> 5
  integer(ref,vco,&refdiv,&feedback) [0x5393E8]
  if not integer: fraction(ref,vco,...) [0x5394E0]
  if neither feasible: return 1
  write vco selector, mode, refdiv, feedback, fraction; return 0

gcd(a,b) [0x53937C]:
  swap when original quiet compare reports negative
  repeat up to 16:
    if b < 2^-23: return a
    next = VMLS(a, original_floor(a/b), b)
    a = b; b = next
  return -1
```

The human-readable ordered pseudocode above describes finite normal inputs. Exact quiet/unordered predicates and float exception/saturation behavior are implemented explicitly in`generator.c`; do not replace them with host double math. Source float predicates preserve originalN/V flags, including malformedNaN behavior.

Config layout is12 bytes:reference0,vco1,mode2,refdiv3,post1/2 at4/5,u16feedback6,u32fraction8. Base writes1/2/3/6..11 only; min adds4/5 only after PFD acceptance; top copies1..11 only after selecting a valid local candidate. Success means parameter generation, not PLL lock or measured output. Scalar table/weight/literal provenance is in function-bindings.
