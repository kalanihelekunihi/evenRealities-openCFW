
longlong FUN_0050aafc(char *param_1,int param_2,uint param_3,undefined4 param_4)

{
  char cVar1;
  undefined4 *puVar2;
  undefined4 uVar3;
  int iVar4;
  undefined4 local_18;
  undefined4 local_14;
  
  local_18 = param_3;
  local_14 = param_4;
  if (*DAT_0050b044 == 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      local_14 = DAT_0050b048;
      local_18 = 0x26f;
      FUN_0043d574(2,DAT_0050ac28,DAT_0050ac24,DAT_0050b1b8);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0050b050);
    }
  }
  else if (param_2 == 0) {
    iVar4 = FUN_0043d0ce();
    if (iVar4 << 0x1e < 0) {
      local_14 = DAT_0050b428;
      local_18 = 0x274;
      FUN_0043d574(2,DAT_0050ac28,DAT_0050ac24,DAT_0050b1b8);
    }
    iVar4 = FUN_0043d0ce();
    if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0050b42c);
    }
  }
  else {
    cVar1 = *param_1;
    if (cVar1 == '\0') {
      iVar4 = ui_onboarding_main_sub_004A979C(param_1,1,&local_18);
      uVar3 = local_14;
      puVar2 = DAT_0050b5d4;
      if (iVar4 == 0) {
        if (((local_18._1_1_ == '\x02') && (local_18._2_1_ == '\x06')) && ((char)local_18 == 'H')) {
          osMutexAcquire(*DAT_0050b5d4,0xffffffff);
          *(undefined1 *)(DAT_0050b040 + 1) = 7;
          osMutexRelease(*puVar2);
          ui_onboarding_main_sub_004A9EDC();
          FUN_0050a670(0x48,uVar3);
        }
      }
    }
    else if (cVar1 == '\x01') {
      ui_onboarding_main_sub_004A93B0(param_1 + 1,param_2 + -1);
    }
    else if (cVar1 == '\x03') {
      FUN_0050a094();
    }
  }
  return (ulonglong)local_18 << 0x20;
}

