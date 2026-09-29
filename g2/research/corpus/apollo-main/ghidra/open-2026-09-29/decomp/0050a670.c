
undefined8 FUN_0050a670(char param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int *piVar1;
  int iVar2;
  int *piVar3;
  undefined4 *puVar4;
  int iVar5;
  int iVar6;
  
  piVar1 = DAT_0050b044;
  if (*DAT_0050b044 == 0) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      param_2 = 0x18c;
      FUN_0043d574(2,DAT_0050ac28,DAT_0050ac24,DAT_0050b04c,0x18c,DAT_0050b048);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0050b050);
    }
    iVar5 = -1;
  }
  else {
    iVar5 = (int)param_2 >> 0x10;
    if (param_1 == '\n') {
      for (iVar5 = 0; iVar2 = DAT_0050b14c, iVar5 < 4; iVar5 = iVar5 + 1) {
        if ((*(int *)(iVar5 * 0x30 + DAT_0050b14c + 4) != 0) &&
           (iVar6 = FUN_0043e2ea(*(undefined4 *)(iVar5 * 0x30 + DAT_0050b14c + 4)), iVar6 != 0)) {
          FUN_00450500(*(undefined4 *)(iVar2 + iVar5 * 0x30 + 4),DAT_0050b150);
        }
      }
      FUN_00450500(DAT_0050b14c,DAT_0050b154);
      *DAT_0050b158 = 0;
      *DAT_0050b15c = 0;
      *DAT_0050af9c = 0;
      piVar3 = DAT_0050b160;
      if (*DAT_0050b160 != 0) {
        ui_common_api_fn_00509c96(*DAT_0050b160);
        *piVar3 = 0;
      }
      puVar4 = DAT_0050b164;
      iVar5 = FUN_0044ddea(*DAT_0050b164);
      while (iVar5 = iVar5 + -1, -1 < iVar5) {
        iVar6 = FUN_0044dce2(*puVar4,iVar5);
        if (iVar6 != 0) {
          FUN_0044d7b8();
        }
      }
      for (iVar5 = 0; iVar5 < 4; iVar5 = iVar5 + 1) {
        *(undefined4 *)(iVar2 + iVar5 * 0x30) = 0;
        *(undefined4 *)(iVar5 * 0x30 + iVar2 + 4) = 0;
        *(undefined4 *)(iVar5 * 0x30 + iVar2 + 8) = 0;
        *(undefined4 *)(iVar5 * 0x30 + iVar2 + 0xc) = 0;
        *(undefined4 *)(iVar5 * 0x30 + iVar2 + 0x10) = 0;
        *(undefined4 *)(iVar5 * 0x30 + iVar2 + 0x14) = 0;
        *(undefined4 *)(iVar5 * 0x30 + iVar2 + 0x18) = 0;
        *(undefined1 *)(iVar5 * 0x30 + iVar2 + 0x29) = 0;
      }
      *piVar1 = 0;
      if (*(int *)(DAT_0050aaf8 + *DAT_0050aaf4 * 8 + 4) != 0) {
        FUN_0044d878(*(undefined4 *)(DAT_0050aaf8 + *DAT_0050aaf4 * 8 + 4));
      }
      FUN_0050a094();
      iVar5 = ui_onboarding_main_sub_004A9DE8();
    }
    else if (param_1 == 'D') {
      iVar5 = FUN_0050b744(1,iVar5,param_2 & 0xffff,param_4,param_2,param_3,param_4);
    }
    else if (param_1 == 'E') {
      iVar5 = FUN_0050b744(0xffffffff,iVar5,param_2 & 0xffff,param_4,param_2,param_3,param_4);
    }
    else if (param_1 != 'F') {
      if (param_1 == 'H') {
        for (iVar5 = 0; iVar2 = DAT_0050b14c, iVar5 < 4; iVar5 = iVar5 + 1) {
          if ((*(int *)(iVar5 * 0x30 + DAT_0050b14c + 4) != 0) &&
             (iVar6 = FUN_0043e2ea(*(undefined4 *)(iVar5 * 0x30 + DAT_0050b14c + 4)), iVar6 != 0)) {
            FUN_00450500(*(undefined4 *)(iVar2 + iVar5 * 0x30 + 4),DAT_0050b150);
          }
        }
        FUN_00450500(DAT_0050b14c,DAT_0050b154);
        *DAT_0050b158 = 0;
        *DAT_0050b15c = 0;
        *DAT_0050af9c = 0;
        piVar3 = DAT_0050b160;
        if (*DAT_0050b160 != 0) {
          ui_common_api_fn_00509c96(*DAT_0050b160);
          *piVar3 = 0;
        }
        puVar4 = DAT_0050b164;
        iVar5 = FUN_0044ddea(*DAT_0050b164);
        while (iVar5 = iVar5 + -1, -1 < iVar5) {
          iVar6 = FUN_0044dce2(*puVar4,iVar5);
          if (iVar6 != 0) {
            FUN_0044d7b8();
          }
        }
        for (iVar5 = 0; iVar5 < 4; iVar5 = iVar5 + 1) {
          *(undefined4 *)(iVar2 + iVar5 * 0x30) = 0;
          *(undefined4 *)(iVar5 * 0x30 + iVar2 + 4) = 0;
          *(undefined4 *)(iVar5 * 0x30 + iVar2 + 8) = 0;
          *(undefined4 *)(iVar5 * 0x30 + iVar2 + 0xc) = 0;
          *(undefined4 *)(iVar5 * 0x30 + iVar2 + 0x10) = 0;
          *(undefined4 *)(iVar5 * 0x30 + iVar2 + 0x14) = 0;
          *(undefined4 *)(iVar5 * 0x30 + iVar2 + 0x18) = 0;
          *(undefined1 *)(iVar5 * 0x30 + iVar2 + 0x29) = 0;
        }
        *piVar1 = 0;
        if (*(int *)(DAT_0050aaf8 + *DAT_0050aaf4 * 8 + 4) != 0) {
          FUN_0044d878(*(undefined4 *)(DAT_0050aaf8 + *DAT_0050aaf4 * 8 + 4));
        }
        FUN_0050a094();
        iVar5 = ui_onboarding_main_sub_004A9DE8();
      }
      else if (param_1 == 'I') {
        for (iVar5 = 0; iVar2 = DAT_0050b14c, iVar5 < 4; iVar5 = iVar5 + 1) {
          if ((*(int *)(iVar5 * 0x30 + DAT_0050b14c + 4) != 0) &&
             (iVar6 = FUN_0043e2ea(*(undefined4 *)(iVar5 * 0x30 + DAT_0050b14c + 4)), iVar6 != 0)) {
            FUN_00450500(*(undefined4 *)(iVar2 + iVar5 * 0x30 + 4),DAT_0050b150);
          }
        }
        FUN_00450500(DAT_0050b14c,DAT_0050b154);
        *DAT_0050b158 = 0;
        *DAT_0050b15c = 0;
        *DAT_0050af9c = 0;
        ui_onboarding_main_sub_004A96DC(1);
        iVar5 = 0;
        *piVar1 = 0;
      }
    }
  }
  return CONCAT44(param_2,iVar5);
}

