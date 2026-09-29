
undefined8 pt_cmd_24_handler(int param_1,uint param_2,undefined1 *param_3,undefined1 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     ((param_2 & 0xff) < 5)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x79e;
      param_3 = DAT_00573200;
      param_4 = DAT_005731fc;
      FUN_0043d574(1,DAT_00572ae8,DAT_00572ae4,DAT_005731fc,0x79e,DAT_00573200,DAT_005731fc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00572850,DAT_00572850,DAT_005731fc,param_2,param_3,param_4);
    }
    uVar2 = 0xffffffff;
  }
  else {
    param_1 = param_1 + 4;
    *param_3 = 0x29;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 1;
    iVar1 = productModeGet();
    if (iVar1 == 1) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        param_2 = 0x7ad;
        FUN_0043d574(3,DAT_00572ae8,DAT_00572ae4,DAT_005731fc,0x7ad,DAT_00573204,param_1);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_00573208,DAT_00573208,param_1);
      }
      SVC_NvdbWriteSysData(1,param_1);
      uVar2 = SVC_NvdbReadSysData(1);
      iVar1 = FUN_004751c8(param_1,uVar2,0x15);
      if (iVar1 == 0) {
        param_3[4] = 0;
      }
      else {
        param_3[4] = 1;
      }
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        param_2 = 0x7bb;
        FUN_0043d574(1,DAT_00572ae8,DAT_00572ae4,DAT_005731fc,0x7bb,DAT_00572854);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_00572ad8,DAT_00572ad8);
      }
      param_3[4] = 5;
    }
    *param_4 = 5;
    uVar2 = 0;
  }
  return CONCAT44(param_2,uVar2);
}

