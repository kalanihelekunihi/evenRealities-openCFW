
undefined8 osMemoryPoolNew(int param_1,int param_2,int *param_3,undefined4 param_4)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 *puVar3;
  int iVar4;
  uint uVar5;
  int iVar6;
  
  iVar1 = IRQ_Context();
  if (iVar1 == 0) {
    if ((param_1 == 0) || (param_2 == 0)) {
      puVar3 = (undefined4 *)0x0;
    }
    else {
      uVar5 = param_1 * (param_2 + 3U >> 2) * 4;
      iVar6 = 0;
      iVar4 = -1;
      iVar1 = -1;
      if (param_3 == (int *)0x0) {
        iVar1 = 0;
        iVar4 = 0;
      }
      else {
        if (*param_3 != 0) {
          iVar6 = *param_3;
        }
        if ((param_3[2] == 0) || ((uint)param_3[3] < 0x74)) {
          if ((param_3[2] == 0) && (param_3[3] == 0)) {
            iVar1 = 0;
          }
        }
        else {
          iVar1 = 1;
        }
        if ((param_3[4] == 0) && (param_3[5] == 0)) {
          iVar4 = 0;
        }
        else if ((param_3[4] != 0) &&
                (((*(byte *)(param_3 + 4) & 3) == 0 && (uVar5 <= (uint)param_3[5])))) {
          iVar4 = 1;
        }
      }
      if (iVar1 == 0) {
        puVar3 = (undefined4 *)pvPortMalloc(0x74);
      }
      else {
        puVar3 = (undefined4 *)param_3[2];
      }
      if (puVar3 != (undefined4 *)0x0) {
        uVar2 = FUN_00441790(param_1,param_1,puVar3 + 9);
        puVar3[1] = uVar2;
        if (puVar3[1] != 0) {
          if (iVar4 == 0) {
            uVar2 = pvPortMalloc(uVar5);
            puVar3[2] = uVar2;
          }
          else {
            puVar3[2] = param_3[4];
          }
        }
      }
      if ((puVar3 == (undefined4 *)0x0) || (puVar3[2] == 0)) {
        if ((iVar1 == 0) && (puVar3 != (undefined4 *)0x0)) {
          vPortFree(puVar3);
        }
        puVar3 = (undefined4 *)0x0;
      }
      else {
        *puVar3 = 0;
        puVar3[3] = uVar5;
        puVar3[4] = iVar6;
        puVar3[5] = param_2;
        puVar3[6] = param_1;
        puVar3[7] = 0;
        puVar3[8] = DAT_00449e90;
        if (iVar1 == 0) {
          puVar3[8] = puVar3[8] | 1;
        }
        if (iVar4 == 0) {
          puVar3[8] = puVar3[8] | 2;
        }
      }
    }
  }
  else {
    puVar3 = (undefined4 *)0x0;
  }
  return CONCAT44(param_4,puVar3);
}

