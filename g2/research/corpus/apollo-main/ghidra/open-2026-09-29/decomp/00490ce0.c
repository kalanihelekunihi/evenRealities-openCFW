
void FUN_00490ce0(undefined4 param_1,undefined4 param_2,uint param_3,uint param_4)

{
  uint local_10;
  
  if ((param_4 == 0) && (param_3 < 0x80)) {
    local_10 = param_3 & 0xff;
    FUN_00490616(param_1,&local_10,1);
  }
  else {
    local_10 = param_4;
    FUN_00490c84(param_1,param_3,param_4);
  }
  return;
}

