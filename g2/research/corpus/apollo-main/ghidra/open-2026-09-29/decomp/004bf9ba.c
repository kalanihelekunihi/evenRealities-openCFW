
undefined4 WsfMsgSend(undefined1 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  uVar1 = WsfTaskMsgQueue(param_1);
  WsfMsgEnq(uVar1,param_1,param_2);
  WsfTaskSetReady(param_1,1);
  return param_4;
}

