
void threadBleMsgRxDeinit(void)

{
  int iVar1;
  
  iVar1 = DAT_0048f324;
  if (*(int *)(DAT_0048f324 + 8) != 0) {
    osThreadTerminate(*(undefined4 *)(DAT_0048f324 + 8));
    *(undefined4 *)(iVar1 + 8) = 0;
  }
  return;
}

