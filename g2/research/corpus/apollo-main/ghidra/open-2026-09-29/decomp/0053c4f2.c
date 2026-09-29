
void aud_thread_terminate(void)

{
  int iVar1;
  
  iVar1 = DAT_0053cea4;
  if (*(int *)(DAT_0053cea4 + 8) != 0) {
    osThreadTerminate(*(undefined4 *)(DAT_0053cea4 + 8));
    *(undefined4 *)(iVar1 + 8) = 0;
  }
  return;
}

