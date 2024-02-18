import os
import tempfile
import pandas as pd
from flask import Flask, render_template, send_file
import numpy as np

EXCEL_FILE = r"C:\Users\82108\Desktop\pandas.xlsx"
app = Flask(__name__)


def extract_df():
    dfs = pd.read_excel(EXCEL_FILE, sheet_name=None, header=None)
    for sheet_name, df in dfs.items():
        dfs[sheet_name] = update_df(df)
    return dfs

        
def update_df(df):
    df.fillna(np.nan, inplace=True)
    r_idx = (df.notna()).any(axis=1).idxmax()
    c_idx = (df.notna()).any(axis=0).idxmax()
    print(f"r_idx, c_idx : {r_idx}, {c_idx}")
    df = df.iloc[r_idx:, c_idx:]
    return df   


dfs = extract_df()


@app.route("/")
def display_home():
    sheet_names = list(dfs.keys())
    return render_template("home.html", sheet_names=sheet_names)


@app.route("/display/<sheet_name>")
def display_sheet(sheet_name):
    df = dfs.get(sheet_name, pd.DataFrame())
    html_table = df.to_html()
    return render_template("sheet.html", sheet_name=sheet_name, df=html_table, excel_file=f'/download/{sheet_name}')


@app.route("/download/<sheet_name>")
def download_sheet(sheet_name):
    df = dfs.get(sheet_name, pd.DataFrame())
    fd, temp_file = tempfile.mkstemp(suffix='.xlsx')
    df.to_excel(temp_file, index=False)
    return send_file(temp_file, as_attachment=True, download_name=f'{sheet_name}.xlsx', mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


if __name__ == "__main__":
    app.run(debug=True)
    
    
    