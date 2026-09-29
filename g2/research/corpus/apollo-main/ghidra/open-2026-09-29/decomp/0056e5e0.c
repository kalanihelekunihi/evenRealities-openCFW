
void smpCleanup(int param_1)

{
  undefined1 uVar1;
  
  if (*(int *)(param_1 + 0x30) != 0) {
    WsfBufFree(*(undefined4 *)(param_1 + 0x30));
    *(undefined4 *)(param_1 + 0x30) = 0;
  }
  WsfTimerStop(param_1);
  WsfTimerStop(param_1 + 0x10);
  *(undefined1 *)(param_1 + 0x3b) = 0;
  if (*(char *)(param_1 + 0x3a) == '\0') {
    uVar1 = 1;
  }
  else {
    uVar1 = 0xb;
  }
  *(undefined1 *)(param_1 + 0x3f) = uVar1;
  *(undefined1 *)(param_1 + 0x43) = 0;
  return;
}

