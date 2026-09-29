
undefined4 task_vote_acquire_current(void)

{
  int iVar1;
  undefined4 unaff_r7;
  
  iVar1 = osThreadGetId();
  if (iVar1 != 0) {
    task_vote_acquire_for_handle();
  }
  return unaff_r7;
}

