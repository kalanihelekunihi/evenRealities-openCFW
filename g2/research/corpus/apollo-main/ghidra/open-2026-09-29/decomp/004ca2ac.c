
undefined8 uled_clean_fb_data(undefined1 param_1,uint param_2,int param_3,uint param_4,int param_5)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  
  uVar5 = param_4;
  if (0x27f < (int)param_4) {
    uVar5 = 0x27f;
  }
  if (0x1df < param_5) {
    param_5 = 0x1df;
  }
  if (((int)uVar5 < (int)param_2) || (param_5 < param_3)) {
    iVar2 = FUN_0043d0ce();
    uVar6 = param_2;
    if (iVar2 << 0x1e < 0) {
      uVar6 = 0x128;
      FUN_0043d574(1,DAT_004ca674,DAT_004ca670,DAT_004ca6e4,0x128,DAT_004ca6e0);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004ca6e8,DAT_004ca6e8);
    }
    uVar3 = 0xffffffff;
  }
  else {
    uVar6 = param_2;
    if (((int)(param_2 << 0x1f) < 0) || (iVar2 = param_3, (int)uVar5 % 2 != 1)) {
      iVar2 = param_3;
      if ((param_2 & 1) == 0 && (uVar5 & 1) == 0) {
        for (; piVar1 = DAT_004ca6b0, param_3 <= param_5; param_3 = param_3 + 1) {
          iVar4 = *DAT_004ca6b0 + param_3 * 0x140;
          FUN_0043c0e4(iVar4 + (int)param_2 / 2,(int)uVar5 / 2 - (int)param_2 / 2,param_1,iVar4,
                       uVar6,iVar2,param_4);
          *(byte *)((int)uVar5 / 2 + (int)param_2 / 2 + *piVar1 + param_3 * 0x140 +
                   (int)param_2 / -2) =
               *(byte *)((int)uVar5 / 2 + (int)param_2 / 2 + *piVar1 + param_3 * 0x140 +
                        (int)param_2 / -2) & 0xf;
        }
      }
      else if (((int)param_2 % 2 == 1) && ((int)uVar5 % 2 == 1)) {
        for (; piVar1 = DAT_004ca6b0, param_3 <= param_5; param_3 = param_3 + 1) {
          iVar4 = *DAT_004ca6b0 + param_3 * 0x140;
          FUN_0043c0e4((int)param_2 / 2 + iVar4 + 1,(int)uVar5 / 2 - (int)param_2 / 2,param_1,iVar4,
                       uVar6,iVar2,param_4);
          *(byte *)(*piVar1 + param_3 * 0x140 + (int)param_2 / 2) =
               *(byte *)(*piVar1 + param_3 * 0x140 + (int)param_2 / 2) & 0xf0;
        }
      }
      else if (((int)param_2 % 2 == 1) && (-1 < (int)(uVar5 << 0x1f))) {
        for (; piVar1 = DAT_004ca6b0, param_3 <= param_5; param_3 = param_3 + 1) {
          iVar4 = *DAT_004ca6b0 + param_3 * 0x140;
          FUN_0043c0e4((int)param_2 / 2 + iVar4 + 1,((int)uVar5 / 2 - (int)param_2 / 2) + -1,param_1
                       ,iVar4,uVar6,iVar2,param_4);
          *(byte *)(*piVar1 + param_3 * 0x140 + (int)param_2 / 2) =
               *(byte *)(*piVar1 + param_3 * 0x140 + (int)param_2 / 2) & 0xf0;
          *(byte *)((int)uVar5 / 2 + (int)param_2 / 2 + *piVar1 + param_3 * 0x140 +
                   (int)param_2 / -2) =
               *(byte *)((int)uVar5 / 2 + (int)param_2 / 2 + *piVar1 + param_3 * 0x140 +
                        (int)param_2 / -2) & 0xf;
        }
      }
    }
    else {
      for (; param_3 <= param_5; param_3 = param_3 + 1) {
        iVar4 = *DAT_004ca6b0 + param_3 * 0x140;
        FUN_0043c0e4(iVar4 + (int)param_2 / 2,((int)uVar5 / 2 - (int)param_2 / 2) + 1,param_1,iVar4,
                     uVar6,iVar2,param_4);
      }
    }
    uVar3 = 0;
  }
  return CONCAT44(uVar6,uVar3);
}

