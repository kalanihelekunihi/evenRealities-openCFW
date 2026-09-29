
undefined8
_masterMaybeNotifyRingConnectFailure
          (uint param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  byte *pbVar1;
  int iVar2;
  uint uVar3;
  
  pbVar1 = DAT_004a1fb0;
  uVar3 = param_1;
  if (*DAT_004a2058 != '\0') {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      param_3 = param_1 & 0xff;
      uVar3 = 899;
      param_2 = DAT_004a205c;
      FUN_0043d574(3,DAT_004a1af4,DAT_004a1af0,DAT_004a2060,899,DAT_004a205c,param_3,param_4);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_004a2064,DAT_004a2064,param_1 & 0xff,uVar3,param_2,param_3);
    }
    goto LAB_004a17f2;
  }
  if ((param_1 & 0xff) != 8) {
    if (*DAT_004a1fac == '\0') {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uVar3 = 0x389;
        param_2 = DAT_004a2164;
        FUN_0043d574(3,DAT_004a1af4,DAT_004a1af0,DAT_004a2060,0x389,DAT_004a2164,param_1 & 0xff);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_004a218c,DAT_004a218c,param_1 & 0xff);
      }
      goto LAB_004a17f2;
    }
    *DAT_004a1fb0 = *DAT_004a1fb0 + 1;
    if (((param_1 & 0xff) == 0x3e) || (*pbVar1 < 2)) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uVar3 = 0x38f;
        param_2 = DAT_004a21c0;
        FUN_0043d574(3,DAT_004a1af4,DAT_004a1af0,DAT_004a2060,0x38f,DAT_004a21c0,param_1 & 0xff);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_004a21c4,DAT_004a21c4,param_1 & 0xff);
      }
      goto LAB_004a17f2;
    }
  }
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    uVar3 = 0x394;
    param_2 = DAT_004a21c8;
    FUN_0043d574(3,DAT_004a1af4,DAT_004a1af0,DAT_004a2060,0x394,DAT_004a21c8,param_1 & 0xff);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc400000,DAT_004a2250,DAT_004a2250,param_1 & 0xff);
  }
  *DAT_004a1fac = '\0';
  *DAT_004a1fb0 = 0;
  fw_event_loop_push_delayed(DAT_004a2360,param_1 & 0xff,1000);
LAB_004a17f2:
  return CONCAT44(param_2,uVar3);
}

