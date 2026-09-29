
undefined4
attcCtrlCback(undefined2 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  
  iVar1 = attcCcbByConnId((char)*param_1,0);
  if (iVar1 != 0) {
    AttcIndConfirm((char)*param_1);
    attcWriteCmdCallback((char)*param_1,iVar1,0);
  }
  return param_4;
}

