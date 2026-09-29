
undefined4 FUN_005390fc(uint *param_1)

{
  undefined4 uVar1;
  uint *puVar2;
  
  if ((param_1 == (uint *)0x0) || ((*param_1 & 0x1ffffff) != DAT_0053924c)) {
    uVar1 = 2;
  }
  else if ((int)(*param_1 << 6) < 0) {
    **(uint **)param_1[9] = **(uint **)param_1[9] & 0xfffffffe;
    puVar2 = (uint *)**(int **)(param_1[9] + 4);
    while ((*puVar2 & 0xfffffffe) != *(uint *)(param_1[9] + 8)) {
      if (*puVar2 == *(uint *)(param_1[9] + 4)) {
        puVar2 = (uint *)puVar2[1];
      }
      else {
        puVar2 = puVar2 + 2;
      }
    }
    *puVar2 = *(uint *)(param_1[9] + 8);
    **(int **)(param_1[9] + 4) = (int)puVar2;
    *param_1 = *param_1 & 0xfdffffff;
    uVar1 = 0;
  }
  else {
    uVar1 = 0;
  }
  return uVar1;
}

