
undefined4 FUN_00536470(int param_1,int param_2,undefined1 param_3,undefined4 param_4)

{
  *(int *)(param_1 + 4) = param_1 + 0x10;
  FUN_00542a44(*(undefined4 *)(param_1 + 4),param_2 + 5);
  WsfMsgSend(param_3,param_1);
  return param_4;
}

