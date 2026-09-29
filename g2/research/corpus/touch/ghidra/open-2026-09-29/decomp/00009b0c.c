
void Cy_SCB_I2C_SlaveInterrupt(int *param_1,int param_2,int param_3,undefined4 param_4)

{
  uint uVar1;
  uint uVar2;
  bool bVar3;
  
  if (*(int *)((int)param_1 + DAT_00009c20) << 0x1f < 0) {
    *(undefined4 *)(param_2 + 4) = 0x1000;
    param_3 = 1;
    param_1[0x3a0] = 1;
  }
  uVar2 = *(uint *)((int)param_1 + DAT_00009c24);
  if ((uVar2 & 0x101) == 0) {
    if ((((int)(uVar2 << 0x1b) < 0) && ((param_1[0xc2] & 0x1ffU) != 0)) &&
       (*(int *)(param_2 + 0x3c) != 0)) {
      *(undefined4 *)((int)param_1 + DAT_00009c30) = 1;
      param_3 = DAT_00009c28;
      *(undefined4 *)((int)param_1 + DAT_00009c28) = 1;
    }
  }
  else {
    if ((int)(uVar2 << 0x17) < 0) {
      uVar1 = 0x100;
    }
    else {
      uVar1 = 0x80;
    }
    *(uint *)(param_2 + 0x20) = *(uint *)(param_2 + 0x20) | uVar1;
    param_3 = 0;
    *(undefined4 *)((int)param_1 + DAT_00009c28) = 0;
    uVar2 = uVar2 | 0x10;
  }
  if ((uVar2 & 0x3000000) != 0) {
    SlaveHandleHsMode(param_1,param_2,param_3,0x3000000,param_4);
  }
  if (*(int *)((int)param_1 + DAT_00009c2c) << 0x1f < 0) {
    if (*param_1 << 0xf < 0) {
      bVar3 = (*(uint *)((int)param_1 + DAT_00009c24) & 0x40) != 0;
      if (bVar3) goto LAB_00009bbe;
    }
    else {
      bVar3 = false;
    }
    SlaveHandleDataReceive(param_1,param_2);
    param_1[0x3f0] = 1;
  }
  else {
    bVar3 = false;
  }
LAB_00009bbe:
  if ((int)(uVar2 << 0x1b) < 0) {
    SlaveHandleStop(param_1,bVar3,param_2);
    param_1[0x3d0] = 0x10;
    uVar2 = *(uint *)((int)param_1 + DAT_00009c24);
  }
  if ((uVar2 & 0xc0) != 0) {
    SlaveHandleAddress(param_1,param_2);
    param_1[0x3a0] = 1;
    param_1[0x3d0] = 0xc0;
  }
  if ((*(uint *)((int)param_1 + DAT_00009c34) & 0x41) != 0) {
    SlaveHandleDataTransmit(param_1,param_2);
    param_1[0x3e0] = 1;
  }
  return;
}

