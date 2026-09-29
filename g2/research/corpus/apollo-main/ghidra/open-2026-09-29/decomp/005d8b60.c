
undefined8 FUN_005d8b60(uint *param_1,undefined4 param_2,undefined4 *param_3,undefined4 param_4)

{
  int iVar1;
  int iVar2;
  uint uVar3;
  undefined4 *puVar4;
  
  iVar1 = 0;
  puVar4 = (undefined4 *)0x0;
  uVar3 = *param_1 + 1;
  if ((uVar3 < param_1[1]) || (iVar1 = FUN_005d8b2a(param_1,uVar3,param_2), iVar1 == 0)) {
    iVar2 = param_1[2] + uVar3 * 0xc;
    puVar4 = (undefined4 *)(iVar2 + -0xc);
    *puVar4 = 0;
    *(undefined4 *)(iVar2 + -8) = 0;
    *(undefined4 *)(iVar2 + -4) = 0;
    *param_1 = uVar3;
  }
  *param_3 = puVar4;
  return CONCAT44(param_4,iVar1);
}

