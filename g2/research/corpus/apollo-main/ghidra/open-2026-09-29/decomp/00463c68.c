
undefined8 FUN_00463c68(int param_1,int *param_2,undefined4 param_3,undefined4 param_4)

{
  int iVar1;
  int *piVar2;
  uint uVar3;
  int *piVar4;
  
  if ((((param_1 == 0) || (param_2 == (int *)0x0)) || (*param_2 == 0)) || (param_2[1] == 0)) {
    iVar1 = FUN_0043d0ce();
    if (iVar1 << 0x1e < 0) {
      param_2 = (int *)0x13;
      FUN_0043d574(1,DAT_004642cc,DAT_004642c8,DAT_004642c4,0x13,DAT_004642c0,param_4);
    }
    iVar1 = FUN_0043d0ce();
    if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_004642d0);
    }
    piVar2 = (int *)0x0;
    piVar4 = param_2;
  }
  else {
    for (uVar3 = 0; piVar4 = param_2, uVar3 < (uint)param_2[1]; uVar3 = uVar3 + 1) {
      if (*(int *)(*param_2 + uVar3 * 4) == 0) {
        piVar2 = (int *)0x0;
        goto LAB_00463e1a;
      }
    }
    piVar2 = (int *)file_heap_allocate(0x2c);
    if (piVar2 == (int *)0x0) {
      iVar1 = FUN_0043d0ce();
      if (iVar1 << 0x1e < 0) {
        piVar4 = (int *)0x21;
        FUN_0043d574(1,DAT_004642cc,DAT_004642c8,DAT_004642c4,0x21,DAT_004642d4);
      }
      iVar1 = FUN_0043d0ce();
      if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
        compress_log_output(0x4000000,DAT_004642d8,DAT_004642d8);
      }
      piVar2 = (int *)0x0;
    }
    else {
      FUN_0043c0e4(piVar2,0x2c,0);
      iVar1 = FUN_00498668(param_1);
      *piVar2 = iVar1;
      if (*piVar2 == 0) {
        file_heap_free(piVar2);
        iVar1 = FUN_0043d0ce(0);
        if (iVar1 << 0x1e < 0) {
          piVar4 = (int *)0x2d;
          FUN_0043d574(1,DAT_004642cc,DAT_004642c8,DAT_004642c4,0x2d,DAT_004642dc);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_004642e0,DAT_004642e0);
        }
        piVar2 = (int *)0x0;
      }
      else {
        piVar2[1] = *param_2;
        piVar2[2] = param_2[1];
        if (param_2[2] == 0) {
          iVar1 = 0x32;
        }
        else {
          iVar1 = param_2[2];
        }
        piVar2[4] = iVar1;
        *(char *)((int)piVar2 + 0x19) = (char)param_2[3];
        piVar2[7] = param_2[4];
        piVar2[8] = param_2[5];
        FUN_00439be4(piVar2 + 9,param_2 + 6,3);
        *(undefined1 *)((int)piVar2 + 0x27) = *(undefined1 *)((int)param_2 + 0x1b);
        FUN_00439be4(piVar2 + 10,param_2 + 7,3);
        *(undefined1 *)((int)piVar2 + 0x2b) = *(undefined1 *)((int)param_2 + 0x1f);
        piVar2[3] = 0;
        piVar2[5] = 0;
        *(undefined1 *)(piVar2 + 6) = 0;
        *(undefined1 *)((int)piVar2 + 0x1a) = 1;
        *(undefined1 *)((int)piVar2 + 0x1b) = 0;
        FUN_00463fb0(piVar2);
        if ((piVar2[1] != 0) && (*(int *)piVar2[1] != 0)) {
          FUN_00498680(*piVar2,*(undefined4 *)piVar2[1]);
        }
      }
    }
  }
LAB_00463e1a:
  return CONCAT44(piVar4,piVar2);
}

