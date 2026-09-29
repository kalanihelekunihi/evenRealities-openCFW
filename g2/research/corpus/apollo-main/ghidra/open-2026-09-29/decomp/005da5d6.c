
undefined1 FUN_005da5d6(int param_1,short param_2,int *param_3,int *param_4)

{
  undefined1 uVar1;
  int iVar2;
  short *psVar3;
  
  *param_3 = -1;
  *param_4 = -1;
  for (iVar2 = 0; iVar2 < (int)(uint)*(ushort *)(param_1 + 0x154); iVar2 = iVar2 + 1) {
    psVar3 = (short *)(iVar2 * 0x14 + *(int *)(param_1 + 0x164));
    if ((psVar3[3] == param_2) && (psVar3[4] != 0)) {
      if ((*psVar3 == 3) && (((psVar3[1] == 1 || (psVar3[1] == 0)) && (psVar3[2] == 0x409)))) {
        *param_3 = iVar2;
      }
      if (((*psVar3 == 1) && (psVar3[1] == 0)) && (psVar3[2] == 0)) {
        *param_4 = iVar2;
      }
    }
  }
  if ((*param_3 < 0) && (*param_4 < 0)) {
    uVar1 = 0;
  }
  else {
    uVar1 = 1;
  }
  return uVar1;
}

