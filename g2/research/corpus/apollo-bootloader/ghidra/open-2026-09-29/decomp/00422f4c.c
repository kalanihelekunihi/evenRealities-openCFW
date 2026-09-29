
undefined8 FUN_00422f4c(int param_1,undefined4 *param_2)

{
  bool bVar1;
  uint uVar2;
  undefined4 uVar3;
  
  uVar2 = critical_save();
  uVar3 = DAT_00423854;
  if (*(char *)(param_1 + 0x11a) == '\0') {
    *(undefined1 *)(param_1 + 0x11a) = 1;
    *(undefined1 *)(param_1 + 0x98) = *(undefined1 *)(param_2 + 0xd);
    *(undefined4 *)(param_1 + 100) = *param_2;
    *(undefined4 *)(param_1 + 0x68) = param_2[1];
    *(undefined4 *)(param_1 + 0x6c) = param_2[2];
    *(undefined4 *)(param_1 + 0x70) = param_2[3];
    *(undefined4 *)(param_1 + 0x74) = param_2[4];
    *(undefined4 *)(param_1 + 0x78) = param_2[5];
    *(undefined4 *)(param_1 + 0x7c) = param_2[6];
    *(undefined4 *)(param_1 + 0x9c) = 0;
    uVar3 = 0;
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar2 & 1) == 1);
  }
  return CONCAT44(uVar2,uVar3);
}

