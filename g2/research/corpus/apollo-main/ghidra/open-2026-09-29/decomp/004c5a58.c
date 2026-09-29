
undefined8 FUN_004c5a58(uint param_1,int param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  int iVar4;
  
  uVar3 = param_1;
  iVar4 = param_2;
  uVar2 = param_3;
  iVar1 = onboarding_should_run();
  if (iVar1 == 1) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      uVar3 = 0x7f;
      iVar4 = DAT_004c61a8;
      FUN_0043d574(2,DAT_004c6184,DAT_004c6180,DAT_004c61ac,0x7f,DAT_004c61a8,uVar2,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_004c61b0,DAT_004c61b0);
    }
  }
  else {
    iVar1 = settings_get_terminal_mode();
    if (iVar1 == 0) {
      if ((param_1 & 0xffff) == 0) {
        if (param_2 == 0xd) {
          *DAT_004c618c = param_3;
        }
        else {
          if (param_2 != 0xe) goto LAB_004c5c2e;
          *DAT_004c618c = 0;
        }
      }
      else {
        if ((param_1 & 0xffff) != 1) goto LAB_004c5c2e;
        if (param_2 == 0xd) {
          *DAT_004c6190 = param_3;
        }
        else {
          if (param_2 != 0xe) goto LAB_004c5c2e;
          *DAT_004c6190 = 0;
        }
      }
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        uVar3 = 0xab;
        iVar4 = DAT_004c61b4;
        FUN_0043d574(4,DAT_004c6184,DAT_004c6180,DAT_004c61ac,0xab,DAT_004c61b4,*DAT_004c618c,
                     *DAT_004c6190);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        uVar3 = *DAT_004c6190;
        compress_log_output(0x10800000,DAT_004c61b8,DAT_004c61b8,*DAT_004c618c);
      }
      if ((*DAT_004c618c == 0) || (*DAT_004c6190 == 0)) {
        fw_event_loop_remove_delayed(DAT_004c61bc);
      }
      else {
        uVar2 = FUN_00509694(*DAT_004c618c - *DAT_004c6190);
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          uVar3 = 0xb4;
          iVar4 = DAT_004c61c0;
          FUN_0043d574(4,DAT_004c6184,DAT_004c6180,DAT_004c61ac,0xb4,DAT_004c61c0,uVar2);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x10400000,DAT_004c61c4,DAT_004c61c4,uVar2);
        }
        if (uVar2 < 0x7d1) {
          iVar1 = FUN_0043d0ce();
          if (iVar1 << 0x1e < 0) {
            uVar3 = 0xba;
            iVar4 = DAT_004c61c8;
            FUN_0043d574(3,DAT_004c6184,DAT_004c6180,DAT_004c61ac);
          }
          iVar1 = FUN_0043d0ce();
          if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
            compress_log_output(0xc000000,DAT_004c61cc,DAT_004c61cc);
          }
          fw_event_loop_push_delayed(DAT_004c61bc,0,1000);
        }
        else {
          fw_event_loop_remove_delayed(DAT_004c61bc);
        }
      }
    }
  }
LAB_004c5c2e:
  return CONCAT44(iVar4,uVar3);
}

