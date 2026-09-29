
void FUN_0047b3e2(int param_1,ushort param_2,undefined2 param_3)

{
  undefined1 uVar1;
  int iVar2;
  
  *(undefined2 *)(param_1 + (uint)param_2 * 2 + 0x6c) = param_3;
  uVar1 = FUN_004bb05a();
  iVar2 = FUN_004bad26(uVar1);
  if (iVar2 != 0) {
    FUN_00479b74(param_1);
    FUN_0047b730(param_1);
  }
  return;
}

