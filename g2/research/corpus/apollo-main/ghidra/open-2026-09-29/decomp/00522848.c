
void FUN_00522848(undefined4 *param_1)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  
  puVar1 = (undefined4 *)FUN_00514aec(9);
  if (puVar1 != (undefined4 *)0x0) {
    *puVar1 = 0x174;
    uVar2 = param_1[5];
    puVar1[2] = 0x168;
    puVar1[1] = uVar2;
    uVar2 = param_1[2];
    puVar1[4] = 0x178;
    puVar1[3] = uVar2;
    uVar2 = param_1[6];
    puVar1[6] = 0x17c;
    puVar1[5] = uVar2;
    uVar2 = param_1[7];
    puVar1[8] = 0x180;
    puVar1[7] = uVar2;
    uVar2 = param_1[8];
    puVar1[10] = 0x160;
    puVar1[9] = uVar2;
    uVar2 = *param_1;
    puVar1[0xc] = 0x164;
    puVar1[0xb] = uVar2;
    uVar2 = param_1[1];
    puVar1[0xe] = 0x16c;
    puVar1[0xd] = uVar2;
    uVar2 = param_1[3];
    puVar1[0x10] = 0x170;
    puVar1[0xf] = uVar2;
    puVar1[0x11] = param_1[4];
  }
  return;
}

