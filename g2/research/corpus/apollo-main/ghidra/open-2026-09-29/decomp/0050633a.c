
uint FUN_0050633a(int param_1,undefined2 *param_2)

{
  undefined2 uVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = FUN_00508e5c(param_1,0x12,2,param_2);
  uVar3 = FUN_00508e5c(param_1,0x12,2,param_2);
  if (*(char *)(param_1 + 0x11) == '\x01') {
    uVar1 = CONCAT11(*(undefined1 *)param_2,*(undefined1 *)((int)param_2 + 1));
  }
  else {
    uVar1 = *param_2;
  }
  *param_2 = uVar1;
  return uVar2 | uVar3;
}

