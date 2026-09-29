
longlong FUN_0041ca5c(void)

{
  bool bVar1;
  uint *puVar2;
  uint uVar3;
  
  uVar3 = critical_save();
  if (0x21 < (*DAT_0041cb04 & 0xff)) {
    *DAT_0041cb94 = *DAT_0041cb94 & 0xffdfffff;
    delay_us(1);
  }
  puVar2 = DAT_0041cc00;
  *DAT_0041cc00 = *DAT_0041cc00 & 0x7fffffff;
  *puVar2 = *puVar2 & 0xbfffffff;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar3 & 1) == 1);
  }
  delay_us(5);
  return (ulonglong)uVar3 << 0x20;
}

