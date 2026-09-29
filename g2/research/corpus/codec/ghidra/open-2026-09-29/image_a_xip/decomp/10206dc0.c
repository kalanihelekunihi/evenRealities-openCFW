
void gx8002_buffer_initialize(void)

{
  undefined4 *puVar1;
  undefined4 uVar2;
  undefined4 *puVar3;
  
  puVar1 = puRam10206e58;
  puVar3 = puRam10206e58 + 0x20;
  gx8002_memset(puRam10206e58,0,0x78);
  gx8002_memset(puVar3,0,0x63c0);
  gx8002_memset(uRam10206e5c,0,0x410);
  puVar1[0x1c] = uRam10206e60;
  puVar1[0x1d] = 0xf00;
  puVar1[0xc] = 0x30;
  puVar1[7] = 10;
  puVar1[8] = 16000;
  puVar1[9] = 4;
  puVar1[10] = 0xc;
  uVar2 = uRam10206e64;
  puVar1[0x1b] = 0x28;
  *puVar1 = uVar2;
  puVar1[2] = 2;
  puVar1[0x18] = 0x100;
  puVar1[0x14] = uRam10206e68;
  puVar1[0x11] = 0x2120;
  puVar1[0x15] = 0x1e00;
  puVar1[0x10] = 0x2140;
  puVar1[3] = 0;
  puVar1[0x16] = 0;
  puVar1[0x17] = 0;
  puVar1[4] = 0;
  puVar1[0x19] = 0;
  puVar1[0x1a] = 0;
  puVar1[0xb] = 0;
  puVar1[5] = 1;
  puVar1[6] = 0;
  puVar1[0x12] = 0;
  puVar1[0x13] = 0;
  puVar1[0xd] = 0;
  puVar1[0xe] = puVar3;
  puVar1[0xf] = 3;
  puVar1[1] = 1;
  return;
}

