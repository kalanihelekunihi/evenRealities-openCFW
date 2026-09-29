
int * case_drain_receive_u16(uint *param_1)

{
  bool bVar1;
  uint uVar2;
  int *piVar3;
  uint uVar4;
  uint uVar5;
  int iVar6;
  uint uVar7;
  uint uVar8;
  
  uVar5 = param_1[0x18];
  piVar3 = (int *)*param_1;
  uVar8 = piVar3[7];
  iVar6 = *piVar3;
  uVar7 = piVar3[2];
  if (param_1[0x23] == 0x22) {
    uVar2 = param_1[0x1a];
    while (((short)uVar2 != 0 && ((int)(uVar8 << 0x1a) < 0))) {
      *(ushort *)param_1[0x16] = (ushort)*(undefined4 *)(*param_1 + 0x24) & (ushort)uVar5;
      param_1[0x16] = param_1[0x16] + 2;
      *(short *)((int)param_1 + 0x5e) = *(short *)((int)param_1 + 0x5e) + -1;
      uVar8 = *(uint *)(*param_1 + 0x1c);
      if ((uVar8 & 7) != 0) {
        if (((uVar8 & 1) != 0) && (iVar6 << 0x17 < 0)) {
          *(undefined4 *)(*param_1 + 0x20) = 1;
          param_1[0x24] = param_1[0x24] | 1;
        }
        if (((int)(uVar8 << 0x1e) < 0) && ((uVar7 & 1) != 0)) {
          *(undefined4 *)(*param_1 + 0x20) = 2;
          param_1[0x24] = param_1[0x24] | 4;
        }
        if (((int)(uVar8 << 0x1d) < 0) && ((uVar7 & 1) != 0)) {
          *(undefined4 *)(*param_1 + 0x20) = 4;
          param_1[0x24] = param_1[0x24] | 2;
        }
        if (param_1[0x24] != 0) {
          FUN_08005f42(param_1);
          param_1[0x24] = 0;
        }
      }
      if (*(short *)((int)param_1 + 0x5e) == 0) {
        uVar4 = 0;
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          uVar4 = isIRQinterruptsEnabled();
        }
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          enableIRQinterrupts(1);
        }
        *(uint *)*param_1 = *(uint *)*param_1 & 0xfffffeff;
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          enableIRQinterrupts((uVar4 & 1) == 1);
        }
        uVar4 = 0;
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          uVar4 = isIRQinterruptsEnabled();
        }
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          enableIRQinterrupts(1);
        }
        *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & DAT_08008990;
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          enableIRQinterrupts((uVar4 & 1) == 1);
        }
        param_1[0x23] = 0x20;
        param_1[0x1d] = 0;
        param_1[0x1c] = 0;
        if (param_1[0x1b] == 1) {
          param_1[0x1b] = 0;
          uVar4 = 0;
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            uVar4 = isIRQinterruptsEnabled();
          }
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            enableIRQinterrupts(1);
          }
          *(uint *)*param_1 = *(uint *)*param_1 & 0xffffffef;
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            enableIRQinterrupts((uVar4 & 1) == 1);
          }
          if (-1 < (int)(~*(uint *)(*param_1 + 0x1c) << 0x1b)) {
            *(undefined4 *)(*param_1 + 0x20) = 0x10;
          }
          FUN_08005e6a(param_1,(short)param_1[0x17]);
        }
        else {
          case_process_frame_byte(param_1);
        }
      }
    }
    piVar3 = (int *)(uint)*(ushort *)((int)param_1 + 0x5e);
    if ((piVar3 != (int *)0x0) && (piVar3 < (int *)(uint)(ushort)param_1[0x1a])) {
      uVar5 = 0;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        uVar5 = isIRQinterruptsEnabled();
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts(1);
      }
      *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & 0xefffffff;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((uVar5 & 1) == 1);
      }
      param_1[0x1d] = DAT_08008994;
      piVar3 = (int *)0x0;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        piVar3 = (int *)isIRQinterruptsEnabled();
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts(1);
      }
      *(uint *)*param_1 = *(uint *)*param_1 | 0x20;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts(((uint)piVar3 & 1) == 1);
      }
    }
  }
  else {
    piVar3[6] = piVar3[6] | 8;
  }
  return piVar3;
}

