
undefined4 gx8002_uart_stage1_pmu_fill_desc(uint param_1,int *param_2)

{
  uint *puVar1;
  int iVar2;
  int iVar3;
  uint *puVar4;
  
  puVar4 = DAT_10000834;
  iVar2 = 0x19;
  if ((param_1 < 0x1a) && (param_2 != (int *)0x0)) {
    *param_2 = 0;
    if (param_1 == puVar4[param_1 * 4]) {
      puVar4 = puVar4 + param_1 * 4;
      *param_2 = (int)puVar4;
    }
    else {
      if (param_1 != *puVar4) {
        iVar3 = 1;
        puVar1 = puVar4;
        while (puVar1 = puVar1 + 4, param_1 != *puVar1) {
          iVar3 = iVar3 + 1;
          iVar2 = iVar2 + -1;
          if (iVar2 == 0) {
            return 0xffffffff;
          }
        }
        puVar4 = puVar4 + iVar3 * 4;
      }
      *param_2 = (int)puVar4;
    }
    if (puVar4 != (uint *)0x0) {
      if (param_1 < 10) {
        param_2[1] = 0;
        param_2[2] = DAT_1000083c;
        param_2[3] = 0x18;
        param_2[4] = 0x1c;
        param_2[5] = 0x20;
        return 0;
      }
      param_2[1] = 0;
      param_2[2] = DAT_10000838;
      param_2[3] = 0x18;
      param_2[4] = 0x1c;
      param_2[5] = 0x20;
      return 0;
    }
  }
  return 0xffffffff;
}

