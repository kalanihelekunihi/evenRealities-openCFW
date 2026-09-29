
uint task_vote_find_free_slot(void)

{
  uint uVar1;
  
  uVar1 = 0;
  while( true ) {
    if (0x1f < uVar1) {
      return 0xffffffff;
    }
    if (*(int *)(DAT_0046d878 + uVar1 * 8) == 0) break;
    uVar1 = uVar1 + 1;
  }
  return uVar1;
}

