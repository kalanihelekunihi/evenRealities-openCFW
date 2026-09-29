
void dmConnMsgHandler(undefined2 *param_1)

{
  int iVar1;
  
  iVar1 = dmConnCcbById((char)*param_1);
  if (iVar1 != 0) {
    dmConnSmExecute(iVar1,param_1);
  }
  return;
}

