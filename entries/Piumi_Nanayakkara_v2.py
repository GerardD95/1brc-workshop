import sys

def main():
    path = sys.argv[1]

    stats = {}
    stats_get = stats.get

    with open(path, "rb") as f:
        for line in f:
            # ---- trim newline ----
            if line[-1] == 10:     # \n
                if line[-2] == 13:  # \r\n
                    line = line[:-2]
                else:
                    line = line[:-1]

            # ---- find separator ----
            sep = line.find(b';')
            if sep == -1:
                continue

            name = line[:sep]   # bytes key
            t = line[sep + 1:]

            # ---- parse temperature ----
            i = 0
            neg = False
            b0 = t[0]
            if b0 == 45:  # '-'
                neg = True
                i = 1

            whole = 0
            b = t[i]
            while b != 46:  # '.'
                whole = whole * 10 + (b - 48)
                i += 1
                b = t[i]

            # exactly one fractional digit
            frac = t[i + 1] - 48
            temp = whole * 10 + frac
            if neg:
                temp = -temp

            # ---- update stats ----
            entry = stats_get(name)
            if entry is None:
                stats[name] = [1, temp, temp, temp]
            else:
                entry[0] += 1
                entry[1] += temp
                if temp < entry[2]:
                    entry[2] = temp
                if temp > entry[3]:
                    entry[3] = temp

    # ---- output ----
    out = []
    for name, entry in sorted(stats.items()):
        count, total, mn, mx = entry

        # mean as float in tenths to match ground truth
        mean_tenths = total / count

        out.append(
            f"{name.decode('utf-8', 'replace')}={(mn/10):.1f}/{(mean_tenths/10):.1f}/{(mx/10):.1f}"
        )

    sys.stdout.write("\n".join(out))


if __name__ == "__main__":
    main()
