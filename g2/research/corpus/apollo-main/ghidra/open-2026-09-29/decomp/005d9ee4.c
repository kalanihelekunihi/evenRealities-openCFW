
longlong nvdbAdvMagicLoadAndMigrate(void)

{
  int iVar1;
  uint unaff_r7;
  
  iVar1 = SVC_NvdbRead(DAT_005d9f44,&stack0xfffffff8,4);
  if (iVar1 < 1) {
    nvdbAdvMagicUpdate(*(undefined1 *)(DAT_005d9f40 + 1));
  }
  else if (((short)(unaff_r7 >> 0x10) != *(short *)(DAT_005d9f40 + 2)) && ((char)unaff_r7 == '\0'))
  {
    nvdbAdvMagicUpdate(*(undefined1 *)(DAT_005d9f40 + 1));
  }
  return (ulonglong)unaff_r7 << 0x20;
}

