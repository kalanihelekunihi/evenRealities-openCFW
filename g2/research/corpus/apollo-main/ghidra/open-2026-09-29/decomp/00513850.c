
undefined8 FUN_00513850(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  
  iVar2 = FUN_005137c4(param_1);
  if ((iVar2 == 0) && (iVar2 = FUN_005137de(), iVar1 = DAT_0051389c, iVar2 == 0)) {
    *(uint *)(DAT_0051389c + param_1) = param_2;
    do {
    } while (-1 < *DAT_005138a0 << 0x1f);
    do {
    } while (*DAT_00513898 << 0x1f < 0);
    if ((*(uint *)(iVar1 + param_1) & param_2) != param_2) {
      iVar2 = 1;
    }
  }
  return CONCAT44(param_4,iVar2);
}

