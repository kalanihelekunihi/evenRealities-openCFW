
undefined8
AttcReadByTypeReq(undefined1 param_1,short param_2,uint param_3,uint param_4,undefined4 param_5,
                 byte param_6)

{
  short *psVar1;
  uint local_20;
  
  psVar1 = (short *)attMsgAlloc((param_4 & 0xff) + 0xd);
  local_20 = param_3;
  if (psVar1 != (short *)0x0) {
    *psVar1 = ((ushort)param_4 & 0xff) + 5;
    psVar1[1] = param_2;
    psVar1[2] = (short)param_3;
    *(undefined1 *)(psVar1 + 4) = 8;
    FUN_00439be4((int)psVar1 + 0xd,param_5,param_4 & 0xff);
    local_20 = (uint)param_6;
    attcSendMsg(param_1,param_2,4,psVar1);
  }
  return CONCAT44(param_4,local_20);
}

