import sqlite3
import os
import MolDisplay
from MolDisplay import Atom, Bond, Molecule

#database class to handle SQL functionality
class Database():
    def __init__( self, reset=False ):
        if reset:
            try:
                os.remove("molecules.db")
            except OSError:
                pass

        self.conn = sqlite3.connect("molecules.db")
        self.cursor = self.conn.cursor()

    def create_tables(self):
        # create cursor object
        c = self.conn.cursor()

        # Create the Elements table.
        c.execute('''CREATE TABLE Elements
                    (ELEMENT_NO INTEGER NOT NULL,
                    ELEMENT_CODE VARCHAR(3) NOT NULL,
                    ELEMENT_NAME VARCHAR(32) NOT NULL,
                    COLOUR1 CHAR(6) NOT NULL,
                    COLOUR2 CHAR(6) NOT NULL,
                    COLOUR3 CHAR(6) NOT NULL,
                    RADIUS DECIMAL(3) NOT NULL,
                    PRIMARY KEY (ELEMENT_NAME))''')

        # create Atoms
        c.execute('''CREATE TABLE Atoms
                    (ATOM_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    ELEMENT_CODE VARCHAR(3) NOT NULL,
                    X DECIMAL(7, 4) NOT NULL,
                    Y DECIMAL(7, 4) NOT NULL,
                    Z DECIMAL(7, 4) NOT NULL,
                    FOREIGN KEY (ELEMENT_CODE) REFERENCES Elements (ELEMENT_CODE))''')

        # create Bonds table
        c.execute('''CREATE TABLE Bonds
                    (BOND_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    A1 INTEGER NOT NULL,
                    A2 INTEGER NOT NULL,
                    EPAIRS INTEGER NOT NULL)''')

        # create Molecules table
        c.execute('''CREATE TABLE Molecules
                    (MOLECULE_ID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                    NAME TEXT UNIQUE NOT NULL)''')

        # create MoleculeAtom table
        c.execute('''CREATE TABLE MoleculeAtom
                    (MOLECULE_ID INTEGER NOT NULL,
                    ATOM_ID INTEGER NOT NULL,
                    PRIMARY KEY (MOLECULE_ID, ATOM_ID),
                    FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules (MOLECULE_ID),
                    FOREIGN KEY (ATOM_ID) REFERENCES Atoms (ATOM_ID))''')

        # create MoleculeBond table
        c.execute('''CREATE TABLE MoleculeBond
                    (MOLECULE_ID INTEGER NOT NULL,
                    BOND_ID INTEGER NOT NULL,
                    PRIMARY KEY (MOLECULE_ID, BOND_ID),
                    FOREIGN KEY (MOLECULE_ID) REFERENCES Molecules (MOLECULE_ID),
                    FOREIGN KEY (BOND_ID) REFERENCES Bonds (BOND_ID))''')

        # commit changes
        self.conn.commit()

        # close cursor
        c.close()

    def __setitem__(self, table, values):
        # Construct an SQL query string using table and values.
        query = f"INSERT INTO {table} VALUES {values}"
        self.cursor.execute(query)
        self.conn.commit()

    def remove_element(self, name):
        try:
            # Construct an SQL query to delete the row from the Elements table with the specified name
            query = "DELETE FROM Elements WHERE ELEMENT_NAME = ?"
            values = (name,)

            # Execute the SQL query using the cursor object stored in `self`
            self.cursor.execute(query, values)

            # Commit the changes to the database
            self.conn.commit()

            # Return a success message
            return True
        except:
            # Return a failure message
            return False

    def add_atom(self, molname, atom):
        # Get molecule ID from Molecules table
        query = "SELECT MOLECULE_ID FROM Molecules WHERE NAME = ?"
        values = (molname,)
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        if not result:
            raise ValueError("No such molecule in database")
        molecule_id = result[0]

        # Insert atom attributes into the Atoms table
        query = "INSERT INTO Atoms (ELEMENT_CODE, X, Y, Z) VALUES (?, ?, ?, ?)"
        values = (atom.element, atom.x, atom.y, atom.z)
        self.cursor.execute(query, values)
        atom_id = self.cursor.lastrowid

        # Create entry in the MoleculeAtom table linking the atom to the specified molecule
        query = "INSERT INTO MoleculeAtom (MOLECULE_ID, ATOM_ID) VALUES (?, ?)"
        values = (molecule_id, atom_id)
        self.cursor.execute(query, values)

        # Commit changes to the database
        self.conn.commit()

    def add_bond(self, molname, bond):
        # Get molecule ID from Molecules table
        query = "SELECT MOLECULE_ID FROM Molecules WHERE NAME = ?"
        values = (molname,)
        self.cursor.execute(query, values)
        result = self.cursor.fetchone()
        if not result:
            raise ValueError("No such molecule in database")
        molecule_id = result[0]

        # Insert bond attributes into the Bonds table
        query = "INSERT INTO Bonds (A1, A2, EPAIRS) VALUES (?, ?, ?)"
        values = (bond.a1, bond.a2, bond.epairs)
        self.cursor.execute(query, values)
        bond_id = self.cursor.lastrowid

        # Create entry in the MoleculeBond table linking the bond to the specified molecule
        query = "INSERT INTO MoleculeBond (MOLECULE_ID, BOND_ID) VALUES (?, ?)"
        values = (molecule_id, bond_id)
        self.cursor.execute(query, values)

        # Commit changes to the database
        self.conn.commit()

    def add_molecule(self, name, fp):
        # Create a Molecule object and parse its contents from fp
        molecule = Molecule()
        molecule.parse(fp)

        # Add an entry to the Molecules table
        query = "INSERT INTO Molecules (NAME) VALUES (?)"
        values = (name,)
        self.cursor.execute(query, values)
        molecule_id = self.cursor.lastrowid

        # Add each atom in the molecule to the Atoms table and the MoleculeAtom table
        for i in range(molecule.atom_no):
            atom = molecule.get_atom(i)
            self.add_atom(name, atom)

        # Add each bond in the molecule to the Bonds table and the MoleculeBond table
        for j in range(molecule.bond_no):
            bond = molecule.get_bond(j)
            self.add_bond(name, bond)

        # Commit changes to the database
        self.conn.commit()
        
        return molecule

    def load_mol(self, name):
        # Create a new Molecule object
        mol = Molecule()

        # Query the database to get all the atoms associated with the named molecule, in increasing order of ATOM_ID
        query = '''
            SELECT a.ATOM_ID, a.ELEMENT_CODE, a.X, a.Y, a.Z 
            FROM Molecules m 
            JOIN MoleculeAtom ma ON m.MOLECULE_ID = ma.MOLECULE_ID 
            JOIN Atoms a ON ma.ATOM_ID = a.ATOM_ID 
            WHERE m.NAME = ? 
            ORDER BY a.ATOM_ID ASC
        '''
        atoms = self.conn.execute(query, (name,)).fetchall()

        # Add each atom to the Molecule object
        for atom in atoms:
            mol.append_atom(atom[1], atom[2], atom[3], atom[4])

        # Query the database to get all the bonds associated with the named molecule, in increasing order of BOND_ID
        query = '''
            SELECT b.BOND_ID, b.A1, b.A2, b.EPAIRS 
            FROM Molecules m 
            JOIN MoleculeBond mb ON m.MOLECULE_ID = mb.MOLECULE_ID 
            JOIN Bonds b ON mb.BOND_ID = b.BOND_ID 
            WHERE m.NAME = ? 
            ORDER BY b.BOND_ID ASC
        '''
        bonds = self.conn.execute(query, (name,)).fetchall()

        # Add each bond to the Molecule object
        for bond in bonds:
            mol.append_bond(bond[1], bond[2], bond[3])

        # Return the Molecule object
        return mol
    
    def radius(self):
        # Connect to the database using the `conn` object stored in `self`
        c = self.conn.cursor()
        
        # Execute a SQL query to select `ELEMENT_CODE` and `RADIUS` from the `Elements` table
        c.execute("SELECT ELEMENT_CODE, RADIUS FROM Elements")

        rows = c.fetchall()

        radius_dict = {}

        for row in rows:
            # Get the `element_code` and `radius` values from the row
            element_code = row[0]
            radius = row[1]

            # Add the `element_code` and `radius` values to the dictionary
            radius_dict[element_code] = radius

        return radius_dict

    def element_name(self):
        # Connect to the database using the `conn` object stored in `self`
        c = self.conn.cursor()

        # Execute a SQL query to select `ELEMENT_CODE` and `ELEMENT_NAME` from the `Elements` table
        c.execute("SELECT ELEMENT_CODE, ELEMENT_NAME FROM Elements")

        rows = c.fetchall()

        element_name_dict = {}
        for row in rows:
            # Get the `element_code` and `element_name` values from the row
            element_code = row[0]
            element_name = row[1]
            element_name_dict[element_code] = element_name

        return element_name_dict

    def radial_gradients(self):
        # Connect to the database using the `conn` object stored in `self`
        c = self.conn.cursor()

         # Execute a SQL query to select `ELEMENT_NAME`, `COLOUR1`, `COLOUR2`, and `COLOUR3` from the `Elements` table
        c.execute("SELECT ELEMENT_NAME, COLOUR1, COLOUR2, COLOUR3 FROM Elements")

        rows = c.fetchall()

        radial_gradients_svg = ""

        for row in rows:
            # Get the `ELEMENT_NAME`, `COLOUR1`, `COLOUR2`, and `COLOUR3` values from the row
            element_name = row[0]
            colour1 = row[1]
            colour2 = row[2]
            colour3 = row[3]
            radial_gradient_svg = """
            <radialGradient id="%s" cx="-50%%" cy="-50%%" r="220%%" fx="20%%" fy="20%%">
            <stop offset="0%%" stop-color="#%s"/>
            <stop offset="50%%" stop-color="#%s"/>
            <stop offset="100%%" stop-color="#%s"/>
            </radialGradient>""" % (element_name, colour1, colour2, colour3)
            
            # Append the SVG gradient definition string to the `radial_gradients_svg` string
            radial_gradients_svg += radial_gradient_svg

        return radial_gradients_svg
