
void HAL_PWR_EnterSTANDBYMode(void)

{
  *DAT_080050e0 = (*DAT_080050e0 & 0xfffffff8) + 3;
  *(uint *)(DAT_080050e4 + 0x10) = *(uint *)(DAT_080050e4 + 0x10) | 4;
  WaitForInterrupt();
  return;
}

