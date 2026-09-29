
undefined4 FUN_08008bd8(int *param_1)

{
  uint uVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  undefined4 uVar6;
  
  uVar6 = 0;
  *(uint *)*param_1 =
       *(uint *)*param_1 & DAT_08008d68 | param_1[2] | param_1[4] | param_1[5] | param_1[7];
  *(uint *)(*param_1 + 4) = *(uint *)(*param_1 + 4) & 0xffffcfff | param_1[3];
  *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & DAT_08008d6c | param_1[8] | param_1[6];
  *(uint *)(*param_1 + 0x2c) = *(uint *)(*param_1 + 0x2c) & 0xfffffff0 | param_1[9];
  uVar1 = DAT_08008d94;
  iVar5 = DAT_08008d90;
  iVar2 = *param_1;
  if (iVar2 == DAT_08008d70) {
    uVar3 = *(uint *)(DAT_08008d74 + 0x14) & 3;
    if (uVar3 != 0) {
      if (uVar3 == 1) {
LAB_08008c84:
        uVar3 = 4;
      }
      else if (uVar3 != 2) {
        if (uVar3 != 3) goto LAB_08008ca2;
LAB_08008c88:
        uVar3 = 8;
      }
    }
  }
  else if (iVar2 == DAT_08008d78) {
    uVar3 = *(uint *)(DAT_08008d74 + 0x14) & 0xc;
    if ((uVar3 != 0) && (uVar3 != 4)) {
      if (uVar3 != 8) {
        if (uVar3 == 0xc) goto LAB_08008c88;
        goto LAB_08008ca2;
      }
LAB_08008c80:
      uVar3 = 2;
    }
  }
  else if (iVar2 == DAT_08008d7c) {
    uVar4 = *(uint *)(DAT_08008d74 + 0x14) & 0x30;
    uVar3 = 0;
    if (uVar4 != 0) {
      if (uVar4 == 0x10) goto LAB_08008c84;
      if (uVar4 == 0x20) goto LAB_08008c80;
      if (uVar4 == 0x30) goto LAB_08008c88;
LAB_08008ca2:
      uVar3 = 0x10;
    }
  }
  else {
    if (((iVar2 != DAT_08008d80) && (iVar2 != DAT_08008d84)) && (iVar2 != DAT_08008d88))
    goto LAB_08008ca2;
    uVar3 = 0;
  }
  if (param_1[7] == 0x8000) {
    if (uVar3 == 0) {
      iVar2 = case_shift_selected();
LAB_08008cd4:
      if (iVar2 == 0) goto LAB_08008d52;
    }
    else {
      iVar2 = DAT_08008d8c;
      if (uVar3 != 2) {
        if (uVar3 != 4) {
          iVar2 = 0x8000;
          if (uVar3 == 8) goto LAB_08008cd8;
          goto LAB_08008d48;
        }
        iVar2 = case_derive_clock();
        goto LAB_08008cd4;
      }
    }
LAB_08008cd8:
    iVar5 = __aeabi_uidiv(iVar2,*(undefined2 *)(iVar5 + param_1[9] * 2));
    uVar3 = __aeabi_uidiv(iVar5 * 2 + ((uint)param_1[1] >> 1));
    if (uVar1 < uVar3 - 0x10) {
LAB_08008d48:
      uVar6 = 1;
      goto LAB_08008d52;
    }
    uVar3 = (uVar3 & 0xf) >> 1 | DAT_08008d94 + 1 & uVar3;
  }
  else {
    if (uVar3 == 0) {
      iVar2 = case_shift_selected();
LAB_08008d26:
      if (iVar2 == 0) goto LAB_08008d52;
    }
    else {
      iVar2 = DAT_08008d8c;
      if (uVar3 != 2) {
        if (uVar3 == 4) {
          iVar2 = case_derive_clock();
          goto LAB_08008d26;
        }
        iVar2 = 0x8000;
        if (uVar3 != 8) goto LAB_08008d48;
      }
    }
    iVar5 = __aeabi_uidiv(iVar2,*(undefined2 *)(iVar5 + param_1[9] * 2));
    uVar3 = __aeabi_uidiv(iVar5 + ((uint)param_1[1] >> 1));
    if (uVar1 < uVar3 - 0x10) goto LAB_08008d48;
    uVar3 = uVar3 & 0xffff;
  }
  *(uint *)(*param_1 + 0xc) = uVar3;
LAB_08008d52:
  *(undefined2 *)((int)param_1 + 0x6a) = 1;
  *(undefined2 *)(param_1 + 0x1a) = 1;
  param_1[0x1d] = 0;
  param_1[0x1e] = 0;
  return uVar6;
}

