from molecule import molecule
import math

# head of the html output
header = """<svg version="1.1" width="1000" height="1000" xmlns="http://www.w3.org/2000/svg">"""

# footer of the html output
footer = """</svg>"""

offsetx = 500
offsety = 500

def isfloat(value):
        try:
            float(value)
            return True
        except ValueError:
            return False

class Atom:
    def __init__(self, c_atom):
        self.c_atom = c_atom
        self.z = c_atom.z

    #convert the contents of the atom into a string and return
    def __str__(self):
        return "Element: %s, x: %f, y: %f, z: %f" % (self.c_atom.element, self.c_atom.x, self.c_atom.y, self.c_atom.z)

    #convert the atom into an svg shape
    def svg(self):
        cx = self.c_atom.x * 100.0 + offsetx
        cy = self.c_atom.y * 100.0 + offsety
        r = radius[self.c_atom.element]
        fill = element_name[self.c_atom.element]
        return ' <circle cx="%.2f" cy="%.2f" r="%d" fill="url(#%s)"/>\n' % (cx, cy, r, fill)

class Bond:
    def __init__(self, c_bond):
        self.c_bond = c_bond
        self.z = c_bond.z
        
    #convert contents of the bond to a string and return
    def __str__(self):
        return "Atom 1: {0}, Atom 2: {1}".format(self.c_bond.a1, self.c_bond.a2)
    
    def svg(self):
        # calculate coordinates of the two ends of the line
        x1 = self.c_bond.x1 * 100.0 + offsetx
        y1 = self.c_bond.y1 * 100.0 + offsety
        x2 = self.c_bond.x2 * 100.0 + offsetx
        y2 = self.c_bond.y2 * 100.0 + offsety

        self.__str__()
        
        # calculate the direction of the bond
        dx = x2 - x1
        dy = y2 - y1
        d = (dx ** 2 + dy ** 2) ** 0.5
        
        # calculate the perpendicular vectors
        px = dy / d * 10.0
        py = -dx / d * 10.0
        
        # calculate the coordinates of the four points of the rectangle
        x11 = x1 - px
        y11 = y1 - py
        x12 = x1 + px
        y12 = y1 + py
        x21 = x2 + px
        y21 = y2 + py
        x22 = x2 - px
        y22 = y2 - py
        
        # return the SVG string
        return '  <polygon points="%.2f,%.2f %.2f,%.2f %.2f,%.2f %.2f,%.2f" fill="green"/>\n' % (x11, y11, x12, y12, x21, y21, x22, y22)

class Molecule(molecule):

    #convert the contents of the molecule into a string and return
    def __str__(self):
        s = "Atoms:\n"
        for i in range(self.atom_no):
            atom = self.get_atom(i)
            s += "Atom %s at (%.3f, %.3f, %.3f)\n" % (atom.element, atom.x, atom.y, atom.z)
        s += "\nBonds:\n"
        for j in range(self.bond_no):
            bond = self.get_bond(j)
            s += "Bond between atoms %d and %d\n" % (bond.a1, bond.a2)
        return s
    
     #convert the contents of the molecule into a string and return
    def molecule_data(self):
        output = "Number of Atoms: " + str(self.atom_no) + "\n"
        output += " | Number of Bonds: " + str(self.bond_no)
        return output

    # This function generates an SVG image based on atom and bond data stored in the object.
    def svg(self):

        # Initialize lists to store Atom and Bond objects.
        atoms = [];
        bonds = [];

        # Convert each atom and bond in the object to an Atom or Bond object and add to appropriate list.
        for i in range(self.atom_no):
            atom = self.get_atom(i)
            atoms.append(Atom(atom))
            
        for j in range(self.bond_no):
            bond = self.get_bond(j)
            bonds.append(Bond(bond))

        # Sort the Atom and Bond lists by z-coordinate (depth).
        atoms = sorted(atoms, key=lambda atom: atom.z)
        bonds = sorted(bonds, key=lambda bond: bond.z)

        # Create the SVG output by iterating through the sorted Atom and Bond lists.
        output = header
        output += "\n"
        i, j = 0, 0
        while i < len(atoms) and j < len(bonds):
            if atoms[i].z < bonds[j].z:
                output += atoms[i].svg()
                i += 1
            else:
                output += bonds[j].svg()
                j += 1
        while i < len(atoms):
            output += atoms[i].svg()
            i += 1
        while j < len(bonds):
            output += bonds[j].svg()
            j += 1
        output += footer

        # Add footer to SVG output and return.
        return output

    def parse(self, fileObj):
        for i, line in enumerate(fileObj):
            # Split the line into individual tokens.
            tokens = line.strip().split()

            # If there are 16 tokens and all of the first 3 are floats, then parse atom data.
            if len(tokens) == 16 and all([isfloat(s) for s in tokens[:3]]):
                # Check that the symbol is a string and the remaining tokens are floats
                if isinstance(tokens[3], str) and all([isfloat(s) for s in tokens[4:]]):
                    # Convert the first 4 tokens to floats if there is a decimal point.
                    x, y, z, symbol = [float(s) if '.' in s else s for s in tokens[:4]]
                    # Append the atom data to a data structure.
                    self.append_atom(symbol, x, y, z)

            # If there are 7 tokens and all of the first 3 are integers, then parse bond data.
            elif len(tokens) == 7 and len(tokens) <= 7 and all([s.isdigit() for s in tokens[:3]]):
                # Check that all tokens are integers
                if all([s.isdigit() for s in tokens]):
                    # Convert the first 3 tokens to integers.
                    atom1, atom2, bondType = [int(s) for s in tokens[:3]]
                    self.append_bond(atom1 - 1, atom2 - 1, bondType)

        return









