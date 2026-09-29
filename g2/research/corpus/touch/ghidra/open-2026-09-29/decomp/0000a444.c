
int Cy_SysPm_ExecuteCallback(uint param_1,uint param_2)

{
  int iVar1;
  undefined4 *puVar2;
  undefined4 *puVar3;
  undefined4 local_18;
  undefined4 local_14;
  
  if (1 < param_1) {
    software_bkpt(1);
  }
  if ((param_2 - 1 & 0xff) < 2) {
    puVar2 = *(undefined4 **)(param_1 * 4 + DAT_0000a518);
  }
  else {
    if (param_2 == 4) {
      puVar2 = *(undefined4 **)(param_1 * 4 + DAT_0000a518);
      goto LAB_0000a48c;
    }
    if (param_2 == 8) {
      puVar2 = *(undefined4 **)(param_1 * 4 + DAT_0000a518);
    }
    else {
      software_bkpt(1);
      puVar2 = *(undefined4 **)(param_1 * 4 + DAT_0000a518);
    }
  }
  if (param_2 != 1) {
    if (param_2 == 2) {
      puVar3 = (undefined4 *)0x0;
      if (*DAT_0000a520 != 0) {
        puVar3 = *(undefined4 **)(*DAT_0000a520 + 0x10);
      }
    }
    else {
      do {
        puVar3 = puVar2;
        puVar2 = (undefined4 *)puVar3[5];
      } while ((undefined4 *)puVar3[5] != (undefined4 *)0x0);
    }
    iVar1 = 0;
    for (; puVar3 != (undefined4 *)0x0; puVar3 = (undefined4 *)puVar3[4]) {
      if ((puVar3[2] & param_2) == 0) {
        local_18 = *(undefined4 *)puVar3[3];
        local_14 = ((undefined4 *)puVar3[3])[1];
        iVar1 = (*(code *)*puVar3)(&local_18,param_2);
      }
    }
    return iVar1;
  }
LAB_0000a48c:
  iVar1 = 0;
  while ((puVar2 != (undefined4 *)0x0 && ((iVar1 != DAT_0000a51c || (param_2 != 1))))) {
    if ((puVar2[2] & param_2) == 0) {
      local_18 = *(undefined4 *)puVar2[3];
      local_14 = ((undefined4 *)puVar2[3])[1];
      iVar1 = (*(code *)*puVar2)(&local_18,param_2);
      *DAT_0000a520 = (int)puVar2;
    }
    puVar2 = (undefined4 *)puVar2[5];
  }
  if (param_2 == 1) {
    if (iVar1 == DAT_0000a51c) {
      *(int *)(param_1 * 4 + DAT_0000a524) = *DAT_0000a520;
    }
    else {
      *(undefined4 *)(param_1 * 4 + DAT_0000a524) = 0;
    }
  }
  return iVar1;
}

