
uint AttcFindByTypeValueReq
               (undefined1 param_1,short param_2,short param_3,uint param_4,short param_5,
               undefined4 param_6,byte param_7)

{
  short *psVar1;
  uint local_20;
  
  psVar1 = (short *)attMsgAlloc(param_5 + 0xf);
  local_20 = param_4;
  if (psVar1 != (short *)0x0) {
    *psVar1 = param_5 + 7;
    psVar1[1] = param_2;
    psVar1[2] = param_3;
    *(undefined1 *)(psVar1 + 4) = 6;
    *(char *)((int)psVar1 + 0xd) = (char)param_4;
    *(char *)(psVar1 + 7) = (char)(param_4 >> 8);
    FUN_00439be4((int)psVar1 + 0xf,param_6,param_5);
    local_20 = (uint)param_7;
    attcSendMsg(param_1,param_2,3,psVar1);
  }
  return local_20;
}

