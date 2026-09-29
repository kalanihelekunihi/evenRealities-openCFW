
undefined4 case_start_context_transfer(int *param_1,uint param_2,int param_3)

{
  bool bVar1;
  undefined4 uVar2;
  uint uVar3;
  uint *puVar4;
  
  if (param_1[0x23] != 0x20) {
    return 2;
  }
  if (((param_2 != 0) && (param_3 != 0)) &&
     ((param_1[2] != 0x1000 || ((param_1[4] != 0 || ((param_2 & 1) == 0)))))) {
    param_1[0x1b] = 0;
    puVar4 = (uint *)*param_1;
    if ((int)(puVar4[1] << 8) < 0) {
      uVar3 = 0;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        uVar3 = isIRQinterruptsEnabled();
      }
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts(1);
      }
      *puVar4 = *puVar4 | 0x4000000;
      bVar1 = (bool)isCurrentModePrivileged();
      if (bVar1) {
        enableIRQinterrupts((uVar3 & 1) == 1);
      }
    }
    uVar2 = case_begin_receive();
    return uVar2;
  }
  return 1;
}

