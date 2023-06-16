from http.server import HTTPServer, BaseHTTPRequestHandler;

# Name: Prabhjot Sidhu
# Student Number: 1178871
# Assignmnet 4

import sys;     # to get command line argument for port
import urllib;  # code to parse for data
import sqlite3
from io import BytesIO
import io
import molecule;
from molsql import Database;
import MolDisplay;

#INITIALIZE DATABASE. REMEMBER TO CHANGE REST TO FALSE (Maybe)
db = Database(reset=True);
db.create_tables();
MolDisplay.radius = db.radius();
MolDisplay.element_name = db.element_name();
MolDisplay.header += db.radial_gradients();

# list of files that we allow the web-server to serve to clients
# (we don't want to serve any file that the client requests)
public_files = [ '/index.html', '/upload.html', '/display.html', '/style.css', '/script.js', '/displayScript.js' ];
molecule_name = "nothing"

class MyHandler( BaseHTTPRequestHandler ):
    def do_GET(self):

        print("GET PATH IS: " + self.path + "\n")

        if self.path == "/molecule_list.html":
            molecule_name_data = db.conn.execute( "SELECT * FROM Molecules;" ).fetchall()

            # Iterate over the array and extract the second element from each tuple
            molecule_name_list = [tup[1] for tup in molecule_name_data]

            # create and send headers
            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            # join the list elements with a separator
            response = "\n".join(molecule_name_list)

            # send the contents
            self.wfile.write(bytes(response, "utf-8"))
        # used to GET a file from the list ov public_files, above
        elif self.path in public_files:   # make sure it's a valid file
            self.send_response( 200 );  # OK
            self.send_header( "Content-type", "text/html" );

            fp = open( self.path[1:] ); 
            # [1:] to remove leading / so that file is found in current dir

            # load the specified file
            page = fp.read();
            fp.close();

            # create and send headers
            self.send_header( "Content-length", len(page) );
            self.end_headers();

            # send the contents
            self.wfile.write( bytes( page, "utf-8" ) );

        else:
            # if the requested URL is not one of the public_files
            self.send_response( 404 );
            self.end_headers();
            self.wfile.write( bytes( "404: not found", "utf-8" ) );



    def do_POST(self):
        global molecule_name

        print("POST PATH IS: " + self.path + "\n")

        if self.path == "/sdf_upload.html":
            # code to handle sdf_upload

            content_length = int(self.headers['Content-Length'])

            try:
                content_length = int(self.headers['Content-Length'])
                text = self.rfile.read(content_length).decode('utf-8')
                fileObj = io.StringIO(text)

                # Rest of the code here, such as reading and processing lines

            except Exception as e:
                self.send_error(400, "Bad Request: Incorrect value")

            print(fileObj)

            for i in range(8):    # skip 4 lines
                string = next(fileObj);
                print(str(string))

            #get number of atoms and bonds indicated by file
            lst = string.split()
            a = int(lst[0])
            b = int(lst[1])

            temp_molecule = MolDisplay.Molecule()
            
            #check if molecule file is parsable
            try:
                temp_molecule.parse(fileObj)
            except Exception as e:
                self.send_error(400, "Bad Request: Incorrect value")

            #check if correct number of bonds and atoms were found
            if(temp_molecule.atom_no != a or temp_molecule.bond_no != b):
                self.send_error(400, "Bad Request: Incorrect value")
            else:
                fileObj.seek(0)
                #ANY FILE COMING WILL BE CAFFEINE FOR NOW
                db.add_molecule( molecule_name, fileObj)

            #send success response
            message = "sdf file uploaded to database";
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/plain" );
            self.send_header( "Content-length", len(message) );
            self.end_headers();

            self.wfile.write( bytes( message, "utf-8" ) );

        elif self.path == "/add_element_name.html":
            # this is specific to 'multipart/form-data' encoding used by POST
            content_length = int(self.headers['Content-Length']);
            body = self.rfile.read(content_length);

            print( repr( body.decode('utf-8') ) );

            # convert POST content into a dictionary
            postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) );

            received_mol_name = postvars['name'][0]

            molecule_name = received_mol_name

            #send success response
            message = "Data received"
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-length", len(message))
            self.end_headers()
            self.wfile.write(bytes(message, "utf-8"))

        elif self.path == "/submit_handler.html":

            # this is specific to 'multipart/form-data' encoding used by POST
            content_length = int(self.headers['Content-Length']);
            body = self.rfile.read(content_length);

            print( repr( body.decode('utf-8') ) );

            # convert POST content into a dictionary
            postvars = urllib.parse.parse_qs( body.decode( 'utf-8' ) );

            #send success response
            message = "data received";
            self.send_response( 200 ); # OK
            self.send_header( "Content-type", "text/plain" );
            self.send_header( "Content-length", len(message) );
            self.end_headers();

            self.wfile.write( bytes( message, "utf-8" ) );

        elif self.path == "/add_element_handler.html":
            # this is specific to 'multipart/form-data' encoding used by POST
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            # convert POST content into a dictionary
            data_dict = urllib.parse.parse_qs(body.decode('utf-8'))

            element_number = data_dict['element-number'][0]
            element_code = data_dict['element-code'][0]
            element_name = data_dict['element-name'][0]
            color1 = data_dict['color1'][0]
            color2 = data_dict['color2'][0]
            color3 = data_dict['color3'][0]
            radius = data_dict['radius'][0]

            #store element data in database
            db['Elements'] = ( int(element_number), str(element_code), str(element_name), str(color1[1:]), str(color2[1:]), str(color3[1:]), int(radius) );

            #update molecule generation disctionaries
            MolDisplay.radius = db.radius();
            MolDisplay.element_name = db.element_name();
            MolDisplay.header += db.radial_gradients();

            #send success response
            message = "Data received"
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-length", len(message))
            self.end_headers()
            self.wfile.write(bytes(message, "utf-8"))

        elif self.path == "/molecule_data.html":
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            # convert POST content into a dictionary
            data_dict = urllib.parse.parse_qs(body.decode('utf-8'))

            element_to_load = data_dict['data'][0]

            #find molecule
            mol = db.load_mol(element_to_load)

            #send back molecule data as response
            response = mol.molecule_data()
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-length", len(response))
            self.end_headers()
            self.wfile.write(bytes(response, "utf-8"))

        elif self.path == "/molecule_svg.html":
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            # convert POST content into a dictionary
            data_dict = urllib.parse.parse_qs(body.decode('utf-8'))

            element_to_load = data_dict['data'][0]
            mol = db.load_mol(element_to_load)
            mol.sort()

            #create svg and send it back as response
            response = mol.svg()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-length", len(response))
            self.end_headers()
            self.wfile.write(bytes(response, "utf-8"))

        elif self.path == "/molecule_rotate.html":
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            # convert POST content into a dictionary
            data_dict = urllib.parse.parse_qs(body.decode('utf-8'))

            x = data_dict['x'][0]
            y = data_dict['y'][0]
            z = data_dict['z'][0]
            name = data_dict['name'][0]

            if x == 0 and y == 0 and z == 0:
                self.send_error(400, "Bad Request: Incorrect value")

            #calcualte and apply rotation to molecule
            mol = db.load_mol(name)
            mol.sort()
            mx = molecule.mx_wrapper(int(x), int(y), int(z))
            mol.xform( mx.xform_matrix )

            #send rotated svg as response
            response = mol.svg()
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.send_header("Content-length", len(response))
            self.end_headers()
            self.wfile.write(bytes(response, "utf-8"))
        
        elif self.path == "/element_delete_handler.html":


            # this is specific to 'multipart/form-data' encoding used by POST
            content_length = int(self.headers['Content-Length'])
            body = self.rfile.read(content_length)

            # convert POST content into a dictionary
            data_dict = urllib.parse.parse_qs(body.decode('utf-8'))

            element_name = data_dict['element_name'][0]

            if element_name == "":
                # send bad request error response
                self.send_error(400, "Bad Request: Incorrect value")

            result = db.remove_element(element_name);

            #update dictionaries for molecule generation
            MolDisplay.radius = db.radius();
            MolDisplay.element_name = db.element_name();
            MolDisplay.header += db.radial_gradients();

            #create response message and send it
            message = "Element: " + element_name + " Was Deleted"
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.send_header("Content-length", len(message))
            self.end_headers()
            self.wfile.write(bytes(message, "utf-8"))


        else:
            self.send_response( 404 );
            self.end_headers();
            self.wfile.write( bytes( "404: not found", "utf-8" ) );




httpd = HTTPServer( ( 'localhost', int(sys.argv[1]) ), MyHandler );
httpd.serve_forever();