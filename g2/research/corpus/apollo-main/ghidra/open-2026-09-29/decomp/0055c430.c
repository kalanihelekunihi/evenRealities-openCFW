
undefined4 FUN_0055c430(uint *param_1)

{
  int iVar1;
  undefined4 uVar2;
  uint *puVar3;
  
  iVar1 = DAT_0055c548;
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0055cc14)) {
    uVar2 = 2;
  }
  else if ((int)(*param_1 << 6) < 0) {
    if (param_1[9] == 0) {
      puVar3 = (uint *)(DAT_0055c548 + param_1[1] * 0x1000 + 0x11c);
      *puVar3 = *puVar3 & 0xfffffffe;
      puVar3 = (uint *)(iVar1 + param_1[1] * 0x1000 + 0x11c);
      *puVar3 = *puVar3 & 0xffffffef;
      FUN_0055c11a();
      *param_1 = *param_1 & 0xfdffffff;
      uVar2 = 0;
    }
    else {
      uVar2 = 3;
    }
  }
  else {
    uVar2 = 0;
  }
  return uVar2;
}

