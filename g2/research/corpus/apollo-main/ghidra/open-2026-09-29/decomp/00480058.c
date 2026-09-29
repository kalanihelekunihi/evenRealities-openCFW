
longlong FUN_00480058(void)

{
  bool bVar1;
  uint *puVar2;
  uint uVar3;
  
  uVar3 = FUN_00473940();
  if (0x21 < (*DAT_00480100 & 0xff)) {
    *DAT_00480190 = *DAT_00480190 & 0xffdfffff;
    FUN_004807a0(1);
  }
  puVar2 = DAT_004801f8;
  *DAT_004801f8 = *DAT_004801f8 & 0x7fffffff;
  *puVar2 = *puVar2 & 0xbfffffff;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar3 & 1) == 1);
  }
  FUN_004807a0(5);
  return (ulonglong)uVar3 << 0x20;
}

