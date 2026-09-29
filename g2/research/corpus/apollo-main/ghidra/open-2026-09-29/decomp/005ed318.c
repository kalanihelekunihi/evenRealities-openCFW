
undefined4 FUN_005ed318(char param_1,uint param_2)

{
  short sVar1;
  int iVar2;
  uint uVar3;
  
  uVar3 = param_2 >> 0x1e & 1;
  if (uVar3 == 0) {
    sVar1 = FUN_005ecaac();
  }
  else {
    sVar1 = *(short *)(DAT_005ed744 + 0x27a);
  }
  if ((int)param_2 < 0) {
    FUN_005ec268();
    FUN_005ebbc6();
    FUN_005ec770();
    FUN_005ec9c0();
    iVar2 = DAT_005ed744;
    *(undefined1 *)(DAT_005ed744 + 0x280) = 0;
    *(undefined4 *)(iVar2 + 0x284) = 0;
    FUN_005eae2c(4);
    if ((param_1 == '\x02') || (param_1 == '\f')) {
      FUN_005e57c6(param_1,0);
    }
  }
  if ((param_1 == '\v') && (*(char *)(DAT_005ed744 + 0x27d) != '\0')) {
    *(short *)(DAT_005ed744 + 0x27a) = sVar1;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_terminal_ui_005ed9dc,DAT_005ed9d8,DAT_005ed9f0,0x1ea,DAT_005ed9ec,
                   (int)sVar1,param_2 >> 0x1f,uVar3);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xcc00000,DAT_005ed9f4,DAT_005ed9f4,(int)sVar1,param_2 >> 0x1f,uVar3);
    }
  }
  else {
    if (param_1 == '\v') {
      FUN_005ecef6((int)sVar1);
    }
    else {
      *(short *)(DAT_005ed744 + 0x27a) = sVar1;
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(3,PTR_s_terminal_ui_005ed9dc,DAT_005ed9d8,DAT_005ed9f0,499,DAT_005ed9f8,param_1,
                   (int)sVar1,param_2 >> 0x1f,uVar3);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xd000000,DAT_005ed9fc,DAT_005ed9fc,param_1,(int)sVar1,param_2 >> 0x1f,
                          uVar3);
    }
  }
  return 0;
}

