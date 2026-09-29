
void hub_thread_terminate(void)

{
  int iVar1;
  
  iVar1 = DAT_004a6ecc;
  if (*(int *)(DAT_004a6ecc + 8) != 0) {
    osThreadTerminate(*(undefined4 *)(DAT_004a6ecc + 8));
    *(undefined4 *)(iVar1 + 8) = 0;
  }
  return;
}

