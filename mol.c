#include "mol.h"

/**
 * CIS 2750
 * Assignment 1
 * Prabhjot Sidhu
 * Student Number: 1178871
 */

//set atom structure values to the paramater values
void atomset( atom *atom, char element[3], double *x, double *y, double *z ) {
    //element symbol is copied
    strncpy(atom->element, element, 3);

    //3d space coordinates are copied
    atom->x = *x;
    atom->y = *y;
    atom->z = *z;
}

//values from a structure are copied into the passed paramaters
void atomget( atom *atom, char element[3], double *x, double *y, double *z ) {
    //set element symbol
    strncpy(element, atom->element, 3);

    //3d space coordinates are copied
    *x = atom->x;
    *y = atom->y;
    *z = atom->z;
}

//set bond structure values
void bondset( bond *bond, unsigned short *a1, unsigned short *a2, atom **atoms, unsigned char *epairs ) {
    //set epairs
    bond->epairs = *epairs;

    //set atoms in bond
    bond->atoms[0] = *(atoms[*a1]);
    bond->atoms[1] = *(atoms[*a2]);

    //will calculate and store this bond's coordinates
    compute_coords(bond);
}

//get the bond structure values
void bondget( bond *bond, unsigned short *a1, unsigned short *a2, atom
**atoms, unsigned char *epairs ) {
    //get epairs
    *epairs = bond->epairs;

    //get atoms in bond
    *(atoms[*a1]) = bond->atoms[0];
    *(atoms[*a2]) = bond->atoms[1];
}

//comput the length of the bond
void compute_coords(bond *bond) {
    // Calculate average z value
    bond->z = (bond->atoms[bond->a1].z + bond->atoms[bond->a2].z) / 2;

    // Calculate x and y coordinates of atoms
    bond->x1 = bond->atoms[bond->a1].x;
    bond->y1 = bond->atoms[bond->a1].y;
    bond->x2 = bond->atoms[bond->a2].x;
    bond->y2 = bond->atoms[bond->a2].y;

    // Calculate bond length
    bond->len = sqrt(pow(bond->x2 - bond->x1, 2) + pow(bond->y2 - bond->y1, 2));

    // Calculate dx and dy
    bond->dx = (bond->x2 - bond->x1) / bond->len;
    bond->dy = (bond->y2 - bond->y1) / bond->len;
}


//allocates memory for a new molecule, and initializes array tracking variables
molecule *molmalloc( unsigned short atom_max, unsigned short bond_max ) {
    //create new molecule
    molecule * newMolecule = (molecule*)malloc(sizeof(molecule));

    //set values in newMolecule
    newMolecule->atom_max = atom_max;
    newMolecule->atom_no = 0;
    newMolecule->bond_max = bond_max;
    newMolecule->bond_no = 0;

    //create space for arrays
    newMolecule->atoms = (atom*)malloc(sizeof(atom) * atom_max);
    newMolecule->atom_ptrs = (atom**)malloc(sizeof(atom*) * atom_max);
    newMolecule->bonds = (bond*)malloc(sizeof(bond) * bond_max);
    newMolecule->bond_ptrs = (bond**)malloc(sizeof(bond*) * bond_max);

    //return new created molecule
    return newMolecule;
}

//create a copy of the molecule
molecule *molcopy( molecule *src ) {
    //allocate space for copy of molecle
    molecule * dest = molmalloc(src->atom_max, src->bond_max);

    //append the atoms from the atoms array to the copy of molecule
    for (int i = 0; i < src->atom_no; i++) {
        molappend_atom(dest, &src->atoms[i]);
    }

    //append bonds form the bonds array to the copy of molecule
    for (int i = 0; i < src->bond_no; i++) {
        molappend_bond(dest, &src->bonds[i]);
    }

    //return the copy of molecule
    return dest;
}

//free the memory associate with a molecule
void molfree( molecule *ptr ) {
    //free struct variables first
    free(ptr->atoms);
    free(ptr->atom_ptrs);
    free(ptr->bonds);
    free(ptr->bond_ptrs);
    //free entire struct after
    free(ptr);
}

//add an atom to the atoms list in the molecule
void molappend_atom( molecule *molecule, atom *atom ) {

    //check if number of atoms is too large for the atoms array
    if (molecule->atom_no >= molecule->atom_max) {
        //if max number of atoms is still zero, then make it 1, otherwise, double it
        if (molecule->atom_max == 0) {
            molecule->atom_max = 1;
        } else {
            molecule->atom_max *= 2;
        }

        //to hold atoms temporarily
        struct atom* tempAtoms = (struct atom*) malloc(sizeof(struct atom) * molecule->atom_max);

        //copy the atoms from the current molecule atoms array into tempAtoms
        memcpy(tempAtoms, molecule->atoms, sizeof(struct atom) * molecule->atom_no);

        //free the old atoms array in molecule
        free(molecule->atoms);

        //make the new atoms array the tempAtoms array
        molecule->atoms = tempAtoms;
        
        //to hold atom pointers temporarily
        struct atom** tempAtomPtrs = (struct atom**) malloc(sizeof(struct atom*) * molecule->atom_max);

        //copy all pointers for atoms into temporary poitners array
        for (int i=0; i < molecule->atom_no; i++) {
            tempAtomPtrs[i] = &tempAtoms[i];
        }

        //free original atom pointers array in molecule
        free(molecule->atom_ptrs);

        //assign atom pointers array in molecule to temporary pointers
        molecule->atom_ptrs = tempAtomPtrs;
    }

    //store last atom and atom pointer, and increment atom numbers
    molecule->atoms[molecule->atom_no] = *atom;
    molecule->atom_ptrs[molecule->atom_no] = &molecule->atoms[molecule->atom_no];
    molecule->atom_no++;
}

//add a bond to the bond list in the molecule
void molappend_bond( molecule *molecule, bond *bond ) {
    //check if number of bonds is too large for the bonds array
    if (molecule->bond_no >= molecule->bond_max) {
        //if max number of bonds is still zero, then make it 1, otherwise, double it
        if (molecule->bond_max == 0) {
            molecule->bond_max = 1;
        } else {
            molecule->bond_max *= 2;
        }

        //to hold bonds temporarily
        struct bond* tempBonds = malloc(sizeof(struct bond) * molecule->bond_max);
        
        //copy the bonds from the current molecule bonds array into tempBonds
        memcpy(tempBonds, molecule->bonds, sizeof(struct bond) * molecule->bond_no);

        //free current bonds array in molecule
        free(molecule->bonds);

        //assign molecule bonds array the value of tempBonds array
        molecule->bonds = tempBonds;

        //to hold atom pointers temporarily
        struct bond** tempBondPtrs = malloc(sizeof(struct bond*) * molecule->bond_max);
        
        //copy all pointers for bonds into temporary pointers array
        for (int i = 0; i < molecule->bond_no; i++) {
            tempBondPtrs[i] = &(molecule->bonds[i]);
        }

        //free original bond pointers array in molecule
        free(molecule->bond_ptrs);

        //assign temporary bond pointers array to molecule
        molecule->bond_ptrs = tempBondPtrs;
    }

    //add last bond pointer and bond and increment bond number
    molecule->bonds[molecule->bond_no] = *bond;
    molecule->bond_ptrs[molecule->bond_no] = &molecule->bonds[molecule->bond_no];
    molecule->bond_no++;
}

//for sorting the molecules
void molsort( molecule *molecule ) {

    //user qsort method to apply quick sort algorithm
    qsort(molecule->atom_ptrs, molecule->atom_no, sizeof(atom**), compareAtoms);
    qsort(molecule->bond_ptrs, molecule->bond_no, sizeof(bond**), compareBonds);

}

//helper function used to compare two values at a time in quicksort algorithm
int compareAtoms(const void* a, const void* b) {
    atom *x = *((atom**)a);
    atom *y = *((atom**)b);
    if ((x)->z < (y)->z) {
        return -1;
    } else if ((x)->z > (y)->z) {
        return 1;
    } else {
        return 0;
    }
}

//helper function used to compare two values at a time in quicksort algorithm
int compareBonds(const void* a, const void* b) {
    bond *aa = (bond*)a;
    bond *bb = (bond*)b;

    // Find average z values and compare
    double z1 = (aa->z);
    double z2 = (bb->z);

    if (z1 < z2) {
        return -1;
    } else if (z1 > z2) {
        return 1;
    } else {
        return 0;
    }
}


//rotate the molecule across the x-axis
void xrotation( xform_matrix xform_matrix, unsigned short deg ) {
    //convert degrees to radians
    double rad = convertDegToRad(deg);

    //calculate the cosine and sine values
    double cosValue = cos(rad);
    double sinValue = sin(rad);

    //change the corresponding values in the xform matrix
    xform_matrix[0][0] = 1;
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = 0;

    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = cosValue;
    xform_matrix[1][2] = -sinValue;

    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = sinValue;
    xform_matrix[2][2] = cosValue;

}

//rotate the molecule across the x-axis
void yrotation( xform_matrix xform_matrix, unsigned short deg ) {
    //convert degrees to radians
    double rad = convertDegToRad(deg);

    //calculate the cosine and sine values
    double cosValue = cos(rad);
    double sinValue = sin(rad);

    //change the corresponding values in the xform matrix
    xform_matrix[0][0] = cosValue;
    xform_matrix[0][1] = 0;
    xform_matrix[0][2] = sinValue;

    xform_matrix[1][0] = 0;
    xform_matrix[1][1] = 1;
    xform_matrix[1][2] = 0;

    xform_matrix[2][0] = -sinValue;
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = cosValue;

}

//rotate the molecule across the x-axis
void zrotation( xform_matrix xform_matrix, unsigned short deg ) {
    //convert degrees to radians
    double rad = convertDegToRad(deg);

    //calculate the cosine and sine values
    double cosValue = cos(rad);
    double sinValue = sin(rad);

    //change the corresponding values in the xform matrix
    xform_matrix[0][0] = cosValue;
    xform_matrix[0][1] = -sinValue;
    xform_matrix[0][2] = 0;

    xform_matrix[1][0] = sinValue;
    xform_matrix[1][1] = cosValue;
    xform_matrix[1][2] = 0;

    xform_matrix[2][0] = 0;
    xform_matrix[2][1] = 0;
    xform_matrix[2][2] = 1;

}

//helper function to convert degrees to radians
double convertDegToRad(unsigned short deg) {
    //convert degrees to radians
    double rad = deg * acos(-1) / 180.0;

    return rad;
}

//applies the matrix transformation to the atoms in a molecule
void mol_xform(molecule *molecule, xform_matrix matrix) {
    // Apply transformation matrix to each atom in the molecule
    for (int i = 0; i < molecule->atom_no; i++) {
        double x, y, z;
        char element[3];
        atomget(molecule->atom_ptrs[i], element, &x, &y, &z);

        double newX = x * matrix[0][0] + y * matrix[0][1] + z * matrix[0][2];
        double newY = x * matrix[1][0] + y * matrix[1][1] + z * matrix[1][2];
        double newZ = x * matrix[2][0] + y * matrix[2][1] + z * matrix[2][2];

        atomset(molecule->atom_ptrs[i], element, &newX, &newY, &newZ);
    }

    // Apply compute_coords function to each bond in the molecule
    for (int i = 0; i < molecule->bond_no; i++) {
        compute_coords(&molecule->bonds[i]);
    }
}

rotations *spin( molecule *mol )
{
  int i;

  // Allocate memory for rotations struct
  rotations *r = malloc( sizeof( rotations ) );

  // Initialize all pointers to NULL
  for ( i = 0; i < 72; i++ )
  {
    r->x[i] = NULL;
    r->y[i] = NULL;
    r->z[i] = NULL;
  }

  // Generate 72 rotated versions of the molecule, 5 degrees apart
  for ( i = 0; i < 72; i++ )
  {
    xform_matrix matrix;
    xrotation( matrix, i * 5 );
    molecule *copy = molcopy( mol );
    mol_xform( copy, matrix );
    r->x[i] = copy;

    yrotation( matrix, i * 5 );
    copy = molcopy( mol );
    mol_xform( copy, matrix );
    r->y[i] = copy;

    zrotation( matrix, i * 5 );
    copy = molcopy( mol );
    mol_xform( copy, matrix );
    r->z[i] = copy;
  }

  return r;
}

void rotationsfree( rotations *rotations )
{
  int i;

  // Free all rotated molecules
  for ( i = 0; i < 72; i++ )
  {
    if ( rotations->x[i] )
    {
      molfree( rotations->x[i] );
    }
    if ( rotations->y[i] )
    {
      molfree( rotations->y[i] );
    }
    if ( rotations->z[i] )
    {
      molfree( rotations->z[i] );
    }
  }

  // Free the rotations struct itself
  free( rotations );
}




