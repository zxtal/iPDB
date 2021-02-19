import sqlite3
import requests
import xml.etree.ElementTree as ET


class CreatePDBfile:
    """
    Represent a PDB file to be stored, and retrieve and save user-supplied relevant data.
    """
    def __init__(self, pdb_name, protein_name, species, hi_resolution, Rwork, Rfree, space_group, sequence):
        self.pdb_name = pdb_name
        self.protein_name = protein_name
        self.species = species
        self.hi_resolution = hi_resolution
        self.Rwork = Rwork
        self.Rfree = Rfree
        self.space_group = space_group
        self.sequence = sequence


class PdbDbInteraction:
    """
    Encapsulating database-facing methods that save, retrieve, update,
    search, and delete PDB files from/to the database.
    """

    con = sqlite3.connect("mydatabase.db")

    def __init__(self):
        self.cursor_obj = PdbDbInteraction.con.cursor()

    def save(self, pdb):
        entities = (pdb.pdb_name, pdb.protein_name, pdb.species, pdb.hi_resolution, pdb.Rwork,
                    pdb.Rfree, pdb.space_group, pdb.sequence)
        self.cursor_obj.execute("INSERT INTO PDBs (pdb_name, protein_name, species, hi_resolution, "
                           "Rwork, Rfree, space_group, sequence) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", entities)
        PdbDbInteraction.con.commit()

    def retrieve_pdb(self, pdb_id=None):
        if pdb_id is not None:
            queryset = self.cursor_obj.execute(f"SELECT * FROM PDBs WHERE id=?", (pdb_id,)).fetchall()
        else:
            queryset = self.cursor_obj.execute("SELECT * FROM PDBs").fetchall()
        return queryset

    def update_pdb(self, pdb, pdb_id):
        entities = (pdb.pdb_name, pdb.protein_name, pdb.species, pdb.hi_resolution, pdb.Rwork, pdb.Rfree,
                    pdb.space_group, pdb.sequence, pdb_id)
        self.cursor_obj.execute("UPDATE PDBs SET pdb_name=?, protein_name=?, species=?, hi_resolution=?, Rwork=?, "
                           "Rfree=?, space_group=?, sequence=? WHERE id=?", entities)
        PdbDbInteraction.con.commit()

    def delete_pdb(self, pdb_id):
        self.cursor_obj.execute("DELETE FROM PDBs WHERE id=?", (pdb_id,))
        PdbDbInteraction.con.commit()

    def search_pdb(self, keywords):
        queryset = []
        search_word_list = keywords.split(' ')
        for word in search_word_list:
            results = self.cursor_obj.execute("SELECT * FROM PDBs WHERE pdb_name like ? OR protein_name LIKE ? OR "
                                        "species LIKE ? OR space_group LIKE ? OR sequence LIKE ?",
                                        ('%' +word+'%', '%' +word+'%', '%' +word+'%', '%' +word+'%', '%' +word+'%'))
            [queryset.append(result) for result in results if result not in queryset]

        return queryset


class CreateTable:
    """
    Constructing database tables. This should only be run at the beginning of a project.
    """

    @staticmethod
    def Connect_DB():
        con = sqlite3.connect("mydatabase.db")
        return con

    def create_table(self):
        cursor_obj = CreateTable.Connect_DB().cursor()

        cursor_obj.execute("CREATE TABLE PDBs(id INTEGER PRIMARY KEY,pdb_name text, protein_name text, species text, hi_resolution float, Rwork float, Rfree float, space_group text, sequence text)")
        CreateTable.Connect_DB().commit()


class QueryPDBWebSite:
    """
    Retrieving the specified PDB file from the PDB Repository.
    """
    def retrieve_pdb_info(self, pdb_id):
        print("Running retrieve_pdb_info method")
        url = f'http://www.rcsb.org/pdb/rest/customReport.xml?pdbids={pdb_id}.A&customReportColumns=structureId,structureTitle,source,highResolutionLimit,rWork,rFree,spaceGroup,sequence'
        query_xml = requests.get(url=url)

        result = []
        root = ET.fromstring(query_xml.text)
        print(root)

        for i in root[0]:
            print(i)
            result.append(i.text)
        return result