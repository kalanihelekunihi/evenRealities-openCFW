
void sflash_trim_load(void)

{
  *(uint *)(DAT_0000a3a8 + 4) = (uint)*(ushort *)(DAT_0000a3a4 + 0x152);
  *(uint *)(DAT_0000a3ac + 0x10) = *(uint *)(DAT_0000a3ac + 0x10) | 4;
  WaitForInterrupt();
  return;
}

