
undefined2 DmConnCheckIdle(uint param_1)

{
  undefined2 uVar1;
  
  WsfTaskLock();
  uVar1 = *(undefined2 *)(DAT_004b7430 + (param_1 & 0xff) * 0x30 + -0x22);
  WsfTaskUnlock();
  return uVar1;
}

