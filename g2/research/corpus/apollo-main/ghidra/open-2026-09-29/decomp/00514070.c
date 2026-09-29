
undefined8 FUN_00514070(uint param_1,int param_2,uint param_3,undefined4 param_4)

{
  int iVar1;
  uint local_20;
  int local_1c;
  uint local_18;
  undefined4 local_14;
  
  local_20 = param_1;
  local_1c = param_2;
  local_18 = param_3;
  local_14 = param_4;
  iVar1 = FUN_00514050(param_2);
  if (*(char *)(iVar1 + 0x18) == '\0') {
    if (((param_2 == 1) || (param_2 == 2)) || (param_2 == 0)) {
      local_18 = FUN_004841d8(iVar1,param_3,8);
    }
    else {
      local_18 = FUN_00484180(iVar1,param_3);
    }
  }
  else {
    param_3 = param_3 + 0x1f & 0xffffffe0;
    local_18 = FUN_004841d8(iVar1,param_3,0x20);
  }
  local_20 = param_3;
  local_1c = param_2;
  local_14 = local_18;
  FUN_00439c04(param_1,&local_20,0x10);
  return CONCAT44(local_1c,local_20);
}

