
uint AttcFindInfoReq(undefined1 param_1,undefined2 param_2,undefined2 param_3,uint param_4)

{
  undefined2 *puVar1;
  uint local_18;
  
  puVar1 = (undefined2 *)attMsgAlloc(0xd);
  local_18 = param_4;
  if (puVar1 != (undefined2 *)0x0) {
    *puVar1 = 5;
    puVar1[1] = param_2;
    puVar1[2] = param_3;
    *(undefined1 *)(puVar1 + 4) = 4;
    local_18 = param_4 & 0xff;
    attcSendMsg(param_1,param_2,2,puVar1);
  }
  return local_18;
}

