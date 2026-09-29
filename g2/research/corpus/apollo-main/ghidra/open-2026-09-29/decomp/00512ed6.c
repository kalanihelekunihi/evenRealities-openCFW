
void thread_input_terminate(void)

{
  int iVar1;
  
  iVar1 = DAT_005134b4;
  if (*(int *)(DAT_005134b4 + 8) != 0) {
    osThreadTerminate(*(undefined4 *)(DAT_005134b4 + 8));
    *(undefined4 *)(iVar1 + 8) = 0;
  }
  return;
}

