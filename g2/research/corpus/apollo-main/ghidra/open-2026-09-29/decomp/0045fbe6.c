
undefined4 FUN_0045fbe6(int param_1,int param_2)

{
  undefined4 uVar1;
  int iVar2;
  uint uVar3;
  undefined4 *puVar4;
  
  if ((param_1 == 0) || (param_2 == 0)) {
    uVar1 = 0;
  }
  else {
    iVar2 = FUN_0045fbd0(param_1 + 0x24);
    if (iVar2 == 0) {
      puVar4 = (undefined4 *)(param_1 + 0x24 + (uint)*(byte *)(param_1 + 0xe5) * 0xc);
      uVar1 = FUN_00450286(param_2);
      *puVar4 = uVar1;
      if (*(undefined4 **)(param_2 + 0x10) == (undefined4 *)0x0) {
        puVar4[1] = 0;
        *(undefined1 *)(puVar4 + 2) = 0;
      }
      else {
        puVar4[1] = **(undefined4 **)(param_2 + 0x10);
        *(undefined1 *)(puVar4 + 2) = 1;
      }
      uVar3 = *(byte *)(param_1 + 0xe5) + 1;
      *(char *)(param_1 + 0xe5) = (char)uVar3 + (char)(uVar3 / 0x10) * -0x10;
      *(char *)(param_1 + 0xe6) = *(char *)(param_1 + 0xe6) + '\x01';
      uVar1 = 1;
    }
    else {
      uVar1 = 0;
    }
  }
  return uVar1;
}

