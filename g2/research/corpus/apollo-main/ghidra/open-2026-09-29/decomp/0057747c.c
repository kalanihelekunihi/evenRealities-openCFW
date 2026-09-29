
undefined8 pt_cmd_6C_handler(int param_1,uint param_2,undefined1 *param_3,undefined1 *param_4)

{
  int iVar1;
  undefined4 uVar2;
  uint uVar3;
  undefined1 *puVar4;
  
  uVar3 = param_2;
  puVar4 = param_4;
  iVar1 = FUN_0043d0ce();
  if (iVar1 << 0x1e < 0) {
    uVar3 = 0xe51;
    FUN_0043d574(3,DAT_00577bbc,DAT_00577bb8,DAT_00577bcc,0xe51,DAT_00577bc8,puVar4);
  }
  iVar1 = FUN_0043d0ce();
  if (-1 < iVar1 << 0x1f) {
    iVar1 = FUN_0043d0ce();
    if (-1 < iVar1 << 0x1d) goto LAB_005774ca;
  }
  compress_log_output(0xc000000,DAT_00577bd0,DAT_00577bd0);
LAB_005774ca:
  if ((((param_3 == (undefined1 *)0x0) || (param_4 == (undefined1 *)0x0)) || (param_1 == 0)) ||
     ((param_2 & 0xff) < 4)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = 0xe54;
      FUN_0043d574(1,DAT_00577bbc,DAT_00577bb8,DAT_00577bcc,0xe54,DAT_00577bc4,DAT_00577bcc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_00577bd4,DAT_00577bd4,DAT_00577bcc);
    }
    uVar2 = 0xffffffff;
  }
  else {
    *param_3 = 0x6b;
    param_3[1] = 1;
    param_3[2] = 3;
    param_3[3] = 1;
    param_3[4] = *DAT_00577bd8;
    *param_4 = 5;
    uVar2 = 0;
  }
  return CONCAT44(uVar3,uVar2);
}

