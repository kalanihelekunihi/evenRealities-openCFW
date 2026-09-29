
int touch_config_197c_initialize
              (int *param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4)

{
  uint uVar1;
  int iVar2;
  int iVar3;
  undefined4 *puVar4;
  
  if (param_1 == (int *)0x0) {
    iVar2 = 1;
  }
  else {
    puVar4 = (undefined4 *)param_1[2];
    *(undefined1 *)(puVar4 + 0x1d) = 0;
    *(undefined1 *)((int)puVar4 + 0x75) = 0;
    *puVar4 = 0;
    puVar4[1] = 0;
    puVar4[3] = 0;
    puVar4[2] = 0;
    iVar2 = *(int *)param_1[3];
    for (uVar1 = 0; uVar1 < 3; uVar1 = uVar1 + 1) {
      *(byte *)(iVar2 + 0x23) = *(byte *)(iVar2 + 0x23) | 6;
      iVar2 = iVar2 + 0x3c;
    }
    puVar4[7] = 0;
    puVar4[0xb] = DAT_00004da8;
    iVar2 = *param_1;
    puVar4[5] = 0;
    *(undefined1 *)(puVar4 + 0x13) = 0;
    *(undefined1 *)((int)puVar4 + 0x57) = *(undefined1 *)(iVar2 + 0x2f);
    *(undefined1 *)(puVar4 + 0x16) = *(undefined1 *)(iVar2 + 0x2d);
    *(undefined1 *)((int)puVar4 + 0x59) = *(undefined1 *)(iVar2 + 0x31);
    *(undefined2 *)(puVar4 + 0xc) = *(undefined2 *)(iVar2 + 0x16);
    *(undefined2 *)((int)puVar4 + 0x32) = *(undefined2 *)(iVar2 + 0x18);
    *(undefined1 *)((int)puVar4 + 0x53) = *(undefined1 *)(iVar2 + 0x34);
    *(undefined1 *)(puVar4 + 0x15) = *(undefined1 *)(iVar2 + 0x35);
    *(short *)(puVar4 + 0xf) = (short)DAT_00004dac;
    *(undefined1 *)((int)puVar4 + 0x4e) = 0;
    *(undefined1 *)((int)puVar4 + 0x4f) = 0xff;
    *(undefined1 *)(puVar4 + 0x14) = 0x8e;
    *(undefined1 *)((int)puVar4 + 0x51) = 1;
    iVar3 = *(int *)param_1[3];
    for (uVar1 = 0; uVar1 < 3; uVar1 = uVar1 + 1) {
      if (*(short *)(iVar3 + 4) == 0) {
        *(byte *)(iVar3 + 0x23) = *(byte *)(iVar3 + 0x23) | 8;
      }
      if (*(short *)(iVar3 + 6) == 0) {
        *(byte *)(iVar3 + 0x23) = *(byte *)(iVar3 + 0x23) | 0x10;
      }
      iVar3 = iVar3 + 0x3c;
    }
    *(undefined2 *)(puVar4 + 0x10) = *(undefined2 *)(iVar2 + 0x1e);
    *(undefined2 *)((int)puVar4 + 0x3e) = *(undefined2 *)(iVar2 + 0x1c);
    *(undefined2 *)(puVar4 + 0x11) = *(undefined2 *)(iVar2 + 0x22);
    *(undefined2 *)((int)puVar4 + 0x42) = *(undefined2 *)(iVar2 + 0x20);
    *(undefined1 *)((int)puVar4 + 0x72) = 1;
    *(undefined1 *)((int)puVar4 + 0x4d) = 3;
    *(undefined1 *)((int)puVar4 + 0x5a) = 1;
    *(undefined1 *)((int)puVar4 + 0x5b) = 0;
    *(undefined1 *)(puVar4 + 0x17) = 0;
    *(undefined1 *)((int)puVar4 + 0x5d) = 6;
    *(undefined1 *)((int)puVar4 + 0x5e) = 4;
    *(undefined1 *)((int)puVar4 + 0x5f) = 10;
    *(undefined1 *)(puVar4 + 0x18) = 1;
    puVar4[9] = DAT_00004db0;
    *(undefined2 *)((int)puVar4 + 0x4a) = 0x20;
    iVar2 = event_dispatcher(0,param_1,0x4a,puVar4,param_4);
    if (iVar2 == 0) {
      iVar2 = touch_config_1972_start_wrapper(param_1);
    }
  }
  return iVar2;
}

