
undefined8 FUN_0044b0b6(uint param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  bool bVar1;
  uint uVar2;
  
  uVar2 = FUN_00473940();
  *DAT_0044b570 = *DAT_0044b570 & 0xffffffbf | (param_1 & 1) << 6;
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar2 & 1) == 1);
  }
  return CONCAT44(param_4,uVar2);
}

