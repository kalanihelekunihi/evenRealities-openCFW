
undefined4 FUN_00442456(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int *piVar2;
  undefined4 uVar3;
  int iVar4;
  int iVar5;
  
  if (param_1 == 2) {
    iVar5 = param_2;
    iVar4 = FUN_0045bbf4();
    if (iVar4 == 1) {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(3,DAT_00442cf4,DAT_00442cf0,DAT_00442d08,0x80,DAT_00442d04,param_2);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_00442d0c,DAT_00442d0c,param_2);
      }
      uVar3 = 0xffffffff;
    }
    else {
      for (iVar4 = 0; piVar2 = DAT_00442cdc, iVar1 = DAT_00442cd8, iVar4 < *DAT_00442cd4;
          iVar4 = iVar4 + 1) {
        if (((*(char *)(*(int *)(iVar4 * 0x10 + DAT_00442cd8 + 0xc) + 0xb) == '\x01') &&
            (*(int *)(iVar4 * 0x10 + DAT_00442cd8 + 8) != 0)) &&
           (**(int **)(iVar4 * 0x10 + DAT_00442cd8 + 0xc) != param_2)) {
          (**(code **)(iVar4 * 0x10 + DAT_00442cd8 + 8))
                    (2,0,0,*(undefined4 *)(*DAT_00442cdc + 0x20),param_1,iVar5,param_3,param_4);
          FUN_0045f3c8(*piVar2,*(undefined4 *)(iVar4 * 0x10 + iVar1 + 0xc));
        }
      }
      uVar3 = 0;
    }
  }
  else {
    uVar3 = 0xffffffff;
  }
  return uVar3;
}

