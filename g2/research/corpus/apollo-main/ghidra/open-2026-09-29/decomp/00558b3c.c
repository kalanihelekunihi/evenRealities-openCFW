
int APP_DecodePbRxQuicklistData(void)

{
  byte bVar1;
  byte *pbVar2;
  int iVar3;
  int iVar4;
  
  pbVar2 = DAT_005591a4;
  iVar4 = 3;
  bVar1 = *DAT_005591a4;
  if (bVar1 == 1) {
    iVar4 = FUN_0058d51c(DAT_005591a4 + 8);
    if (iVar4 != 0) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00559194,DAT_0055936c,DAT_00559440,0x6d,DAT_0055943c,iVar4);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00559444,DAT_00559444,iVar4);
      }
    }
  }
  else if (bVar1 != 0) {
    if (bVar1 == 3) {
      iVar4 = 0;
      if (DAT_005591a4[8] - 1 < 2) {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(4,DAT_00559194,DAT_0055936c,DAT_00559440,0x83,DAT_00559450,pbVar2[8],
                       *(undefined4 *)(pbVar2 + 0xc));
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x10800000,DAT_00559454,DAT_00559454,pbVar2[8],
                              *(undefined4 *)(pbVar2 + 0xc));
        }
      }
      else {
        iVar3 = FUN_0043d0ce();
        if (iVar3 << 0x1e < 0) {
          FUN_0043d574(2,DAT_00559194,DAT_0055936c,DAT_00559440,0x87,DAT_00559458,pbVar2[8]);
        }
        iVar3 = FUN_0043d0ce();
        if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
          compress_log_output(0x8400000,DAT_005595e0,DAT_005595e0,pbVar2[8]);
        }
      }
    }
    else if ((bVar1 < 3) && (iVar4 = FUN_0058d668(DAT_005591a4 + 8), iVar4 != 0)) {
      iVar3 = FUN_0043d0ce();
      if (iVar3 << 0x1e < 0) {
        FUN_0043d574(1,DAT_00559194,DAT_0055936c,DAT_00559440,0x77,DAT_00559448,iVar4);
      }
      iVar3 = FUN_0043d0ce();
      if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_0055944c,DAT_0055944c,iVar4);
      }
    }
  }
  return iVar4;
}

