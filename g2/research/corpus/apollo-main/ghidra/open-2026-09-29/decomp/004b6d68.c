
undefined4
dmConnSetConnSpec(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  
  WsfTaskLock();
  bVar1 = DmInitPhyToIdx(param_1);
  FUN_00439be4((uint)bVar1 * 0xc + DAT_004b7430 + 0xa4,param_2,0xc);
  WsfTaskUnlock();
  return param_4;
}

