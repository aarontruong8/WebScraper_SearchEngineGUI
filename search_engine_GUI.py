from tkinter import *
import newestInvertedIndex
from pathlib import Path
import math
import json
from lxml import html
from re import findall
import pickle

class InvertedIndexGUI:
    def __init__(self, i_index, i):
        self.root_window = Tk()
        self.root_window.geometry('460x500')
        self.root_window.title("CS 121 Search Engine")

        # search engine name
        self.lbl = Label(self.root_window, text="ICSearch")
        self.lbl.grid(row = 0, column = 0)

        # search box
        self.input = Entry(self.root_window,width=75, justify = 'center')
        self.input.grid(row = 1, column = 0)

        # search button
        self.search_button = Button(self.root_window, text="Search", command=self.clicked)
        self.search_button.grid(row = 2, column = 0)

        # search results
        self.search_results = Label(self.root_window, text = "")
        self.search_results.grid(row = 3, column = 0)

        # inverted index
        self.index = i_index
        
    def clicked(self):
        '''event that displays search results'''
        url_string = self.index.query(self.input.get(), i)
        print(url_string)
        self.search_results.config(text = url_string)

    def run(self):
        self.root_window.mainloop()


            
if __name__ == "__main__":
    index_instance = newestInvertedIndex.InvertedIndex()
    index_instance.parse_json()

    # if the inverted index has not been created, create it
    my_file = Path("newinvertedindex.txt")
    if not my_file.is_file():
        index_instance.extract_content()
        index_instance.write_to_file()

    # otherwise, load it (will be slow)
    index_file = open("newinvertedindex.txt", 'rb')
    i = pickle.load(index_file)
    index_file.close()
    
    gui = InvertedIndexGUI(index_instance, i)
    gui.run()
