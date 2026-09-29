
uint FUN_0043c260(void)

{
  uint uVar1;
  uint uVar2;
  uint uVar3;
  bool bVar4;
  double dVar5;
  undefined1 in_q0 [16];
  double dVar6;
  
  uVar2 = in_q0._4_4_;
  dVar5 = ABS(in_q0._0_8_);
  uVar1 = uVar2 >> 0x1f;
  uVar3 = uVar2 & 0x7fffffff;
  if ((uVar3 == 0) && (in_q0._0_4_ == 0)) {
    return uVar1 << 0x1f;
  }
  bVar4 = uVar3 == 0x3fc00000;
  if (0x3fbfffff < uVar3) {
    bVar4 = uVar3 + 0xc0400000 == 0x300000;
  }
  if ((0x3fbfffff < uVar3 && 0x2fffff < uVar3 + 0xc0400000) && (!bVar4 || in_q0._0_4_ != 0)) {
    if (0xffe00000 < uVar2 * 2) {
      return uVar1;
    }
    *DAT_00439cd4 = 0x21;
    return uVar1;
  }
  dVar6 = SQRT((DAT_0043c2e0 + dVar5) * (DAT_0043c2e0 - dVar5));
  if ((int)((uint)(DAT_0043c2d8 < dVar5) << 0x1f) < 0) {
    uVar1 = 4;
    dVar6 = dVar6 / dVar5;
  }
  else {
    dVar6 = dVar5 / dVar6;
  }
  if (DAT_0043c370 <= dVar6) {
    uVar1 = uVar1 | 2;
  }
  return uVar1 >> 1;
}

