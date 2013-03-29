#!/usr/bin/env python
import sys
import fileinput
from optparse import OptionParser

from molecule import Molecule, Atom

def get_arguments(args=None):
    if args is None:
        args == sys.argv[1:]

    parser = OptionParser(usage="xyz2xyz [options]",
                          version="0.1",
                          description="converts the xyz file to a valid fmoxyz group")
    parser.add_option("-x", dest="shiftx", default=0.0, help="shifts the molecule x angstrom in the x-direction")
    parser.add_option("-y", dest="shifty", default=0.0, help="shifts the molecule y angstrom in the y-direction")
    parser.add_option("-z", dest="shiftz", default=0.0, help="shifts the molecule z angstrom in the z-direction")
    (options, args) = parser.parse_args(args)

    #if len(args) != 1:
    #    parser.print_help()
    #    sys.exit()

    # fileinput tries to read everything from args
    # so we reset it here to make it no try and do that.
    sys.argv = []

    return (options, args)
    
def parse_lines():
    #f = open(filename,'r')
    isParsing = True
    mol = None
    line_counter = 0
    n_atoms = 0
    mol = Molecule("")
    title = ""
    to_angs = False
    datas = []
    for line in fileinput.input():
        data = line.split()
        if isParsing:
            line_counter += 1
            if line_counter == 1: n_atoms = int(data[0])
            if line_counter == 2:
                uline = line.upper()
                to_angs = "AU" in uline
            if line_counter > 2:
                toangs = 1.0
                if to_angs: toangs = 0.529177249
                char = data[0]
                data = map(float, data[1:])
                atom = Atom(char, data[0]*toangs, data[1]*toangs, data[2]*toangs)
                if mol is not None:
                    mol.addAtom(atom)
    #f.close()
    return mol

char2charge = {'H':1.0, 'C':6.0, 'N':7.0, 'O':8.0, 'S':16.0}

def tostr(mol):
    s = "%i\n%s\n" % (len(mol.atoms), mol.title)
    temp = "\n".join("%s %20.12f %20.12f %20.12f" % (atom.char, atom.x, atom.y, atom.z) for atom in mol.atoms)
    return "%s%s" % (s, temp)

if __name__ == '__main__':
    (options,args) = get_arguments()
    mol = parse_lines()

    # apply perturbations by arguments, we can apply x,y and z
    # simultaniously
    for atom in mol.atoms:
        atom.x += float(options.shiftx)
        atom.y += float(options.shifty)
        atom.z += float(options.shiftz)

    print tostr(mol)
