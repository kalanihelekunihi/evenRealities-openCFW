
undefined4 anccActionListPush(undefined1 *param_1)

{
  int iVar1;
  ushort uVar2;
  
  iVar1 = DAT_004bf6c0;
  uVar2 = 0;
  while( true ) {
    if (0x3f < uVar2) {
      uVar2 = 0;
      while( true ) {
        if (0x3f < uVar2) {
          return 0;
        }
        if (*(char *)((uint)uVar2 * 0xc + DAT_004bf6c0 + 0x24) == '\0') break;
        uVar2 = uVar2 + 1;
      }
      *(undefined4 *)((uint)uVar2 * 0xc + DAT_004bf6c0 + 0x20) = *(undefined4 *)(param_1 + 4);
      *(undefined1 *)((uint)uVar2 * 0xc + iVar1 + 0x1c) = *param_1;
      *(undefined1 *)((uint)uVar2 * 0xc + iVar1 + 0x1d) = param_1[1];
      *(undefined1 *)((uint)uVar2 * 0xc + iVar1 + 0x1e) = param_1[2];
      *(undefined1 *)((uint)uVar2 * 0xc + iVar1 + 0x1f) = param_1[3];
      *(undefined1 *)(iVar1 + (uint)uVar2 * 0xc + 0x24) = 1;
      return 1;
    }
    if ((*(int *)((uint)uVar2 * 0xc + DAT_004bf6c0 + 0x20) == *(int *)(param_1 + 4)) &&
       (*(char *)((uint)uVar2 * 0xc + DAT_004bf6c0 + 0x24) == '\x01')) break;
    uVar2 = uVar2 + 1;
  }
  *(undefined4 *)((uint)uVar2 * 0xc + DAT_004bf6c0 + 0x20) = *(undefined4 *)(param_1 + 4);
  *(undefined1 *)((uint)uVar2 * 0xc + iVar1 + 0x1c) = *param_1;
  *(undefined1 *)((uint)uVar2 * 0xc + iVar1 + 0x1d) = param_1[1];
  *(undefined1 *)((uint)uVar2 * 0xc + iVar1 + 0x1e) = param_1[2];
  *(undefined1 *)((uint)uVar2 * 0xc + iVar1 + 0x1f) = param_1[3];
  return 1;
}

