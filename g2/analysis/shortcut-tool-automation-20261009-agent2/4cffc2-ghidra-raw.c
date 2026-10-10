// Private authenticated original-byte program; raw decompiler output.
// ARM:LE:32:v8 default
// Body [[004cffc2, 004d0039]]

/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 bounded_4cffc2(int param_1,int *param_2,uint *param_3)

{
  uint uVar1;
  int iVar2;
  
  iVar2 = *param_2;
  uVar1 = -1 << (*param_3 & 0xff) & *(uint *)(param_1 + iVar2 * 4 + 0x14);
  if (uVar1 == 0) {
    uVar1 = -1 << (iVar2 + 1U & 0xff) & *(uint *)(param_1 + 0x10);
    if (uVar1 == 0) {
      return 0;
    }
    iVar2 = bounded_4cfd56(uVar1);
    *param_2 = iVar2;
    uVar1 = *(uint *)(param_1 + iVar2 * 4 + 0x14);
  }
  if (uVar1 == 0) {
    func_0x004d09b4(_DAT_004d0858,_DAT_004d06ac,0x238);
  }
  uVar1 = bounded_4cfd56(uVar1);
  *param_3 = uVar1;
  return *(undefined4 *)(param_1 + iVar2 * 0x80 + uVar1 * 4 + 0x74);
}

