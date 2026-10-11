#!/usr/bin/env python3
"""Conservative literal-format inventory of sweep-disassembly BL sites."""
import collections
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
DIS = ROOT / 'g2/analysis/coverage-audit-parallel-2026-10-09/TDK-TRANSPORT-MAIN-DISASSEMBLY.txt'
OTA = ROOT / 'g2/blobs/official/g2-2.2.6.10/ota_s200_firmware_ota.bin'
BASE = 0x437fe0

def string_at(blob, addr):
    offset = addr - BASE
    if not 0 <= offset < len(blob):
        return None
    end = blob.find(b'\0', offset, min(len(blob), offset + 512))
    if end < 0:
        return None
    raw = blob[offset:end]
    if not raw or any(c < 32 and c not in (9, 10, 13) for c in raw):
        return None
    return raw.decode('utf-8', 'replace')

def signature(s):
    result = []
    i = 0
    while i < len(s):
        if s[i] != '%':
            i += 1
            continue
        i += 1
        if i < len(s) and s[i] == '%':
            i += 1
            continue
        while i < len(s) and s[i] in '-+ #0': i += 1
        if i < len(s) and s[i] == '*': result.append('*'); i += 1
        while i < len(s) and s[i].isdigit(): i += 1
        if i < len(s) and s[i] == '.':
            i += 1
            if i < len(s) and s[i] == '*': result.append('*'); i += 1
            while i < len(s) and s[i].isdigit(): i += 1
        while i < len(s) and s[i] in 'hlLjzt': i += 1
        if i < len(s): result.append(s[i]); i += 1
    return ''.join(result)

def main():
    blob = OTA.read_bytes()
    lines = DIS.read_text().splitlines()
    sites = []
    for index, line in enumerate(lines):
        if not re.search(r'\bbl\s+0x43d574\b', line): continue
        addr = int(line.split(':', 1)[0], 16)
        # Require a nearby store of a register into the stock format slot.
        window = lines[max(0, index - 32):index]
        store = None
        for j in range(len(window)-1, -1, -1):
            m = re.search(r'\bstr(?:\.w)?\s+(r\d+), \[sp, #4\]', window[j])
            if m:
                store = (j, m.group(1)); break
        fmt = None
        if store:
            j, reg = store
            for instruction in reversed(window[:j]):
                m = re.search(r'\bldr(?:\.w)?\s+'+reg+r', \[pc, #\d+\].*?0x([0-9a-f]+)', instruction)
                if m:
                    lit = int(m.group(1), 16) - BASE
                    if 0 <= lit <= len(blob)-4:
                        ptr = int.from_bytes(blob[lit:lit+4], 'little')
                        fmt = string_at(blob,ptr)
                        if fmt is not None: fmt = {'address':hex(ptr),'text':fmt,'signature':signature(fmt)}
                    break
                m=re.search(r'\badr\s+'+reg+r', 0x([0-9a-f]+)',instruction)
                if m:
                    ptr=int(m.group(1),16)
                    fmt_text=string_at(blob,ptr)
                    if fmt_text is not None:
                        fmt={'address':hex(ptr),'text':fmt_text,
                             'signature':signature(fmt_text)}
                    break
                if re.search(r'\b(?:mov|add|sub|ldr|adr|pop)\S*\s+'+reg+r'\b',instruction): break
        sites.append({'call':hex(addr),'format':fmt})
    resolved = [s for s in sites if s['format']]
    unique = {x['format']['address']:x['format'] for x in resolved}
    signatures = collections.Counter(x['format']['signature'] for x in resolved)
    result = {'image_sha256':hashlib.sha256(blob[32:]).hexdigest(),
              'sweep_bl_count':len(sites),'literal_resolved_sites':len(resolved),
              'unique_literal_formats':len(unique),'signature_site_counts':dict(signatures.most_common()),
              'formats':sorted(unique.values(), key=lambda x:int(x['address'],16)),
              'sites':sites,
              'limit':'Syntactic BL sites in linear sweep; this is not reachable-call or exhaustive argument-count proof. Unresolved sites may use other materialization patterns.'}
    Path(__file__).with_name('inventory.json').write_text(json.dumps(result,indent=2,ensure_ascii=False)+'\n')
    print(json.dumps({k:result[k] for k in ('image_sha256','sweep_bl_count','literal_resolved_sites','unique_literal_formats','signature_site_counts')},indent=2))

if __name__ == '__main__': main()
