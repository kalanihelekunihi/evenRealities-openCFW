
undefined8
FUN_00559d82(undefined1 *param_1,undefined1 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  if ((param_1 == (undefined1 *)0x0) || (param_2 == (undefined1 *)0x0)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_3 = 0x128;
      FUN_0043d574(1,DAT_00559fb0,DAT_00559fac,DAT_0055a2e0,0x128,DAT_0055a2dc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0055a2e4);
    }
    uVar2 = 1;
  }
  else {
    FUN_0043c0e4(param_2,0x18,0,param_4,param_3,param_4);
    *param_2 = *param_1;
    *(undefined4 *)(param_2 + 4) = *(undefined4 *)(param_1 + 4);
    *(undefined4 *)(param_2 + 8) = *(undefined4 *)(param_1 + 8);
    *(undefined4 *)(param_2 + 0xc) = *(undefined4 *)(param_1 + 0xc);
    *(undefined4 *)(param_2 + 0x10) = *(undefined4 *)(param_1 + 0x10);
    param_2[0x14] = param_1[0x15];
    uVar2 = 0;
  }
  return CONCAT44(param_3,uVar2);
}

