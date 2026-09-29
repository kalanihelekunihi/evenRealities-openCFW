
void case_copy64_protected(undefined4 *param_1,undefined4 *param_2)

{
  bool bVar1;
  int iVar2;
  uint uVar3;
  byte bVar4;
  undefined4 uVar5;
  
  iVar2 = DAT_08003f68;
  bVar4 = 0;
  *(uint *)(DAT_08003f68 + 0x14) = *(uint *)(DAT_08003f68 + 0x14) | 0x40000;
  uVar3 = 0;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    uVar3 = isIRQinterruptsEnabled();
  }
  disableIRQinterrupts();
  do {
    uVar5 = *param_2;
    param_2 = param_2 + 1;
    bVar4 = bVar4 + 1;
    *param_1 = uVar5;
    param_1 = param_1 + 1;
  } while (bVar4 < 0x40);
  do {
  } while ((*(uint *)(iVar2 + 0x10) & 0x3ffff) >> 0x10 != 0);
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar3 & 1) == 1);
  }
  return;
}

