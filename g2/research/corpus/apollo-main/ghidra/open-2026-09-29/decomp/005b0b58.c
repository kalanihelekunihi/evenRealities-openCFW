
int FUN_005b0b58(void)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar1 = DAT_005b15d8;
  if (*(int *)(DAT_005b15d8 + 0x80) == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      FUN_0043d574(1,DAT_005b15d0,DAT_005b15cc,DAT_005b16cc,0x41,DAT_005b15dc);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_005b16d8,DAT_005b16d8);
    }
    iVar2 = -2;
  }
  else {
    iVar3 = FUN_0044e498(*(undefined4 *)(DAT_005b15d8 + 100));
    iVar2 = *(int *)(iVar1 + 0x84) - iVar3 / 0x28;
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      FUN_0043d574(4,DAT_005b15d0,DAT_005b15cc,DAT_005b16cc,0x48,DAT_005b16f8,
                   *(undefined4 *)(iVar1 + 0x84),iVar2);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0x10800000,DAT_005b171c,DAT_005b171c,*(undefined4 *)(iVar1 + 0x84),iVar2);
    }
  }
  return iVar2;
}

