
undefined4 DmConnRegister(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  WsfTaskLock();
  *(undefined4 *)(DAT_004b7430 + (param_1 & 0xff) * 4 + 0x90) = param_2;
  WsfTaskUnlock();
  return param_4;
}

