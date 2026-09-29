
undefined4 FUN_0043f648(int param_1)

{
  int iVar1;
  undefined4 uVar2;
  undefined4 unaff_r7;
  
  *(ushort *)(param_1 + 0x2a) = *(ushort *)(param_1 + 0x2a) | 1;
  iVar1 = FUN_0044dbc4();
  *(ushort *)(iVar1 + 0x2a) = *(ushort *)(iVar1 + 0x2a) | 4;
  uVar2 = FUN_0044dc0a();
  FUN_0044fdbe(uVar2,0x38,0);
  return unaff_r7;
}

