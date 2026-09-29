
undefined4 FUN_0047cbe8(undefined4 param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  bool bVar1;
  uint uVar2;
  
  uVar2 = FUN_00473940(param_1);
  FUN_004d0a2c(DAT_0047cc18,param_2,param_1,param_3 + 3U >> 2);
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar2 & 1) == 1);
  }
  return param_4;
}

