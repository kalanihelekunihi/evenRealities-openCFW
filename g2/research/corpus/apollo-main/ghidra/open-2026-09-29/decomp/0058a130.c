
/* WARNING: Removing unreachable block (ram,0x0058a2ca) */

undefined4 FUN_0058a130(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

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
  FUN_00589a4e();
  if (param_1 == 2) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      local_2c = DAT_0058a3cc;
      local_30 = 0x14d;
      FUN_0043d574(3,DAT_0058a320,DAT_0058a31c,DAT_0058a3d0);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_0058a3d4,DAT_0058a3d4);
    }
    iVar3 = osKernelGetTickCount();
    *DAT_0058a3d8 = iVar3;
    if (*DAT_0058a368 == '\0') {
      local_28[0] = 1;
    }
    else {
      local_28[0] = 2;
    }
    ble_state_skip_manual_start(0);
    FUN_00589cb4();
    FUN_0055448e(param_4);
    FUN_00554170(local_28[0],local_24);
    *(undefined4 *)(DAT_0058a3dc + 4) = *DAT_0058a3a0;
  }
  else if (1 < param_1) {
    if (param_1 == 4) {
      FUN_0058922c();
      FUN_00589cca();
      FUN_0055468c();
    }
    else if (param_1 < 4) {
      FUN_00439be4(local_28,param_2,8);
      FUN_00554170(local_28[0],local_24);
    }
    else if (param_1 == 5) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        local_2c = DAT_0058a3e0;
        local_30 = 0x164;
        FUN_0043d574(3,DAT_0058a320,DAT_0058a31c,DAT_0058a3d0);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_0058a3e4,DAT_0058a3e4);
      }
      teleprompt_file_list_reset();
      teleprompt_page_data_deinit();
      FUN_0055462e();
      ble_param_reset_delayed_event(10000);
      AUDM_appRelease(2);
      pcVar2 = DAT_0058a368;
      if ((*DAT_0058a368 == '\x01') && (iVar3 = FUN_0045a568(), iVar3 == 1)) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          local_2c = DAT_0058a3e8;
          local_30 = 0x16c;
          FUN_0043d574(3,DAT_0058a320,DAT_0058a31c,DAT_0058a3d0);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0xc000000,DAT_0058a3ec,DAT_0058a3ec);
        }
        local_30 = CONCAT22(local_30._2_2_,*DAT_0058a3f0);
        APP_PbTxEncodeStatusNotify(&local_30);
      }
      FUN_0043c0e4(pcVar2,0x44,0);
      iVar3 = osKernelGetTickCount();
      lVar1 = (ulonglong)(uint)(iVar3 - *DAT_0058a3d8) * 1000;
      uVar4 = FUN_0047cc60((int)lVar1,(int)((ulonglong)lVar1 >> 0x20),1000,0);
      iVar3 = FUN_0045a568();
      if (iVar3 == 1) {
        local_20 = *DAT_0058a3f4;
        local_1c = uVar4;
        FUN_0048eb32(DAT_0058a3f8,2,&local_20);
      }
    }
  }
  FUN_00589b08();
  return 0;
}

