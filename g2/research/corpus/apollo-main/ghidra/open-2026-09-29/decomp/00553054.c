
void animate_text(int *param_1)

{
  byte bVar1;
  int iVar2;
  uint uVar3;
  uint uVar4;
  
  if (param_1 != (int *)0x0) {
    if ((char)param_1[5] == '\0') {
      if (param_1[3] < param_1[4]) {
        iVar2 = ensure_text_capacity(param_1,param_1,param_1 + 9,param_1[4] + 1);
        if (iVar2 == 0) {
          if ((param_1[8] != 0) && (iVar2 = osMutexAcquire(param_1[8],0xffffffff), iVar2 == 0)) {
            if (param_1[7] != 0) {
              osTimerStop(param_1[7]);
            }
            osMutexRelease(param_1[8]);
          }
        }
        else {
          uVar3 = 1;
          bVar1 = *(byte *)(param_1[1] + param_1[3]);
          if (0x7f < bVar1) {
            if ((bVar1 & 0xe0) == 0xc0) {
              uVar3 = 2;
            }
            else if ((bVar1 & 0xf0) == 0xe0) {
              uVar3 = 3;
            }
            else if ((bVar1 & 0xf8) == 0xf0) {
              uVar3 = 4;
            }
          }
          for (uVar4 = 0; (uVar4 < uVar3 && (uVar4 + param_1[3] < (uint)param_1[4]));
              uVar4 = uVar4 + 1) {
            *(undefined1 *)(*param_1 + uVar4 + param_1[3]) =
                 *(undefined1 *)(param_1[1] + uVar4 + param_1[3]);
          }
          *(undefined1 *)(*param_1 + uVar3 + param_1[3]) = 0;
          param_1[3] = uVar3 + param_1[3];
          if (param_1[6] != 0) {
            (*(code *)param_1[6])(*param_1);
          }
          if ((((param_1 != (int *)0x0) && (param_1[4] <= param_1[3])) && (param_1[8] != 0)) &&
             (iVar2 = osMutexAcquire(param_1[8],0xffffffff), iVar2 == 0)) {
            if (param_1[7] != 0) {
              osTimerStop(param_1[7]);
            }
            osMutexRelease(param_1[8]);
          }
        }
      }
      else if ((param_1[8] != 0) && (iVar2 = osMutexAcquire(param_1[8],0xffffffff), iVar2 == 0)) {
        if (param_1[7] != 0) {
          osTimerStop(param_1[7]);
        }
        osMutexRelease(param_1[8]);
      }
    }
    else if ((param_1[8] != 0) && (iVar2 = osMutexAcquire(param_1[8],0xffffffff), iVar2 == 0)) {
      if (param_1[7] != 0) {
        osTimerStop(param_1[7]);
      }
      osMutexRelease(param_1[8]);
    }
  }
  return;
}

