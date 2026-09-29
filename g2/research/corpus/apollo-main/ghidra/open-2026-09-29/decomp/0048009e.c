
longlong FUN_0048009e(void)

{
  bool bVar1;
  uint *puVar2;
  uint uVar3;
  
  uVar3 = FUN_00473940();
  puVar2 = DAT_004801f8;
  *DAT_004801f8 = *DAT_004801f8 | 0x80000000;
  *puVar2 = *puVar2 | 0x40000000;
  if (0x21 < (*DAT_00480100 & 0xff)) {
    FUN_004807a0(1);
    *DAT_00480190 = *DAT_00480190 | 0x200000;
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar3 & 1) == 1);
  }
  return (ulonglong)uVar3 << 0x20;
}

