
undefined8
FUN_0058da28(undefined4 *param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined2 uVar1;
  int iVar2;
  undefined4 uVar3;
  
  if ((param_1 == (undefined4 *)0x0) || (param_2 == (undefined4 *)0x0)) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = 0x1e6;
      FUN_0043d574(1,DAT_0058dad4,DAT_0058dad0,DAT_0058dadc,0x1e6,DAT_0058dad8);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0058dae0);
    }
    uVar3 = 2;
  }
  else {
    FUN_0043c0e4(param_2,0xe8,0,param_4,param_3,param_4);
    *param_2 = *param_1;
    param_2[1] = param_1[1];
    param_2[2] = param_1[2];
    uVar3 = param_1[5];
    param_2[4] = param_1[4];
    param_2[5] = uVar3;
    *(undefined1 *)(param_2 + 6) = *(undefined1 *)((int)param_1 + 0xe5);
    if (*(ushort *)(param_1 + 6) < 0xc9) {
      uVar1 = *(undefined2 *)(param_1 + 6);
    }
    else {
      uVar1 = 200;
    }
    *(undefined2 *)((int)param_2 + 0xe2) = uVar1;
    FUN_00439be4((int)param_2 + 0x19,(int)param_1 + 0x1a,*(undefined2 *)((int)param_2 + 0xe2));
    *(undefined1 *)((int)param_2 + *(ushort *)((int)param_2 + 0xe2) + 0x19) = 0;
    uVar3 = 0;
  }
  return CONCAT44(param_3,uVar3);
}

