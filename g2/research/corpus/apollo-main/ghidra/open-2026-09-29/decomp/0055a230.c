
undefined8
FUN_0055a230(undefined1 *param_1,undefined1 *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  
  if ((param_1 == (undefined1 *)0x0) || (param_2 == (undefined1 *)0x0)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_3 = 0x1e6;
      FUN_0043d574(1,PTR_s_health_data_mgr_0055a310,DAT_0055a30c,DAT_0055a348,0x1e6,DAT_0055a344);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0055a34c);
    }
    uVar2 = 1;
  }
  else {
    FUN_0043c0e4(param_2,0x101,0,param_4,param_3,param_4);
    *param_2 = *param_1;
    uVar3 = (uint)*(ushort *)(param_1 + 2);
    if (0xff < uVar3) {
      uVar3 = 0xff;
    }
    FUN_00439be4(param_2 + 1,param_1 + 4,uVar3);
    param_2[uVar3 + 1] = 0;
    uVar2 = 0;
  }
  return CONCAT44(param_3,uVar2);
}

