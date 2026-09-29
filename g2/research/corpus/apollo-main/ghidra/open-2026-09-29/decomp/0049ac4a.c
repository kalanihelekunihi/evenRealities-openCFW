
uint FUN_0049ac4a(int *param_1,char param_2,undefined4 param_3,uint param_4,undefined4 param_5,
                 undefined4 param_6,undefined4 param_7,uint param_8)

{
  int iVar1;
  int iVar2;
  undefined4 local_18;
  
  if (param_2 == '\x02') {
    local_18 = param_8 & 0xff;
    iVar1 = FUN_004899a4(param_3,param_4,param_5,param_6);
    iVar2 = FUN_00451598(param_7);
    *param_1 = (iVar2 / 2 + *param_1) - iVar1 / 2;
  }
  else {
    local_18 = param_4;
    if (param_2 == '\x03') {
      local_18 = param_8 & 0xff;
      iVar1 = FUN_004899a4(param_3,param_4,param_5,param_6);
      iVar2 = FUN_00451598(param_7);
      *param_1 = (iVar2 + *param_1) - iVar1;
    }
  }
  return local_18;
}

