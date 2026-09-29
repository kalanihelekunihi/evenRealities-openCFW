
undefined8 am_devices_mspi_hongshi_read_chipId(undefined2 *param_1,undefined4 param_2)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  
  cVar1 = am_devices_mspi_hongshi_read_bank(6,0);
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0x27c;
    FUN_0043d574(3,DAT_005bc8ac,DAT_005bc8a8,DAT_005bd2d0,0x27c,DAT_005bd2cc,cVar1);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc400000,DAT_005bd2d4,DAT_005bd2d4,cVar1);
  }
  if (cVar1 != '\x01') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_2 = 0x27f;
      FUN_0043d574(1,DAT_005bc8ac,DAT_005bc8a8,DAT_005bd2d0,0x27f,DAT_005bd2d8,cVar1);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_005bd2dc,DAT_005bd2dc,cVar1);
    }
    uVar3 = 0xffffffff;
    goto LAB_005bc878;
  }
  FUN_00491102(100);
  if (param_1 != (undefined2 *)0x0) {
    *param_1 = 1;
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    param_2 = 0x289;
    FUN_0043d574(4,DAT_005bc8ac,DAT_005bc8a8,DAT_005bd2d0,0x289,DAT_005bd2e0,*param_1);
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1f < 0) {
LAB_005bc862:
    compress_log_output(0x10400000,DAT_005bd2e4,DAT_005bd2e4,*param_1);
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1d < 0) goto LAB_005bc862;
  }
  am_device_mspi_hongshi_read_sn();
  uVar3 = 0;
LAB_005bc878:
  return CONCAT44(param_2,uVar3);
}

