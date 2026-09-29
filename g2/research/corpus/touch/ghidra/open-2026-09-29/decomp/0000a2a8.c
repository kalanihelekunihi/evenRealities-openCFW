
undefined4 Cy_SysInt_Init(short *param_1,undefined4 param_2)

{
  undefined4 uVar1;
  
  uVar1 = DAT_0000a2ec;
  if (param_1 != (short *)0x0) {
    if (3 < *(uint *)(param_1 + 2)) {
      software_bkpt(1);
    }
    NVIC_SetPriority((int)*param_1,*(undefined4 *)(param_1 + 2));
    if (*(int *)(DAT_0000a2e4 + 8) == DAT_0000a2e8) {
      Cy_SysInt_SetVector((int)*param_1,param_2);
      uVar1 = 0;
    }
    else {
      uVar1 = 0;
    }
  }
  return uVar1;
}

