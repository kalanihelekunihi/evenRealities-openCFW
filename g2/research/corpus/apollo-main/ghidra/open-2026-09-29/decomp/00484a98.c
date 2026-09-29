
undefined8 FUN_00484a98(int param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  undefined4 uVar1;
  undefined4 uVar2;
  int iVar3;
  int iVar4;
  undefined4 local_20;
  undefined4 local_1c;
  undefined4 uStack_18;
  
  local_20 = param_2;
  local_1c = param_3;
  uStack_18 = param_4;
  if ((int)((uint)*(byte *)(param_1 + 0x24) << 0x1f) < 0) {
    local_20 = FUN_0044104c(DAT_0048547c);
  }
  else {
    local_20 = FUN_004882d2(0x12,4);
  }
  FUN_00439be4(param_1 + 0x30,&local_20,3);
  if ((int)((uint)*(byte *)(param_1 + 0x24) << 0x1f) < 0) {
    local_20 = FUN_004882d2(0x12,5);
  }
  else {
    local_20 = FUN_0048834c(0x12,4);
  }
  FUN_00439be4(param_1 + 0x33,&local_20,3);
  if ((int)((uint)*(byte *)(param_1 + 0x24) << 0x1f) < 0) {
    local_20 = FUN_0044104c(DAT_00485480);
  }
  else {
    local_20 = FUN_00441094();
  }
  FUN_00439be4(param_1 + 0x36,&local_20,3);
  if ((int)((uint)*(byte *)(param_1 + 0x24) << 0x1f) < 0) {
    local_20 = FUN_0044104c(DAT_00485484);
  }
  else {
    local_20 = FUN_004882d2(0x12,2);
  }
  FUN_00439be4(param_1 + 0x39,&local_20,3);
  FUN_00488198(param_1 + 0x184);
  FUN_00488198(param_1 + 400);
  uVar1 = DAT_0048548c;
  uVar2 = DAT_00485488;
  local_1c = 0;
  local_20 = 0x46;
  FUN_00482950(param_1 + 0x364,DAT_00485488,DAT_0048548c,0x50);
  local_1c = 0;
  local_20 = 0;
  FUN_00482950(param_1 + 0x378,uVar2,uVar1,0x50);
  FUN_004d4abc(param_1 + 0x184,param_1 + 0x364);
  FUN_004d4abc(param_1 + 400,param_1 + 0x378);
  FUN_00488198(param_1 + 0x4c);
  if ((int)((uint)*(byte *)(param_1 + 0x24) << 0x1f) < 0) {
    uVar2 = FUN_0048834c(0x12,2);
  }
  else {
    uVar2 = FUN_00488290(0x12);
  }
  FUN_004d48aa(param_1 + 0x4c,uVar2);
  FUN_004d4a6e(param_1 + 0x4c,0x7fff);
  if ((*(int *)(param_1 + 0x2c) * 7 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 7 + 0x50) / 0xa0;
  }
  FUN_00484a26(param_1 + 0x4c,iVar3);
  if ((*(int *)(param_1 + 0x2c) * 5 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 5 + 0x50) / 0xa0;
  }
  FUN_004d481a(param_1 + 0x4c,iVar3);
  FUN_004d48c4(param_1 + 0x4c,0x66);
  FUN_004d4abc(param_1 + 0x4c,param_1 + 0x378);
  FUN_00488198(param_1 + 0x58);
  FUN_004d48c4(param_1 + 0x58,0xff);
  FUN_00488198(param_1 + 0x40);
  FUN_004d48c4(param_1 + 0x40,0xff);
  FUN_00439be4(&local_20,param_1 + 0x30,3);
  FUN_004d48aa(param_1 + 0x40,local_20);
  FUN_00439be4(&local_20,param_1 + 0x33,3);
  FUN_004d4a2e(param_1 + 0x40,local_20);
  FUN_004d4a48(param_1 + 0x40,*(undefined4 *)(param_1 + 0x1c));
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0xe;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0xc;
  }
  else {
    iVar3 = 10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0xe;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0xe;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0xc;
      }
      else {
        iVar3 = 10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_004d4892(param_1 + 0x40,iVar3);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0xe;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0xc;
  }
  else {
    iVar3 = 10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0xe;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0xe;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0xc;
      }
      else {
        iVar3 = 10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_004d489e(param_1 + 0x40,iVar3);
  FUN_004d4ac8(param_1 + 0x40,*(int *)(param_1 + 0x2c) / 4 << 8);
  FUN_00488198(param_1 + 100);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0xc;
  }
  else {
    iVar3 = 8;
  }
  if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 8;
    }
    iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
  }
  FUN_004d4a6e(param_1 + 100,iVar3);
  FUN_004d48c4(param_1 + 100,0xff);
  FUN_00439be4(&local_20,param_1 + 0x36,3);
  FUN_004d48aa(param_1 + 100,local_20);
  FUN_00439be4(&local_20,param_1 + 0x39,3);
  FUN_004d48f8(param_1 + 100,local_20);
  if ((*(int *)(param_1 + 0x2c) * 2 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 2 + 0x50) / 0xa0;
  }
  FUN_004d4920(param_1 + 100,iVar3);
  FUN_004d493a(param_1 + 100,1);
  FUN_00439be4(&local_20,param_1 + 0x33,3);
  FUN_004d4a2e(param_1 + 100,local_20);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0x18;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0x14;
  }
  else {
    iVar3 = 0x10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0x18;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0x14;
    }
    else {
      iVar3 = 0x10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0x18;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0x14;
      }
      else {
        iVar3 = 0x10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_00484a26(param_1 + 100,iVar3);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0xe;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0xc;
  }
  else {
    iVar3 = 10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0xe;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0xe;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0xc;
      }
      else {
        iVar3 = 10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_004d4892(param_1 + 100,iVar3);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0xe;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0xc;
  }
  else {
    iVar3 = 10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0xe;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0xe;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0xc;
      }
      else {
        iVar3 = 10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_004d489e(param_1 + 100,iVar3);
  uVar2 = FUN_00488290(0x12);
  FUN_004d49e0(param_1 + 100,uVar2);
  if ((*(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
  }
  FUN_004d49d4(param_1 + 100,iVar3);
  FUN_00488198(param_1 + 0x130);
  FUN_00439be4(&local_20,param_1 + 0x10,3);
  FUN_004d4954(param_1 + 0x130,local_20);
  if ((*(int *)(param_1 + 0x2c) * 3 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 3 + 0x50) / 0xa0;
  }
  FUN_004d4948(param_1 + 0x130,iVar3);
  if ((*(int *)(param_1 + 0x2c) * 3 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 3 + 0x50) / 0xa0;
  }
  FUN_004d497c(param_1 + 0x130,iVar3);
  FUN_004d496e(param_1 + 0x130,0x7f);
  FUN_00488198(param_1 + 0x13c);
  FUN_00439be4(&local_20,param_1 + 0x13,3);
  FUN_004d4954(param_1 + 0x13c,local_20);
  if ((*(int *)(param_1 + 0x2c) * 3 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 3 + 0x50) / 0xa0;
  }
  FUN_004d4948(param_1 + 0x13c,iVar3);
  FUN_004d496e(param_1 + 0x13c,0x7f);
  FUN_00488198(param_1 + 0x70);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0x10;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0xc;
  }
  else {
    iVar3 = 8;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0x10;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 8;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0x10;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0xc;
      }
      else {
        iVar3 = 8;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_004d4a6e(param_1 + 0x70,iVar3);
  FUN_004d48c4(param_1 + 0x70,0xff);
  FUN_00439be4(&local_20,param_1 + 0x39,3);
  FUN_004d48aa(param_1 + 0x70,local_20);
  if (-1 < (int)((uint)*(byte *)(param_1 + 0x24) << 0x1f)) {
    uVar2 = FUN_00488290(0x12);
    FUN_004d49ac(param_1 + 0x70,uVar2);
    iVar3 = FUN_0044fbe6(0);
    if ((iVar3 * 3 + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      iVar3 = FUN_0044fbe6(0);
      iVar3 = (iVar3 * 3 + 0x50) / 0xa0;
    }
    FUN_004d4988(param_1 + 0x70,iVar3);
    FUN_004d49c6(param_1 + 0x70,0x7f);
    iVar3 = FUN_0044fbe6(0);
    if ((iVar3 * 4 + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      iVar3 = FUN_0044fbe6(0);
      iVar3 = (iVar3 * 4 + 0x50) / 0xa0;
    }
    if (iVar3 == 0) {
      iVar3 = 0;
    }
    else {
      iVar3 = FUN_0044fbe6(0);
      if ((iVar3 * 4 + 0x50) / 0xa0 < 2) {
        iVar3 = 1;
      }
      else {
        iVar3 = FUN_0044fbe6(0);
        iVar3 = (iVar3 * 4 + 0x50) / 0xa0;
      }
      if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
        iVar3 = 1;
      }
      else {
        iVar3 = FUN_0044fbe6(0);
        if ((iVar3 * 4 + 0x50) / 0xa0 < 2) {
          iVar3 = 1;
        }
        else {
          iVar3 = FUN_0044fbe6(0);
          iVar3 = (iVar3 * 4 + 0x50) / 0xa0;
        }
        iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
      }
    }
    FUN_004d4994(param_1 + 0x70,iVar3);
  }
  FUN_00439be4(&local_20,param_1 + 0x33,3);
  FUN_004d4a2e(param_1 + 0x70,local_20);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0x18;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0x14;
  }
  else {
    iVar3 = 0x10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0x18;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0x14;
    }
    else {
      iVar3 = 0x10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0x18;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0x14;
      }
      else {
        iVar3 = 0x10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_00484a4e(param_1 + 0x70,iVar3);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0xe;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0xc;
  }
  else {
    iVar3 = 10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0xe;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0xe;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0xc;
      }
      else {
        iVar3 = 10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_00484a66(param_1 + 0x70,iVar3);
  if ((*(int *)(param_1 + 0x2c) * 5 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 5 + 0x50) / 0xa0;
  }
  FUN_004d489e(param_1 + 0x70,iVar3);
  if ((*(int *)(param_1 + 0x2c) * 5 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 5 + 0x50) / 0xa0;
  }
  FUN_004d4892(param_1 + 0x70,iVar3);
  FUN_00488198(param_1 + 0xc4);
  uVar2 = FUN_004410a6();
  FUN_004d4a88(param_1 + 0xc4,uVar2);
  FUN_004d4aa2(param_1 + 0xc4,0x23);
  FUN_00488198(param_1 + 0xd0);
  if ((int)((uint)*(byte *)(*(int *)(DAT_00485df4 + 0x178) + 0x24) << 0x1f) < 0) {
    uVar2 = FUN_0048834c(0x12,2);
    FUN_004d4a88(param_1 + 0xd0,uVar2);
  }
  else {
    uVar2 = FUN_004882d2(0x12,2);
    FUN_004d4a88(param_1 + 0xd0,uVar2);
  }
  FUN_004d4aa2(param_1 + 0xd0,0x7f);
  FUN_00488198(param_1 + 0x160);
  FUN_004d4a7a(param_1 + 0x160,1);
  FUN_004d493a(param_1 + 0x160,1);
  FUN_00488198(param_1 + 0x100);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0x18;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0x14;
  }
  else {
    iVar3 = 0x10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0x18;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0x14;
    }
    else {
      iVar3 = 0x10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0x18;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0x14;
      }
      else {
        iVar3 = 0x10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_00484a26(param_1 + 0x100,iVar3);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0x18;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0x14;
  }
  else {
    iVar3 = 0x10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0x18;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0x14;
    }
    else {
      iVar3 = 0x10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0x18;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0x14;
      }
      else {
        iVar3 = 0x10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_004d4892(param_1 + 0x100,iVar3);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0x18;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0x14;
  }
  else {
    iVar3 = 0x10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0x18;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0x14;
    }
    else {
      iVar3 = 0x10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0x18;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0x14;
      }
      else {
        iVar3 = 0x10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_004d489e(param_1 + 0x100,iVar3);
  FUN_00488198(param_1 + 0xf4);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0xe;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0xc;
  }
  else {
    iVar3 = 10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0xe;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0xe;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0xc;
      }
      else {
        iVar3 = 10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_00484a26(param_1 + 0xf4,iVar3);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0xe;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0xc;
  }
  else {
    iVar3 = 10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0xe;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0xe;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0xc;
      }
      else {
        iVar3 = 10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_00484a7e(param_1 + 0xf4,iVar3);
  FUN_00488198(param_1 + 0x10c);
  if ((*(int *)(param_1 + 0x2c) * 10 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 10 + 0x50) / 0xa0;
  }
  FUN_004d4892(param_1 + 0x10c,iVar3);
  if ((*(int *)(param_1 + 0x2c) * 10 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 10 + 0x50) / 0xa0;
  }
  FUN_004d489e(param_1 + 0x10c,iVar3);
  FUN_00488198(param_1 + 0x118);
  if ((*(int *)(param_1 + 0x2c) * 0x14 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 0x14 + 0x50) / 0xa0;
  }
  FUN_004d4a54(param_1 + 0x118,iVar3);
  FUN_00488198(param_1 + 0x124);
  FUN_004d4a60(param_1 + 0x124,2);
  FUN_00488198(param_1 + 0xdc);
  FUN_00484a26(param_1 + 0xdc,0);
  FUN_004d4892(param_1 + 0xdc,0);
  FUN_004d489e(param_1 + 0xdc,0);
  FUN_00488198(param_1 + 0xe8);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 8;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 6;
  }
  else {
    iVar3 = 2;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 8;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 6;
    }
    else {
      iVar3 = 2;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 8;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 6;
      }
      else {
        iVar3 = 2;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_00484a26(param_1 + 0xe8,iVar3);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 8;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 6;
  }
  else {
    iVar3 = 2;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 8;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 6;
    }
    else {
      iVar3 = 2;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 8;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 6;
      }
      else {
        iVar3 = 2;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_004d4892(param_1 + 0xe8,iVar3);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 8;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 6;
  }
  else {
    iVar3 = 2;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 8;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 6;
    }
    else {
      iVar3 = 2;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 8;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 6;
      }
      else {
        iVar3 = 2;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_004d489e(param_1 + 0xe8,iVar3);
  FUN_00488198(param_1 + 0x7c);
  FUN_00439be4(&local_20,param_1 + 0x10,3);
  FUN_004d48aa(param_1 + 0x7c,local_20);
  uVar2 = FUN_00441094();
  FUN_004d4a2e(param_1 + 0x7c,uVar2);
  FUN_004d48c4(param_1 + 0x7c,0xff);
  FUN_00488198(param_1 + 0x88);
  FUN_00439be4(&local_20,param_1 + 0x10,3);
  FUN_004d48aa(param_1 + 0x88,local_20);
  FUN_00439be4(&local_20,param_1 + 0x10,3);
  FUN_004d4a2e(param_1 + 0x88,local_20);
  FUN_004d48c4(param_1 + 0x88,0x33);
  FUN_00488198(param_1 + 0x94);
  FUN_00439be4(&local_20,param_1 + 0x13,3);
  FUN_004d48aa(param_1 + 0x94,local_20);
  uVar2 = FUN_00441094();
  FUN_004d4a2e(param_1 + 0x94,uVar2);
  FUN_004d48c4(param_1 + 0x94,0xff);
  FUN_00488198(param_1 + 0xa0);
  FUN_00439be4(&local_20,param_1 + 0x13,3);
  FUN_004d48aa(param_1 + 0xa0,local_20);
  FUN_00439be4(&local_20,param_1 + 0x13,3);
  FUN_004d4a2e(param_1 + 0xa0,local_20);
  FUN_004d48c4(param_1 + 0xa0,0x33);
  FUN_00488198(param_1 + 0xac);
  FUN_00439be4(&local_20,param_1 + 0x39,3);
  FUN_004d48aa(param_1 + 0xac,local_20);
  FUN_004d48c4(param_1 + 0xac,0xff);
  FUN_00439be4(&local_20,param_1 + 0x33,3);
  FUN_004d4a2e(param_1 + 0xac,local_20);
  FUN_00488198(param_1 + 0xb8);
  FUN_00439be4(&local_20,param_1 + 0x36,3);
  FUN_004d48aa(param_1 + 0xb8,local_20);
  FUN_004d48c4(param_1 + 0xb8,0xff);
  FUN_00439be4(&local_20,param_1 + 0x33,3);
  FUN_004d4a2e(param_1 + 0xb8,local_20);
  FUN_00488198(param_1 + 0x148);
  FUN_004d4a6e(param_1 + 0x148,0x7fff);
  FUN_00488198(param_1 + 0x154);
  FUN_004d4a6e(param_1 + 0x154,0);
  FUN_00488198(param_1 + 0x16c);
  FUN_004d4ac8(param_1 + 0x16c,*(int *)(param_1 + 0x2c) / 4 << 8);
  FUN_00488198(param_1 + 0x178);
  if ((*(int *)(param_1 + 0x2c) * 3 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 3 + 0x50) / 0xa0;
  }
  FUN_004d484a(param_1 + 0x178,iVar3);
  if ((*(int *)(param_1 + 0x2c) * 3 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 3 + 0x50) / 0xa0;
  }
  FUN_004d4856(param_1 + 0x178,iVar3);
  FUN_00488198(param_1 + 0x1b4);
  FUN_00439be4(&local_20,param_1 + 0x10,3);
  FUN_004d48aa(param_1 + 0x1b4,local_20);
  FUN_004d48c4(param_1 + 0x1b4,0xff);
  if ((*(int *)(param_1 + 0x2c) * 6 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 6 + 0x50) / 0xa0;
  }
  FUN_00484a26(param_1 + 0x1b4,iVar3);
  FUN_004d4a6e(param_1 + 0x1b4,0x7fff);
  FUN_00488198(param_1 + 0x19c);
  FUN_004d4ab0(param_1 + 0x19c,200);
  FUN_00488198(param_1 + 0x1a8);
  FUN_004d4ab0(param_1 + 0x1a8,0x78);
  FUN_00488198(param_1 + 0x1c0);
  FUN_00439be4(&local_20,param_1 + 0x39,3);
  FUN_004d4a14(param_1 + 0x1c0,local_20);
  if ((*(int *)(param_1 + 0x2c) * 0xf + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 0xf + 0x50) / 0xa0;
  }
  FUN_004d49fa(param_1 + 0x1c0,iVar3);
  FUN_004d4a06(param_1 + 0x1c0,1);
  FUN_00488198(param_1 + 0x1cc);
  FUN_00439be4(&local_20,param_1 + 0x10,3);
  FUN_004d4a14(param_1 + 0x1cc,local_20);
  FUN_00488198(param_1 + 0x1fc);
  FUN_004d4832(param_1 + 0x1fc,0x104);
  FUN_00488198(param_1 + 0x208);
  if ((*(int *)(param_1 + 0x2c) * 3 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 3 + 0x50) / 0xa0;
  }
  FUN_00484a26(param_1 + 0x208,iVar3);
  if ((*(int *)(param_1 + 0x2c) * 2 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 2 + 0x50) / 0xa0;
  }
  FUN_004d4920(param_1 + 0x208,iVar3);
  FUN_00439be4(&local_20,param_1 + 0x10,3);
  FUN_004d48f8(param_1 + 0x208,local_20);
  FUN_00439be4(&local_20,param_1 + 0x36,3);
  FUN_004d48aa(param_1 + 0x208,local_20);
  FUN_004d48c4(param_1 + 0x208,0xff);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0xc;
  }
  else {
    iVar3 = 8;
  }
  if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 8;
    }
    iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
  }
  FUN_004d4a6e(param_1 + 0x208,iVar3 / 2);
  FUN_004d4a48(param_1 + 0x208,*(undefined4 *)(param_1 + 0x18));
  uVar2 = FUN_00441094();
  FUN_004d4a2e(param_1 + 0x208,uVar2);
  FUN_00488198(param_1 + 0x214);
  FUN_004d48ec(param_1 + 0x214,&DAT_00485df0);
  FUN_00488198(param_1 + 0x220);
  if ((*(int *)(param_1 + 0x2c) * 4 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 4 + 0x50) / 0xa0;
  }
  FUN_00484a26(param_1 + 0x220,-iVar3);
  uVar2 = FUN_00441094();
  FUN_004d48aa(param_1 + 0x220,uVar2);
  FUN_00488198(param_1 + 0x22c);
  FUN_004d49d4(param_1 + 0x22c,1);
  FUN_00439be4(&local_20,param_1 + 0x33,3);
  FUN_004d49e0(param_1 + 0x22c,local_20);
  FUN_00488198(param_1 + 0x1f0);
  FUN_004d493a(param_1 + 0x1f0,0);
  if ((*(int *)(param_1 + 0x2c) * 10 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 10 + 0x50) / 0xa0;
  }
  FUN_004d489e(param_1 + 0x1f0,iVar3);
  FUN_00439be4(&local_20,param_1 + 0x39,3);
  FUN_004d49e0(param_1 + 0x1f0,local_20);
  FUN_00488198(param_1 + 0x1d8);
  if ((*(int *)(param_1 + 0x2c) * 3 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 3 + 0x50) / 0xa0;
  }
  FUN_004d49d4(param_1 + 0x1d8,iVar3);
  if ((*(int *)(param_1 + 0x2c) * 3 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 3 + 0x50) / 0xa0;
  }
  FUN_004d4a6e(param_1 + 0x1d8,iVar3);
  if ((*(int *)(param_1 + 0x2c) * 8 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 8 + 0x50) / 0xa0;
  }
  FUN_00484a10(param_1 + 0x1d8,iVar3,iVar3);
  if ((*(int *)(param_1 + 0x2c) * 2 + 0x50) / 0xa0 < 2) {
    iVar4 = 1;
  }
  else {
    iVar4 = (*(int *)(param_1 + 0x2c) * 2 + 0x50) / 0xa0;
  }
  FUN_004d489e(param_1 + 0x1d8,iVar4);
  FUN_00488198(param_1 + 0x1e4);
  FUN_004d4a6e(param_1 + 0x1e4,0x7fff);
  FUN_00484a10(param_1 + 0x1e4,iVar3,iVar3);
  FUN_00439be4(&local_20,param_1 + 0x10,3);
  FUN_004d48aa(param_1 + 0x1e4,local_20);
  FUN_004d48c4(param_1 + 0x1e4,0xff);
  FUN_00488198(param_1 + 0x280);
  FUN_00484a26(param_1 + 0x280,0);
  FUN_00484a7e(param_1 + 0x280,0);
  FUN_004d4a6e(param_1 + 0x280,0);
  FUN_004d4a7a(param_1 + 0x280,1);
  FUN_004d492c(param_1 + 0x280,0);
  FUN_00488198(param_1 + 0x2d4);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0xc;
  }
  else {
    iVar3 = 8;
  }
  if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 8;
    }
    iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
  }
  FUN_004d4a6e(param_1 + 0x2d4,iVar3);
  FUN_004d4a7a(param_1 + 0x2d4,1);
  FUN_004d48c4(param_1 + 0x2d4,0xff);
  FUN_00439be4(&local_20,param_1 + 0x36,3);
  FUN_004d48aa(param_1 + 0x2d4,local_20);
  FUN_00439be4(&local_20,param_1 + 0x33,3);
  FUN_004d4a2e(param_1 + 0x2d4,local_20);
  FUN_00488198(param_1 + 0x28c);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0xe;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0xc;
  }
  else {
    iVar3 = 10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0xe;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0xe;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0xc;
      }
      else {
        iVar3 = 10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_00484a4e(param_1 + 0x28c,iVar3);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0xe;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0xc;
  }
  else {
    iVar3 = 10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0xe;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0xe;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0xc;
      }
      else {
        iVar3 = 10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_00484a66(param_1 + 0x28c,iVar3);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0xe;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0xc;
  }
  else {
    iVar3 = 10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0xe;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0xe;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0xc;
      }
      else {
        iVar3 = 10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_00484a7e(param_1 + 0x28c,iVar3);
  if ((*(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
  }
  FUN_004d4920(param_1 + 0x28c,iVar3);
  FUN_004d4912(param_1 + 0x28c,0x19);
  FUN_00439be4(&local_20,param_1 + 0x33,3);
  FUN_004d48f8(param_1 + 0x28c,local_20);
  FUN_004d492c(param_1 + 0x28c,0);
  FUN_00488198(param_1 + 0x298);
  FUN_00484a26(param_1 + 0x298,0);
  FUN_00484a7e(param_1 + 0x298,0);
  if ((*(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
  }
  FUN_004d4920(param_1 + 0x298,iVar3);
  FUN_004d4912(param_1 + 0x298,0x19);
  FUN_00439be4(&local_20,param_1 + 0x33,3);
  FUN_004d48f8(param_1 + 0x298,local_20);
  FUN_004d492c(param_1 + 0x298,8);
  FUN_00488198(param_1 + 0x2a4);
  FUN_00484a26(param_1 + 0x2a4,0);
  FUN_00484a7e(param_1 + 0x2a4,0);
  FUN_00488198(param_1 + 700);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0xe;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0xc;
  }
  else {
    iVar3 = 10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0xe;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0xe;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0xc;
      }
      else {
        iVar3 = 10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_00484a4e(param_1 + 700,iVar3);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 8;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 6;
  }
  else {
    iVar3 = 2;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 8;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 6;
    }
    else {
      iVar3 = 2;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 8;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 6;
      }
      else {
        iVar3 = 2;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_00484a66(param_1 + 700,iVar3);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0xe;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0xc;
  }
  else {
    iVar3 = 10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0xe;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0xe;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0xc;
      }
      else {
        iVar3 = 10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_00484a7e(param_1 + 700,iVar3);
  FUN_00488198(param_1 + 0x2c8);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 8;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 6;
  }
  else {
    iVar3 = 2;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 8;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 6;
    }
    else {
      iVar3 = 2;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 8;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 6;
      }
      else {
        iVar3 = 2;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_00484a4e(param_1 + 0x2c8,iVar3);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 8;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 6;
  }
  else {
    iVar3 = 2;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 8;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 6;
    }
    else {
      iVar3 = 2;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 8;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 6;
      }
      else {
        iVar3 = 2;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_00484a66(param_1 + 0x2c8,iVar3);
  FUN_004d49c6(param_1 + 0x2c8,0);
  FUN_004d48c4(param_1 + 0x2c8,0);
  FUN_00439be4(&local_20,param_1 + 0x33,3);
  FUN_004d4a2e(param_1 + 0x2c8,local_20);
  FUN_00488198(param_1 + 0x2b0);
  FUN_00484a4e(param_1 + 0x2b0,0);
  FUN_00484a7e(param_1 + 0x2b0,0);
  FUN_00488198(param_1 + 0x2e0);
  FUN_004d48c4(param_1 + 0x2e0,0x33);
  uVar2 = FUN_00488290(0x12);
  FUN_004d48aa(param_1 + 0x2e0,uVar2);
  FUN_00488198(param_1 + 0x2ec);
  FUN_004d48c4(param_1 + 0x2ec,0);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 8;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 6;
  }
  else {
    iVar3 = 2;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 8;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 6;
    }
    else {
      iVar3 = 2;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 8;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 6;
      }
      else {
        iVar3 = 2;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_00484a66(param_1 + 0x2ec,iVar3);
  FUN_00488198(param_1 + 0x238);
  if ((*(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
  }
  FUN_004d4920(param_1 + 0x238,iVar3);
  FUN_00439be4(&local_20,param_1 + 0x39,3);
  FUN_004d48f8(param_1 + 0x238,local_20);
  FUN_004d492c(param_1 + 0x238,3);
  FUN_00488198(param_1 + 0x244);
  FUN_00439be4(&local_20,param_1 + 0x33,3);
  FUN_004d48f8(param_1 + 0x244,local_20);
  if ((*(int *)(param_1 + 0x2c) * 2 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 2 + 0x50) / 0xa0;
  }
  FUN_004d4920(param_1 + 0x244,iVar3);
  if ((*(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
  }
  FUN_004d487a(param_1 + 0x244,-iVar3);
  FUN_004d492c(param_1 + 0x244,4);
  FUN_004d4ab0(param_1 + 0x244,400);
  FUN_00488198(param_1 + 0x250);
  if ((int)((uint)*(byte *)(param_1 + 0x24) << 0x1f) < 0) {
    uVar2 = FUN_0048834c(0x12,2);
  }
  else {
    uVar2 = FUN_004882d2(0x12,1);
  }
  FUN_004d4a2e(param_1 + 0x250,uVar2);
  FUN_00488198(param_1 + 0x25c);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0xe;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0xc;
  }
  else {
    iVar3 = 10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0xe;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0xe;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0xc;
      }
      else {
        iVar3 = 10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_00484a26(param_1 + 0x25c,iVar3);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0xe;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0xc;
  }
  else {
    iVar3 = 10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0xe;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0xe;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0xc;
      }
      else {
        iVar3 = 10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_00484a7e(param_1 + 0x25c,iVar3 / 2);
  FUN_00488198(param_1 + 0x268);
  if ((*(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
  }
  FUN_004d4920(param_1 + 0x268,iVar3);
  FUN_00439be4(&local_20,param_1 + 0x39,3);
  FUN_004d48f8(param_1 + 0x268,local_20);
  FUN_00439be4(&local_20,param_1 + 0x36,3);
  FUN_004d48aa(param_1 + 0x268,local_20);
  FUN_004d48c4(param_1 + 0x268,0x33);
  FUN_00488198(param_1 + 0x274);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0xe;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0xc;
  }
  else {
    iVar3 = 10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0xe;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0xe;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0xc;
      }
      else {
        iVar3 = 10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_00484a4e(param_1 + 0x274,iVar3);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0xe;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0xc;
  }
  else {
    iVar3 = 10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0xe;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0xe;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0xc;
      }
      else {
        iVar3 = 10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_004d4862(param_1 + 0x274,iVar3);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 8;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 6;
  }
  else {
    iVar3 = 2;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 8;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 6;
    }
    else {
      iVar3 = 2;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 8;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 6;
      }
      else {
        iVar3 = 2;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_004d486e(param_1 + 0x274,iVar3);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0xe;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0xc;
  }
  else {
    iVar3 = 10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0xe;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0xe;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0xc;
      }
      else {
        iVar3 = 10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_00484a7e(param_1 + 0x274,iVar3);
  FUN_00488198(param_1 + 0x2f8);
  uVar2 = FUN_00488290(0x12);
  FUN_004d48aa(param_1 + 0x2f8,uVar2);
  FUN_004d48c4(param_1 + 0x2f8,0x7f);
  FUN_00488198(param_1 + 0x304);
  FUN_004d4988(param_1 + 0x304,0);
  if (*(char *)(param_1 + 0x28) == '\x03') {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 8;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0xc;
      }
      else {
        iVar3 = 8;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
    iVar3 = iVar3 / 2;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 8;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0xc;
      }
      else {
        iVar3 = 8;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_004d4a6e(param_1 + 0x304,iVar3);
  FUN_00488198(param_1 + 0x340);
  FUN_00439be4(&local_20,param_1 + 0x10,3);
  FUN_004d48f8(param_1 + 0x340,local_20);
  if ((*(int *)(param_1 + 0x2c) * 2 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 2 + 0x50) / 0xa0;
  }
  FUN_004d4920(param_1 + 0x340,iVar3 << 1);
  FUN_004d492c(param_1 + 0x340,1);
  if ((*(int *)(param_1 + 0x2c) * 2 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 2 + 0x50) / 0xa0;
  }
  FUN_004d4862(param_1 + 0x340,iVar3 << 1);
  FUN_00488198(param_1 + 0x334);
  if ((*(int *)(param_1 + 0x2c) * 2 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 2 + 0x50) / 0xa0;
  }
  FUN_004d497c(param_1 + 0x334,-iVar3);
  FUN_00488198(param_1 + 0x310);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0x18;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0x14;
  }
  else {
    iVar3 = 0x10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0x18;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0x14;
    }
    else {
      iVar3 = 0x10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0x18;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0x14;
      }
      else {
        iVar3 = 0x10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_00484a4e(param_1 + 0x310,iVar3);
  FUN_00484a66(param_1 + 0x310,0);
  FUN_00484a7e(param_1 + 0x310,0);
  FUN_004d4a7a(param_1 + 0x310,1);
  FUN_00488198(param_1 + 0x31c);
  if ((*(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
  }
  FUN_004d4920(param_1 + 0x31c,iVar3);
  FUN_00439be4(&local_20,param_1 + 0x39,3);
  FUN_004d48f8(param_1 + 0x31c,local_20);
  FUN_004d492c(param_1 + 0x31c,1);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0xe;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0xc;
  }
  else {
    iVar3 = 10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0xe;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0xe;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0xc;
      }
      else {
        iVar3 = 10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_00484a26(param_1 + 0x31c,iVar3);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0xe;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0xc;
  }
  else {
    iVar3 = 10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0xe;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0xc;
    }
    else {
      iVar3 = 10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0xe;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0xc;
      }
      else {
        iVar3 = 10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_004d489e(param_1 + 0x31c,iVar3);
  FUN_00488198(param_1 + 0x328);
  if (*(char *)(param_1 + 0x28) == '\x01') {
    iVar3 = 0x18;
  }
  else if (*(char *)(param_1 + 0x28) == '\x02') {
    iVar3 = 0x14;
  }
  else {
    iVar3 = 0x10;
  }
  if (iVar3 == 0) {
    iVar3 = 0;
  }
  else {
    if (*(char *)(param_1 + 0x28) == '\x01') {
      iVar3 = 0x18;
    }
    else if (*(char *)(param_1 + 0x28) == '\x02') {
      iVar3 = 0x14;
    }
    else {
      iVar3 = 0x10;
    }
    if ((iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0 < 2) {
      iVar3 = 1;
    }
    else {
      if (*(char *)(param_1 + 0x28) == '\x01') {
        iVar3 = 0x18;
      }
      else if (*(char *)(param_1 + 0x28) == '\x02') {
        iVar3 = 0x14;
      }
      else {
        iVar3 = 0x10;
      }
      iVar3 = (iVar3 * *(int *)(param_1 + 0x2c) + 0x50) / 0xa0;
    }
  }
  FUN_004d484a(param_1 + 0x328,iVar3);
  FUN_00488198(param_1 + 0x34c);
  FUN_004d48c4(param_1 + 0x34c,0xff);
  uVar2 = FUN_00441094();
  FUN_004d48aa(param_1 + 0x34c,uVar2);
  uVar2 = FUN_00488290(0x12);
  FUN_004d48d2(param_1 + 0x34c,uVar2);
  FUN_004d4a6e(param_1 + 0x34c,0x7fff);
  if ((*(int *)(param_1 + 0x2c) * 0xf + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 0xf + 0x50) / 0xa0;
  }
  FUN_004d4988(param_1 + 0x34c,iVar3);
  uVar2 = FUN_00441094();
  FUN_004d49ac(param_1 + 0x34c,uVar2);
  if ((*(int *)(param_1 + 0x2c) * 5 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = (*(int *)(param_1 + 0x2c) * 5 + 0x50) / 0xa0;
  }
  FUN_004d49a0(param_1 + 0x34c,iVar3);
  FUN_00488198(param_1 + 0x358);
  FUN_00439be4(&local_20,param_1 + 0x33,3);
  FUN_004d49e0(param_1 + 0x358,local_20);
  iVar3 = FUN_0044fbe6(0);
  if ((iVar3 * 2 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = FUN_0044fbe6(0);
    iVar3 = (iVar3 * 2 + 0x50) / 0xa0;
  }
  FUN_004d49d4(param_1 + 0x358,iVar3);
  FUN_00439be4(&local_20,param_1 + 0x33,3);
  FUN_004d4a14(param_1 + 0x358,local_20);
  iVar3 = FUN_0044fbe6(0);
  if ((iVar3 * 2 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = FUN_0044fbe6(0);
    iVar3 = (iVar3 * 2 + 0x50) / 0xa0;
  }
  FUN_004d49fa(param_1 + 0x358,iVar3);
  iVar3 = FUN_0044fbe6(0);
  if ((iVar3 * 6 + 0x50) / 0xa0 < 2) {
    iVar3 = 1;
  }
  else {
    iVar3 = FUN_0044fbe6(0);
    iVar3 = (iVar3 * 6 + 0x50) / 0xa0;
  }
  FUN_004d483e(param_1 + 0x358,iVar3);
  return CONCAT44(local_1c,local_20);
}

