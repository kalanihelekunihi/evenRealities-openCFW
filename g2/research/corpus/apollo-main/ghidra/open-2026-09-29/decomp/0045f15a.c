
int FUN_0045f15a(undefined4 param_1)

{
  int *piVar1;
  int iVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  
  piVar1 = DAT_0045fa78;
  iVar2 = file_heap_allocate(0xec);
  *piVar1 = iVar2;
  if (*piVar1 == 0) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(1,DAT_0045f688,DAT_0045f684,DAT_0045fa80,0x197,DAT_0045fa7c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x4000000,DAT_0045fa84,DAT_0045fa84);
    }
    if (*DAT_0045fa88 == 0) {
      FUN_0043d574(0,DAT_0045fa90,DAT_0045f684,DAT_0045fa80,0x198,DAT_0045fa8c,&DAT_0045f3c4,
                   DAT_0045fa80,0x198);
      do {
        FUN_0044b0ae();
      } while( true );
    }
    (*(code *)*DAT_0045fa88)(&DAT_0045f3c4,DAT_0045fa80,0x198);
    iVar2 = 0;
  }
  else {
    uVar3 = FUN_0044fa1a();
    uVar4 = FUN_00488290(0);
    uVar5 = FUN_00488290(0);
    uVar4 = FUN_00487022(uVar3,uVar5,uVar4,0,DAT_0045fa94);
    FUN_0044fe0e(uVar3,uVar4);
    uVar3 = FUN_0043de82(param_1);
    *(undefined4 *)(*piVar1 + 0x18) = uVar3;
    FUN_0043f4c0(*(undefined4 *)(*piVar1 + 0x18),0x240,0x120);
    FUN_0045ec7c(*(undefined4 *)(*piVar1 + 0x18),0,0);
    FUN_0044131c(*(undefined4 *)(*piVar1 + 0x18),0,0);
    FUN_0044129e(*(undefined4 *)(*piVar1 + 0x18),0,0);
    FUN_0043dfa4(*(undefined4 *)(*piVar1 + 0x18),0x10);
    uVar3 = FUN_0043de82(*(undefined4 *)(*piVar1 + 0x18));
    *(undefined4 *)(*piVar1 + 0x1c) = uVar3;
    uVar3 = DAT_0045fa98;
    FUN_0043f4c0(*(undefined4 *)(*piVar1 + 0x1c),DAT_0045fa98,DAT_0045fa98);
    FUN_0045ec7c(*(undefined4 *)(*piVar1 + 0x1c),0,0);
    FUN_0044131c(*(undefined4 *)(*piVar1 + 0x1c),0,0);
    uVar4 = FUN_0044104c(0);
    FUN_0044127e(*(undefined4 *)(*piVar1 + 0x1c),uVar4,0);
    FUN_0044129e(*(undefined4 *)(*piVar1 + 0x1c),0xff,0);
    FUN_0044146a(*(undefined4 *)(*piVar1 + 0x1c),0,0);
    FUN_0044133a(*(undefined4 *)(*piVar1 + 0x1c),0,0);
    FUN_00441378(*(undefined4 *)(*piVar1 + 0x1c),0,0);
    FUN_00441386(*(undefined4 *)(*piVar1 + 0x1c),0,0);
    FUN_004413b0(*(undefined4 *)(*piVar1 + 0x1c),0,0);
    FUN_00441394(*(undefined4 *)(*piVar1 + 0x1c),0,0);
    FUN_004413a2(*(undefined4 *)(*piVar1 + 0x1c),0,0);
    FUN_0043dfa4(*(undefined4 *)(*piVar1 + 0x1c),0x10);
    uVar4 = FUN_0043de82(*(undefined4 *)(*piVar1 + 0x18));
    *(undefined4 *)(*piVar1 + 0x20) = uVar4;
    FUN_0043f4c0(*(undefined4 *)(*piVar1 + 0x20),uVar3,uVar3);
    FUN_0045ec7c(*(undefined4 *)(*piVar1 + 0x20),0,0);
    FUN_0044131c(*(undefined4 *)(*piVar1 + 0x20),0,0);
    FUN_0044129e(*(undefined4 *)(*piVar1 + 0x20),0,0);
    FUN_0043dfa4(*(undefined4 *)(*piVar1 + 0x20),0x10);
    *(undefined4 *)*piVar1 = 0;
    *(undefined4 *)(*piVar1 + 4) = 0;
    *(undefined4 *)(*piVar1 + 8) = 0;
    *(undefined4 *)(*piVar1 + 0xc) = 0;
    *(undefined4 *)(*piVar1 + 0x10) = 0;
    *(undefined1 *)(*piVar1 + 0x14) = 0;
    *(undefined1 *)(*piVar1 + 0xe8) = 0;
    FUN_0045fba2(*piVar1 + 0x24);
    *(int *)(*(int *)(*piVar1 + 0x18) + 0x10) = *piVar1;
    FUN_00451740(*(undefined4 *)(*piVar1 + 0x18),0x45f915,0,*piVar1);
    iVar2 = *piVar1;
  }
  return iVar2;
}

