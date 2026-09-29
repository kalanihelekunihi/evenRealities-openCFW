
undefined8 FT_Outline_Done_Internal(int param_1,int param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  
  if (param_2 == 0) {
    uVar1 = 0x14;
  }
  else if (param_1 == 0) {
    uVar1 = 6;
  }
  else {
    if ((int)((uint)*(byte *)(param_2 + 0x10) << 0x1f) < 0) {
      ft_mem_free(param_1,*(undefined4 *)(param_2 + 4));
      *(undefined4 *)(param_2 + 4) = 0;
      ft_mem_free(param_1,*(undefined4 *)(param_2 + 8));
      *(undefined4 *)(param_2 + 8) = 0;
      ft_mem_free(param_1,*(undefined4 *)(param_2 + 0xc));
      *(undefined4 *)(param_2 + 0xc) = 0;
    }
    FUN_0048949c(param_2,0x14);
    uVar1 = 0;
  }
  return CONCAT44(param_4,uVar1);
}

