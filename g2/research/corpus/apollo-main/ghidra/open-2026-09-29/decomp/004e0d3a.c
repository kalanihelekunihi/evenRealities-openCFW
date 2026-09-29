
undefined4 FUN_004e0d3a(undefined4 param_1,undefined4 param_2,int param_3,uint *param_4)

{
  int *piVar1;
  int iVar2;
  undefined2 uVar3;
  ushort uVar4;
  uint uVar5;
  uint local_18;
  uint uStack_14;
  uint *puStack_10;
  
  puStack_10 = param_4;
  if (param_3 == 0x42) {
    uVar5 = 0;
    if (param_4 != (uint *)0x0) {
      uVar5 = *param_4;
    }
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      local_18 = uVar5;
      FUN_0043d574(3,DAT_004e1464,DAT_004e1460,DAT_004e1470,0x76,DAT_004e146c);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0xc400000,DAT_004e1474,DAT_004e1474,uVar5);
    }
    piVar1 = DAT_004e1454;
    if ((((*DAT_004e1454 != 0) && (*(int *)*DAT_004e1454 != 0)) && (uVar5 != 0)) && (uVar5 != 0x21))
    {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004e1464,DAT_004e1460,DAT_004e1470,0x79,DAT_004e1478);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004e147c,DAT_004e147c);
      }
      *DAT_004e1480 = 1;
      FUN_00441488(*(undefined4 *)*piVar1,0x7f,0);
    }
    FUN_004da16a(0,0,0,4,0,0);
    *DAT_004e1484 = 0;
  }
  else if (param_3 == 0x43) {
    FUN_004da16a(0,0,0,5,0,0);
    piVar1 = DAT_004e1454;
    if ((*DAT_004e1454 != 0) && (*(int *)*DAT_004e1454 != 0)) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004e1464,DAT_004e1460,DAT_004e1470,0x84,DAT_004e1488);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004e148c,DAT_004e148c);
      }
      if (*DAT_004e1480 == 1) {
        *DAT_004e1480 = 0;
        FUN_00441488(*(undefined4 *)*piVar1,0xff,0);
      }
    }
    *DAT_004e1484 = 1;
    piVar1 = DAT_004e1444;
    if ((*DAT_004e1444 == 1) && (iVar2 = FUN_0045a568(), iVar2 == 1)) {
      *piVar1 = 0;
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(3,DAT_004e1464,DAT_004e1460,DAT_004e1470,0x8e,DAT_004e1958);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc000000,DAT_004e195c,DAT_004e195c);
      }
      FUN_00464c36(0xe0,0,0,0);
    }
  }
  else if (param_3 == 10) {
    if ((((*DAT_004e1454 != 0) && (*(int *)*DAT_004e1454 != 0)) &&
        (*(char *)(*DAT_004e1454 + 0x34) == '\x01')) &&
       (iVar2 = FUN_00494610(*DAT_004e1454,10,param_4), iVar2 == 1)) {
      uVar3 = 0;
      if ((param_4 != (uint *)0x0) && ((undefined2 *)param_4[4] != (undefined2 *)0x0)) {
        uVar3 = *(undefined2 *)param_4[4];
      }
      FUN_004da16a(0,0,0,0,0,uVar3);
    }
  }
  else if (param_3 == 0x44) {
    if (((*DAT_004e1454 != 0) && (*(int *)*DAT_004e1454 != 0)) &&
       ((*(char *)(*DAT_004e1454 + 0x34) == '\x01' &&
        (iVar2 = FUN_00494610(*DAT_004e1454,0x44,param_4), iVar2 == 1)))) {
      FUN_004da16a(0,0,0,1,0,0);
    }
  }
  else if (param_3 == 0x45) {
    if ((((*DAT_004e1454 != 0) && (*(int *)*DAT_004e1454 != 0)) &&
        (*(char *)(*DAT_004e1454 + 0x34) == '\x01')) &&
       (iVar2 = FUN_00494610(*DAT_004e1454,0x45,param_4), iVar2 == 1)) {
      FUN_004da16a(0,0,0,2,0,0);
    }
  }
  else if (param_3 == 0x48) {
    if ((*DAT_004e1454 != 0) && (*(int *)*DAT_004e1454 != 0)) {
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004e1464,DAT_004e1460,DAT_004e1470,0xb7,DAT_004e1960);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004e1964,DAT_004e1964);
      }
      uVar4 = 0;
      if ((param_4 != (uint *)0x0) && ((ushort *)param_4[4] != (ushort *)0x0)) {
        uVar4 = *(ushort *)param_4[4];
      }
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        local_18 = (uint)uVar4;
        FUN_0043d574(3,DAT_004e1464,DAT_004e1460,DAT_004e1470,0xbf,DAT_004e1968);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0xc400000,DAT_004e196c,DAT_004e196c,uVar4);
      }
      FUN_004da16a(0,0,0,3,0,uVar4);
    }
  }
  else if (param_3 == 0x4f) {
    iVar2 = FUN_0043d0ce();
    if (iVar2 << 0x1e < 0) {
      FUN_0043d574(4,DAT_004e1464,DAT_004e1460,DAT_004e1470,0xc4,DAT_004e1970);
    }
    iVar2 = FUN_0043d0ce();
    if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
      compress_log_output(0x10000000,DAT_004e1974,DAT_004e1974);
    }
    if ((*DAT_004e1454 != 0) && (*(int *)*DAT_004e1454 != 0)) {
      FUN_004641b6(*(undefined4 *)*DAT_004e1454,0xe0);
      local_18 = *DAT_004e1978;
      uStack_14 = DAT_004e1978[1];
      local_18 = FUN_004935fe();
      FUN_0048eb32(DAT_004e197c,2,&local_18);
      FUN_004e0ca0();
      iVar2 = FUN_0043d0ce();
      if (iVar2 << 0x1e < 0) {
        FUN_0043d574(4,DAT_004e1464,DAT_004e1460,DAT_004e1470,0xcb,DAT_004e1980);
      }
      iVar2 = FUN_0043d0ce();
      if ((iVar2 << 0x1f < 0) || (iVar2 = FUN_0043d0ce(), iVar2 << 0x1d < 0)) {
        compress_log_output(0x10000000,DAT_004e1984,DAT_004e1984);
      }
    }
  }
  return 1;
}

