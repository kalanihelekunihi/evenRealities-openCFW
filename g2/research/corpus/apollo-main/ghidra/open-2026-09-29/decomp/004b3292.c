
void DmAdvSetInterval(uint param_1,undefined2 param_2,undefined2 param_3)

{
  int iVar1;
  
  WsfTaskLock();
  iVar1 = DAT_004b32cc;
  *(undefined2 *)(DAT_004b32cc + (param_1 & 0xff) * 2 + 0x10) = param_2;
  *(undefined2 *)(iVar1 + (param_1 & 0xff) * 2 + 0x14) = param_3;
  WsfTaskUnlock();
  return;
}

