
undefined8
FUN_00491752(undefined4 *param_1,undefined1 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  
  if (param_1 == (undefined4 *)0x0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_3 = 0xdc;
      FUN_0043d574(1,DAT_00491ee8,DAT_00491ee4,DAT_00491ef8,0xdc,DAT_00491ef4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_00491efc);
    }
    uVar2 = 0;
  }
  else {
    uVar2 = param_1[2];
    uVar3 = param_1[1];
    FUN_0043c0e4(param_1,0x7160,0,param_4,param_3,param_4);
    param_1[2] = uVar2;
    param_1[1] = uVar3;
    *(undefined1 *)(param_1 + 3) = param_2;
    *param_1 = 0xa5a5a5a5;
    param_1[0x1c57] = 0x5a5a5a5a;
    uVar2 = 1;
  }
  return CONCAT44(param_3,uVar2);
}

