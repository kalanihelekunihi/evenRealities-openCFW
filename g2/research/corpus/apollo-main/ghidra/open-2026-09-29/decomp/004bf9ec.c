
int WsfMsgDeq(undefined4 param_1,undefined1 *param_2)

{
  int iVar1;
  
  iVar1 = WsfQueueDeq();
  if (iVar1 != 0) {
    *param_2 = *(undefined1 *)(iVar1 + 4);
    iVar1 = iVar1 + 8;
  }
  return iVar1;
}

