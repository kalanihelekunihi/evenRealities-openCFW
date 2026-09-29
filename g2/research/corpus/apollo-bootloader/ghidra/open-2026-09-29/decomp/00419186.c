
undefined4 FUN_00419186(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  uint uVar4;
  uint uVar5;
  
  piVar2 = DAT_00419220;
  uVar5 = *DAT_004191fc;
  FUN_0041b5a8(*DAT_00419220 + 4);
  piVar1 = DAT_00419200;
  if ((param_1 == -1) && (param_2 != 0)) {
    iVar3 = DAT_00419200[1];
    *(int *)(*piVar2 + 8) = iVar3;
    *(undefined4 *)(*piVar2 + 0xc) = *(undefined4 *)(iVar3 + 8);
    *(int *)(*(int *)(iVar3 + 8) + 4) = *piVar2 + 4;
    *(int *)(iVar3 + 8) = *piVar2 + 4;
    *(int **)(*piVar2 + 0x14) = piVar1;
    *piVar1 = *piVar1 + 1;
  }
  else {
    uVar4 = param_1 + uVar5;
    *(uint *)(*piVar2 + 4) = uVar4;
    if (uVar4 < uVar5) {
      FUN_0041b572(*DAT_00419218,*piVar2 + 4);
    }
    else {
      FUN_0041b572(*DAT_00419214,*piVar2 + 4);
      if (uVar4 < *DAT_00419224) {
        *DAT_00419224 = uVar4;
      }
    }
  }
  return param_4;
}

