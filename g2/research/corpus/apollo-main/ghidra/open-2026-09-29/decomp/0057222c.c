
undefined8 pt_cmd_26_handler(int param_1,uint param_2,undefined1 *param_3,undefined1 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  undefined1 *puVar4;
  
  uVar3 = param_2;
  puVar4 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uVar3 = 0x73e;
    FUN_0043d574(3,DAT_00572ae8,DAT_00572ae4,DAT_00572c50,0x73e,DAT_00572c4c,puVar4);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_0057227a;
  }
  compress_log_output(0xc000000,DAT_00572c54,DAT_00572c54);
LAB_0057227a:
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     ((param_2 & 0xff) < 4)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = 0x741;
      FUN_0043d574(1,DAT_00572ae8,DAT_00572ae4,DAT_00572c50,0x741,DAT_005726ec,DAT_00572c50);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00572850,DAT_00572850,DAT_00572c50);
    }
    uVar2 = 0xffffffff;
  }
  else {
    *param_3 = 0x30;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 1;
    iVar1 = productModeGet();
    if (iVar1 == 1) {
      param_3[4] = 0;
    }
    else {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar3 = 0x754;
        FUN_0043d574(1,DAT_00572ae8,DAT_00572ae4,DAT_00572c50,0x754,DAT_00572854);
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
  return CONCAT44(uVar3,uVar2);
}

