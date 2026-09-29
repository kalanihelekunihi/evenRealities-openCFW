
int Init_Context(undefined4 *param_1,undefined4 param_2,int param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int local_10;
  undefined4 uStack_c;
  
  param_1[2] = param_2;
  param_1[0x6d] = 0x20;
  local_10 = param_3;
  uStack_c = param_4;
  uVar1 = ft_mem_realloc(param_2,0x10,0,param_1[0x6d],0,&local_10);
  param_1[0x6e] = uVar1;
  if (local_10 == 0) {
    *(undefined2 *)(param_1 + 0x6f) = 0;
    *(undefined2 *)((int)param_1 + 0x1be) = 0;
    param_1[5] = 0;
    param_1[0x62] = 0;
    param_1[6] = 0;
    param_1[99] = 0;
    *param_1 = 0;
    param_1[1] = 0;
    local_10 = 0;
  }
  else {
    TT_Done_Context(param_1);
  }
  return local_10;
}

