
longlong FUN_0046607c(undefined4 param_1,uint param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  iVar2 = DAT_004667f0;
  iVar1 = DAT_004667ec;
  iVar3 = *(int *)(DAT_004667f0 + 0x14);
  if (*(short *)(iVar3 + 0x12) != *(short *)(DAT_004667ec + 0x12)) {
    SVC_KvdbWriteUniversalSetting(DAT_004667ec);
    FUN_00439be4(iVar1,iVar3,0x14);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x4e;
      FUN_0043d574(3,DAT_00466800,DAT_004667fc,DAT_004667f8,0x4e,DAT_004667f4);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_00466804,DAT_00466804);
    }
  }
  iVar3 = *(int *)(iVar2 + 0xc);
  if (*(short *)(iVar3 + 8) != *(short *)(iVar1 + 0x1c)) {
    SVC_KvdbWriteTimeFormat(iVar1 + 0x14);
    FUN_00439be4(iVar1 + 0x14,iVar3,0xc);
    iVar3 = FUN_0043d0ce();
    if (iVar3 << 0x1e < 0) {
      param_2 = 0x56;
      FUN_0043d574(3,DAT_00466800,DAT_004667fc,DAT_004667f8,0x56,DAT_00466808);
    }
    iVar3 = FUN_0043d0ce();
    if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_0046680c,DAT_0046680c);
    }
  }
  iVar2 = *(int *)(iVar2 + 0x10);
  if (*(short *)(iVar2 + 8) != *(short *)(iVar1 + 0x28)) {
    SVC_KvdbWriteTemperatureUnit(iVar1 + 0x20);
    FUN_00439be4(iVar1 + 0x20,iVar2,0xc);
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = 0x5e;
      FUN_0043d574(3,DAT_00466800,DAT_004667fc,DAT_004667f8,0x5e,DAT_00466810);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0xc000000,DAT_00466814,DAT_00466814);
    }
  }
  return (ulonglong)param_2 << 0x20;
}

