
void case_receive_u16(int *param_1)

{
  bool bVar1;
  int iVar2;
  uint uVar3;
  
  iVar2 = *param_1;
  if (param_1[0x23] == 0x22) {
    *(ushort *)param_1[0x16] = (ushort)*(undefined4 *)(iVar2 + 0x24) & *(ushort *)(param_1 + 0x18);
    param_1[0x16] = param_1[0x16] + 2;
    *(short *)((int)param_1 + 0x5e) = *(short *)((int)param_1 + 0x5e) + -1;
    if (*(short *)((int)param_1 + 0x5e) == 0) {
      uVar3 = 0;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        uVar3 = isIRQinterruptsEnabled();
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts(1);
      }
      *(uint *)*param_1 = *(uint *)*param_1 & 0xfffffedf;
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
      param_1[0x23] = 0x20;
      param_1[0x1d] = 0;
      param_1[0x1c] = 0;
      if (param_1[0x1b] != 1) {
        case_process_frame_byte();
        return;
      }
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
      if (-1 < (int)(~*(uint *)(*param_1 + 0x1c) << 0x1b)) {
        *(undefined4 *)(*param_1 + 0x20) = 0x10;
      }
      FUN_08005e6a(param_1,(short)param_1[0x17]);
      return;
    }
  }
  else {
    *(uint *)(iVar2 + 0x18) = *(uint *)(iVar2 + 0x18) | 8;
  }
  return;
}

