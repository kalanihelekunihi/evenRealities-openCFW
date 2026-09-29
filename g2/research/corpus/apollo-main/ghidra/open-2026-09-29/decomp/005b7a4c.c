
undefined8 FUN_005b7a4c(int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 local_10;
  
  local_10 = param_3;
  if (((param_1 != (int *)0x0) && (*param_1 != 0)) && (param_1[1] != 0)) {
    if (*(char *)((int)param_1 + 9) == '\0') {
      FUN_0043f6ac(param_1[1],3);
      FUN_0043f0e0(param_1[1],0);
      FUN_0043f142(param_1[1],0x109);
      local_10 = 0;
      FUN_0043f6d6(*param_1,param_1[1],0x11,0xfffffff8);
    }
    else {
      FUN_0043f0e0(*param_1,0);
      FUN_0043f142(*param_1,0x106);
      local_10 = 0;
      FUN_0043f6d6(param_1[1],*param_1,0x14,8);
    }
  }
  return CONCAT44(param_4,local_10);
}

