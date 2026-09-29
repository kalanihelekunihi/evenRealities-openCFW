
undefined8 FUN_004558cc(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  int iVar3;
  undefined4 uVar4;
  
  piVar1 = DAT_00455c34;
  uVar4 = 0;
  if (param_1 != 0) {
    if (*(uint *)(param_1 + 0x2c) < *(uint *)(*DAT_00455c34 + 0x2c)) {
      if (-1 < *(int *)(param_1 + 0x18)) {
        *(int *)(param_1 + 0x18) = 0x38 - *(int *)(*DAT_00455c34 + 0x2c);
      }
      iVar2 = DAT_00455dbc;
      if (*(int *)(param_1 + 0x14) == *(int *)(param_1 + 0x2c) * 0x14 + DAT_00455dbc) {
        uxListRemove(param_1 + 4);
        *(undefined4 *)(param_1 + 0x2c) = *(undefined4 *)(*piVar1 + 0x2c);
        if (*DAT_0045606c < *(uint *)(param_1 + 0x2c)) {
          *DAT_0045606c = *(uint *)(param_1 + 0x2c);
        }
        iVar3 = *(int *)(*(int *)(param_1 + 0x2c) * 0x14 + iVar2 + 4);
        *(int *)(param_1 + 8) = iVar3;
        *(undefined4 *)(param_1 + 0xc) = *(undefined4 *)(iVar3 + 8);
        *(int *)(*(int *)(iVar3 + 8) + 4) = param_1 + 4;
        *(int *)(iVar3 + 8) = param_1 + 4;
        *(int *)(param_1 + 0x14) = *(int *)(param_1 + 0x2c) * 0x14 + iVar2;
        *(int *)(iVar2 + *(int *)(param_1 + 0x2c) * 0x14) =
             *(int *)(iVar2 + *(int *)(param_1 + 0x2c) * 0x14) + 1;
      }
      else {
        *(undefined4 *)(param_1 + 0x2c) = *(undefined4 *)(*piVar1 + 0x2c);
      }
      uVar4 = 1;
    }
    else if (*(uint *)(param_1 + 0x60) < *(uint *)(*DAT_00455c34 + 0x2c)) {
      uVar4 = 1;
    }
  }
  return CONCAT44(param_4,uVar4);
}

