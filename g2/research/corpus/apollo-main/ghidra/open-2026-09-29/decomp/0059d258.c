
ulonglong _internal_frexpf_bits(uint param_1)

{
  uint uVar1;
  int iVar2;
  
  uVar1 = (param_1 & 0x7fffffff) >> 0x17;
  if (uVar1 == 0) {
    if ((param_1 & 0x7fffffff) != 0) {
      iVar2 = LZCOUNT(param_1 << 9);
      return CONCAT44(-(iVar2 + 0x7e),
                      (param_1 & 0x80000000 | ((param_1 << 9) << iVar2) >> 8) + 0x3e800000);
    }
  }
  else if (uVar1 != 0xff) {
    return CONCAT44(uVar1 - 0x7e,param_1 + (uVar1 - 0x7e) * -0x800000);
  }
  return (ulonglong)param_1;
}

