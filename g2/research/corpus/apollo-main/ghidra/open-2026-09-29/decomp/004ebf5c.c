
undefined4 FUN_004ebf5c(int param_1)

{
  int *piVar1;
  int *piVar2;
  uint *puVar3;
  int iVar4;
  undefined4 uVar5;
  undefined1 local_14;
  undefined1 local_13;
  undefined1 local_12;
  undefined1 local_11;
  undefined1 local_10;
  
  iVar4 = FUN_0043d0ce();
  if (iVar4 << 0x1e < 0) {
    FUN_0043d574(4,DAT_004ecd50,DAT_004ec294,DAT_004ec2b4,0x4f9,DAT_004ec2b0,*DAT_004ecd4c);
  }
  iVar4 = FUN_0043d0ce();
  if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
    compress_log_output(0x10400000,DAT_004ec2b8,DAT_004ec2b8,*DAT_004ecd4c);
  }
  puVar3 = DAT_004ece48;
  if (*DAT_004ecdac == 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004ecd50,DAT_004ec294,DAT_004ec2b4,0x4fc,DAT_004ec2bc);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004ec2c0);
    }
    uVar5 = 0;
  }
  else if (param_1 == 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004ecd50,DAT_004ec294,DAT_004ec2b4,0x501,DAT_004ec2c4);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004ec2c8,DAT_004ec2c8);
    }
    uVar5 = 0xffffffff;
  }
  else if (*DAT_004ece48 < 6) {
    if (*(int *)(DAT_004ece4c + *DAT_004ece48 * 8 + 4) != 0) {
      FUN_0044d878(*(undefined4 *)(DAT_004ece4c + *DAT_004ece48 * 8 + 4));
    }
    FUN_004ec2dc(*puVar3);
    piVar2 = DAT_004ec298;
    piVar1 = DAT_004ec218;
    if (((*DAT_004ec2a4 == 1) && (*DAT_004ec298 != 0)) && (*DAT_004ec218 != 0)) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004ecd50,DAT_004ec294,DAT_004ec2b4,0x514,DAT_004ec2d4);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004ec2d8,DAT_004ec2d8);
      }
      if (*(char *)(DAT_004ec248 + 0x124) == '\0') {
        FUN_0044d878(*piVar1);
        FUN_004eb7b8(*piVar1);
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004ecd50,DAT_004ec294,DAT_004ec2b4,0x51a,DAT_004ece50);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10000000,DAT_004ece54,DAT_004ece54);
        }
      }
      else {
        local_14 = 0x47;
        local_13 = 0;
        local_12 = 0;
        local_11 = 0;
        local_10 = 0;
        ui_common_api_fn_00509ca2(*piVar2,&local_14,5);
        iVar4 = FUN_0043d0ce();
        if (iVar4 << 0x1e < 0) {
          FUN_0043d574(4,DAT_004ecd50,DAT_004ec294,DAT_004ec2b4,0x525,DAT_004ece58,local_14);
        }
        iVar4 = FUN_0043d0ce();
        if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_004ecec0,DAT_004ecec0,local_14);
        }
      }
    }
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004ecd50,DAT_004ec294,DAT_004ec2b4,0x529,DAT_004ecee4);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004ecfb4,DAT_004ecfb4);
    }
    uVar5 = 0;
  }
  else {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004ecd50,DAT_004ec294,DAT_004ec2b4,0x506,DAT_004ec2cc,*puVar3);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_004ec2d0,DAT_004ec2d0,*puVar3);
    }
    uVar5 = 0xffffffff;
  }
  return uVar5;
}

