
void threadBleMsgTxDeinit(void)

{
  int iVar1;
  
  iVar1 = DAT_00475d70;
  if (*(int *)(DAT_00475d70 + 8) != 0) {
    osThreadTerminate(*(undefined4 *)(DAT_00475d70 + 8));
    *(undefined4 *)(iVar1 + 8) = 0;
  }
  return;
}

