/* Analysis pseudocode for 0x311554; provider/IRQ/opcode semantics opaque. */
void activate(void) {
 unsigned saved=load_byte(0x801394), p=load_byte(0x801395);
 if(p==0) assert_3117d8(0x33451c,500);
 store_byte(0x801395,0);
 do {
  store_byte(0x801394,p);
  void *a=load_word(0x80131c+4*p);
  /* seti 0: encoding observed, live interrupt delivery not modeled. */
  enable_irq_encoding();
  void *e=call_310d38(a);
  indirect_dispatch(load_word(load_word(a)+4),a,e);
  call_310fb8(e);
  disable_irq_encoding(); sync_encoding();
  if(load_word(a+12)==0) store_half(0x80139a,load_half(0x80139a)&~(1u<<(p-1)));
  p=(unsigned char)opaque_vendor_7_0(load_half(0x80139a));
  if(p<=saved || p<=load_byte(0x801396)) break;
  if(p>=17) assert_3117d8(0x33451c,510);
 }while(p!=0);
 store_byte(0x801394,saved);
}
