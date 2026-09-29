
int SVC_CodecCheckAndUpgrade(char param_1)

{
  undefined1 *puVar1;
  int iVar2;
  int iVar3;
  int local_5c;
  int local_58;
  int local_54;
  undefined1 auStack_50 [4];
  undefined1 auStack_4c [32];
  undefined1 auStack_2c [32];
  
  local_58 = 0;
  local_54 = 0;
  FUN_0043c0e4(auStack_2c,0x20,0);
  FUN_0043c0e4(auStack_4c,0x20,0);
  DRV_Gx8002_Reboot(0);
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    FUN_0043d574(3,DAT_0057a3d4,DAT_0057a3d0,DAT_0057a410,0x2ef,DAT_0057a40c);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_0057a414,DAT_0057a414);
  }
  iVar2 = semantic_CodecGetPackageVersion(&local_58);
  if (iVar2 != 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0057a3d4,DAT_0057a3d0,DAT_0057a410,0x2f5,DAT_0057a418,iVar2);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0057a41c,DAT_0057a41c,iVar2);
    }
    return -1;
  }
  semantic_CodecFormatVersion(local_58,auStack_2c,0x20);
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    local_5c = local_58;
    FUN_0043d574(3,DAT_0057a3d4,DAT_0057a3d0,DAT_0057a410,0x2fa,DAT_0057a420,auStack_2c);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc800000,DAT_0057a424,DAT_0057a424,auStack_2c,local_58);
  }
  if (param_1 == '\0') {
    FUN_0043c0e4(auStack_50,4,0);
    iVar2 = GX8002_ReadVersion(auStack_50,200);
    if (iVar2 == 0) {
      iVar2 = semantic_CodecParseVersionBytes(auStack_50,&local_54);
      if (iVar2 != 0) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0057a3d4,DAT_0057a3d0,DAT_0057a410,0x309,DAT_0057a430,iVar2);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x4400000,DAT_0057a434,DAT_0057a434,iVar2);
        }
        return -1;
      }
      semantic_CodecFormatVersion(local_54,auStack_4c,0x20);
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_5c = local_54;
        FUN_0043d574(3,DAT_0057a3d4,DAT_0057a3d0,DAT_0057a410,0x30e,DAT_0057a438,auStack_4c);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc800000,DAT_0057a43c,DAT_0057a43c,auStack_4c,local_54);
      }
      if (local_54 == local_58) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(3,DAT_0057a3d4,DAT_0057a3d0,DAT_0057a410,0x312,DAT_0057a440);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_0057a444,DAT_0057a444);
        }
        return 1;
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_0057a3d4,DAT_0057a3d0,DAT_0057a410,0x316,DAT_0057a448);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_0057a44c,DAT_0057a44c);
      }
    }
    else {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0057a3d4,DAT_0057a3d0,DAT_0057a410,0x302,DAT_0057a428,iVar2);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_0057a42c,DAT_0057a42c,iVar2);
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_0057a3d4,DAT_0057a3d0,DAT_0057a410,0x318,DAT_0057a450);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_0057a454,DAT_0057a454);
    }
  }
  iVar2 = SVC_CodecDfu(0);
  if (iVar2 == 0) {
    uart_init();
    do {
      iVar2 = FUN_0058fad2(&local_5c,100);
    } while (iVar2 == 1);
    uart_close();
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,DAT_0057a3d4,DAT_0057a3d0,DAT_0057a410,0x32e,DAT_0057a460,auStack_2c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_0057a464,DAT_0057a464,auStack_2c);
    }
    puVar1 = DAT_0057a468;
    *DAT_0057a468 = (char)((uint)local_58 >> 0x18);
    puVar1[1] = (char)((uint)local_58 >> 0x10);
    puVar1[2] = (char)((uint)local_58 >> 8);
    puVar1[3] = (char)local_58;
    iVar2 = 0;
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0057a3d4,DAT_0057a3d0,DAT_0057a410,0x321,DAT_0057a458,iVar2);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4400000,DAT_0057a45c,DAT_0057a45c,iVar2);
    }
  }
  return iVar2;
}

