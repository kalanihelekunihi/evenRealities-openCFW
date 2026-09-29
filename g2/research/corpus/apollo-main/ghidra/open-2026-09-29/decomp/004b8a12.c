
undefined1 * _getOrCreateContext(int param_1,char param_2,undefined4 param_3,undefined4 param_4)

{
  short sVar1;
  undefined4 uVar2;
  int iVar3;
  undefined1 *puVar4;
  ushort uVar5;
  
  puVar4 = (undefined1 *)0x0;
  sVar1 = slave_cmd_pipe_get_0046f2c6();
  uVar5 = sVar1 - 0xb;
  iVar3 = 0;
  do {
    if (3 < iVar3) {
LAB_004b8aa6:
      if ((puVar4 == (undefined1 *)0x0) && (*(char *)(param_1 + 5) == '\x01')) {
        for (iVar3 = 0; iVar3 < 4; iVar3 = iVar3 + 1) {
          if (*(char *)(iVar3 * 0x38 + DAT_004b90ec + 0x30) == '\0') {
            puVar4 = (undefined1 *)(DAT_004b90ec + iVar3 * 0x38);
            FUN_0043c0e4(puVar4,0x32,0);
            puVar4[0x30] = 1;
            *puVar4 = *(undefined1 *)(param_1 + 6);
            puVar4[1] = *(undefined1 *)(param_1 + 2);
            puVar4[4] = *(byte *)(param_1 + 1) & 0xf;
            puVar4[5] = *(byte *)(param_1 + 1) >> 4;
            puVar4[0x32] = *(undefined1 *)(param_1 + 4);
            puVar4[0x33] = param_2;
            *(undefined2 *)(puVar4 + 2) = 0;
            uVar2 = file_heap_allocate((uint)uVar5 * (uint)(byte)puVar4[0x32]);
            *(undefined4 *)(puVar4 + 8) = uVar2;
            if (*(int *)(puVar4 + 8) != 0) {
              return puVar4;
            }
            iVar3 = FUN_0043d0ce();
            if (iVar3 << 0x1e < 0) {
              FUN_0043d574(1,PTR_s_prot_tran_004b9100,DAT_004b90fc,DAT_004b9610,0xba,DAT_004b960c,
                           puVar4[0x32],uVar5,(uint)uVar5 * (uint)(byte)puVar4[0x32],param_4);
            }
            iVar3 = FUN_0043d0ce();
            if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
              compress_log_output(0x4c00000,DAT_004b9614,DAT_004b9614,puVar4[0x32],uVar5,
                                  (uint)uVar5 * (uint)(byte)puVar4[0x32]);
            }
            puVar4[0x30] = 0;
            return (undefined1 *)0x0;
          }
        }
      }
      return puVar4;
    }
    if (((((*(char *)(iVar3 * 0x38 + DAT_004b90ec + 0x30) != '\0') &&
          (*(char *)(DAT_004b90ec + iVar3 * 0x38) == *(char *)(param_1 + 6))) &&
         (*(char *)(iVar3 * 0x38 + DAT_004b90ec + 1) == *(char *)(param_1 + 2))) &&
        ((*(byte *)(iVar3 * 0x38 + DAT_004b90ec + 4) == (*(byte *)(param_1 + 1) & 0xf) &&
         (*(byte *)(iVar3 * 0x38 + DAT_004b90ec + 5) == *(byte *)(param_1 + 1) >> 4)))) &&
       (*(char *)(iVar3 * 0x38 + DAT_004b90ec + 0x33) == param_2)) {
      puVar4 = (undefined1 *)(DAT_004b90ec + iVar3 * 0x38);
      goto LAB_004b8aa6;
    }
    iVar3 = iVar3 + 1;
  } while( true );
}

