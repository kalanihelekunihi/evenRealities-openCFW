
longlong am_freertos_sleep(void)

{
  int iVar1;
  uint unaff_r7;
  
  FUN_004b29f8();
  iVar1 = task_vote_blocks_deep_sleep();
  if (iVar1 == 0) {
    FUN_0044ab42(1);
  }
  else {
    FUN_0044ab42(0);
  }
  return (ulonglong)unaff_r7 << 0x20;
}

