
undefined4
raccess_guess_vfat(undefined4 *param_1,undefined4 param_2,undefined4 param_3,int *param_4,
                  undefined4 *param_5)

{
  int iVar1;
  undefined4 uVar2;
  
  iVar1 = raccess_make_file_name(*param_1,param_3,DAT_00528edc);
  if (iVar1 == 0) {
    uVar2 = 0x40;
  }
  else {
    *param_4 = iVar1;
    *param_5 = 0;
    uVar2 = 0;
  }
  return uVar2;
}

