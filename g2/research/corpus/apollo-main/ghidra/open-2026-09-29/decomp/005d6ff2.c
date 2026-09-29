
void FUN_005d6ff2(int param_1,uint param_2,int param_3)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  undefined4 *puVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  int iVar9;
  int iVar10;
  
  uVar5 = *DAT_005d7098;
  uVar7 = DAT_005d7098[1];
  if (1 < (int)param_2) {
    uVar1 = FUN_005d6e44(param_1);
    if (uVar1 < param_2) {
      FUN_005d2a0a(*(undefined4 *)(param_1 + 4),0x82);
    }
    else {
      if (param_3 < 0) {
        iVar2 = param_2 * (-param_3 / (int)param_2);
      }
      else {
        iVar2 = -(param_2 * (param_3 / (int)param_2));
      }
      if (iVar2 + param_3 != 0) {
        iVar10 = -1;
        iVar9 = -1;
        for (iVar3 = 0; iVar3 < (int)param_2; iVar3 = iVar3 + 1) {
          uVar6 = uVar5;
          uVar8 = uVar7;
          if (iVar9 == iVar10) {
            iVar9 = iVar9 + 1;
            puVar4 = (undefined4 *)(*(int *)(param_1 + 8) + iVar9 * 8);
            uVar6 = *puVar4;
            uVar8 = puVar4[1];
            iVar10 = iVar9;
          }
          iVar10 = iVar2 + param_3 + iVar10;
          if (iVar10 < (int)param_2) {
            if (iVar10 < 0) {
              iVar10 = param_2 + iVar10;
            }
          }
          else {
            iVar10 = iVar10 - param_2;
          }
          puVar4 = (undefined4 *)(*(int *)(param_1 + 8) + iVar10 * 8);
          uVar5 = *puVar4;
          uVar7 = puVar4[1];
          puVar4 = (undefined4 *)(*(int *)(param_1 + 8) + iVar10 * 8);
          *puVar4 = uVar6;
          puVar4[1] = uVar8;
        }
      }
    }
  }
  return;
}

