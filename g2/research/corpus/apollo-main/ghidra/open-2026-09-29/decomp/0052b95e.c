
void WsfTaskSetReady(undefined4 param_1,byte param_2)

{
  WsfCsEnter();
  *(byte *)(DAT_0052bac4 + 0x3c) = param_2 | *(byte *)(DAT_0052bac4 + 0x3c);
  WsfCsExit();
  WsfSetOsSpecificEvent();
  return;
}

