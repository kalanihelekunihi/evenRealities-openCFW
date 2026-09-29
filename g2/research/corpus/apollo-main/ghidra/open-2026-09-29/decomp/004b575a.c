
undefined4 AttcReadReq(undefined1 param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  undefined2 *puVar1;
  undefined4 local_10;
  
  puVar1 = (undefined2 *)attMsgAlloc(0xb);
  local_10 = param_4;
  if (puVar1 != (undefined2 *)0x0) {
    *puVar1 = 3;
    *(undefined1 *)(puVar1 + 4) = 10;
    *(char *)((int)puVar1 + 9) = (char)param_2;
    *(char *)(puVar1 + 5) = (char)(param_2 >> 8);
    local_10 = 0;
    attcSendMsg(param_1,param_2 & 0xffff,5);
  }
  return local_10;
}

