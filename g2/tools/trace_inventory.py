"""Deduplicate authenticated instruction traces by payload and byte address."""


def add_trace(ledger, payload, trace):
    items = ({"pc": pc, "bytes": raw} for pc, raw in trace.items()) if isinstance(trace, dict) else trace
    added = 0
    for item in items:
        pc = int(item["pc"], 0) if isinstance(item["pc"], str) else item["pc"]
        for offset, value in enumerate(bytes.fromhex(item["bytes"])):
            key = (payload, pc + offset)
            if key in ledger:
                if ledger[key] != value:
                    raise ValueError(f"Conflicting trace byte at {key}: {ledger[key]} != {value}")
            else:
                ledger[key] = value
                added += 1
    return added


def summarize(ledger):
    counts = {}
    for payload, address in ledger:
        counts[payload] = counts.get(payload, 0) + 1
    return {"unique_original_trace_bytes": counts, "unique_original_trace_total": len(ledger)}
