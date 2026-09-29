
void FUN_005675b4(void)

{
  int *piVar1;
  undefined4 uVar2;
  int iVar3;
  
  uVar2 = FUN_00515096();
  piVar1 = DAT_005675e4;
  *(undefined4 *)(*DAT_005675e4 + 100) = uVar2;
  uVar2 = FUN_00514ebc();
  *(undefined4 *)(*piVar1 + 0x68) = uVar2;
  uVar2 = FUN_0051510e();
  iVar3 = *piVar1;
  *(undefined4 *)(iVar3 + 0x6c) = uVar2;
  *(undefined4 *)(iVar3 + 0x5c) = 800;
  *(undefined4 *)(iVar3 + 0x60) = 600;
  *(undefined4 *)(iVar3 + 0x70) = 0;
  return;
}

