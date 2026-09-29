
undefined8 FUN_0048869a(int param_1,int param_2,int param_3,int param_4,int param_5)

{
  int iVar1;
  uint uVar2;
  int iVar3;
  uint uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  int iVar9;
  int iVar10;
  int iVar11;
  int iVar12;
  
  if ((param_1 != 0) && (param_1 != 0x400)) {
    iVar12 = param_2 * 3;
    iVar3 = param_4 * 3 + param_2 * -6;
    iVar8 = (param_2 * -3 + 0x400) - iVar3;
    param_2 = param_3 * 3;
    iVar6 = param_5 * 3 + param_3 * -6;
    iVar11 = (param_3 * -3 + 0x400) - iVar6;
    iVar9 = param_1;
    for (iVar10 = 0; iVar10 < 8; iVar10 = iVar10 + 1) {
      iVar1 = FUN_00488686(iVar9,iVar8,iVar3,iVar12,param_2,iVar6,param_4);
      uVar2 = iVar1 - param_1;
      uVar4 = uVar2;
      if ((int)uVar2 < 1) {
        uVar4 = -uVar2;
      }
      if ((int)uVar4 < 2) goto LAB_004887ac;
      iVar7 = iVar12 + (iVar9 * ((iVar9 * iVar8 * 3 >> 10) + iVar3 * 2) >> 10);
      iVar1 = iVar7;
      if (iVar7 < 1) {
        iVar1 = -iVar7;
      }
      if ((iVar1 < 2) ||
         (iVar1 = FUN_0047cc1c(uVar2 * 0x400,((int)uVar2 >> 0x1f) << 10 | uVar2 >> 0x16,iVar7,
                               iVar7 >> 0x1f), iVar1 == 0)) break;
      iVar9 = iVar9 - iVar1;
    }
    iVar10 = 0;
    if (param_1 < 0) {
      iVar9 = 0;
    }
    else {
      iVar9 = param_1;
      iVar1 = 0x400;
      if (param_1 < 0x401) {
        do {
          if (iVar1 <= iVar10) break;
          iVar7 = FUN_00488686(iVar9,iVar8,iVar3,iVar12,param_2,iVar6,param_4);
          if (iVar7 - param_1 < 1) {
            iVar5 = param_1 - iVar7;
          }
          else {
            iVar5 = iVar7 - param_1;
          }
          if (iVar5 < 2) break;
          iVar5 = iVar9;
          if (iVar7 < param_1) {
            iVar10 = iVar9;
            iVar5 = iVar1;
          }
          iVar9 = iVar10 + (iVar5 - iVar10) / 2;
          iVar1 = iVar5;
        } while (iVar9 != iVar10);
      }
      else {
        iVar9 = 0x400;
      }
    }
LAB_004887ac:
    param_1 = FUN_00488686(iVar9,iVar11,iVar6,param_2,param_2,iVar6,param_4);
  }
  return CONCAT44(param_2,param_1);
}

