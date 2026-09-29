
undefined4 __module_get_info(uint param_1,int *param_2)

{
  int iVar1;
  int iVar2;
  int iVar3;
  uint uVar4;
  
  iVar1 = DAT_10024adc;
  if ((param_1 < 0x1a) && (param_2 != (int *)0x0)) {
    iVar3 = 0;
    uVar4 = *(uint *)(param_1 * 0x10 + DAT_10024adc);
    *param_2 = 0;
    if (param_1 == uVar4) {
      *param_2 = iVar1 + param_1 * 0x10;
    }
    else {
      iVar2 = 0x1a;
      do {
        if (param_1 == *(uint *)(iVar1 + iVar3 * 0x10)) {
          *param_2 = iVar1 + iVar3 * 0x10;
          break;
        }
        iVar3 = iVar3 + 1;
        iVar2 = iVar2 + -1;
      } while (iVar2 != 0);
    }
    if (*param_2 != 0) {
      if (param_1 < 10) {
        param_2[1] = 0;
        param_2[2] = DAT_10024ae0;
        param_2[3] = 0x18;
        param_2[4] = 0x1c;
      }
      else {
        param_2[1] = 0;
        param_2[2] = DAT_10024ae4;
        param_2[3] = 0x18;
        param_2[4] = 0x1c;
      }
      param_2[5] = 0x20;
      return 0;
    }
  }
  return 0xffffffff;
}

