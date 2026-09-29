
/* WARNING: Control flow encountered bad instruction data */
/* WARNING: Removing unreachable block (ram,0x10010172) */
/* WARNING: Removing unreachable block (ram,0x100105d4) */
/* WARNING: Removing unreachable block (ram,0x1001069a) */
/* WARNING: Removing unreachable block (ram,0x100105e0) */
/* WARNING: Removing unreachable block (ram,0x1001017e) */
/* WARNING: Removing unreachable block (ram,0x100105e4) */
/* WARNING: Removing unreachable block (ram,0x1001012e) */
/* WARNING: Removing unreachable block (ram,0x10010236) */
/* WARNING: Removing unreachable block (ram,0x10010136) */
/* WARNING: Removing unreachable block (ram,0x10010188) */
/* WARNING: Removing unreachable block (ram,0x10010244) */
/* WARNING: Removing unreachable block (ram,0x1001018c) */
/* WARNING: Removing unreachable block (ram,0x10010142) */
/* WARNING: Removing unreachable block (ram,0x10010152) */
/* WARNING: Removing unreachable block (ram,0x10010156) */
/* WARNING: Removing unreachable block (ram,0x1001015e) */
/* WARNING: Removing unreachable block (ram,0x1001026e) */
/* WARNING: Removing unreachable block (ram,0x1001016a) */
/* WARNING: Removing unreachable block (ram,0x10010280) */
/* WARNING: Removing unreachable block (ram,0x100105d0) */
/* WARNING: Removing unreachable block (ram,0x10010288) */
/* WARNING: Removing unreachable block (ram,0x100102a0) */
/* WARNING: Removing unreachable block (ram,0x100102bc) */
/* WARNING: Removing unreachable block (ram,0x1001071a) */
/* WARNING: Removing unreachable block (ram,0x100102c4) */
/* WARNING: Removing unreachable block (ram,0x100102d8) */
/* WARNING: Removing unreachable block (ram,0x100102ee) */
/* WARNING: Removing unreachable block (ram,0x10010208) */
/* WARNING: Removing unreachable block (ram,0x1001020c) */
/* WARNING: Removing unreachable block (ram,0x10010218) */
/* WARNING: Removing unreachable block (ram,0x1001021c) */
/* WARNING: Removing unreachable block (ram,0x100101de) */
/* WARNING: Removing unreachable block (ram,0x100105b8) */
/* WARNING: Removing unreachable block (ram,0x100101c8) */
/* WARNING: Removing unreachable block (ram,0x10010224) */
/* WARNING: Removing unreachable block (ram,0x10010228) */
/* WARNING: Removing unreachable block (ram,0x100101cc) */
/* WARNING: Removing unreachable block (ram,0x100101d0) */
/* WARNING: Removing unreachable block (ram,0x10010182) */
/* WARNING: Removing unreachable block (ram,0x100101fa) */
/* WARNING: Removing unreachable block (ram,0x10010126) */
/* WARNING: Removing unreachable block (ram,0x10010200) */
/* WARNING: Removing unreachable block (ram,0x1001024e) */
/* WARNING: Removing unreachable block (ram,0x10010204) */
/* WARNING: Removing unreachable block (ram,0x1001019c) */
/* WARNING: Removing unreachable block (ram,0x100101a0) */
/* WARNING: Removing unreachable block (ram,0x1001025c) */
/* WARNING: Removing unreachable block (ram,0x100101ac) */
/* WARNING: Removing unreachable block (ram,0x100101b2) */

undefined4 FUN_100100bc(undefined4 param_1)

{
  uint in_vr0;
  uint in_vr1;
  
  if ((in_vr1 & 0x3fffffff) != 0) {
    if ((in_vr0 & 0x3fffffff) == 0) {
      if (((in_vr1 & 0x3fffffff) == 0) && ((int)in_vr0 < 0)) {
        param_1 = 0xffffffff;
      }
    }
    else {
      param_1 = FUN_10011298(PTR_s__100138c8_0x28_10010568);
    }
  }
  return param_1;
}

