
undefined4 FUN_0045d302(void)

{
  undefined4 unaff_r7;
  
  if (*DAT_0045dd38 != 0) {
    osSemaphoreRelease(*DAT_0045dd38);
    osEventFlagsSet(*DAT_0045df14,4);
  }
  return unaff_r7;
}

