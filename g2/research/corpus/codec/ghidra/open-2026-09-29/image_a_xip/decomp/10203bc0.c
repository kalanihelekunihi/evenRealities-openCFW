
void gx8002_dma_initialize(void)

{
  int *piVar1;
  int iVar2;
  
  piVar1 = piRam10203c38;
  *piRam10203c38 = -0x5f000000;
  piVar1[1] = 2;
  piVar1[0xda] = (int)piVar1 + 0x17U & 0xfffffff0;
  *(undefined1 *)(piVar1 + 0xdc) = 0;
  piVar1[0xdb] = (int)piVar1 + 0x1c7U & 0xfffffff0;
  *(undefined1 *)((int)piVar1 + 0x371) = 0;
  func_0x10025080(0x19,1);
  iVar2 = *piVar1;
  *(undefined4 *)(iVar2 + 0x398) = 0;
  *(undefined4 *)(iVar2 + 0x338) = 0xffffffff;
  *(undefined4 *)(iVar2 + 0x340) = 0xffffffff;
  *(undefined4 *)(iVar2 + 0x348) = 0xffffffff;
  *(undefined4 *)(iVar2 + 0x350) = 0xffffffff;
  *(undefined4 *)(iVar2 + 0x358) = 0xffffffff;
  *(undefined4 *)(iVar2 + 0x398) = 1;
  func_0x10025080(0x19,0);
  func_0x1002553c(10,uRam10203c3c,0);
  return;
}

