
void FUN_004d5888(undefined4 *param_1,undefined4 *param_2)

{
  bool bVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  uint uVar4;
  
  uVar4 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar4 = isIRQinterruptsEnabled();
  }
  disableIRQinterrupts();
  uVar2 = *param_1;
  uVar3 = *param_1;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar4 & 1) == 1);
  }
  *param_2 = *param_1;
  param_2[1] = uVar2;
  param_2[2] = uVar3;
  return;
}

