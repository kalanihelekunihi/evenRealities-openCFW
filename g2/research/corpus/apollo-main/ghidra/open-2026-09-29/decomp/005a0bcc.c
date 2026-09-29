
uint FUN_005a0bcc(void)

{
  bool bVar1;
  char *pcVar2;
  uint *puVar3;
  uint uVar4;
  
  uVar4 = FUN_00473940();
  FUN_005a0b9c();
  puVar3 = DAT_005a1700;
  pcVar2 = DAT_005a16f8;
  if (*DAT_005a16f8 != '\0') {
    if ((*DAT_005a16fc != 8) && (*DAT_005a16fc != 0xc)) {
      *DAT_005a1700 = *DAT_005a1700 | 8;
      *puVar3 = *puVar3 | 0x40;
    }
    *pcVar2 = '\0';
  }
  FUN_004802ce();
  FUN_005a0b54(1);
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar4 & 1) == 1);
  }
  return uVar4;
}

