
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 gx8002_tws_audio_callback(int param_1)

{
  byte bVar1;
  uint uVar2;
  int iVar3;
  int *piStack_20;
  undefined1 auStack_1c [4];
  undefined4 uStack_18;
  int iStack_14;
  
  if (-1 < param_1) {
    func_0x10206ec8(param_1,&piStack_20,auStack_1c);
    piStack_20[2] = param_1;
    *(byte *)(piStack_20 + 3) = *(byte *)(piStack_20 + 3) & 0x3f;
    bVar1 = func_0x10207394();
    iVar3 = *piStack_20;
    for (uVar2 = 0; uVar2 < *(uint *)(iVar3 + 8); uVar2 = uVar2 + 1) {
      func_0x10206f08(piStack_20,uVar2,0);
    }
    func_0x102075c8(piStack_20);
    if (*(int *)(*piStack_20 + 4) == 0) {
      *(byte *)(piStack_20 + 3) = *(byte *)(piStack_20 + 3) & 0xf8 | 1;
    }
    else {
      iVar3 = func_0x10206e9c();
      if (*(uint *)(iVar3 + 0x30) / *(uint *)(iVar3 + 0x24) < (uint)piStack_20[2]) {
        bVar1 = *(byte *)(piStack_20 + 3) & 0xf8 | bVar1 & 7;
      }
      else {
        bVar1 = *(byte *)(piStack_20 + 3) & 0xf8 | 1;
      }
      *(byte *)(piStack_20 + 3) = bVar1;
    }
    gx8002_tws_standby_loop();
    iVar3 = _gx8002_active_snpu_queue_pointer;
    if ((*(byte *)(piStack_20 + 3) & 7) != 0) {
      *(undefined4 *)(_gx8002_active_snpu_queue_pointer + 0x4c) = 2;
      *(undefined4 *)(iVar3 + 0x50) = 0x32;
    }
    func_0x100260e4();
    uVar2 = piStack_20[2];
    if ((uVar2 == (uVar2 / 0xf) * 0xf) ||
       ((*(byte *)(piStack_20 + 3) & 7) != *(uint *)(iVar3 + 0x54))) {
      func_0x10206c24(uRam100264d8,uVar2,*(byte *)(piStack_20 + 3) & 7,
                      *(byte *)((int)piStack_20 + 0xe) & 7,0);
      if ((*(byte *)(piStack_20 + 3) & 7) != *(uint *)(iVar3 + 0x54)) {
        *(uint *)(iVar3 + 0x54) = *(byte *)(piStack_20 + 3) & 7;
      }
    }
    uStack_18 = 0x5b;
    iStack_14 = piStack_20[2];
    func_0x10208cc0(&uStack_18);
  }
  return 0;
}

