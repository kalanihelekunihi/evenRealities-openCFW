
void threadBleWsfDeinit(void)

{
  int iVar1;
  
  func_0x004abcbc();
  iVar1 = DAT_004d0cdc;
  if (*(int *)(DAT_004d0cdc + 8) != 0) {
    osThreadTerminate(*(undefined4 *)(DAT_004d0cdc + 8));
    *(undefined4 *)(iVar1 + 8) = 0;
  }
  return;
}

