
uint gx8002_uart_stage1_udiv(uint param_1,uint param_2)

{
  int iVar1;
  uint uVar2;
  uint uVar3;
  
  if ((param_2 < param_1) && (-1 < (int)param_2)) {
    iVar1 = 0x20;
    uVar3 = 1;
    do {
      param_2 = param_2 * 2;
      uVar3 = uVar3 * 2;
      if (param_1 <= param_2) {
        if (uVar3 == 0) {
          return 0;
        }
        break;
      }
      iVar1 = iVar1 + -1;
      if (iVar1 == 0) {
        return 0;
      }
    } while (-1 < (int)param_2);
  }
  else {
    uVar3 = 1;
  }
  uVar2 = 0;
  do {
    if (param_2 <= param_1) {
      param_1 = param_1 - param_2;
      uVar2 = uVar2 | uVar3;
    }
    uVar3 = uVar3 >> 1;
    param_2 = param_2 >> 1;
  } while (uVar3 != 0);
  return uVar2;
}

