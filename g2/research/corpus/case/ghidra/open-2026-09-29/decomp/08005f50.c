
void HAL_UART_IRQHandler(int *param_1)

{
  bool bVar1;
  short sVar2;
  uint uVar3;
  uint uVar4;
  int iVar5;
  code *pcVar6;
  uint uVar7;
  uint *puVar8;
  int *piVar9;
  uint uVar10;
  
  puVar8 = (uint *)*param_1;
  uVar4 = puVar8[7];
  uVar3 = *puVar8;
  uVar7 = puVar8[2];
  piVar9 = param_1 + 0x20;
  if ((uVar4 & DAT_08006230) == 0) {
    if ((-1 < (int)(uVar4 << 0x1a)) || ((uVar3 & 0x20) == 0 && (uVar7 & 0x10000000) == 0))
    goto LAB_08006086;
    pcVar6 = (code *)param_1[0x1d];
  }
  else {
    uVar10 = DAT_08006234 & uVar7;
    if ((DAT_08006238 & uVar3) != 0 || uVar10 != 0) {
      if (((uVar4 & 1) != 0) && ((int)(uVar3 << 0x17) < 0)) {
        puVar8[8] = 1;
        param_1[0x24] = param_1[0x24] | 1;
      }
      if (((int)(uVar4 << 0x1e) < 0) && ((uVar7 & 1) != 0)) {
        *(undefined4 *)(*param_1 + 0x20) = 2;
        param_1[0x24] = param_1[0x24] | 4;
      }
      if (((int)(uVar4 << 0x1d) < 0) && ((uVar7 & 1) != 0)) {
        *(undefined4 *)(*param_1 + 0x20) = 4;
        param_1[0x24] = param_1[0x24] | 2;
      }
      if (((int)(uVar4 << 0x1c) < 0) && ((uVar3 & 0x20) != 0 || uVar10 != 0)) {
        *(undefined4 *)(*param_1 + 0x20) = 8;
        param_1[0x24] = param_1[0x24] | 8;
      }
      if (((int)(uVar4 << 0x14) < 0) && ((int)(uVar3 << 5) < 0)) {
        *(undefined4 *)(*param_1 + 0x20) = 0x800;
        param_1[0x24] = param_1[0x24] | 0x20;
      }
      if (param_1[0x24] == 0) {
        return;
      }
      if ((((int)(uVar4 << 0x1a) < 0) && ((uVar3 & 0x20) != 0 || (uVar7 & 0x10000000) != 0)) &&
         ((code *)param_1[0x1d] != (code *)0x0)) {
        (*(code *)param_1[0x1d])(param_1);
      }
      if ((-1 < *(int *)(*param_1 + 8) << 0x19) && ((param_1[0x24] & 0x28U) == 0)) {
        FUN_08005f42(param_1);
        param_1[0x24] = 0;
        return;
      }
      case_reset_context_transfer(param_1);
      iVar5 = *param_1;
      if (-1 < *(int *)(iVar5 + 8) << 0x19) {
LAB_08006072:
        FUN_08005f42(param_1);
        return;
      }
      uVar3 = 0;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        uVar3 = isIRQinterruptsEnabled();
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts(1);
      }
      *(uint *)(iVar5 + 8) = *(uint *)(iVar5 + 8) & 0xffffffbf;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((uVar3 & 1) == 1);
      }
      if (*piVar9 == 0) goto LAB_08006072;
      *(undefined4 *)(*piVar9 + 0x38) = DAT_0800623c;
      iVar5 = FUN_080048e6(*piVar9);
      if (iVar5 == 0) {
        return;
      }
      param_1 = (int *)*piVar9;
      pcVar6 = (code *)param_1[0xe];
      goto LAB_0800606e;
    }
LAB_08006086:
    if (((param_1[0x1b] == 1) && ((int)(uVar4 << 0x1b) < 0)) && ((int)(uVar3 << 0x1b) < 0)) {
      puVar8[8] = 0x10;
      puVar8 = (uint *)*param_1;
      if ((int)(puVar8[2] * 0x2000000) < 0) {
        uVar3 = *(uint *)(*(int *)*piVar9 + 4);
        uVar4 = uVar3 & 0xffff;
        if ((uVar4 != 0) && (uVar4 < *(ushort *)(param_1 + 0x17))) {
          *(short *)((int)param_1 + 0x5e) = (short)uVar3;
          if (-1 < **(int **)*piVar9 << 0x1a) {
            uVar3 = 0;
            bVar1 = (bool)isCurrentModePrivileged();
            if (bVar1) {
              uVar3 = isIRQinterruptsEnabled();
            }
            bVar1 = (bool)isCurrentModePrivileged();
            if (bVar1) {
              enableIRQinterrupts(1);
            }
            *puVar8 = *puVar8 & 0xfffffeff;
            bVar1 = (bool)isCurrentModePrivileged();
            if (bVar1) {
              enableIRQinterrupts((uVar3 & 1) == 1);
            }
            uVar3 = 0;
            bVar1 = (bool)isCurrentModePrivileged();
            if (bVar1) {
              uVar3 = isIRQinterruptsEnabled();
            }
            bVar1 = (bool)isCurrentModePrivileged();
            if (bVar1) {
              enableIRQinterrupts(1);
            }
            *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & 0xfffffffe;
            bVar1 = (bool)isCurrentModePrivileged();
            if (bVar1) {
              enableIRQinterrupts((uVar3 & 1) == 1);
            }
            uVar3 = 0;
            bVar1 = (bool)isCurrentModePrivileged();
            if (bVar1) {
              uVar3 = isIRQinterruptsEnabled();
            }
            bVar1 = (bool)isCurrentModePrivileged();
            if (bVar1) {
              enableIRQinterrupts(1);
            }
            *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & 0xffffffbf;
            bVar1 = (bool)isCurrentModePrivileged();
            if (bVar1) {
              enableIRQinterrupts((uVar3 & 1) == 1);
            }
            param_1[0x23] = 0x20;
            param_1[0x1b] = 0;
            uVar3 = 0;
            bVar1 = (bool)isCurrentModePrivileged();
            if (bVar1) {
              uVar3 = isIRQinterruptsEnabled();
            }
            bVar1 = (bool)isCurrentModePrivileged();
            if (bVar1) {
              enableIRQinterrupts(1);
            }
            *(uint *)*param_1 = *(uint *)*param_1 & 0xffffffef;
            bVar1 = (bool)isCurrentModePrivileged();
            if (bVar1) {
              enableIRQinterrupts((uVar3 & 1) == 1);
            }
            FUN_0800487a(*piVar9);
          }
          param_1[0x1c] = 2;
          sVar2 = (short)param_1[0x17] - *(short *)((int)param_1 + 0x5e);
LAB_080061a6:
          FUN_08005e6a(param_1,sVar2);
          return;
        }
      }
      else {
        sVar2 = (short)param_1[0x17] - *(short *)((int)param_1 + 0x5e);
        if ((*(short *)((int)param_1 + 0x5e) != 0) && (sVar2 != 0)) {
          uVar3 = 0;
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            uVar3 = isIRQinterruptsEnabled();
          }
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            enableIRQinterrupts(1);
          }
          *puVar8 = *puVar8 & 0xfffffedf;
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            enableIRQinterrupts((uVar3 & 1) == 1);
          }
          uVar3 = 0;
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            uVar3 = isIRQinterruptsEnabled();
          }
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            enableIRQinterrupts(1);
          }
          *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & ~DAT_08006234;
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            enableIRQinterrupts((uVar3 & 1) == 1);
          }
          param_1[0x23] = 0x20;
          param_1[0x1b] = 0;
          param_1[0x1d] = 0;
          uVar3 = 0;
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            uVar3 = isIRQinterruptsEnabled();
          }
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            enableIRQinterrupts(1);
          }
          *(uint *)*param_1 = *(uint *)*param_1 & 0xffffffef;
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            enableIRQinterrupts((uVar3 & 1) == 1);
          }
          param_1[0x1c] = 2;
          goto LAB_080061a6;
        }
      }
      return;
    }
    if (((int)(uVar4 << 0xb) < 0) && ((int)(uVar7 << 9) < 0)) {
      puVar8[8] = 0x100000;
      FUN_08005efe(param_1);
      return;
    }
    if ((-1 < (int)(uVar4 << 0x18)) || ((uVar3 & 0x80) == 0 && (uVar7 & 0x800000) == 0)) {
      if (((int)(uVar4 << 0x19) < 0) && ((int)(uVar3 << 0x19) < 0)) {
        uVar3 = 0;
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          uVar3 = isIRQinterruptsEnabled();
        }
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          enableIRQinterrupts(1);
        }
        *puVar8 = *puVar8 & 0xffffffbf;
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          enableIRQinterrupts((uVar3 & 1) == 1);
        }
        param_1[0x22] = 0x20;
        param_1[0x1e] = 0;
        case_hook_08006776();
        return;
      }
      if (((int)(uVar4 << 8) < 0) && ((int)(uVar3 << 1) < 0)) {
        FUN_08005efc(param_1);
      }
      else if (((int)(uVar4 << 7) < 0) && ((int)uVar3 < 0)) {
        FUN_08005e6c(param_1);
        return;
      }
      return;
    }
    pcVar6 = (code *)param_1[0x1e];
  }
  if (pcVar6 == (code *)0x0) {
    return;
  }
LAB_0800606e:
  (*pcVar6)(param_1);
  return;
}

