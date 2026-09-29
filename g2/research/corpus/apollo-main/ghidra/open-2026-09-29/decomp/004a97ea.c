
undefined4
ui_onboarding_main_sub_004A97EA
          (char *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  char cVar1;
  char cVar2;
  undefined4 *puVar3;
  int *piVar4;
  undefined4 uVar5;
  undefined4 local_70;
  undefined4 local_6c;
  undefined4 local_60;
  undefined4 local_50;
  undefined4 local_40;
  undefined4 uStack_10;
  
  puVar3 = DAT_004a9ed0;
  cVar1 = *param_1;
  cVar2 = param_1[2];
  uStack_10 = param_4;
  if (param_1[1] == '\x02') {
    if (cVar2 == '\0') {
      if (cVar1 == 'H') {
        osMutexAcquire(*DAT_004a9ed0,0xffffffff);
        *(undefined1 *)(DAT_004aa200 + 1) = 1;
        osMutexRelease(*puVar3);
        ui_onboarding_main_sub_004A9EDC();
      }
    }
    else if (cVar2 == '\x02') {
      if (cVar1 == 'D') {
        osMutexAcquire(*DAT_004a9ed0,0xffffffff);
        *(undefined1 *)(DAT_004aa200 + 1) = 3;
        osMutexRelease(*puVar3);
        ui_onboarding_main_sub_004A9EDC();
        ui_onboarding_main_sub_004A8B90(1);
      }
    }
    else if (cVar2 == '\x04') {
      if (cVar1 == '\n') {
        osMutexAcquire(*DAT_004a9ed0,0xffffffff);
        *(undefined1 *)(DAT_004aa200 + 1) = 5;
        osMutexRelease(*puVar3);
        ui_onboarding_main_sub_004A9EDC();
        puVar3 = DAT_004aa164;
        piVar4 = DAT_004aa03c;
        if (*DAT_004a99cc == 0) {
          if (*DAT_004aa03c != 0) {
            return 1;
          }
          FUN_0043dfa4(*DAT_004aa164,1);
          FUN_004503d6(&local_70);
          local_70 = *puVar3;
          FUN_004506ce(&local_70,0x160,0x240);
          local_40 = 0xfa;
          local_6c = DAT_004aa204;
          local_50 = DAT_004aa0c0;
          local_60 = DAT_004aa208;
          *piVar4 = 1;
          *DAT_004a99c8 = *DAT_004aa64c;
          FUN_00450408(&local_70);
        }
      }
    }
    else if (cVar2 != '\x06') {
      if (cVar2 == '\b') {
        if (cVar1 == '\b') {
          osMutexAcquire(*DAT_004a9ed0,0xffffffff);
          *(undefined1 *)(DAT_004aa200 + 1) = 9;
          osMutexRelease(*puVar3);
          ui_onboarding_main_sub_004A9EDC();
        }
      }
      else if (cVar2 == '\v') {
        if (cVar1 == 'H') {
          osMutexAcquire(*DAT_004a9ed0,0xffffffff);
          *(undefined1 *)(DAT_004aa200 + 1) = 0xc;
          osMutexRelease(*puVar3);
          ui_onboarding_main_sub_004A9EDC();
        }
      }
      else if ((cVar2 == '\r') && (cVar1 == 'H')) {
        osMutexAcquire(*DAT_004a9ed0,0xffffffff);
        *(undefined1 *)(DAT_004aa200 + 1) = 0xe;
        osMutexRelease(*puVar3);
        ui_onboarding_main_sub_004A9EDC();
      }
    }
  }
  else if ((param_1[1] == '\x03') && (cVar1 == 'K')) {
    *DAT_004aa20c = 1;
    uVar5 = osKernelGetTickCount();
    *(undefined4 *)(DAT_004aa200 + 4) = uVar5;
    ui_onboarding_main_sub_004AAB4C();
  }
  return 0;
}

