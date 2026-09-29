
undefined4 FUN_005d7f04(int *param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  undefined4 uVar4;
  int iVar5;
  
  uVar4 = *(undefined4 *)(param_2 * 0xcc + param_1[6] + 200);
  iVar5 = param_1[2];
  for (iVar2 = *param_1; iVar2 != 0; iVar2 = iVar2 + -1) {
    piVar3 = *(int **)(iVar5 + 0x18);
    if (piVar3 != (int *)0x0) {
      if (*(int *)(iVar5 + 0x10) << 0x16 < 0) {
        *(int *)(iVar5 + 0x24) = piVar3[2];
      }
      else if (*(int *)(iVar5 + 0x10) << 0x15 < 0) {
        *(int *)(iVar5 + 0x24) = piVar3[3] + piVar3[2];
      }
      else {
        iVar1 = *(int *)(iVar5 + 0x1c) - *piVar3;
        if (iVar1 < 1) {
          iVar1 = FT_MulFix(iVar1,uVar4);
          *(int *)(iVar5 + 0x24) = iVar1 + piVar3[2];
        }
        else if (iVar1 < piVar3[1]) {
          iVar1 = FT_MulDiv(iVar1,piVar3[3],piVar3[1]);
          *(int *)(iVar5 + 0x24) = iVar1 + piVar3[2];
        }
        else {
          iVar1 = FT_MulFix(iVar1 - piVar3[1],uVar4);
          *(int *)(iVar5 + 0x24) = iVar1 + piVar3[3] + piVar3[2];
        }
      }
      *(uint *)(iVar5 + 0x10) = *(uint *)(iVar5 + 0x10) | 0x20;
    }
    iVar5 = iVar5 + 0x28;
  }
  return param_4;
}

