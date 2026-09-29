
undefined4 smpiActSendKey(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  if ((*(char *)(param_1 + 0x3f) == '\0') &&
     (iVar1 = smpSendKey(param_1,*(byte *)(param_1 + 0x2c) & *(byte *)(param_1 + 0x25)), iVar1 != 0)
     ) {
    *(undefined1 *)(param_2 + 2) = 0xe;
    smpSmExecute(param_1,param_2);
  }
  return param_4;
}

