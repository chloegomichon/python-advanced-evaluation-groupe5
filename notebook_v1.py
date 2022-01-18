#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
an object-oriented version of the notebook toolbox
"""
from json import load
from notebook_v0 import *

# définition de deux fonctions perso dont je me sers plus tard

def clean_cells(ipynb):
    '''enlève metadata et outputs, renvoie liste des cells'''
    cells = get_cells(ipynb)
    C = []
    for cell in cells:
        clean = dict()
        for key in cell.keys():
            if key != 'metadata' and key!='outputs':
                clean[key]=cell[key]
        C.append(clean)
    return(C)

def cells_conv(ipynb):
    '''convertit avec les classes crées'''
    C = []
    for cell in clean_cells(ipynb):
        if cell['cell_type'] == 'markdown':
            C.append(MarkdownCell(cell))
        if cell['cell_type'] == 'code':
            C.append(CodeCell(cell))
    return(C)




class CodeCell:
    r"""A Cell of Python code in a Jupyter notebook.

    Args:
        ipynb (dict): a dictionary representing the cell in a Jupyter Notebook.

    Attributes:
        id (int): the cell's id.
        source (list): the cell's source code, as a list of str.
        execution_count (int): number of times the cell has been executed.

    Usage:

        >>> code_cell = CodeCell({
        ...     "cell_type": "code",
        ...     "execution_count": 1,
        ...     "id": "b777420a",
        ...     'source': ['print("Hello world!")']
        ... })
        >>> code_cell.id
        'b777420a'
        >>> code_cell.execution_count
        1
        >>> code_cell.source
        ['print("Hello world!")']
    """

    def __init__(self, ipynb):
        self.id = ipynb["id"]
        self.source = ipynb['source']
        self.execution_count = ipynb["execution_count"]


class MarkdownCell:
    r"""A Cell of Markdown markup in a Jupyter notebook.

    Args:
        ipynb (dict): a dictionary representing the cell in a Jupyter Notebook.

    Attributes:
        id (int): the cell's id.
        source (list): the cell's source code, as a list of str.

    Usage:

        >>> markdown_cell = MarkdownCell({
        ...    "cell_type": "markdown",
        ...    "id": "a9541506",
        ...    "source": [
        ...        "Hello world!\n",
        ...        "============\n",
        ...        "Print `Hello world!`:"
        ...    ]
        ... })
        >>> markdown_cell.id
        'a9541506'
        >>> markdown_cell.source
        ['Hello world!\n', '============\n', 'Print `Hello world!`:']
    """

    def __init__(self, ipynb):
        self.id = ipynb["id"]
        self.source = ipynb["source"]


class Notebook:
    r"""A Jupyter Notebook.

    Args:
        ipynb (dict): a dictionary representing a Jupyter Notebook.

    Attributes:
        version (str): the version of the notebook format.
        cells (list): a list of cells (either CodeCell or MarkdownCell).

    Usage:

        - checking the verion number:

            >>> ipynb = toolbox.load_ipynb("samples/minimal.ipynb")
            >>> nb = Notebook(ipynb)
            >>> nb.version
            '4.5'

        - checking the type of the notebook parts:

            >>> ipynb = toolbox.load_ipynb("samples/hello-world.ipynb")
            >>> nb = Notebook(ipynb)
            >>> isinstance(nb.cells, list)
            True
            >>> isinstance(nb.cells[0], Cell)
            True
    """

    def __init__(self, ipynb):
        self.version = get_format_version(ipynb)
        self.cells = cells_conv(ipynb)

    @staticmethod
    def from_file(filename):
        r"""Loads a notebook from an .ipynb file.

        Usage:

            >>> nb = Notebook.from_file("samples/minimal.ipynb")
            >>> nb.version
            '4.5'
        """
        return(Notebook(load_ipynb(filename)))

    def __iter__(self):
        r"""Iterate the cells of the notebook.

        Usage:

            >>> nb = Notebook.from_file("samples/hello-world.ipynb")
            >>> for cell in nb:
            ...     print(cell.id)
            a9541506
            b777420a
            a23ab5ac
        """
        return iter(self.cells) # bien défini car self.cells est une liste, elle devient ici un itérateur 

class PyPercentSerializer:
    r"""Prints a given Notebook in py-percent format.

    Args:
        notebook (Notebook): the notebook to print.

    Usage:
            >>> nb = Notebook.from_file("samples/hello-world.ipynb")
            >>> ppp = PyPercentSerializer(nb)
            >>> print(ppp.to_py_percent()) # doctest: +NORMALIZE_WHITESPACE
            # %% [markdown]
            # Hello world!
            # ============
            # Print `Hello world!`:
            <BLANKLINE>
            # %%
            print("Hello world!")
            <BLANKLINE>
            # %% [markdown]
            # Goodbye! 👋
    """
    def __init__(self, notebook):
        self.notebook = notebook

    def to_py_percent(self):
        r"""Converts the notebook to a string in py-percent format.
        """
        nb0 = self.notebook
        nb = dict() # dictionnaire qui contiendra le futur notebook
        nb['cells'] = [] # liste qui contiendra les cellules

        for cell in nb0.cells:
            cell_new = dict() # dictionnaire qui contiendra les cellules
            if type(cell) == MarkdownCell: # on reconstruit la cellule pas à pas
                cell_new["cell_type"] = 'markdown'
                cell_new["id"] = cell.id
                cell_new['metadata'] = {}
                cell_new["source"] = cell.source

            else: # idem, mais avec les clés propres aux cellules de code
                cell_new['cell_type'] = 'code'
                cell_new["execution_count"] = cell.execution_count
                cell_new["id"] = cell.id
                cell_new['metadata'] = {}
                cell_new['outputs'] = []
                cell_new["source"] = cell.source
            nb['cells'].append(cell_new) # on ajoute la cellule construire à la liste de cellules

        nb['metadata'] = {}
        v = nb0.version
        v.split('.') # séparation des deux indicateurs de version
        nb['nbformat'] = int(v[0])
        nb['nbformat_minor'] = int(v[-1])
        
        
        return(to_percent(nb))

    def to_file(self, filename):
        r"""Serializes the notebook to a file

        Args:
            filename (str): the name of the file to write to.

        Usage:

                >>> nb = Notebook.from_file("samples/hello-world.ipynb")
                >>> s = PyPercentSerializer(nb)
                >>> s.to_file("samples/hello-world-serialized-py-percent.py")
        """
        ipynb = self.to_py_percent()
        save_ipynb(ipynb, filename)
        
class Serializer:
    r"""Serializes a Jupyter Notebook to a file.

    Args:
        notebook (Notebook): the notebook to print.

    Usage:

        >>> nb = Notebook.from_file("samples/hello-world.ipynb")
        >>> s = Serializer(nb)
        >>> pprint.pprint(s.serialize())  # doctest: +NORMALIZE_WHITESPACE
            {'cells': [{'cell_type': 'markdown',
                'id': 'a9541506',
                'medatada': {},
                'source': ['Hello world!\n',
                           '============\n',
                           'Print `Hello world!`:']},
               {'cell_type': 'code',
                'execution_count': 1,
                'id': 'b777420a',
                'medatada': {},
                'outputs': [],
                'source': ['print("Hello world!")']},
               {'cell_type': 'markdown',
                'id': 'a23ab5ac',
                'medatada': {},
                'source': ['Goodbye! 👋']}],
            'metadata': {},
            'nbformat': 4,
            'nbformat_minor': 5}
        >>> s.to_file("samples/hello-world-serialized.ipynb")
    """

    def __init__(self, notebook):
        self.notebook = notebook

    def serialize(self):
        r"""Serializes the notebook to a JSON object

        Returns:
            dict: a dictionary representing the notebook.
        """
        nb0 = self.notebook
        nb = dict()
        nb['cells'] = []

        for cell in nb0.cells:
            cell_new = dict()
            if type(cell) == MarkdownCell:
                cell_new["cell_type"] = 'markdown'
                cell_new["id"] = cell.id
                cell_new['metadata'] = {}
                cell_new["source"] = cell.source
            else:
                cell_new['cell_type'] = 'code'
                cell_new["execution_count"] = cell.execution_count
                cell_new["id"] = cell.id
                cell_new['metadata'] = {}
                cell_new['outputs'] = []
                cell_new["source"] = cell.source
            nb['cells'].append(cell_new)

        nb['metadata'] = {}
        v = nb0.version
        v.split('.')
        nb['nbformat'] = int(v[0])
        nb['nbformat_minor'] = int(v[-1])
        

        return(nb)

    def to_file(self, filename):
        r"""Serializes the notebook to a file

        Args:
            filename (str): the name of the file to write to.

        Usage:

                >>> nb = Notebook.from_file("samples/hello-world.ipynb")
                >>> s = Serializer(nb)
                >>> s.to_file("samples/hello-world-serialized.ipynb")
                >>> nb = Notebook.from_file("samples/hello-world-serialized.ipynb")
                >>> for cell in nb:
                ...     print(cell.id)
                a9541506
                b777420a
                a23ab5ac
        """
        pass

class Outliner:
    r"""Quickly outlines the strucure of the notebook in a readable format.

    Args:
        notebook (Notebook): the notebook to outline.

    Usage:

            >>> nb = Notebook.from_file("samples/hello-world.ipynb")
            >>> o = Outliner(nb)
            >>> print(o.outline()) # doctest: +NORMALIZE_WHITESPACE
                Jupyter Notebook v4.5
                └─▶ Markdown cell #a9541506
                    ┌  Hello world!
                    │  ============
                    └  Print `Hello world!`:
                └─▶ Code cell #b777420a (1)
                    | print("Hello world!")
                └─▶ Markdown cell #a23ab5ac
                    | Goodbye! 👋
    """
    def __init__(self, notebook):
        self.notebook = notebook

    def outline(self):
        r"""Outlines the notebook in a readable format.

        Returns:
            str: a string representing the outline of the notebook.
        """
        code_cell = CodeCell({"cell_type": "code","execution_count": 1,"id": "b777420a",'source': ['print("Hello world!")']}) 
        #cellule de code utilisée plus tard 
        
        r = f"Jupyter notebook v{self.notebook.version}\n" # string dans laquelle on va construire l'objet retourné par la fonction
        for cell in self.notebook.cells:

            if type(cell)==type(code_cell): # je n'ai pas trouvé comment faire ce test de type de façon plus jolie sans créer une cellule de code plus haut
                t = 'Code Cell'
            else :
                t = 'Markdown Cell'
            r = r + f"└─▶ {t} #{cell.id}\n"
            source = cell.source
            number_lines = len(source) # nombre de lignes de code
            for k in range(number_lines):
                current_line = source[k]

                if k ==0 and number_lines !=1 : #première ligne
                    r = r + f"    ┌  {current_line}"
                elif k==(number_lines-1) and number_lines !=1:
                    r = r + f"   └  {current_line} " 
                else :
                     r = r + f"    |  {current_line} "
                if k==(number_lines-1):#dernière ligne
                    r = r + f"""\n"""
        
        return(r)



