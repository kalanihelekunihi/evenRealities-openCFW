
void touch_sub_2f20(uint param_1)

{
  uint uVar1;
  uint uVar2;
  
  uVar1 = DAT_00006238;
  for (uVar2 = 0x8000; (1 < uVar1 && ((param_1 & uVar2) == 0)); uVar2 = uVar2 >> 1) {
    uVar1 = uVar1 >> 1;
  }
  return;
}

