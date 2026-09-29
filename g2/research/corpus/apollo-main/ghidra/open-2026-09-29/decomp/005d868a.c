
undefined4 FUN_005d868a(int *param_1,int param_2,int param_3,undefined4 param_4)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  int *piVar6;
  int *piVar7;
  
  if (param_2 < DAT_005d8ab8) {
    *(bool *)(param_1 + 0x208) = param_2 * 0x7d < param_1[0x204] * 8;
  }
  else {
    *(bool *)(param_1 + 0x208) = param_2 < (param_1[0x204] << 3) / 0x7d;
  }
  iVar4 = param_1[0x205];
  while ((0 < iVar4 && (iVar1 = FT_MulFix(iVar4,param_2), 0x20 < iVar1))) {
    iVar4 = iVar4 + -1;
  }
  param_1[0x206] = iVar4;
  for (uVar5 = 0; uVar5 < 4; uVar5 = uVar5 + 1) {
    piVar2 = param_1;
    if (uVar5 != 0) {
      if (uVar5 == 2) {
        piVar2 = param_1 + 0x102;
      }
      else if (uVar5 < 2) {
        piVar2 = param_1 + 0x81;
      }
      else {
        piVar2 = param_1 + 0x183;
      }
    }
    piVar6 = piVar2 + 1;
    for (iVar4 = *piVar2; iVar4 != 0; iVar4 = iVar4 + -1) {
      iVar1 = FT_MulFix(piVar6[2],param_2);
      piVar6[7] = param_3 + iVar1;
      iVar1 = FT_MulFix(piVar6[3],param_2);
      piVar6[6] = param_3 + iVar1;
      iVar1 = FT_MulFix(*piVar6,param_2);
      piVar6[4] = param_3 + iVar1;
      iVar1 = FT_MulFix(piVar6[1],param_2);
      piVar6[5] = iVar1;
      piVar6[4] = piVar6[4] + 0x20U & 0xffffffc0;
      piVar6 = piVar6 + 8;
    }
  }
  uVar5 = 0;
  do {
    if (1 < uVar5) {
      return param_4;
    }
    if (uVar5 == 0) {
      piVar6 = param_1 + 0x102;
      piVar2 = param_1;
    }
    else {
      piVar2 = param_1 + 0x81;
      piVar6 = param_1 + 0x183;
    }
    piVar7 = piVar2 + 1;
    for (iVar4 = *piVar2; iVar4 != 0; iVar4 = iVar4 + -1) {
      piVar2 = piVar6 + 1;
      for (iVar1 = *piVar6; iVar1 != 0; iVar1 = iVar1 + -1) {
        iVar3 = *piVar7 - *piVar2;
        if (iVar3 < 0) {
          iVar3 = -iVar3;
        }
        iVar3 = FT_MulFix(iVar3,param_2);
        if (iVar3 < 0x40) {
          piVar7[7] = piVar2[7];
          piVar7[6] = piVar2[6];
          piVar7[4] = piVar2[4];
          piVar7[5] = piVar2[5];
          break;
        }
        piVar2 = piVar2 + 8;
      }
      piVar7 = piVar7 + 8;
    }
    uVar5 = uVar5 + 1;
  } while( true );
}

