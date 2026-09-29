
undefined4 FUN_004fef04(undefined4 *param_1,int param_2,int *param_3,undefined4 param_4)

{
  byte bVar1;
  undefined1 *puVar2;
  undefined4 uVar3;
  int iVar4;
  undefined1 auStack_40 [12];
  int local_34;
  undefined1 auStack_2c [20];
  undefined4 uStack_18;
  
  puVar2 = DAT_004ff318;
  if ((((param_1 == (undefined4 *)0x0) || (param_2 == 0)) || (param_3 == (int *)0x0)) ||
     (*param_3 == 0)) {
    uVar3 = 0;
  }
  else {
    uStack_18 = param_4;
    FUN_004fdd6e(DAT_004ff318);
    *puVar2 = 3;
    *(undefined4 *)(puVar2 + 4) = DAT_004ff498;
    *(undefined2 *)(puVar2 + 8) = 6;
    *(undefined4 *)(puVar2 + 0x10) = *param_1;
    puVar2[0x14] = *(undefined1 *)(param_1 + 1);
    bVar1 = *(byte *)((int)param_1 + 5);
    if (bVar1 == 1) {
      *(undefined2 *)(puVar2 + 0x16) = 3;
      puVar2[0x18] = 1;
      *(undefined4 *)(puVar2 + 0x1c) = param_1[2];
      if ((0.0 <= (float)param_1[3]) || (0.0 <= (float)param_1[4])) {
        puVar2[0x20] = 1;
        *(undefined4 *)(puVar2 + 0x24) = param_1[3];
        *(undefined4 *)(puVar2 + 0x28) = param_1[4];
      }
    }
    else if (bVar1 != 0) {
      if (bVar1 == 3) {
        *(undefined2 *)(puVar2 + 0x16) = 5;
        FUN_00439c04(puVar2 + 0x18,param_1 + 2,0x40);
      }
      else if (bVar1 < 3) {
        bVar1 = *(byte *)(param_1 + 2);
        if (bVar1 == 1) {
          *(undefined2 *)(puVar2 + 0x16) = 4;
          *(undefined2 *)(puVar2 + 0x18) = 1;
          if (*(char *)(param_1 + 4) == '\x01') {
            *(undefined2 *)(puVar2 + 0x20) = 1;
            *(undefined4 *)(puVar2 + 0x28) = param_1[6];
            *(undefined4 *)(puVar2 + 0x2c) = param_1[7];
          }
          else if (*(char *)(param_1 + 4) == '\x02') {
            *(undefined2 *)(puVar2 + 0x20) = 2;
            *(undefined4 *)(puVar2 + 0x28) = param_1[6];
            uVar3 = param_1[9];
            *(undefined4 *)(puVar2 + 0x30) = param_1[8];
            *(undefined4 *)(puVar2 + 0x34) = uVar3;
          }
        }
        else if (bVar1 != 0) {
          if (bVar1 == 3) {
            *(undefined2 *)(puVar2 + 0x16) = 4;
            *(undefined2 *)(puVar2 + 0x18) = 3;
            *(undefined4 *)(puVar2 + 0x20) = param_1[4];
            *(undefined4 *)(puVar2 + 0x24) = param_1[5];
          }
          else if (bVar1 < 3) {
            *(undefined2 *)(puVar2 + 0x16) = 4;
            *(undefined2 *)(puVar2 + 0x18) = 2;
            FUN_0044b5a0(puVar2 + 0x20,param_1 + 4,0x3f);
          }
        }
      }
    }
    FUN_004905f4(auStack_2c,param_2,*param_3);
    FUN_00439c04(auStack_40,auStack_2c,0x14);
    iVar4 = FUN_00490c32(auStack_40,DAT_004ff494,puVar2);
    if (iVar4 == 0) {
      iVar4 = FUN_0043d0ce();
      if (iVar4 << 0x1e < 0) {
        FUN_0043d574(1,DAT_004ff4a8,DAT_004ff4a4,DAT_004ff4a0,0x43b,DAT_004ff49c);
      }
      iVar4 = FUN_0043d0ce();
      if ((iVar4 << 0x1f < 0) || (iVar4 = FUN_0043d0ce(), iVar4 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_004ff4ac,DAT_004ff4ac);
      }
      uVar3 = 0;
    }
    else {
      *param_3 = local_34;
      uVar3 = 1;
    }
  }
  return uVar3;
}

