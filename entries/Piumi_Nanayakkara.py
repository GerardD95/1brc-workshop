#!/usr/bin/env python3
"""
Compute min, mean, max temperature per station from a large measurements file.

Constraints:
- No external libraries.
- Measurements format: "<station>;<temperature>" with one fractional digit.
- Up to 10,000 unique station names.
- Must stream the file (no preloading).
- Output sorted by station: "Station;min;mean;max" with one fractional digit.
"""

import sys


def parse_line(line: str):
    # Using find instead of split for speed
    sep_idx = line.find(';')
    name = line[:sep_idx]
    t = line[sep_idx + 1:].rstrip('\n\r')

    # t like "-12.3" with exactly one fractional digit
    sign = -1 if t[0] == '-' else 1
    start = 1 if sign == -1 else 0
    dot = t.find('.', start)
    if dot == -1:
        return None, None
    whole = int(t[start:dot])
    frac = int(t[dot+1:dot+2])  # one digit
    temp_tenths = sign * (whole * 10 + frac)
    return name, temp_tenths


def compute_stats(measurements_path: str):
    stats = {}
    # Use buffered iteration; Python reads in chunks internally
    with open(measurements_path, "r", encoding="utf-8", newline="") as f:
        for line in f:
            name, temp = parse_line(line)
            entry = stats.get(name)
            if entry is None:
                # Initialize: count=1, sum=temp, min=temp, max=temp
                stats[name] = [1, temp, temp, temp]
            else:
                entry[0] += 1
                entry[1] += temp
                if temp < entry[2]:
                    entry[2] = temp
                if temp > entry[3]:
                    entry[3] = temp

    out_lines = []
    for name in sorted(stats.keys()):
        count, total, min_v, max_v = stats[name]
        out_lines.append(
            f"{name}={(min_v/10):.1f}/{(total/count/10):.1f}/{(max_v/10):.1f}"
        )
    return "\n".join(out_lines)

def main():
    measurements_path = sys.argv[1]
    result = compute_stats(measurements_path)
    print(result)

if __name__ == "__main__":
    main()