
void dmConnUpdMsgHandler(undefined2 *param_1)

{
  int iVar1;
  
  iVar1 = dmConnCcbById((char)*param_1);
  if ((iVar1 != 0) && (*(char *)(iVar1 + 0x15) == '\x03')) {
    dmConnUpdExecute(iVar1,param_1);
  }
  return;
}

