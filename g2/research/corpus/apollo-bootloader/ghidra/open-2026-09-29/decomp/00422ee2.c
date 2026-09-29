
undefined8 FUN_00422ee2(int param_1,undefined4 *param_2)

{
  bool bVar1;
  uint uVar2;
  undefined4 uVar3;
  
  uVar2 = critical_save();
  uVar3 = DAT_00423850;
  if (*(char *)(param_1 + 0x119) == '\0') {
    *(undefined1 *)(param_1 + 0x119) = 1;
    *(undefined1 *)(param_1 + 0xd4) = *(undefined1 *)(param_2 + 0xd);
    *(undefined4 *)(param_1 + 0xa0) = *param_2;
    *(undefined4 *)(param_1 + 0xa4) = param_2[1];
    *(undefined4 *)(param_1 + 0xa8) = param_2[2];
    *(undefined4 *)(param_1 + 0xac) = param_2[3];
    *(undefined4 *)(param_1 + 0xb0) = param_2[4];
    *(undefined4 *)(param_1 + 0xb4) = param_2[5];
    *(undefined4 *)(param_1 + 0xb8) = param_2[6];
    *(undefined4 *)(param_1 + 0xd8) = 0;
    *(undefined1 *)(param_1 + 0xde) = 0;
    uVar3 = 0;
  }
  bVar1 = (bool)isCurrentModePrivileged();
  if (bVar1) {
    enableIRQinterrupts((uVar2 & 1) == 1);
  }
  return CONCAT44(uVar2,uVar3);
}

