
ulonglong semantic_TouchFrameReadU16
                    (undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 local_10;
  undefined4 uStack_c;
  
  local_10 = param_3;
  uStack_c = param_4;
  FUN_00439be4(&local_10,param_1,2);
  return CONCAT44(local_10,local_10) & 0xffffffff0000ffff;
}

