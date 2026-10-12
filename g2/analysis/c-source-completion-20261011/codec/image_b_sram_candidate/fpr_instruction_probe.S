.text
.global fpr_probe
fpr_probe:
  fsts fr16, (r14, 0)
  fsts fr17, (r14, 4)
  fsts fr18, (r14, 8)
  fsts fr19, (r14, 12)
  fld.s fr16, (r14, 0)
  nir
