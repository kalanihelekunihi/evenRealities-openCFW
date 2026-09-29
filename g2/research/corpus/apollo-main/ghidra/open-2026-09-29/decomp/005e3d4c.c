
undefined4 smprActRcvKey(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = smpProcRcvKey(param_1,*(undefined4 *)(param_1 + 0x30),*(undefined4 *)(param_2 + 4),
                        *(byte *)(param_1 + 0x2c) & *(byte *)(param_1 + 0x25));
  if (iVar1 != 0) {
    *(undefined1 *)(param_2 + 2) = 0xe;
    smpSmExecute(param_1,param_2);
  }
  return param_4;
}

