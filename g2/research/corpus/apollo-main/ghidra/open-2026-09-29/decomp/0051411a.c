
undefined8
FUN_0051411a(undefined4 *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 local_10;
  undefined4 local_c;
  
  local_10 = param_3;
  local_c = param_4;
  iVar1 = FUN_00514050(param_1[1]);
  if (*(char *)(iVar1 + 0x18) != '\0') {
    local_c = *param_1;
    local_10 = param_1[3];
    FUN_00475014(&local_10,0);
  }
  return CONCAT44(local_c,local_10);
}

