
void thread_ring_terminate(void)

{
  int iVar1;
  
  iVar1 = DAT_004c5648;
  if (*(int *)(DAT_004c5648 + 8) != 0) {
    osThreadTerminate(*(undefined4 *)(DAT_004c5648 + 8));
    *(undefined4 *)(iVar1 + 8) = 0;
  }
  return;
}

