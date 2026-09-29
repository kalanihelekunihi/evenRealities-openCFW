
void FUN_004201ba(void)

{
  undefined4 *puVar1;
  int iVar2;
  undefined4 local_10;
  undefined4 uStack_c;
  
  memset_wrapper_426c10(&local_10,0,6);
  iVar2 = FUN_00420002(&local_10);
  puVar1 = DAT_00420a04;
  if (iVar2 == 0) {
    *DAT_00420a04 = local_10;
    puVar1[1] = uStack_c;
    elog_output(2,DAT_00420adc,DAT_00420978,DAT_00420afc,499,DAT_00420af8,*(undefined1 *)puVar1,
                *(undefined1 *)((int)puVar1 + 1),*(undefined1 *)((int)puVar1 + 2),
                *(undefined1 *)((int)puVar1 + 3),*(undefined1 *)(puVar1 + 1),
                *(undefined1 *)((int)puVar1 + 5));
  }
  else {
    elog_output(1,DAT_00420adc,DAT_00420978,DAT_00420afc,0x1fb,DAT_00420b00,
                *(undefined1 *)DAT_00420a04,*(undefined1 *)((int)DAT_00420a04 + 1),
                *(undefined1 *)((int)DAT_00420a04 + 2),*(undefined1 *)((int)DAT_00420a04 + 3),
                *(undefined1 *)(DAT_00420a04 + 1),*(undefined1 *)((int)DAT_00420a04 + 5));
  }
  return;
}

