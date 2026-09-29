
undefined8 FUN_004bafda(undefined2 *param_1,undefined4 param_2,uint param_3,undefined4 param_4)

{
  uint local_10;
  undefined1 local_c;
  undefined1 local_b;
  undefined1 local_a;
  undefined1 uStack_9;
  
  local_c = (undefined1)param_4;
  local_b = (undefined1)((uint)param_4 >> 8);
  local_a = (undefined1)((uint)param_4 >> 0x10);
  uStack_9 = (undefined1)((uint)param_4 >> 0x18);
  local_10 = param_3;
  if (*(char *)((int)param_1 + 5) == '\0') {
    FUN_004bd054(0xe);
  }
  else {
    FUN_0053634e(&local_10,4);
    local_10 = local_10 - DAT_004bb3c8 * (local_10 / DAT_004bb3c8);
    local_c = (undefined1)local_10;
    local_b = (undefined1)(local_10 >> 8);
    local_a = (undefined1)(local_10 >> 0x10);
    DmSecAuthRsp((char)*param_1,3,&local_c);
    FUN_004bd7fa(local_10);
  }
  return CONCAT17(uStack_9,CONCAT16(local_a,CONCAT15(local_b,CONCAT14(local_c,local_10))));
}

