from elfpatch.map import parse_map

f = open("map.map")
t = f.read()
f.close()

print(parse_map(t))
