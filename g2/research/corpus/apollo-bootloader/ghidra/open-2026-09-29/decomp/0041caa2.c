
longlong FUN_0041caa2(void)

{
  bool bVar1;
  uint *puVar2;
  uint uVar3;
  
  uVar3 = critical_save();
  puVar2 = DAT_0041cc00;
  *DAT_0041cc00 = *DAT_0041cc00 | 0x80000000;
  *puVar2 = *puVar2 | 0x40000000;
  if (0x21 < (*DAT_0041cb04 & 0xff)) {
    delay_us(1);
    *DAT_0041cb94 = *DAT_0041cb94 | 0x200000;
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar3 & 1) == 1);
  }
  return (ulonglong)uVar3 << 0x20;
}

