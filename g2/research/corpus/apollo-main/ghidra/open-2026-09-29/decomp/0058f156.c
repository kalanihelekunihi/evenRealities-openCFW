
undefined4 FUN_0058f156(undefined4 *param_1,int param_2)

{
  undefined4 uVar1;
  
  if (param_1 == (undefined4 *)0x0) {
    uVar1 = 0x21;
  }
  else if (param_2 == 0) {
    uVar1 = 6;
  }
  else {
    ft_mem_free(*param_1,*(undefined4 *)(param_2 + 0xc));
    *(undefined4 *)(param_2 + 0xc) = 0;
    FUN_0048949c(param_2,0x18);
    uVar1 = 0;
  }
  return uVar1;
}

