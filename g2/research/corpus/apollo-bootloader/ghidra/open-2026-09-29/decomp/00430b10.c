
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4
word_transfer_critical_430b10(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  bool bVar1;
  uint uVar2;
  
  uVar2 = critical_save(param_1);
  alignment_dispatch_42e4f4(_DAT_00430b3c,param_2,param_1,param_3 + 3U >> 2);
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar2 & 1) == 1);
  }
  return param_4;
}

