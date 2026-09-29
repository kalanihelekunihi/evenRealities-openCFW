
undefined4 FUN_004816c6(uint param_1,uint param_2)

{
  uint uVar1;
  code *pcVar2;
  int iVar3;
  undefined4 uVar4;
  
  uVar4 = 0;
  if ((param_1 - 0x7d < 7) || (param_1 - 0x38 < 7)) {
    if (param_1 < 0x3f) {
      if (param_1 < 0x7d) {
        iVar3 = param_1 - 0x38;
      }
      else {
        iVar3 = param_1 - 0x7d;
      }
    }
    else {
      if (param_1 < 0x7d) {
        iVar3 = -0x38;
      }
      else {
        iVar3 = -0x7d;
      }
      iVar3 = param_1 + iVar3 + 7;
    }
    while (param_2 != 0) {
      uVar1 = 0x1f - LZCOUNT(-param_2 & param_2);
      param_2 = param_2 & ~(1 << (uVar1 & 0xff));
      pcVar2 = *(code **)(DAT_00481810 + iVar3 * 0x80 + uVar1 * 4);
      if (pcVar2 == (code *)0x0) {
        uVar4 = 7;
      }
      else {
        (*pcVar2)(*(undefined4 *)(DAT_00481814 + iVar3 * 0x80 + uVar1 * 4));
      }
    }
  }
  else {
    uVar4 = 5;
  }
  return uVar4;
}

