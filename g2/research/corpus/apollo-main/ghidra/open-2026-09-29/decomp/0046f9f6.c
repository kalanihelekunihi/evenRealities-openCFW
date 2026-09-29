
void FUN_0046f9f6(void)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 local_10;
  undefined4 uStack_c;
  
  FUN_0043bb00(&local_10,0,6);
  iVar2 = FUN_0046f788(&local_10);
  puVar1 = DAT_00470218;
  if (iVar2 == 0) {
    *DAT_00470218 = local_10;
    puVar1[1] = uStack_c;
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(2,DAT_004700a8,DAT_004700a4,DAT_0047049c,499,DAT_00470498,*(undefined1 *)puVar1,
                   *(undefined1 *)((int)puVar1 + 1),*(undefined1 *)((int)puVar1 + 2),
                   *(undefined1 *)((int)puVar1 + 3),*(undefined1 *)(puVar1 + 1),
                   *(undefined1 *)((int)puVar1 + 5));
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x9800000,DAT_004704a0,DAT_004704a0,*(undefined1 *)puVar1,
                          *(undefined1 *)((int)puVar1 + 1),*(undefined1 *)((int)puVar1 + 2),
                          *(undefined1 *)((int)puVar1 + 3),*(undefined1 *)(puVar1 + 1),
                          *(undefined1 *)((int)puVar1 + 5));
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_004700a8,DAT_004700a4,DAT_0047049c,0x1fb,DAT_004704a4,
                   *(undefined1 *)DAT_00470218,*(undefined1 *)((int)DAT_00470218 + 1),
                   *(undefined1 *)((int)DAT_00470218 + 2),*(undefined1 *)((int)DAT_00470218 + 3),
                   *(undefined1 *)(DAT_00470218 + 1),*(undefined1 *)((int)DAT_00470218 + 5));
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x5800000,DAT_004704a8,DAT_004704a8,*(undefined1 *)DAT_00470218,
                          *(undefined1 *)((int)DAT_00470218 + 1),
                          *(undefined1 *)((int)DAT_00470218 + 2),
                          *(undefined1 *)((int)DAT_00470218 + 3),*(undefined1 *)(DAT_00470218 + 1),
                          *(undefined1 *)((int)DAT_00470218 + 5));
    }
  }
  return;
}

