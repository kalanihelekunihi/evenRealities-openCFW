
undefined4 Cy_GPIO_Pin_Init(int param_1,uint param_2,uint *param_3)

{
  undefined4 uVar1;
  
  uVar1 = DAT_00008f9c;
  if ((param_1 != 0) && (param_3 != (uint *)0x0)) {
    if (7 < param_2) {
      software_bkpt(1);
    }
    if (1 < *param_3) {
      software_bkpt(1);
    }
    if (0xf < param_3[1]) {
      software_bkpt(1);
    }
    if (0xf < (byte)param_3[2]) {
      software_bkpt(1);
    }
    if (3 < param_3[3]) {
      software_bkpt(1);
    }
    if (1 < param_3[4]) {
      software_bkpt(1);
    }
    if (1 < param_3[5]) {
      software_bkpt(1);
    }
    Cy_GPIO_Write(param_1,param_2,*param_3);
    Cy_GPIO_SetDrivemode(param_1,param_2,param_3[1]);
    Cy_GPIO_SetHSIOM(param_1,param_2,(char)param_3[2]);
    Cy_GPIO_SetInterruptEdge(param_1,param_2,param_3[3]);
    if (1 < param_3[4]) {
      software_bkpt(1);
    }
    *(uint *)(param_1 + 8) = (param_3[4] & 1) << 0x18 | *(uint *)(param_1 + 8) & DAT_00008f94;
    if (1 < param_3[5]) {
      software_bkpt(1);
    }
    *(uint *)(param_1 + 8) = (param_3[5] & 1) << 0x19 | *(uint *)(param_1 + 8) & DAT_00008f98;
    uVar1 = 0;
  }
  return uVar1;
}

