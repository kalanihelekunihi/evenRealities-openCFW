
void case_apply_controller_profile(uint *param_1,uint *param_2)

{
  uint *puVar1;
  uint *puVar2;
  uint *puVar3;
  uint uVar4;
  
  puVar3 = DAT_0800854c;
  puVar2 = DAT_08008548;
  puVar1 = DAT_0800853c;
  uVar4 = *param_1;
  if (((param_1 == DAT_0800853c) || (param_1 == DAT_08008540)) || (param_1 == DAT_08008544)) {
    uVar4 = uVar4 & 0xffffff8f | param_2[1];
  }
  if ((((param_1 == DAT_0800853c) || (param_1 == DAT_08008540)) ||
      ((param_1 == DAT_08008544 || ((param_1 == DAT_08008550 || (param_1 == DAT_08008548)))))) ||
     ((param_1 == DAT_0800854c || (param_1 == DAT_08008554)))) {
    uVar4 = uVar4 & 0xfffffcff | param_2[3];
  }
  *param_1 = uVar4 & 0xffffff7f | param_2[5];
  param_1[0xb] = param_2[2];
  param_1[10] = *param_2;
  if ((((param_1 == puVar1) || (param_1 == puVar2)) || (param_1 == puVar3)) ||
     (param_1 == DAT_08008554)) {
    param_1[0xc] = param_2[4];
  }
  param_1[5] = 1;
  return;
}

