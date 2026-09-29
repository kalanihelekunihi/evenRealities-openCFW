
void sleep_wfi_entry(void)

{
  *(uint *)(DAT_0000a384 + 0x10) = *(uint *)(DAT_0000a384 + 0x10) & 0xfffffffb;
  WaitForInterrupt();
  return;
}

