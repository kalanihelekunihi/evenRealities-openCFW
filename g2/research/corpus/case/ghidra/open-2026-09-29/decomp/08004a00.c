
void case_build_register_descriptor(undefined4 *param_1)

{
  int iVar1;
  uint uVar2;
  undefined4 uVar3;
  int iVar4;
  
  *param_1 = 7;
  iVar1 = DAT_08004a64;
  iVar4 = param_1[1];
  if (iVar4 == 1) {
    param_1[2] = *(uint *)(DAT_08004a64 + 0x2c) & 0x7f;
    uVar2 = *(uint *)(iVar1 + 0x2c);
  }
  else if (iVar4 == 4) {
    param_1[2] = *(uint *)(DAT_08004a64 + 0x4c) & 0x7f;
    uVar2 = *(uint *)(iVar1 + 0x4c);
  }
  else if (iVar4 == 8) {
    param_1[2] = *(uint *)(DAT_08004a64 + 0x50) & 0x7f;
    uVar2 = *(uint *)(iVar1 + 0x50);
  }
  else {
    param_1[2] = *(uint *)(DAT_08004a64 + 0x30) & 0x7f;
    uVar2 = *(uint *)(iVar1 + 0x30);
  }
  param_1[3] = (uVar2 & 0x7fffff) >> 0x10;
  uVar3 = case_flash_status_classify();
  param_1[4] = uVar3;
  uVar3 = case_flash_status_masked();
  param_1[6] = uVar3;
  param_1[5] = DAT_08004a68;
  return;
}

