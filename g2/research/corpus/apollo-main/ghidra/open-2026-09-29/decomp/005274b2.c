
undefined8 FT_New_Library(int param_1,undefined4 *param_2,undefined4 param_3,int param_4)

{
  int *piVar1;
  int iVar2;
  int local_10;
  
  local_10 = param_4;
  if ((param_1 == 0) || (param_2 == (undefined4 *)0x0)) {
    iVar2 = 6;
  }
  else {
    piVar1 = (int *)ft_mem_alloc(param_1,0xb8,&local_10);
    iVar2 = local_10;
    if (local_10 == 0) {
      *piVar1 = param_1;
      piVar1[1] = 2;
      piVar1[2] = 9;
      piVar1[3] = 1;
      piVar1[0x2d] = 1;
      *param_2 = piVar1;
      iVar2 = 0;
    }
  }
  return CONCAT44(local_10,iVar2);
}

