
void FUN_00414cbc(int param_1,ushort param_2,undefined4 *param_3)

{
  uint uVar1;
  undefined4 uVar2;
  
  if (param_2 == 0x3ff) {
    uVar1 = 0;
  }
  else {
    uVar1 = DAT_004152dc | (uint)param_2 << 10;
  }
  *(uint *)(param_1 + 0x30) = uVar1 | *(uint *)(param_1 + 0x30) & 0x800003ff;
  if (param_2 == 0x3ff) {
    uVar2 = 0;
  }
  else {
    uVar2 = *param_3;
  }
  *(undefined4 *)(param_1 + 0x34) = uVar2;
  if (param_2 == 0x3ff) {
    uVar2 = 0;
  }
  else {
    uVar2 = param_3[1];
  }
  *(undefined4 *)(param_1 + 0x38) = uVar2;
  return;
}

