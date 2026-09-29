
void FUN_00515676(void)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = DAT_005156ac;
  *(byte *)(*DAT_005156ac + 0x1bd) = *(byte *)(*DAT_005156ac + 0x90) & 1;
  iVar2 = *piVar1;
  *(uint *)(iVar2 + 0x90) = *(uint *)(iVar2 + 0x90) & 0xfffffffe;
  FUN_00561810(iVar2 + 0xa4);
  FUN_00561810(*piVar1 + 200);
  return;
}

