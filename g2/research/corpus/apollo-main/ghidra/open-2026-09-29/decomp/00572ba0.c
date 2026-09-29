
undefined4 pt_cmd_08_handler(int param_1,uint param_2,undefined1 *param_3,undefined1 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     ((param_2 & 0xff) < 4)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_1 = 0x822;
      param_2 = DAT_00573200;
      param_3 = DAT_00573898;
      FUN_0043d574(1,DAT_005735f4,DAT_005735f0,DAT_00573898,0x822,DAT_00573200,DAT_00573898,param_4)
      ;
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00573300,DAT_00573300,DAT_00573898,param_1,param_2,param_3);
    }
    uVar2 = 0xffffffff;
  }
  else {
    *param_3 = 0xb;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 1;
    param_3[4] = 0;
    *param_4 = 5;
    uVar2 = 0;
  }
  return uVar2;
}

