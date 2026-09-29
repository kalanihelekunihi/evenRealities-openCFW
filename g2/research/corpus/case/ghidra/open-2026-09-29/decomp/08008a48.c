
uint case_drain_receive_u8(int *param_1)

{
  bool bVar1;
  int iVar2;
  int iVar3;
  int iVar4;
  uint uVar5;
  uint uVar6;
  int *piVar7;
  uint uVar8;
  
  iVar2 = param_1[0x18];
  piVar7 = (int *)*param_1;
  uVar8 = piVar7[7];
  iVar4 = *piVar7;
  uVar5 = piVar7[2];
  if (param_1[0x23] == 0x22) {
    iVar3 = param_1[0x1a];
    while (((short)iVar3 != 0 && ((int)(uVar8 << 0x1a) < 0))) {
      *(byte *)param_1[0x16] = (byte)*(undefined4 *)(*param_1 + 0x24) & (byte)(short)iVar2;
      param_1[0x16] = param_1[0x16] + 1;
      *(short *)((int)param_1 + 0x5e) = *(short *)((int)param_1 + 0x5e) + -1;
      uVar8 = *(uint *)(*param_1 + 0x1c);
      if ((uVar8 & 7) != 0) {
        if (((uVar8 & 1) != 0) && (iVar4 << 0x17 < 0)) {
          *(undefined4 *)(*param_1 + 0x20) = 1;
          param_1[0x24] = param_1[0x24] | 1;
        }
        if (((int)(uVar8 << 0x1e) < 0) && ((uVar5 & 1) != 0)) {
          *(undefined4 *)(*param_1 + 0x20) = 2;
          param_1[0x24] = param_1[0x24] | 4;
        }
        if (((int)(uVar8 << 0x1d) < 0) && ((uVar5 & 1) != 0)) {
          *(undefined4 *)(*param_1 + 0x20) = 4;
          param_1[0x24] = param_1[0x24] | 2;
        }
        if (param_1[0x24] != 0) {
          FUN_08005f42(param_1);
          param_1[0x24] = 0;
        }
      }
      if (*(short *)((int)param_1 + 0x5e) == 0) {
        uVar6 = 0;
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          uVar6 = isIRQinterruptsEnabled();
        }
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          enableIRQinterrupts(1);
        }
        *(uint *)*param_1 = *(uint *)*param_1 & 0xfffffeff;
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          enableIRQinterrupts((uVar6 & 1) == 1);
        }
        uVar6 = 0;
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          uVar6 = isIRQinterruptsEnabled();
        }
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          enableIRQinterrupts(1);
        }
        *(uint *)(*param_1 + 8) = *(uint *)(*param_1 + 8) & DAT_08008bd0;
        bVar1 = (bool)isCurrentModePrivileged();
        if (bVar1) {
          enableIRQinterrupts((uVar6 & 1) == 1);
        }
        param_1[0x23] = 0x20;
        param_1[0x1d] = 0;
        param_1[0x1c] = 0;
        if (param_1[0x1b] == 1) {
          param_1[0x1b] = 0;
          uVar6 = 0;
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            uVar6 = isIRQinterruptsEnabled();
          }
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            enableIRQinterrupts(1);
          }
          *(uint *)*param_1 = *(uint *)*param_1 & 0xffffffef;
          bVar1 = (bool)isCurrentModePrivileged();
          if (bVar1) {
            enableIRQinterrupts((uVar6 & 1) == 1);
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
    uVar5 = (uint)*(ushort *)((int)param_1 + 0x5e);
    if ((uVar5 != 0) && (uVar5 < *(ushort *)(param_1 + 0x1a))) {
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
      param_1[0x1d] = DAT_08008bd4;
      uVar5 = 0;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        uVar5 = isIRQinterruptsEnabled();
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts(1);
      }
      *(uint *)*param_1 = *(uint *)*param_1 | 0x20;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((uVar5 & 1) == 1);
      }
    }
  }
  else {
    uVar5 = piVar7[6] | 8;
    piVar7[6] = uVar5;
  }
  return uVar5;
}

