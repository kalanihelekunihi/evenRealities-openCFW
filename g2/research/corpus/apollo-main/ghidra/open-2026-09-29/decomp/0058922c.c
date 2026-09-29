
undefined8 FUN_0058922c(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int *piVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  
  iVar3 = FUN_0045a568();
  if (iVar3 == 1) {
    iVar3 = osKernelGetTickCount();
    if ((*DAT_00589370 != '\0') && (-1 < iVar3 - *DAT_00589374)) {
      *DAT_00589370 = '\0';
      *DAT_0058936c = '\x01';
      iVar1 = DAT_00589350;
      uVar4 = service_time_rtc_refresh();
      *(undefined4 *)(iVar1 + 0x24) = uVar4;
      iVar5 = FUN_0043d0ce();
      if (iVar5 << 0x1e < 0) {
        param_1 = 0x138;
        param_2 = DAT_005893e0;
        FUN_0043d574(3,DAT_00589364,DAT_00589360,DAT_005893e4,0x138,DAT_005893e0,
                     *(undefined4 *)(iVar1 + 0x24),param_4);
      }
      iVar5 = FUN_0043d0ce();
      if ((iVar5 << 0x1f < 0) || (iVar5 = FUN_0043d0ce(), iVar5 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_005893e8,DAT_005893e8,*(undefined4 *)(iVar1 + 0x24));
      }
      FUN_00588f1a(2);
    }
    piVar2 = DAT_00589394;
    iVar1 = DAT_00589354;
    if (((((*DAT_00589384 != '\0') && (*(char *)(DAT_00589350 + 0x20) == '\x02')) &&
         (*(char *)(DAT_00589354 + 4) == '\x02')) &&
        ((*(int *)(DAT_00589354 + 0x1c) != 0 && (*DAT_0058936c == '\x01')))) &&
       (-1 < iVar3 - *DAT_00589394)) {
      if (((*(int *)(DAT_00589350 + 0x40) == 0) && (*(char *)(DAT_00589350 + 0x21) == '\0')) &&
         (*(char *)(DAT_00589354 + 0x2c) != '\x02')) {
        uVar4 = FUN_005548c4(*(undefined4 *)(DAT_00589350 + 0x18),0x1c,0);
        FUN_00589b68(0xd,uVar4);
      }
      *piVar2 = *(int *)(iVar1 + 0x1c) + iVar3;
    }
  }
  return CONCAT44(param_2,param_1);
}

