
void DmAdvSetAddrType(undefined1 param_1)

{
  WsfTaskLock();
  *(undefined1 *)(DAT_004b32d0 + 0xe) = param_1;
  WsfTaskUnlock();
  return;
}

