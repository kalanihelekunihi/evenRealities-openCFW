
undefined4
hciEvtProcessCmdCmpl(undefined1 *param_1,byte param_2,undefined4 param_3,undefined4 param_4)

{
  undefined1 uVar1;
  uint uVar2;
  undefined2 *puVar3;
  undefined1 *puVar4;
  undefined1 *extraout_r1;
  uint uVar5;
  byte bVar6;
  code *pcVar7;
  undefined8 uVar8;
  
  bVar6 = 0;
  pcVar7 = *(code **)(DAT_0056b7c8 + 8);
  uVar1 = *param_1;
  uVar2 = (uint)(byte)param_1[2] * 0x100 + (uint)(byte)param_1[1];
  uVar5 = DAT_0056b7c8;
  if (uVar2 == 0xc2d) {
    bVar6 = 9;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0xc7c) {
    bVar6 = 0x27;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0xc83) {
    bVar6 = 0x4c;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x100d) {
    bVar6 = 0x4d;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x100e) {
    bVar6 = 0x4e;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x100f) {
    bVar6 = 0x4f;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x1405) {
    bVar6 = 7;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x200a) {
    bVar6 = 0x35;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x200c) {
    bVar6 = 0x34;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x200e) {
    bVar6 = 5;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x2015) {
    bVar6 = 8;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x2017) {
    bVar6 = 0x1b;
    pcVar7 = *(code **)(DAT_0056b7c8 + 0xc);
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x2018) {
    bVar6 = 0x1c;
    pcVar7 = *(code **)(DAT_0056b7c8 + 0xc);
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x201a) {
    bVar6 = 0xc;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x201b) {
    bVar6 = 0xd;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x2020) {
    bVar6 = 0x1d;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x2021) {
    bVar6 = 0x1e;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x2022) {
    bVar6 = 0x21;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x2023) {
    bVar6 = 0x1f;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x2024) {
    bVar6 = 0x20;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x2027) {
    bVar6 = 0x15;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x2028) {
    bVar6 = 0x16;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x2029) {
    bVar6 = 0x17;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x202b) {
    bVar6 = 0x18;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x202c) {
    bVar6 = 0x19;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x202d) {
    bVar6 = 0x1a;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x202f) {
    bVar6 = 0x22;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x2030) {
    bVar6 = 0x29;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x2031) {
    bVar6 = 0x2a;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x2039) {
    bVar6 = 0x37;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x2040) {
    bVar6 = 0x38;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x2042) {
    bVar6 = 0x36;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x2054) {
    bVar6 = 0x3f;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x2055) {
    bVar6 = 0x40;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x2056) {
    bVar6 = 0x41;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x2057) {
    bVar6 = 0x42;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x2062) {
    bVar6 = 0x48;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x2065) {
    bVar6 = 0x49;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x206c) {
    bVar6 = 0x54;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x206e) {
    bVar6 = 0x4a;
    puVar4 = (undefined1 *)0x0;
  }
  else if (uVar2 == 0x206f) {
    bVar6 = 0x4b;
    puVar4 = (undefined1 *)0x0;
  }
  else {
    puVar4 = (undefined1 *)(uVar2 >> 10);
    if ((undefined1 *)(uVar2 >> 10) == (undefined1 *)0x3f) {
      bVar6 = 0x12;
      puVar4 = param_1 + 3;
      uVar5 = (uint)param_2;
    }
  }
  if ((bVar6 != 0) &&
     (uVar8 = WsfBufAlloc(*(undefined1 *)(DAT_0056b7cc + (uint)bVar6),(uint)bVar6,uVar5),
     puVar4 = (undefined1 *)((ulonglong)uVar8 >> 0x20), puVar3 = (undefined2 *)uVar8,
     puVar3 != (undefined2 *)0x0)) {
    *puVar3 = 0;
    *(byte *)(puVar3 + 1) = bVar6;
    *(undefined1 *)((int)puVar3 + 3) = 0;
    (**(code **)(DAT_0056b7d0 + (uint)bVar6 * 4))(puVar3,param_1 + 3,param_2);
    (*pcVar7)(puVar3);
    WsfBufFree(puVar3);
    puVar4 = extraout_r1;
  }
  hciCmdRecvCmpl(uVar1,puVar4);
  return param_4;
}

