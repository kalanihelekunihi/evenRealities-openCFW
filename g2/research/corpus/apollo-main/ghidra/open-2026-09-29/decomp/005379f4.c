
void smpGenerateLtk(int param_1)

{
  undefined1 uVar1;
  int iVar2;
  
  iVar2 = *(int *)(param_1 + 0x30);
  FUN_0053634e(iVar2 + 4,*(undefined1 *)(iVar2 + 0x20));
  FUN_0043c0e4(iVar2 + 4 + (uint)*(byte *)(iVar2 + 0x20),0x10 - (uint)*(byte *)(iVar2 + 0x20),0);
  *(ushort *)(iVar2 + 0x1c) =
       (ushort)*(byte *)(iVar2 + 0x31) * 0x100 + (ushort)*(byte *)(iVar2 + 0x30);
  FUN_00439be4(iVar2 + 0x14,iVar2 + 0x32,8);
  *(undefined1 *)(iVar2 + 0x1e) = 1;
  if ((int)((uint)*(byte *)(param_1 + 0x40) << 0x1d) < 0) {
    uVar1 = 2;
  }
  else {
    uVar1 = 1;
  }
  *(undefined1 *)(iVar2 + 0x1f) = uVar1;
  *(undefined1 *)(iVar2 + 2) = 0x2f;
  DmSmpCbackExec(iVar2);
  return;
}

