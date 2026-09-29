
undefined8 FUN_0045fc5a(int param_1,undefined4 *param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 *puVar3;
  uint uVar4;
  undefined4 uVar5;
  
  if ((param_1 == 0) || (param_2 == (undefined4 *)0x0)) {
    uVar1 = 0;
  }
  else {
    iVar2 = FUN_0045fbba(param_1 + 0x24);
    if (iVar2 == 0) {
      puVar3 = (undefined4 *)(param_1 + 0x24 + (uint)*(byte *)(param_1 + 0xe4) * 0xc);
      uVar1 = puVar3[1];
      uVar5 = puVar3[2];
      *param_2 = *puVar3;
      param_2[1] = uVar1;
      param_2[2] = uVar5;
      uVar4 = *(byte *)(param_1 + 0xe4) + 1;
      *(char *)(param_1 + 0xe4) = (char)uVar4 + (char)(uVar4 / 0x10) * -0x10;
      *(char *)(param_1 + 0xe6) = *(char *)(param_1 + 0xe6) + -1;
      uVar1 = 1;
    }
    else {
      uVar1 = 0;
    }
  }
  return CONCAT44(param_4,uVar1);
}

