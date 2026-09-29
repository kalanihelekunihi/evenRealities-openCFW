
undefined4 AttcWriteCmd(undefined1 param_1,uint param_2,short param_3,undefined4 param_4)

{
  short *psVar1;
  undefined4 local_20;
  
  psVar1 = (short *)attMsgAlloc(param_3 + 0xb);
  local_20 = param_4;
  if (psVar1 != (short *)0x0) {
    *psVar1 = param_3 + 3;
    *(undefined1 *)(psVar1 + 4) = 0x52;
    *(char *)((int)psVar1 + 9) = (char)param_2;
    *(char *)(psVar1 + 5) = (char)(param_2 >> 8);
    FUN_00439be4((int)psVar1 + 0xb,param_4,param_3);
    local_20 = 0;
    attcSendMsg(param_1,param_2 & 0xffff,10,psVar1);
  }
  return local_20;
}

