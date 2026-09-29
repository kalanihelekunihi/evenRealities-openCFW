
undefined4 ui_onboarding_stock_sub_0050D578(char *param_1,int param_2)

{
  int *piVar1;
  int *piVar2;
  int *piVar3;
  undefined4 *puVar4;
  int iVar5;
  undefined4 uVar6;
  int iVar7;
  char local_1c;
  char local_1b;
  char local_1a;
  
  piVar3 = DAT_0050dc64;
  if (*DAT_0050dc64 == 0) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(2,DAT_0050dc5c,DAT_0050dc58,DAT_0050dc74,0x461,DAT_0050dc70);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0050dc78);
    }
    uVar6 = 0;
  }
  else if ((param_1 == (char *)0x0) || (param_2 == 0)) {
    iVar5 = FUN_0043d0ce();
    if (iVar5 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0050dc5c,DAT_0050dc58,DAT_0050dc74,0x466,DAT_0050dc7c);
    }
    iVar5 = FUN_0043d0ce();
    if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0050dc80,DAT_0050dc80);
    }
    uVar6 = 0xffffffff;
  }
  else {
    if (*param_1 == '\0') {
      iVar5 = ui_onboarding_main_sub_004A979C(param_1,1,&local_1c);
      puVar4 = DAT_0050dc9c;
      piVar1 = DAT_0050db30;
      if (iVar5 != 0) {
        return 0xffffffff;
      }
      if ((*DAT_0050db30 != 0) || (*(char *)(DAT_0050db2c + 0x124) != '\0')) {
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(3,DAT_0050dc5c,DAT_0050dc58,DAT_0050dc74,0x479,DAT_0050dc84,*piVar1,
                       *(undefined1 *)(DAT_0050db2c + 0x124),local_1c);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0xcc00000,DAT_0050dc88,DAT_0050dc88,*piVar1,
                              *(undefined1 *)(DAT_0050db2c + 0x124),local_1c);
        }
        if ((local_1c != 'D') && (local_1c != 'E')) {
          if (*DAT_0050dc60 != 0) {
            ui_common_api_fn_00509ca2(*DAT_0050dc60,param_1 + 1,7);
            iVar5 = FUN_0043d0ce();
            if (iVar5 << 0x1e < 0) {
              FUN_0043d574(3,DAT_0050dc5c,DAT_0050dc58,DAT_0050dc74,0x485,DAT_0050dc94,local_1c);
            }
            iVar5 = FUN_0043d0ce();
            if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
              compress_log_output(0xc400000,DAT_0050dc98,DAT_0050dc98,local_1c);
            }
          }
          return 0;
        }
        iVar5 = FUN_0043d0ce();
        if (iVar5 << 0x1e < 0) {
          FUN_0043d574(3,DAT_0050dc5c,DAT_0050dc58,DAT_0050dc74,0x47e,DAT_0050dc8c,local_1c);
        }
        iVar5 = FUN_0043d0ce();
        if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
          compress_log_output(0xc400000,DAT_0050dc90,DAT_0050dc90,local_1c);
        }
        return 0;
      }
      if (((local_1b == '\x02') && (local_1a == '\x06')) && (local_1c == 'H')) {
        osMutexAcquire(*DAT_0050dc9c,0xffffffff);
        *(undefined1 *)(DAT_0050dca0 + 1) = 7;
        osMutexRelease(*puVar4);
        ui_onboarding_main_sub_004A9EDC();
        puVar4 = DAT_0050dc68;
        iVar5 = FUN_0044ddea(*DAT_0050dc68);
        while (piVar2 = DAT_0050dc60, iVar5 = iVar5 + -1, -1 < iVar5) {
          iVar7 = FUN_0044dce2(*puVar4,iVar5);
          if (iVar7 != 0) {
            FUN_0044d7b8();
          }
        }
        if (*DAT_0050dc60 != 0) {
          ui_common_api_fn_00509c96(*DAT_0050dc60);
          *piVar2 = 0;
        }
        *piVar3 = 0;
        *piVar1 = 0;
        ui_onboarding_main_sub_004A9DE8();
      }
    }
    else if (*param_1 == '\x01') {
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        FUN_0043d574(3,DAT_0050dc5c,DAT_0050dc58,DAT_0050dc74,0x50f,DAT_0050dca4);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_0050e45c,DAT_0050e45c);
      }
    }
    uVar6 = 0;
  }
  return uVar6;
}

