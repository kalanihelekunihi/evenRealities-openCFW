
undefined8 FUN_004b38f2(int param_1,int param_2)

{
  undefined4 unaff_r5;
  undefined4 unaff_r6;
  undefined2 local_10;
  undefined2 local_e;
  undefined2 local_c;
  undefined2 local_a;
  
  local_c = (undefined2)unaff_r6;
  local_a = (undefined2)((uint)unaff_r6 >> 0x10);
  local_10 = (undefined2)unaff_r5;
  local_e = (undefined2)((uint)unaff_r5 >> 0x10);
  if (*(char *)*DAT_004b450c == '\0') {
    local_10 = *(undefined2 *)(param_1 + 6);
    local_e = *(undefined2 *)(param_1 + 8);
    local_c = *(undefined2 *)(param_1 + 10);
    local_a = *(undefined2 *)(param_1 + 0xc);
    DmRemoteConnParamReqReply(*(undefined1 *)(param_2 + 4),&local_10);
  }
  else if (*(char *)*DAT_004b450c == '\x01') {
    DmRemoteConnParamReqNegReply(*(undefined1 *)(param_2 + 4),0x11);
  }
  return CONCAT26(local_a,CONCAT24(local_c,CONCAT22(local_e,local_10)));
}

