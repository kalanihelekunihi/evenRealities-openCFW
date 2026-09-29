
void SlaveHandleDataTransmit(uint *param_1,int param_2)

{
  int iVar1;
  undefined4 uVar2;
  
  if ((*(char *)(param_2 + 0x24) == '\0') && (*(int *)(param_2 + 0x2c) == 0)) {
    if (*(code **)(param_2 + 0x44) != (code *)0x0) {
      (**(code **)(param_2 + 0x44))(8);
    }
    *(bool *)(param_2 + 0x24) = *(int *)(param_2 + 0x2c) == 0;
    *(undefined4 *)((int)param_1 + DAT_000098f0) = 1;
  }
  if (*(char *)(param_2 + 0x24) == '\0') {
    if (1 < *(uint *)(param_2 + 0x2c)) {
      if (*(char *)(param_2 + 1) == '\0') {
        iVar1 = 1;
      }
      else {
        iVar1 = *(uint *)(param_2 + 0x2c) - 1;
      }
      iVar1 = Cy_SCB_WriteArray(param_1,*(undefined4 *)(param_2 + 0x28),iVar1);
      *(int *)(param_2 + 0x30) = *(int *)(param_2 + 0x30) + iVar1;
      *(int *)(param_2 + 0x2c) = *(int *)(param_2 + 0x2c) - iVar1;
      *(int *)(param_2 + 0x28) = *(int *)(param_2 + 0x28) + iVar1;
    }
    if (((param_1[0x82] & 0x1ff) != 0x10) && (*(int *)(param_2 + 0x2c) == 1)) {
      Cy_SysLib_EnterCriticalSection();
      param_1[0x90] = (uint)**(byte **)(param_2 + 0x28);
      param_1[0x3e0] = 0x40;
      Cy_SysLib_ExitCriticalSection();
      *(int *)(param_2 + 0x30) = *(int *)(param_2 + 0x30) + 1;
      *(undefined4 *)(param_2 + 0x2c) = 0;
      *(int *)(param_2 + 0x28) = *(int *)(param_2 + 0x28) + 1;
      *(undefined4 *)((int)param_1 + DAT_000098f0) = 0x40;
      if (*(char *)(param_2 + 1) != '\0') {
        *(uint *)(param_2 + 0x20) = *(uint *)(param_2 + 0x20) | 2;
        if (*(code **)(param_2 + 0x44) != (code *)0x0) {
          (**(code **)(param_2 + 0x44))(4);
        }
      }
    }
  }
  else {
    if (*(char *)(param_2 + 1) == '\0') {
      uVar2 = 1;
    }
    else if ((*param_1 & 0xc000) == 0) {
      uVar2 = 0x10;
    }
    else {
      uVar2 = 8;
    }
    iVar1 = Cy_SCB_WriteDefaultArray(param_1,0xff,uVar2);
    *(int *)(param_2 + 0x30) = *(int *)(param_2 + 0x30) + iVar1;
    *(uint *)(param_2 + 0x20) = *(uint *)(param_2 + 0x20) | 8;
  }
  return;
}

