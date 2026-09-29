
undefined8 FUN_005eb576(byte param_1,int param_2)

{
  int iVar1;
  byte bVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  byte bVar8;
  byte bVar9;
  int iStack_30;
  
  iVar1 = DAT_005ebc34;
  bVar8 = 0;
  iStack_30 = param_2;
  if (((*(int *)(DAT_005ebc34 + 0x214) == 0) || (*(int *)(DAT_005ebc34 + 0x21c) == 0)) ||
     (iStack_30 = CONCAT31((int3)((uint)param_2 >> 8),param_1), param_1 == 0)) {
    uVar3 = 0;
  }
  else {
    iVar4 = FUN_005eb438(DAT_005ebc34);
    iVar5 = FUN_0043fce0(*(undefined4 *)(iVar1 + 0x21c));
    bVar2 = FUN_005eb30c();
    for (bVar9 = 0; bVar9 < bVar2; bVar9 = bVar9 + 1) {
      iVar6 = FUN_0044dce2(*(undefined4 *)(iVar1 + 0x21c),bVar9);
      if (iVar6 != 0) {
        iVar7 = FUN_0043fce0(iVar6);
        iVar6 = FUN_0043fdda(iVar6);
        if ((param_2 < iVar6 + iVar7 + iVar5) && (iVar7 + iVar5 < iVar4 + param_2)) {
          bVar8 = bVar8 + 1;
          if (param_1 <= bVar8) {
            uVar3 = 1;
            goto LAB_005eb61a;
          }
        }
      }
    }
    uVar3 = 0;
  }
LAB_005eb61a:
  return CONCAT44(iStack_30,uVar3);
}

