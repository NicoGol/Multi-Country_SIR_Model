# Multi-Country_SIR_Model
Repository containing the source code used in the different experiments presented in the paper "Are Travel Bans the Answer to Stopping the Spread of COVID-19 Variants? Lessons from a Multi-Country SIR Model" by N. Golenvaux, F. Docquier and P. Schaus

The data section comports every data file used for the different experiments
The graph section gathers every graph produced in the paper
The src section contains the different python scripts used to produce the experiments and generate the graphs 
  * Country.py contains the description of the class Country and its related methods used to represent the different countries during the simulation
  * migration_matrix.py is the script used to generate the baseline migration matrix based on the FB data
  * data.py manipulate the csv files and creates the different data structures needed for the experiments
  * plot_functions.py gathers the different functions producing the necessary figures and graphs
  * variantool.py is the python script simulating the spread of a variant accross the european countris using the Multi-Country SIR Model
  * flows_map_and_graphs.ipynb is the script used to generate the figures presented in the "Data and stylized facts on cross-border mobility in Europe" section of the paper
  * Luxembourg.ipynb is the script used to generate the figures related to Luxembourg presented in the Discussion section of the paper
