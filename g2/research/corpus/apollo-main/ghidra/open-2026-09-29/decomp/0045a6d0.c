
undefined8 FUN_0045a6d0(undefined4 param_1,int param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined4 local_c;
  
  local_10 = param_3;
  local_c = param_4;
  if (param_2 == 0) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      local_c = DAT_0045b118;
      local_10 = 0xa7;
      FUN_0043d574(2,DAT_0045b100,DAT_0045b0fc,DAT_0045b11c);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x8000000,DAT_0045b120);
    }
  }
  else {
    FUN_00442524(param_1,param_2,param_3,param_4 & 0xffff);
    file_heap_free(param_2);
  }
  return CONCAT44(local_c,local_10);
}

