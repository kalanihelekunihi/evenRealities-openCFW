
undefined8
raccess_guess_linux_double
          (undefined4 *param_1,undefined4 param_2,undefined4 param_3,int *param_4,undefined4 param_5
          )

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  uVar3 = *param_1;
  iVar1 = raccess_make_file_name(uVar3,param_3,0x5286fc);
  if (iVar1 == 0) {
    iVar2 = 0x40;
  }
  else {
    iVar2 = raccess_guess_linux_double_from_file_name(param_1,iVar1,param_5);
    if (iVar2 == 0) {
      *param_4 = iVar1;
    }
    else {
      ft_mem_free(uVar3,iVar1);
    }
  }
  return CONCAT44(param_4,iVar2);
}

