import struct,sys
B=open(sys.argv[1],'rb').read(); BASE=0x437FE0
def rd(a,n): o=a-BASE; return B[o:o+n]
def u32(a): return struct.unpack('<I',rd(a,4))[0]
def u16(a): return struct.unpack('<H',rd(a,2))[0]
LT={0:'bool',1:'int',2:'uint',3:'sint',4:'fixed32',5:'fixed64',6:'bytes',7:'string',8:'message',9:'message_cb',0xA:'ext',0xB:'fixed_bytes'}
HT={0:'required',1:'optional',2:'repeated',3:'oneof'}
AT={0:'static',2:'pointer',1:'callback'}
seen={}
def dump(d,name,depth=0):
    if d in seen: print('  '*depth+f'{name} -> see {d:#x}'); return
    seen[d]=1
    fi=u32(d); sm=u32(d+4); fc=u16(d+16); rc=u16(d+18); lt=u16(d+20)
    print('  '*depth+f'MSG {name} @{d:#x} fields={fc} required={rc} largest_tag={lt}')
    p=fi; si=0
    for i in range(fc):
        w0=u32(p); n=1<<(w0&3)
        ws=[u32(p+4*k) for k in range(n)]
        t=(w0>>2)&0x3f; typ=(w0>>8)&0xff

        if n==1:
            tag=(w0>>2)&0x3f; so=(w0>>24)&0xf; off=(w0>>16)&0xff; dsz=(w0>>28)&0xf; asz=1
        elif n==2:
            tag=((w0>>2)&0x3f)|(((ws[1]>>28)&0xf)<<6); asz=(w0>>16)&0xfff; so=(w0>>28)&0xf; off=ws[1]&0xffff; dsz=(ws[1]>>16)&0xfff
        elif n==4:
            tag=((w0>>2)&0x3f)|((ws[1]>>8)<<6); asz=w0>>16; so=ws[1]&0xff; off=ws[2]; dsz=ws[3]
        else:
            tag=((w0>>2)&0x3f)|((ws[1]>>8)<<6); asz=ws[4]; so=ws[1]&0xff; off=ws[2]; dsz=ws[3]
        ltyp=typ&0xf; ht=(typ>>4)&3; at=(typ>>6)&3
        print('  '*depth+f'  tag {tag:3d} {AT.get(at)} {HT.get(ht)} {LT.get(ltyp,ltyp)} off={off:#x} size={dsz} array={asz} sizeoff={so}')
        if ltyp in (8,9):
            sub=u32(sm+4*si); si+=1
            dump(sub,f'{name}.{tag}',depth+2)
        p+=4*n
dump(int(sys.argv[2],16),'root')
