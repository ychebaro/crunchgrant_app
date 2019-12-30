""" This file largely follows the steps outlined in the Insight Flask tutorial, except data is stored in a
flat csv (./assets/births2012_downsampled.csv) vs. a postgres database. If you have a large database, or
want to build experience working with SQL databases, you should refer to the Flask tutorial for instructions on how to
query a SQL database from here instead.

May 2019, Donald Lee-Brown
"""

from flask import render_template
from flaskexample import app
from flaskexample.a_model import ModelIt
import pandas as pd
import sqlite3
from flask import request

# here's the homepage
@app.route('/')
def homepage():
		return render_template("bootstrap_template.html")

# example page for linking things
@app.route('/example_linked')
def linked_example():
		return render_template("example_linked.html")

#here's a page that simply displays the births data
@app.route('/example_dbtable')
def birth_table_page():
		births = []
		# let's read in the first 10 rows of births data - note that the directory is relative to run.py
		dbname = './flaskexample/static/data/births2012_downsampled.csv'
		births_db = pd.read_csv(dbname).head(10)
		# when passing to html it's easiest to store values as dictionaries
		for i in range(0, births_db.shape[0]):
				births.append(dict(index=births_db.index[i], attendant=births_db.iloc[i]['attendant'],
													 birth_month=births_db.iloc[i]['birth_month']))
		# note that we pass births as a variable to the html page example_dbtable
		return render_template('/example_dbtable.html', births=births)

# now let's do something fancier - take an input, run it through a model, and display the output on a separate page

@app.route('/model_input')
def birthmodel_input():
	 return render_template("model_input.html")

@app.route('/model_output')
def birthmodel_output():
	 # pull input fields and store them
		investigator = request.args.get('investigator')
		institution = request.args.get('institution')
		keyword = request.args.get('keyword')

		# read in the data
		dbname = './flaskexample/static/data/db.sqlite'
		conn = sqlite3.connect(dbname)
		cur = conn.cursor()
		print(keyword, type(keyword))

		key = '%'+str(keyword)+'%'
		query = "select * from nsf where Abstract like '"+key+"';"
		# result_keyword = cur.execute("select * from nsf where Abstract like ?", [key]).fetchall()
		#print(result_keyword, key)
		result_df = pd.read_sql_query(query, conn)

		results = []
		for i in range(0, result_df.shape[0]):
			results.append(dict(year=result_df.Year[i], title=result_df.AwardTitle[i], amount=result_df.AwardAmount[i], inv=result_df.InvestigatorsNames[i],
				inst=result_df.Institution[i]))
			# , attendant=result_df.iloc[i]['attendant'],
							 # birth_month=result_df.iloc[i]['birth_month']))
		return render_template("model_output.html", results=results, nb_results=result_df.shape[0])
