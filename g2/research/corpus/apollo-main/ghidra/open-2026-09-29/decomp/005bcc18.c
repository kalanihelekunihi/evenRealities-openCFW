
undefined8
am_devices_hongshi_QSPI_PartialReflash
          (int param_1,int param_2,uint param_3,int param_4,int param_5,int param_6)

{
  undefined1 uVar1;
  undefined1 uVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  uint uVar6;
  
  if (*DAT_005bd304 == 0) {
    iVar3 = FUN_0043d0ce();
    uVar6 = param_3;
    if (iVar3 << 0x1e < 0) {
      uVar6 = 0x30b;
      FUN_0043d574(1,DAT_005bd2f4,DAT_005bd2f0,DAT_005bd310,0x30b,DAT_005bd30c);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005bd314,DAT_005bd314);
    }
    uVar4 = 0xffffffff;
  }
  else {
    if (0x27f < param_5) {
      param_5 = 0x27f;
    }
    uVar6 = param_3;
    if (0x1df < param_6) {
      param_6 = 0x1df;
    }
    for (; param_4 <= param_6; param_4 = param_4 + 1) {
      iVar5 = (param_4 * 0x280) / 2 + *DAT_005bd318 + (int)param_3 / 2;
      uVar6 = DAT_005bd31c & (param_4 + param_2) * 0x400;
      iVar3 = param_5 / 2 - (int)param_3 / 2;
      if (param_5 << 0x1f < 0) {
        iVar3 = iVar3 + 1;
      }
      uVar2 = *(undefined1 *)(iVar5 + iVar3);
      *(undefined1 *)(iVar5 + iVar3) = 0;
      uVar1 = *(undefined1 *)(iVar5 + iVar3 + 1);
      *(undefined1 *)(iVar5 + iVar3 + 1) = 0;
      *(undefined1 *)(iVar5 + iVar3) = uVar2;
      *(undefined1 *)(iVar5 + iVar3 + 1) = uVar1;
      uVar6 = param_3 + param_1 & 0x3ff | uVar6;
    }
    FUN_004910f4(1);
    uVar4 = 0;
  }
  return CONCAT44(uVar6,uVar4);
}

