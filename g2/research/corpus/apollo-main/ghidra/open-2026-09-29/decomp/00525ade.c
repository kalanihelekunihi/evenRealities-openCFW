
undefined4 FT_New_Memory_Face(undefined4 param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 local_2c [3];
  int local_20;
  undefined4 local_1c;
  undefined4 uStack_c;
  
  if (param_2 == 0) {
    uVar1 = 6;
  }
  else {
    local_2c[0] = 4;
    local_1c = 0;
    local_20 = param_2;
    uStack_c = param_4;
    uVar1 = FT_Open_Face(param_1,local_2c,param_3,param_4,1);
  }
  return uVar1;
}

