
undefined4 FUN_004cb514(uint *param_1,uint param_2)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  uint uVar4;
  uint uVar5;
  
  uVar4 = DAT_004cc1dc;
  if ((int)(param_2 << 3) < 0) {
    uVar4 = DAT_004cc1d8;
  }
  if ((((param_2 & uVar4) == (uVar4 & *param_1)) || (iVar2 = FUN_004cae74(*param_1), iVar2 != 0)) ||
     ((DAT_004cc1d8 & param_2) == (*param_1 & DAT_004cbfe0 | DAT_004cc1e0))) {
    *param_1 = 0;
    uVar3 = 1;
  }
  else {
    iVar2 = FUN_004cae88(param_2);
    if (iVar2 == 0x400) {
      uVar4 = FUN_004caeb0(*param_1);
      uVar5 = FUN_004caeb0(param_2);
      if (uVar5 <= (uVar4 & 0xffff)) {
        cVar1 = FUN_004caea6(param_2);
        *param_1 = *param_1 + cVar1 * 0x400;
      }
    }
    uVar3 = 0;
  }
  return uVar3;
}

