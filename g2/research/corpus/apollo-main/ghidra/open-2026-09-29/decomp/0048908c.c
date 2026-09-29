
void FUN_0048908c(int *param_1)

{
  int iVar1;
  
  if (*param_1 != 0) {
    if (*(int *)(*param_1 + 0xc) != 0) {
      (**(code **)(*param_1 + 0xc))(*param_1,param_1);
    }
    iVar1 = FUN_004d4b24();
    if (((iVar1 != 0) && (param_1[0x10] != 0)) && (param_1[0x11] != 0)) {
      FUN_004d4e72(param_1[0x10],param_1[0x11],0);
    }
  }
  return;
}

