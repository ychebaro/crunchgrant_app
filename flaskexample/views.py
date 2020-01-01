""" This file largely follows the steps outlined in the Insight Flask tutorial, except data is stored in a
flat csv (./assets/births2012_downsampled.csv) vs. a postgres database. If you have a large database, or
want to build experience working with SQL databases, you should refer to the Flask tutorial for instructions on how to
query a SQL database from here instead.

May 2019, Donald Lee-Brown
"""

from flask import render_template, session
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

# linking about page
@app.route('/about')
def about():
		return render_template("about.html")

@app.route('/details')
def test():
		user_input = request.args.to_dict()

		dbname = './flaskexample/static/data/db.sqlite'
		conn = sqlite3.connect(dbname)
		cur = conn.cursor()

		key = '%'+user_input['title']+'%'
		query = "select * from nsf where AwardTitle like '"+key+"';"
		result_df = pd.read_sql_query(query, conn)

		results = []
		results.append(dict(year=result_df.iloc[0]['Year'], title=result_df.iloc[0]['AwardTitle'], 
				amount=result_df.iloc[0]['AwardAmount'], inv=result_df.iloc[0]['InvestigatorsNames'], 
				inst=result_df.iloc[0]['Institution'], id=result_df.iloc[0]['AwardID'],
				effdate=result_df.iloc[0]['AwardEffectiveDate'], expdate=result_df.iloc[0]['AwardExpirationDate'],
				abstract=result_df.iloc[0]['Abstract']))

		# print(user_input)
		print(results)
		# print(resulta_df)
		return render_template("details.html", results=results)


@app.route('/model_output')
def birthmodel_output():
	 	# pull input fields and store them
		user_input = request.args.to_dict()

		# read in the data
		dbname = './flaskexample/static/data/db.sqlite'
		conn = sqlite3.connect(dbname)
		cur = conn.cursor()

		# search from abstract
		key = '%'+user_input['keyword']+'%'
		query = "select * from nsf where Abstract like '"+key+"';"
		resulta_df = pd.read_sql_query(query, conn)

		# search from investigator
		keyig = '%'+user_input['investigator']+'%'
		query = "select * from nsf where InvestigatorsNames like '"+keyig+"';"
		resultig_df = pd.read_sql_query(query, conn)

		# search from institution
		keyis = '%'+user_input['institution']+'%'
		query = "select * from nsf where Institution like '"+keyis+"';"
		resultis_df = pd.read_sql_query(query, conn)

		# merge the dataframes dropping duplicates
		tmp = pd.merge(resulta_df, resultig_df, how='inner')
		result_df = pd.merge(tmp, resultis_df, how='inner')
		result_df.dropna(inplace=True)
		result_df['AwardAmount'] = result_df['AwardAmount'].astype(int)

		# print(user_input)

		# search from funding amount
		if user_input['funding'] == 'lt50K':
			result_df = result_df[result_df['AwardAmount'] < 50000]
		if user_input['funding'] == '50K-100K':
			result_df = result_df[(result_df['AwardAmount'] >= 50000) & (result_df['AwardAmount'] < 100000)]
		if user_input['funding'] == '100K-500K':
			result_df = result_df[(result_df['AwardAmount'] >= 100000) & (result_df['AwardAmount'] < 500000)]
		if user_input['funding'] == '500K-1M':
			result_df = result_df[(result_df['AwardAmount'] >= 500000) & (result_df['AwardAmount'] < 1000000)]
		if user_input['funding'] == '1M-5M':
			result_df = result_df[(result_df['AwardAmount'] >= 1000000) & (result_df['AwardAmount'] < 5000000)]
		if user_input['funding'] == 'gt5M':
			result_df = result_df[result_df['AwardAmount'] > 5000000]


		results = []
		for i in range(0, result_df.shape[0]):
			results.append(dict(year=result_df.iloc[i]['Year'], title=result_df.iloc[i]['AwardTitle'], 
				amount=result_df.iloc[i]['AwardAmount'], inv=result_df.iloc[i]['InvestigatorsNames'], 
				inst=result_df.iloc[i]['Institution'], id=result_df.iloc[i]['AwardID']))

		return render_template("model_output.html", results=results, nb_results=result_df.shape[0])
