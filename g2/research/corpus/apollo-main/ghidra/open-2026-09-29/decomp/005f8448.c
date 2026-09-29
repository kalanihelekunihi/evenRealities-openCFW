
int tt_glyphzone_new(undefined4 param_1,uint param_2,int param_3,undefined4 *param_4)

{
  bool bVar1;
  undefined4 uVar2;
  int local_20;
  undefined4 *puStack_1c;
  
  local_20 = param_3;
  puStack_1c = param_4;
  FUN_0043c0e4(param_4,0x24,0,param_4,param_1,param_2);
  *param_4 = param_1;
  uVar2 = ft_mem_realloc(param_1,8,0,param_2 & 0xffff,0,&local_20);
  param_4[3] = uVar2;
  if (local_20 == 0) {
    uVar2 = ft_mem_realloc(param_1,8,0,param_2 & 0xffff,0,&local_20);
    param_4[4] = uVar2;
    if (local_20 == 0) {
      uVar2 = ft_mem_realloc(param_1,8,0,param_2 & 0xffff,0,&local_20);
      param_4[5] = uVar2;
      if (local_20 == 0) {
        uVar2 = ft_mem_realloc(param_1,1,0,param_2 & 0xffff,0,&local_20);
        param_4[6] = uVar2;
        if (local_20 == 0) {
          uVar2 = ft_mem_realloc(param_1,2,0,(int)(short)param_3,0,&local_20);
          param_4[7] = uVar2;
          if (local_20 == 0) {
            bVar1 = false;
            goto LAB_005f84fe;
          }
        }
      }
    }
  }
  bVar1 = true;
LAB_005f84fe:
  if (bVar1) {
    tt_glyphzone_done(param_4);
  }
  else {
    *(short *)(param_4 + 1) = (short)param_2;
    *(short *)((int)param_4 + 6) = (short)param_3;
  }
  return local_20;
}

