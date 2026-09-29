
/* WARNING: Removing unreachable block (ram,0x004d428c) */
/* WARNING: Removing unreachable block (ram,0x004d4290) */
/* WARNING: Removing unreachable block (ram,0x004d429e) */
/* WARNING: Removing unreachable block (ram,0x004d4294) */
/* WARNING: Removing unreachable block (ram,0x004d421a) */

undefined4 FUN_004d4208(uint param_1)

{
  double dVar1;
  uint uVar2;
  undefined4 uVar3;
  double dVar4;
  undefined1 in_q0 [16];
  
  dVar4 = in_q0._0_8_;
  uVar2 = in_q0._4_4_ & 0xffff;
  if ((int)param_1 < 0) {
    if ((in_q0._0_4_ & 0xffff) != 0 || uVar2 != 0) {
      if (0x36 < -param_1) goto LAB_004d423c;
      dVar1 = (double)((ulonglong)((param_1 + 0x3ff) * 0x100000) << 0x20);
      in_q0._0_8_ = dVar4 * dVar1;
      in_q0._8_8_ = dVar1;
    }
  }
  else if ((in_q0._0_4_ & 0xffff) != 0 || uVar2 != 0) {
    if (param_1 < 0x3fc) {
      return SUB84(dVar4 * (double)((ulonglong)((param_1 + 0x3ff) * 0x100000) << 0x20),0);
    }
    if ((param_1 - 0x3f8) + (uint)(0x3f7 < param_1) < 0x7ff) {
      return SUB84(dVar4 * 5.486124068793689e+303,0);
    }
LAB_004d423c:
    uVar3 = FUN_00439cb2();
    return uVar3;
  }
  return in_q0._0_4_;
}

