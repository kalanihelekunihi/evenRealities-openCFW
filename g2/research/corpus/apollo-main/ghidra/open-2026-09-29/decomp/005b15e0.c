
undefined8 FUN_005b15e0(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  byte *pbVar2;
  int iVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  
  uVar4 = param_1;
  uVar5 = param_2;
  iVar3 = FUN_0045a568();
  pbVar2 = DAT_005b1ae8;
  if (iVar3 == 1) {
    bVar1 = *DAT_005b1ae8;
    if (bVar1 == 1) {
      FUN_005b2642(param_1,param_2);
    }
    else {
      if (bVar1 != 0) {
        if (bVar1 == 3) {
          conversate_ui_menu_input_handler(param_1,param_2);
          goto LAB_005b16ca;
        }
        if (bVar1 < 3) {
          FUN_005b2652(param_1,param_2);
          goto LAB_005b16ca;
        }
        if (bVar1 == 5) {
          FUN_005b7060(param_1,param_2);
          goto LAB_005b16ca;
        }
        if (bVar1 < 5) {
          conversate_tag_extend_page_input_event_handler(param_1,param_2);
          goto LAB_005b16ca;
        }
      }
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        uVar4 = 0x1d1;
        uVar5 = DAT_005b1aec;
        FUN_0043d574(2,DAT_005b1ae0,DAT_005b1adc,DAT_005b1ad8,0x1d1,DAT_005b1aec,*pbVar2,param_4);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x8400000,DAT_005b1af0,DAT_005b1af0,*pbVar2);
      }
    }
  }
  else {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      uVar4 = 0x1bb;
      uVar5 = DAT_005b1ad4;
      FUN_0043d574(4,DAT_005b1ae0,DAT_005b1adc,DAT_005b1ad8,0x1bb,DAT_005b1ad4,param_3,param_4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_005b1ae4);
    }
  }
LAB_005b16ca:
  return CONCAT44(uVar5,uVar4);
}

