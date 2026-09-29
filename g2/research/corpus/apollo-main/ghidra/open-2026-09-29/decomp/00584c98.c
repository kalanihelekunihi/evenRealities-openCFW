
undefined8 FUN_00584c98(int param_1,uint param_2)

{
  int *piVar1;
  int *piVar2;
  char *pcVar3;
  int *piVar4;
  uint uVar5;
  undefined4 uVar6;
  int iVar7;
  uint uVar8;
  uint uVar9;
  int local_28;
  
  piVar4 = DAT_00584e74;
  piVar2 = DAT_00584e54;
  piVar1 = DAT_00584e48;
  local_28 = 0;
  uVar9 = 0;
  if ((((param_1 == 0) || (param_2 == 0)) || (0x400 < param_2)) ||
     (((*DAT_00584e4c != '\x01' || (*DAT_00584e48 == 0)) ||
      ((*DAT_00584e74 == 0 || (*DAT_00584e54 == 0)))))) {
    uVar6 = 1;
  }
  else {
    iVar7 = osMutexAcquire(*DAT_00584e74,0xffffffff);
    if (iVar7 == 0) {
      osKernelGetTickCount();
      uVar5 = DAT_00584e84;
      FUN_00439be4(DAT_00584e84,param_1,param_2);
      uVar8 = param_2 + 0x1f & 0xffffffe0;
      if (0 < (int)uVar8) {
        iVar7 = (uVar5 & 0x1f) + uVar8;
        DataSynchronizationBarrier(0xf);
        uVar8 = uVar5;
        do {
          *DAT_00584e88 = uVar8;
          uVar8 = uVar8 + 0x20;
          iVar7 = iVar7 + -0x20;
        } while (0 < iVar7);
        DataSynchronizationBarrier(0xf);
        InstructionSynchronizationBarrier(0xf);
      }
      osSemaphoreAcquire(*piVar2,0);
      pcVar3 = DAT_00584e58;
      *DAT_00584e58 = '\0';
      FUN_00584a64();
      FUN_00584a38(uVar5,param_2);
      iVar7 = osSemaphoreAcquire(*piVar2,100);
      if (iVar7 == 0) {
        if (*pcVar3 == '\0') {
          do {
            FUN_0058e754(*piVar1,&local_28);
            if (-1 < local_28 << 0x1c) break;
            FUN_00491102(10);
            uVar9 = uVar9 + 1;
          } while (uVar9 < 100);
          osMutexRelease(*piVar4);
          uVar6 = 0;
        }
        else {
          *pcVar3 = '\0';
          osMutexRelease(*piVar4);
          uVar6 = 1;
        }
      }
      else {
        FUN_00584a64();
        *pcVar3 = '\0';
        osMutexRelease(*piVar4);
        uVar6 = 1;
      }
    }
    else {
      uVar6 = 1;
    }
  }
  return CONCAT44(local_28,uVar6);
}

