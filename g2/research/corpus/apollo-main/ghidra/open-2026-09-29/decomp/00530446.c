
undefined4 * WsfBufAlloc(ushort param_1)

{
  int iVar1;
  ushort *puVar2;
  undefined4 *puVar3;
  char cVar4;
  
  puVar2 = (ushort *)*DAT_00530514;
  cVar4 = *DAT_00530518;
  do {
    if (cVar4 == '\0') {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0053052c,DAT_00530528,DAT_00530524,0x141,DAT_00530520,param_1);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4400000,DAT_00530530,DAT_00530530,param_1);
      }
      return (undefined4 *)0x0;
    }
    if (param_1 <= *puVar2) {
      WsfCsEnter();
      if (*(int *)(puVar2 + 4) != 0) {
        puVar3 = *(undefined4 **)(puVar2 + 4);
        *(undefined4 *)(puVar2 + 4) = *puVar3;
        puVar3[1] = 0;
        WsfCsExit();
        return puVar3;
      }
      WsfCsExit();
    }
    cVar4 = cVar4 + -1;
    puVar2 = puVar2 + 6;
  } while( true );
}

