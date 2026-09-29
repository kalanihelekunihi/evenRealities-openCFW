
undefined4 WsfMsgEnq(undefined4 param_1,undefined1 param_2,int param_3)

{
  undefined4 unaff_r7;
  
  *(undefined1 *)(param_3 + -4) = param_2;
  WsfQueueEnq(param_1,param_3 + -8);
  return unaff_r7;
}

