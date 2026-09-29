
undefined8
FUN_005d11a4(undefined4 *param_1,undefined4 param_2,undefined4 param_3,char *param_4,char param_5)

{
  undefined4 uVar1;
  undefined4 uVar2;
  char *local_20;
  
  uVar2 = 0;
  local_20 = param_4;
  FUN_005d0a68(param_1);
  local_20 = (char *)*param_1;
  if (local_20 < (char *)param_1[2]) {
    if (param_5 != '\0') {
      if (*local_20 != '<') {
        uVar2 = 3;
        goto LAB_005d1214;
      }
      local_20 = local_20 + 1;
    }
    uVar1 = FUN_005d0414(&local_20,param_1[2],param_2,param_3);
    *(undefined4 *)param_4 = uVar1;
    if (param_5 != '\0') {
      if ((local_20 < (char *)param_1[2]) && (*local_20 != '>')) {
        uVar2 = 3;
        goto LAB_005d1214;
      }
      local_20 = local_20 + 1;
    }
    *param_1 = local_20;
  }
LAB_005d1214:
  return CONCAT44(local_20,uVar2);
}

