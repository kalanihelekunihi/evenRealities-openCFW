
uint dmAdvReset(void)

{
  uint unaff_r7;
  
  if ((*(char *)(DAT_004ba49c + 0x1d) == '\x05') ||
     ((*(char *)(DAT_004ba49c + 0x1d) == '\x01' && (*(char *)(DAT_004ba49c + 0x18) != '\x01')))) {
    WsfTimerStop();
    unaff_r7 = (uint)CONCAT12(0x22,(short)unaff_r7);
    (**(code **)(DAT_004ba498 + 8))(&stack0xfffffff8);
  }
  dmAdvInit();
  return unaff_r7;
}

