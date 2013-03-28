"""Converts an EFP potential to the corresponding
   Polarizable Embedding potential
"""
import sys
import fileinput
import numpy

def labelize(label):
    """the goal here is to split the label into more
       sensible parts (count and atom label)
    """
    idx = int(label[1:3])
    symbol = label[3:]
    return (idx, symbol)

def labelize_polarizable_point(label):
    """The naming scheme for polarizable points is somewhat
       ridiculous. CTn, n=1,2, ... here we label it X
    """
    idx = int(label[2:])
    symbol = 'X'
    return (idx, symbol)

def coordinates(line):
    """LABEL  X   Y   Z   WEIGHT  CHARGE
    """
    # from GAMESS, the labels are A**S where
    # S is the symbol of the atom and ** are
    # atom counters.
    line = line[0]
    data = line.split()
    label = labelize(data[0])
    return (label[0], label[1], map(float, data[1:]))


def monopole(line):
    """LABEL  Q    Z
       the partial charge we are interested in is thus
       Q + Z
    """
    line = line[0]
    data = line.split()
    label = labelize(data[0])
    values = float(data[1]) + float(data[2])
    return (label[0], label[1], [values])

def dipole(line):
    """LABEL   X    Y    Z
    """
    line = line[0]
    data = line.split()
    label = labelize(data[0])
    return (label[0], label[1], map(float, data[1:]))

def quadrupoles(line):
    """data comes in in multiple rows, parse it and
       remove stuff we do not need
    """
    data = []
    for item in line:
        data.extend(item.split())
    #data = line.split()
    data.pop(5) # remove the ">"
    label = labelize(data[0])
    return (label[0], label[1], map(float, data[1:]))

def octupoles(line):
    """data comes in in multiple rows, parse it and
       remove stuff we do not need
    """
    data = []
    for item in line:
        data.extend(item.split())
    data.pop(10) # remove the ">"
    data.pop(5) # remove the ">"
    label = labelize(data[0])
    return (label[0], label[1], map(float, data[1:]))

def polarizable_point(line):
    """Contrary to EFP, the PE model uses symmetric polarizability
       tensors. Let us symmetrise them here and store them that way.
       the format is
       LABEL   X   Y   Z
       followed by components of the tensor
       XX XY XZ
       YX YY YZ
       ZX ZY ZZ
    """
    data = []
    for item in line:
        data.extend(item.split())
    data.pop(13) # remove the ">"
    data.pop(8) # remove the ">"
    label = labelize_polarizable_point(data[0])

    data = map(float, data[1:])
    polt = numpy.array(data[3:])
    polt = numpy.reshape(polt,(3,3))
    symt = numpy.dot(polt, polt.transpose()) * 0.5
    symt = numpy.ravel(symt)
    # this extracts the upper half triangle of the symmetric matrix
    data = data[0:3]
    data.extend(symt[numpy.array([True, True, True, False, True, True, False, False, True])])
    return (label[0], label[1], data)
    

# keys to parse
# pointer to function that will parse
# number of lines to read before parsing
keys = {'COORDINATES':(coordinates, 1),
        'MONOPOLES':(monopole,1),
        'DIPOLES':(dipole,1),
        'QUADRUPOLES':(quadrupoles,2),
        'OCTUPOLES':(octupoles,3),
        'POLARIZABLE POINT':(polarizable_point,4)}
values = {}
for key in keys:
    if not values.has_key(key):
        values[key] = {}

def main():
    read_file()
    dump_pe_potential()

def read_file():
    parsing = False
    parser = None
    line_data = []
    multiline_counter = 0
    multiline_count = 0
    for line in fileinput.input():
        if parsing and "STOP" in line:
            parsing = False
            parser = None
            multiline_counter = 0

        if not parsing:
            for key in keys:
                if key in line and not 'DYN' in line:
                    parsing = True
                    parser = keys[key][0]
                    multiline_count = keys[key][1]
                if parsing: break

            if parsing: continue

        if parsing and multiline_counter < multiline_count:
            multiline_counter += 1
            line_data.append(line)

        if parsing and multiline_counter == multiline_count:
            idx,symbol,data = parser(line_data)
            values[key][idx] = data
            line_data = []
            multiline_counter = 0

def dump_pe_potential():
    """The format for the PE potential file is straightforward
       first comes coordinates in xyz-format with a label stating
       either AU (atomic units) or AA (Angstrom)
       2nd is monopoles
       3rd is dipoles
       4th is quadrupoles
       5th is octupoles
       6th is alphas (symmetric!)
       7th is exclusion list
    """
    # we have to make sure of the order of the data is OK
    nat = 3
    npol= 4
    atomids = range(1,nat+1)
    print "coordinates"
    print "%i" % (nat+npol)
    print "AU"
    for idx in atomids:
        data = values['COORDINATES'][idx]
        print "%i %21.12f %21.12f %21.12f" % (idx, data[0], data[1], data[2])

    for idx in range(1,npol+1):
        data = values['POLARIZABLE POINT'][idx][0:3]
        print "%i" % (idx+nat),
        for item in data:
            print " %20.12f" % (item),
        print

    print "monopoles"
    print "%i" % nat
    for idx in atomids:
        data = values['MONOPOLES'][idx]
        print "%2i %21.12f" % (idx, data[0])

    print "dipoles"
    print "%i" % nat
    for idx in atomids:
        data = values['DIPOLES'][idx]
        print "%2i %21.12f %21.12f %21.12f" % (idx, data[0], data[1], data[2])

    print "quadrupoles"
    print "%i" % nat
    for idx in atomids:
        data = values['QUADRUPOLES'][idx]
        print "%2i" % (idx),
        for item in data:
            print " %20.12f" % (item),
        print

    print "octupoles"
    print "%i" % nat
    for idx in atomids:
        data = values['OCTUPOLES'][idx]
        print "%2i" % (idx),
        for item in data:
            print " %20.12f" % (item),
        print

    print "alphas"
    print "%i" % npol
    for idx in range(1,npol+1):
        data = values['POLARIZABLE POINT'][idx][3:]
        print "%2i" % (idx+nat),
        for item in data:
            print " %20.12f" % (item),
        print

    # the exclusion list avoids self-interaction
    # to make a fragment not interact with it self
    # we basically permute all points and print it
    print "exclists"
    print "%i" % (nat+npol)
    datas = range(1,nat+npol+1)
    for k in range(nat+npol):
      for item in datas:
        print "%i" % (item),
      print
      datas.append(datas.pop(0))
if __name__ == '__main__':
    main()
