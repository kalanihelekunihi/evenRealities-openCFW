
undefined4 gx8002_unpack_message(int param_1,ushort param_2,int param_3,undefined4 param_4)

{
  undefined4 uVar1;
  int iVar2;
  int iVar3;
  ushort uVar4;
  ushort uVar5;
  undefined1 auStack_3c [32];
  undefined4 uStack_1c;
  
  if (((param_1 == 0) || (param_3 == 0)) || (param_2 < 0xe)) {
    uVar1 = 0xffffffff;
  }
  else {
    uStack_1c = param_4;
    FUN_00439be4(param_3,param_1,0xe);
    iVar2 = semantic_gx8002_magic_matches(param_3);
    if (iVar2 == 0) {
      uVar4 = *(short *)(param_3 + 8) + 0xe;
      if (param_2 < uVar4) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0057c61c,DAT_0057c618,DAT_0057c81c,0x94,DAT_0057c824,uVar4,param_2);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4800000,DAT_0057c828,DAT_0057c828,uVar4,param_2);
        }
        uVar1 = 0xfffffffd;
      }
      else {
        FUN_00439be4(auStack_3c,param_1,10);
        iVar2 = FUN_0058faac(auStack_3c,10);
        if (iVar2 == *(int *)(param_3 + 10)) {
          uVar5 = *(ushort *)(param_3 + 8);
          if ((int)((uint)*(byte *)(param_3 + 7) << 0x1f) < 0) {
            uVar5 = uVar5 - 4;
          }
          if (uVar5 == 0) {
            *(undefined4 *)(param_3 + 0xe) = 0;
            *(undefined2 *)(param_3 + 0x12) = 0;
          }
          else {
            if (0x10 < uVar5) {
              iVar2 = FUN_0043d0ce();
              if (iVar2 << 0x1e < 0) {
                FUN_0043d574(1,DAT_0057c61c,DAT_0057c618,DAT_0057c81c,0xaa,DAT_0057c9a0,uVar5);
              }
              iVar2 = FUN_0043d0ce();
              if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
                compress_log_output(0x4400000,DAT_0057c9a4,DAT_0057c9a4,uVar5);
              }
              return 0xfffffffb;
            }
            uVar1 = file_heap_allocate(uVar5);
            *(undefined4 *)(param_3 + 0xe) = uVar1;
            if (*(int *)(param_3 + 0xe) == 0) {
              iVar2 = FUN_0043d0ce();
              if (iVar2 << 0x1e < 0) {
                FUN_0043d574(1,DAT_0057c61c,DAT_0057c618,DAT_0057c81c,0xb1,DAT_0057c9a8);
              }
              iVar2 = FUN_0043d0ce();
              if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
                compress_log_output(0x4000000,DAT_0057c9ac,DAT_0057c9ac);
              }
              return 0xfffffffa;
            }
            FUN_00439be4(*(undefined4 *)(param_3 + 0xe),param_1 + 0xe,uVar5);
            *(ushort *)(param_3 + 0x12) = uVar5;
            if ((int)((uint)*(byte *)(param_3 + 7) << 0x1f) < 0) {
              FUN_00439be4(param_3 + 0x14,(uint)uVar5 + param_1 + 0xe,4);
              iVar2 = FUN_0058faac(*(undefined4 *)(param_3 + 0xe),uVar5);
              if (iVar2 != *(int *)(param_3 + 0x14)) {
                iVar3 = FUN_0043d0ce();
                if (iVar3 << 0x1e < 0) {
                  FUN_0043d574(1,DAT_0057c61c,DAT_0057c618,DAT_0057c81c,0xbc,DAT_0057c9b0,
                               *(undefined4 *)(param_3 + 0x14),iVar2);
                }
                iVar3 = FUN_0043d0ce();
                if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
                  compress_log_output(0x4800000,DAT_0057c9b4,DAT_0057c9b4,
                                      *(undefined4 *)(param_3 + 0x14),iVar2);
                }
                file_heap_free(*(undefined4 *)(param_3 + 0xe));
                *(undefined4 *)(param_3 + 0xe) = 0;
                return 0xfffffff9;
              }
            }
          }
          *(ushort *)(param_3 + 0x18) = uVar4;
          iVar2 = FUN_0043d0ce();
          if (iVar2 << 0x1e < 0) {
            FUN_0043d574(4,DAT_0057c61c,DAT_0057c618,DAT_0057c81c,0xca,DAT_0057cb20,
                         *(undefined2 *)(param_3 + 4),*(ushort *)(param_3 + 4) >> 8,
                         *(undefined1 *)(param_3 + 4),*(undefined1 *)(param_3 + 6),
                         *(undefined1 *)(param_3 + 7),*(undefined2 *)(param_3 + 8),
                         *(undefined4 *)(param_3 + 10));
          }
          iVar2 = FUN_0043d0ce();
          if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
            compress_log_output(0x11c00000,DAT_0057cb24,DAT_0057cb24,*(undefined2 *)(param_3 + 4),
                                *(ushort *)(param_3 + 4) >> 8,*(undefined1 *)(param_3 + 4),
                                *(undefined1 *)(param_3 + 6),*(undefined1 *)(param_3 + 7),
                                *(undefined2 *)(param_3 + 8),*(undefined4 *)(param_3 + 10));
          }
          if (*(short *)(param_3 + 0x12) != 0) {
            iVar2 = FUN_0043d0ce();
            if (iVar2 << 0x1e < 0) {
              FUN_0043d574(4,DAT_0057c61c,DAT_0057c618,DAT_0057c81c,0xcc,DAT_0057cb28,
                           *(undefined2 *)(param_3 + 0x12));
            }
            iVar2 = FUN_0043d0ce();
            if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
              compress_log_output(0x10400000,DAT_0057cb2c,DAT_0057cb2c,
                                  *(undefined2 *)(param_3 + 0x12));
            }
            FUN_0043dacc(DAT_0057cb44,0x10,*(undefined4 *)(param_3 + 0xe),
                         *(undefined2 *)(param_3 + 0x12));
          }
          uVar1 = 0;
        }
        else {
          iVar3 = FUN_0043d0ce();
          if (iVar3 << 0x1e < 0) {
            FUN_0043d574(1,DAT_0057c61c,DAT_0057c618,DAT_0057c81c,0x9d,DAT_0057c82c,
                         *(undefined4 *)(param_3 + 10),iVar2);
          }
          iVar3 = FUN_0043d0ce();
          if ((iVar3 << 0x1f < 0) || (iVar3 = FUN_0043d0ce(), iVar3 << 0x1d < 0)) {
            compress_log_output(0x4800000,DAT_0057c99c,DAT_0057c99c,*(undefined4 *)(param_3 + 10),
                                iVar2);
          }
          uVar1 = 0xfffffffc;
        }
      }
    }
    else {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(1,DAT_0057c61c,DAT_0057c618,DAT_0057c81c,0x8d,DAT_0057c818);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0057c820,DAT_0057c820);
      }
      uVar1 = 0xfffffffe;
    }
  }
  return uVar1;
}

