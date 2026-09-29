
/* WARNING: Removing unreachable block (ram,0x0059f3bc) */

undefined4 FUN_0059f236(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  longlong lVar1;
  char *pcVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 local_30;
  undefined4 local_2c;
  undefined1 local_28 [4];
  undefined4 local_24;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 uStack_18;
  
  uStack_18 = param_4;
  FUN_0043c0e4(local_28,8,0);
  FUN_0059eb0e();
  if (param_1 == 2) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_2c = DAT_0059f4dc;
      local_30 = 0x12a;
      FUN_0043d574(3,DAT_0059f414,DAT_0059f410,DAT_0059f4e0);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_0059f4e4,DAT_0059f4e4);
    }
    iVar3 = osKernelGetTickCount();
    *DAT_0059f4e8 = iVar3;
    if (*DAT_0059f4ec == '\0') {
      local_28[0] = 3;
    }
    else {
      local_28[0] = 4;
    }
    ble_state_skip_manual_start(0);
    FUN_0059ed06();
    translate_ui_0059d8f0(param_4);
    translate_ui_0059db9a(local_28[0],local_24);
    *(undefined4 *)(DAT_0059f4f0 + 4) = *DAT_0059f4b0;
  }
  else if (1 < param_1) {
    if (param_1 == 4) {
      FUN_0059ed1c();
      translate_ui_0059df04();
    }
    else if (param_1 < 4) {
      FUN_00439be4(local_28,param_2,8);
      translate_ui_0059db9a(local_28[0],local_24);
    }
    else if (param_1 == 5) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_2c = DAT_0059f4f4;
        local_30 = 0x141;
        FUN_0043d574(3,DAT_0059f414,DAT_0059f410,DAT_0059f4e0);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_0059f4f8,DAT_0059f4f8);
      }
      translate_ui_0059d9d4();
      ble_param_reset_delayed_event(10000);
      AUDM_appRelease(1);
      pcVar2 = DAT_0059f4ec;
      if (*DAT_0059f4ec == '\x01') {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          local_2c = DAT_0059f4fc;
          local_30 = 0x146;
          FUN_0043d574(3,DAT_0059f414,DAT_0059f410,DAT_0059f4e0);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_0059f500,DAT_0059f500);
        }
        local_30 = CONCAT22(local_30._2_2_,*DAT_0059f504);
        APP_PbTranslateTxEncodeNotify(&local_30);
      }
      FUN_0043c0e4(pcVar2,0x10,0);
      iVar3 = osKernelGetTickCount();
      lVar1 = (ulonglong)(uint)(iVar3 - *DAT_0059f4e8) * 1000;
      uVar4 = FUN_0047cc60((int)lVar1,(int)((ulonglong)lVar1 >> 0x20),1000,0);
      iVar3 = FUN_0045a568();
      if (iVar3 == 1) {
        local_20 = *DAT_0059f508;
        local_1c = uVar4;
        FUN_0048eb32(DAT_0059f50c,2,&local_20);
      }
    }
  }
  FUN_0059ebc8();
  return 0;
}

