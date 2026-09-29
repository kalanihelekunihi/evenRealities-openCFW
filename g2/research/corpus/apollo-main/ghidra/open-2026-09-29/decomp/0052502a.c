
undefined4 FT_Stream_Free(int param_1,int param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  
  uVar1 = 0;
  if (param_1 != 0) {
    uVar2 = *(undefined4 *)(param_1 + 0x1c);
    uVar1 = FT_Stream_Close(param_1);
    if (param_2 == 0) {
      ft_mem_free(uVar2,param_1);
      uVar1 = 0;
    }
  }
  return uVar1;
}

