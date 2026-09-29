
undefined4 get_touch_firmware_package_version(undefined4 *param_1)

{
  int iVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  int local_20;
  undefined4 local_1c;
  
  if (param_1 == (undefined4 *)0x0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005608c8,DAT_005608c4,DAT_005610a4,0x2bd,DAT_005610a0);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005610a8,DAT_005610a8);
    }
    uVar2 = 0xffffffff;
  }
  else {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005608c8,DAT_005608c4,DAT_005610a4,0x2c1,DAT_005610b0,DAT_005610ac);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x10400000,DAT_005610b4,DAT_005610b4,DAT_005610ac);
    }
    uVar2 = DAT_005610ac;
    iVar1 = file_open(DAT_005610ac,&DAT_00560a64);
    if (iVar1 == 0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,DAT_005608c8,DAT_005608c4,DAT_005610a4,0x2c7,DAT_005610b8,uVar2);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_005610bc,DAT_005610bc,uVar2);
      }
      uVar2 = 0xffffffff;
    }
    else {
      iVar3 = file_read(&local_20,1,0x10,iVar1);
      if (iVar3 == 0x10) {
        if (iVar1 != 0) {
          file_close(iVar1);
        }
        iVar1 = DAT_005610c8;
        if (local_20 == DAT_005610c8) {
          *param_1 = local_1c;
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            FUN_0043d574(4,DAT_005608c8,DAT_005608c4,DAT_005610a4,0x2dc,DAT_005610d4,*param_1);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0x10400000,DAT_005610d8,DAT_005610d8,*param_1);
          }
          uVar2 = 0;
        }
        else {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(1,DAT_005608c8,DAT_005608c4,DAT_005610a4,0x2d7,DAT_005610cc,local_20,iVar1)
            ;
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_005610d0,DAT_005610d0,local_20,iVar1);
          }
          uVar2 = 0xffffffff;
        }
      }
      else {
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(1,DAT_005608c8,DAT_005608c4,DAT_005610a4,0x2ce,DAT_005610c0,iVar3);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_005610c4,DAT_005610c4,iVar3);
        }
        if (iVar1 != 0) {
          file_close(iVar1);
        }
        uVar2 = 0xffffffff;
      }
    }
  }
  return uVar2;
}

