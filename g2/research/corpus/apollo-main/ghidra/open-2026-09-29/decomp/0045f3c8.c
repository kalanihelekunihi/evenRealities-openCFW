
int FUN_0045f3c8(int param_1,int *param_2)

{
  int iVar1;
  int iVar2;
  undefined4 uVar3;
  
  if ((param_1 == 0) || (param_2 == (int *)0x0)) {
    iVar1 = 0;
  }
  else if (*param_2 == 0) {
    iVar1 = 0;
  }
  else {
    iVar1 = FUN_0045fb44(param_1,*param_2);
    if (iVar1 == 0) {
      iVar1 = 0;
    }
    else {
      iVar1 = file_heap_allocate(0x28);
      if (iVar1 == 0) {
        iVar1 = FUN_0043d0ce();
        if (iVar1 << 0x1e < 0) {
          FUN_0043d574(1,DAT_0045f688,DAT_0045f684,DAT_0045faa0,0x1ec,DAT_0045fa9c);
        }
        iVar1 = FUN_0043d0ce();
        if ((iVar1 << 0x1f < 0) || (iVar1 = FUN_0043d0ce(), iVar1 << 0x1d < 0)) {
          compress_log_output(0x4000000,DAT_0045faa4);
        }
        if (*DAT_0045fa88 == 0) {
          FUN_0043d574(0,DAT_0045fa90,DAT_0045f684,DAT_0045faa0,0x1ed,DAT_0045fa8c,&DAT_0045f678,
                       DAT_0045faa0,0x1ed);
          do {
            FUN_0044b0ae();
          } while( true );
        }
        (*(code *)*DAT_0045fa88)(&DAT_0045f678,DAT_0045faa0,0x1ed);
        iVar1 = 0;
      }
      else {
        FUN_00439c04(iVar1,param_2,0x1c);
        if (*(int *)(iVar1 + 0xc) == 0) {
          *(undefined4 *)(iVar1 + 0xc) = 300;
        }
        if (*(int *)(iVar1 + 0x10) == 0) {
          *(undefined4 *)(iVar1 + 0x10) = 300;
        }
        if (*(short *)(iVar1 + 0x14) == 0) {
          *(undefined2 *)(iVar1 + 0x14) = 0x32;
        }
        if (*(char *)(iVar1 + 0x16) == '\0') {
          *(undefined1 *)(iVar1 + 0x16) = 100;
        }
        if (*(char *)((int)param_2 + 0xb) == '\0') {
          uVar3 = *(undefined4 *)(param_1 + 0x1c);
        }
        else {
          uVar3 = *(undefined4 *)(param_1 + 0x20);
        }
        FUN_0044d94c(param_2[1],uVar3);
        if (*(char *)((int)param_2 + 0xb) == '\0') {
          if (*(char *)((int)param_2 + 0x17) == '\0') {
            FUN_0043ded4(param_2[1],1);
            *(undefined1 *)(iVar1 + 0x1c) = 0;
          }
          else {
            *(undefined1 *)(iVar1 + 0x1c) = 1;
          }
        }
        else {
          FUN_0043f66c(uVar3);
          if ((char)param_2[2] == '\0') {
            iVar2 = FUN_0043fd9e(param_2[1]);
            FUN_0043f0e0(param_2[1],-iVar2);
          }
          else if ((char)param_2[2] == '\x01') {
            uVar3 = FUN_0043fdda(uVar3);
            FUN_0043f142(param_2[1],uVar3);
          }
          else {
            iVar2 = FUN_0043fdda(param_2[1]);
            FUN_0043f142(param_2[1],-iVar2);
          }
          *(undefined1 *)(iVar1 + 0x1c) = 0;
        }
        *(int *)(param_2[1] + 0x10) = iVar1;
        FUN_0043ded4(param_2[1],0x4000);
        if (*(char *)((int)param_2 + 0xb) == '\0') {
          *(undefined4 *)(iVar1 + 0x20) = *(undefined4 *)(param_1 + 0xc);
          *(undefined4 *)(iVar1 + 0x24) = 0;
          if (*(int *)(param_1 + 0xc) != 0) {
            *(int *)(*(int *)(param_1 + 0xc) + 0x24) = iVar1;
          }
          *(int *)(param_1 + 0xc) = iVar1;
          if (*(char *)(iVar1 + 0x1c) == '\x01') {
            *(int *)(param_1 + 4) = iVar1;
          }
        }
        else {
          *(undefined4 *)(iVar1 + 0x20) = *(undefined4 *)(param_1 + 8);
          *(undefined4 *)(iVar1 + 0x24) = 0;
          if (*(int *)(param_1 + 8) != 0) {
            *(int *)(*(int *)(param_1 + 8) + 0x24) = iVar1;
          }
          *(int *)(param_1 + 8) = iVar1;
        }
      }
    }
  }
  return iVar1;
}

