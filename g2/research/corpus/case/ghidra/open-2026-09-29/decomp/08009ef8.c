
undefined4 case_query_low_byte(uint *param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  int iVar1;
  uint local_10;
  
  local_10 = param_4;
  iVar1 = case_invoke_mode_one(0,&local_10);
  if (iVar1 != 0) {
    return 0xffffffff;
  }
  *param_1 = local_10 & 0xff;
  return 0;
}

