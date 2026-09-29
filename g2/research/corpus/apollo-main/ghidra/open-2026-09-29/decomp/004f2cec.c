
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_004f2cec(void)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  undefined1 auStack_18 [8];
  undefined1 auStack_10 [8];
  
  piVar2 = DAT_004f33dc;
  piVar1 = DAT_004f33b4;
  if (*DAT_004f33c0 == 0) {
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004f2eb4,DAT_004f2eb0,PTR_s_NewsWidget_AutoReflash_004f33c8,0x62e,
                   PTR_s_widget_news_ext_init_flag____0__r_004f33c4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x8000000,PTR_s__dashborad_news_widget_widget_ne_004f33cc,
                          PTR_s__dashborad_news_widget_widget_ne_004f33cc);
    }
  }
  else if ((*DAT_004f33d0 == 0) || (*DAT_004f33c0 != 1)) {
    if ((*DAT_004f33c0 == 1) &&
       (((*DAT_004f33bc == 1 && (0 < *DAT_004f33dc)) &&
        (*DAT_004f33dc = *DAT_004f33dc + -1, *piVar2 == 0)))) {
      FUN_0043c0e4(auStack_18,5,0);
      FUN_0043c0e4(auStack_18,5,0);
      auStack_18[0] = 0xe;
      iVar3 = FUN_0045a568();
      if (iVar3 == 1) {
        FUN_00464bb2(1,auStack_18,5,0);
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004f2eb4,DAT_004f2eb0,PTR_s_NewsWidget_AutoReflash_004f33c8,0x64c,
                       _DAT_004f33d4);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0xc000000,_DAT_004f33d8,_DAT_004f33d8);
        }
      }
    }
  }
  else {
    if (*DAT_004f33b4 == 1) {
      FUN_00463f34(*DAT_004f33d0);
    }
    piVar2 = DAT_004f33b8;
    if (((0 < *DAT_004f33b8) && (*piVar1 == 1)) &&
       (*DAT_004f33b8 = *DAT_004f33b8 + -1, *piVar2 == 0)) {
      FUN_0043c0e4(auStack_10,5,0);
      FUN_0043c0e4(auStack_10,5,0);
      auStack_10[0] = 0xc;
      iVar3 = FUN_0045a568();
      if (iVar3 == 1) {
        FUN_00464bb2(1,auStack_10,5,0);
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(3,DAT_004f2eb4,DAT_004f2eb0,PTR_s_NewsWidget_AutoReflash_004f33c8,0x63f,
                       _DAT_004f33d4);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0xc000000,_DAT_004f33d8,_DAT_004f33d8);
        }
      }
    }
  }
  return 0;
}

