
undefined8 FUN_0046cae0(int param_1,uint param_2,undefined4 param_3,undefined4 param_4)

{
  byte bVar1;
  int iVar2;
  undefined4 *puVar3;
  undefined4 uVar4;
  uint uVar5;
  char cVar6;
  int iVar7;
  uint uVar8;
  
  uVar8 = param_2;
  iVar2 = FUN_0043d0ce();
  if (iVar2 << 0x1e < 0) {
    uVar8 = 0x41;
    FUN_0043d574(3,DAT_0046d580,DAT_0046d57c,DAT_0046d448,0x41,DAT_0046d444,param_4);
  }
  iVar2 = FUN_0043d0ce();
  if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
    compress_log_output(0xc000000,DAT_0046d44c,DAT_0046d44c);
  }
  if (param_1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uVar8 = 0x44;
      FUN_0043d574(1,DAT_0046d580,DAT_0046d57c,DAT_0046d448,0x44,DAT_0046d450);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0046d454,DAT_0046d454);
    }
    puVar3 = (undefined4 *)0x0;
  }
  else if ((param_2 & 0xff) == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uVar8 = 0x4a;
      FUN_0043d574(1,DAT_0046d580,DAT_0046d57c,DAT_0046d448,0x4a,DAT_0046d458);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0046d45c,DAT_0046d45c);
    }
    puVar3 = (undefined4 *)0x0;
  }
  else if ((param_2 & 0xff) < 9) {
    puVar3 = (undefined4 *)file_heap_allocate(0xc);
    if (puVar3 == (undefined4 *)0x0) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        uVar8 = 0x59;
        FUN_0043d574(1,DAT_0046d580,DAT_0046d57c,DAT_0046d448,0x59,DAT_0046d58c);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_0046d590,DAT_0046d590);
      }
      puVar3 = (undefined4 *)0x0;
    }
    else {
      *puVar3 = 0;
      puVar3[1] = 0;
      *(undefined1 *)(puVar3 + 2) = 0;
      iVar2 = file_heap_allocate((param_2 & 0xff) << 2);
      if (iVar2 == 0) {
        iVar2 = FUN_0043d0ce();
        if (iVar2 << 0x1e < 0) {
          uVar8 = 0x67;
          FUN_0043d574(1,DAT_0046d580,DAT_0046d57c,DAT_0046d448,0x67,DAT_0046d594);
        }
        iVar2 = FUN_0043d0ce();
        if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_0046d598,DAT_0046d598);
        }
        file_heap_free(puVar3);
        puVar3 = (undefined4 *)0x0;
      }
      else {
        cVar6 = '\0';
        for (bVar1 = 0; (uint)bVar1 < (param_2 & 0xff); bVar1 = bVar1 + 1) {
          *(undefined4 *)(iVar2 + (uint)bVar1 * 4) = 0;
        }
        for (bVar1 = 0; ((uint)bVar1 < (param_2 & 0xff) && (bVar1 < 8)); bVar1 = bVar1 + 1) {
          uVar4 = FUN_0046cfa6((uint)bVar1 * 0xc + param_1);
          *(undefined4 *)(iVar2 + (uint)bVar1 * 4) = uVar4;
          if (*(int *)(iVar2 + (uint)bVar1 * 4) == 0) {
            iVar7 = FUN_0043d0ce();
            if (iVar7 << 0x1e < 0) {
              uVar8 = 0x8b;
              FUN_0043d574(2,DAT_0046d580,DAT_0046d57c,DAT_0046d448,0x8b,DAT_0046d59c);
            }
            iVar7 = FUN_0043d0ce();
            if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
              compress_log_output(0x8000000,DAT_0046d5a0);
            }
          }
          else {
            iVar7 = puVar3[1];
            FUN_0046d158(puVar3,*(undefined4 *)(iVar2 + (uint)bVar1 * 4),
                         *(undefined1 *)(param_1 + (uint)bVar1 * 0xc));
            if (puVar3[1] == iVar7) {
              iVar7 = FUN_0043d0ce();
              if (iVar7 << 0x1e < 0) {
                uVar8 = 0x86;
                FUN_0043d574(1,DAT_0046d580,DAT_0046d57c,DAT_0046d448,0x86,DAT_0046d5a4);
              }
              iVar7 = FUN_0043d0ce();
              if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
                compress_log_output(0x4000000,DAT_0046d5a8,DAT_0046d5a8);
              }
              FUN_0046d1c6(*(undefined4 *)(iVar2 + (uint)bVar1 * 4),
                           *(undefined1 *)(param_1 + (uint)bVar1 * 0xc));
              *(undefined4 *)(iVar2 + (uint)bVar1 * 4) = 0;
            }
            else {
              cVar6 = cVar6 + '\x01';
            }
          }
        }
        if (cVar6 == '\0') {
          iVar7 = FUN_0043d0ce();
          if (iVar7 << 0x1e < 0) {
            uVar8 = 0x91;
            FUN_0043d574(1,DAT_0046d580,DAT_0046d57c,DAT_0046d448,0x91,DAT_0046d5ac);
          }
          iVar7 = FUN_0043d0ce();
          if ((iVar7 << 0x1f < 0) || (iVar7 = FUN_0043d0ce(), iVar7 << 0x1d < 0)) {
            compress_log_output(0x4000000,DAT_0046d5b0,DAT_0046d5b0);
          }
          for (bVar1 = 0; (uint)bVar1 < (param_2 & 0xff); bVar1 = bVar1 + 1) {
            if (*(int *)(iVar2 + (uint)bVar1 * 4) != 0) {
              FUN_0046d1c6(*(undefined4 *)(iVar2 + (uint)bVar1 * 4),
                           *(undefined1 *)(param_1 + (uint)bVar1 * 0xc));
            }
          }
          file_heap_free(iVar2);
          file_heap_free(puVar3);
          puVar3 = (undefined4 *)0x0;
        }
        else {
          iVar7 = 0;
          for (bVar1 = 0; (uint)bVar1 < (param_2 & 0xff); bVar1 = bVar1 + 1) {
            if (*(int *)(iVar2 + (uint)bVar1 * 4) != 0) {
              if (iVar7 != 0) {
                *(undefined4 *)(iVar7 + 0x1c) = *(undefined4 *)(iVar2 + (uint)bVar1 * 4);
              }
              iVar7 = *(int *)(iVar2 + (uint)bVar1 * 4);
            }
          }
          if (iVar7 != 0) {
            *(undefined4 *)(iVar7 + 0x1c) = 0;
          }
          for (uVar5 = 0; (uVar5 & 0xff) < (param_2 & 0xff); uVar5 = uVar5 + 1) {
            if (*(int *)(iVar2 + (uVar5 & 0xff) * 4) != 0) {
              *puVar3 = *(undefined4 *)(iVar2 + (uVar5 & 0xff) * 4);
              *(char *)(puVar3 + 2) = cVar6;
              file_heap_free(iVar2);
              iVar2 = FUN_0043d0ce();
              if (iVar2 << 0x1e < 0) {
                uVar8 = 0xb9;
                FUN_0043d574(3,DAT_0046d580,DAT_0046d57c,DAT_0046d448,0xb9,DAT_0046d5b4);
              }
              iVar2 = FUN_0043d0ce();
              if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
                compress_log_output(0xc000000,DAT_0046d5b8,DAT_0046d5b8);
              }
              goto LAB_0046cf52;
            }
          }
          file_heap_free(iVar2);
          file_heap_free(puVar3);
          puVar3 = (undefined4 *)0x0;
        }
      }
    }
  }
  else {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      uVar8 = 0x4f;
      FUN_0043d574(1,DAT_0046d580,DAT_0046d57c,DAT_0046d448,0x4f,DAT_0046d460);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0046d588,DAT_0046d588);
    }
    puVar3 = (undefined4 *)0x0;
  }
LAB_0046cf52:
  return CONCAT44(uVar8,puVar3);
}

