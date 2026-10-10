import struct
f32 = lambda x: struct.unpack('<f', struct.pack('<f', x))[0]
def contract(us, hp, provider):
    assert 0 <= us <= 16777217
    if provider == 'stock_pinned':
        base = int(f32(f32(us) * 32))
        raw = int(f32(f32(f32(base) * 250) / 96)) if hp else base
        adjustment = 24 if hp else 15
    else:
        raw = (us * 83 + (us + 1) // 3) if hp else us * 32
        adjustment = 25 if hp else 15
    assert raw <= 0xffffffff
    return {'raw': raw, 'adjustment': adjustment, 'calls_loop': raw > adjustment, 'loop_argument': raw - adjustment if raw > adjustment else None}
inputs = sorted(set([0,1,2,3,4,5,10,100,2096,2097,2098,2099,2100,65535,65536,65537,16777215,16777216,16777217]))
rows = [{'us': n, 'hp': hp, 'stock_pinned': contract(n,hp,'stock_pinned'), 'sdk52': contract(n,hp,'sdk52')} for n in inputs for hp in [False,True]]

if __name__ == '__main__':
    import json
    print(json.dumps(rows, indent=2))
