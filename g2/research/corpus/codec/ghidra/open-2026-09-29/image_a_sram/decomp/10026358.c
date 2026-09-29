
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void gx8002_tws_tick(void)

{
  int iVar1;
  int iStack_14;
  int iStack_10;
  uint uStack_c;
  undefined4 uStack_8;
  
  iStack_14 = 0;
  iStack_10 = 0;
  iVar1 = func_0x10206fb0(_gx8002_active_snpu_queue_pointer,&iStack_14);
  if (iVar1 != 0) {
    if (iStack_14 == 0x100) {
      func_0x102088f8(iStack_10);
      func_0x102073a0(1);
    }
    if (*(byte *)(iStack_10 + 0xd) != 0) {
      uStack_8 = *(undefined4 *)(iStack_10 + 8);
      uStack_c = (uint)*(byte *)(iStack_10 + 0xd);
      func_0x10208cc0(&uStack_c);
    }
  }
  if ((*(int *)(_gx8002_active_snpu_queue_pointer + 0x4c) == 4) &&
     (iVar1 = func_0x102077f8(), iVar1 == 0)) {
    func_0x10207808(0xd);
  }
  return;
}

