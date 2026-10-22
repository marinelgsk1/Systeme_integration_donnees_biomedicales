import dash
from dash import html, dcc
import pandas as pd
import json
import plotly.express as px
from dash.dependencies import Input, Output



# -------- HPO --------
with open("data/hpo_data.json", "r", encoding="utf-8") as f:
    data = json.load(f)

df = pd.DataFrame(data)
df["synonym_count"] = df["synonyms"].apply(len)
df_filtered = df[df["synonym_count"] > 0]
df["has_synonyms"] = df["synonym_count"] > 0

fig1 = px.histogram(
    df_filtered,
    x=df_filtered["synonym_count"].astype(str),
    title="Nombre de synonymes par entrée HPO",
    color_discrete_sequence=["#87CEEB"]
)
fig1.update_layout(xaxis_title="Nombre de synonymes", yaxis_title="Nombre d'entrées HPO")

fig2 = px.pie(
    df,
    names="has_synonyms",
    title="Présence de synonymes dans les concepts HPO",
    labels={True: "Avec synonymes", False: "Sans synonymes"},
    color_discrete_sequence=["#87CEEB", "#ADD8E6"]
)

# -------- DRUGBANK --------
with open("drugbank.json", "r", encoding="utf-8") as f:
    drugbank_data = json.load(f)

df_drugbank = pd.DataFrame(drugbank_data)
df_drugbank["has_indication"] = df_drugbank["indication"].apply(lambda x: bool(x and x.strip()))

fig_indication = px.pie(
    df_drugbank,
    names="has_indication",
    title="Présence d'une indication thérapeutique",
    labels={True: "Avec indication", False: "Sans indication"},
    color_discrete_sequence=["#87CEEB", "#ADD8E6"]
)

total_drugs = len(df_drugbank)

df_drugbank["has_toxicity"] = df_drugbank["toxicity"].apply(lambda x: bool(x and x.strip()))

fig_toxicity_presence = px.pie(
    df_drugbank,
    names="has_toxicity",
    title="Présence d’informations de toxicité",
    labels={True: "Avec toxicité", False: "Sans toxicité"},
    color_discrete_sequence=["#FFB6C1", "#FFC0CB"]
)

# -------- SIDER (EFFETS SECONDAIRES) --------
df1 = pd.read_csv(
    "meddra_all_se.tsv",
    sep="\t",
    header=None,
    names=["CID", "OtherCID", "ConceptID", "Type", "ConceptID2", "ConceptName"]
)

effects_per_med = df1.groupby("CID")["ConceptName"].nunique().reset_index()
effects_per_med.columns = ["CID", "NumEffects"]

effect_distribution = effects_per_med["NumEffects"].value_counts().sort_index().reset_index()
effect_distribution.columns = ["NumberOfEffects", "NumDrugs"]

fig_effect_dist = px.bar(
    effect_distribution,
    x="NumberOfEffects",
    y="NumDrugs",
    title="Distribution du nombre d'effets secondaires par médicament",
    labels={"NumberOfEffects": "Nombre d'effets secondaires", "NumDrugs": "Nombre de médicaments"}
)

top_effects = df1["ConceptName"].value_counts().head(10).reset_index()
top_effects.columns = ["EffectName", "Count"]

fig_tp_eff = px.bar(top_effects, x="EffectName", y="Count", title="Top 10 des effets secondaires")

# -------- INDICATIONS --------
df_indications = pd.read_csv(
    "meddra_all_indications.tsv",
    sep="\t",
    header=None,
    names=["CID", "UMLS_code", "Source", "Mention", "Type", "ConceptID2", "ConceptName"]
)

indications_per_med = df_indications.groupby("CID")["Mention"].nunique().reset_index()
indications_per_med.columns = ["CID", "NumIndications"]

fig_indications_count = px.histogram(
    indications_per_med,
    x="NumIndications",
    title="Distribution du nombre d'indications par médicament",
    labels={"NumIndications": "Nombre d'indications", "count": "Nombre de médicaments"}
)
"""OMIM"""
def parse_omim_file(filepath):
    """
    Parse un fichier OMIM-like.
    Retourne un DataFrame avec les champs utiles : no, ti, tx, cs, rf.
    """
    records = []
    current_record = {}
    current_field = None
    field_content = []

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if line.startswith("*RECORD*"):
                if current_record:
                    if current_field:
                        current_record[current_field] = "\n".join(field_content)
                    records.append(current_record)
                current_record = {}
                current_field = None
                field_content = []
            elif line.startswith("*FIELD*"):
                if current_field:
                    current_record[current_field] = "\n".join(field_content)
                current_field = line.replace("*FIELD*", "").strip().lower()
                field_content = []
            else:
                field_content.append(line)

        # Ajouter le dernier record
        if current_field:
            current_record[current_field] = "\n".join(field_content)
        if current_record:
            records.append(current_record)

    return pd.DataFrame(records)
omim_df = parse_omim_file("omim.txt")  # remplace par ton chemin exact

omim_df["has_cs"] = omim_df["cs"].apply(lambda x: bool(x and str(x).strip()))

fig_omim_cs = px.pie(
    omim_df,
    names="has_cs",
    title="Présence d’un synopsis clinique (OMIM)",
    labels={True: "Avec CS", False: "Sans CS"},
    color_discrete_sequence=["#90EE90", "#FFB6C1"]
)
nb_maladies = len(omim_df)
print(f"Nombre total de maladies dans OMIM : {nb_maladies}")







# -------- DASH APP --------
app = dash.Dash(__name__)

app.layout = html.Div([
    html.Div([
        html.H1("🧬 Dashboard de données biomédicales", style={"textAlign": "center"}),
        dcc.Tabs(id="tabs-example", value='tab-hpo', children=[
            dcc.Tab(label='HPO', value='tab-hpo'),
            dcc.Tab(label='SIDER', value='tab-meddra'),
            dcc.Tab(label='DRUGBANK', value='tab-drugbank'),
            dcc.Tab(label='OMIM', value='tab-omim')
         
        ])
    ], style={"backgroundColor": "#f0f8ff", "padding": "10px"}),

    html.Div(id='tabs-content')
])

@app.callback(
    Output('tabs-content', 'children'),
    Input('tabs-example', 'value')
)
def render_content(tab):

    if tab == 'tab-hpo':
        return html.Div([
            html.H2("Distribution du nombre de synonymes"),
            dcc.Graph(figure=fig1),
            html.H2("Présence ou absence de synonymes"),
            dcc.Graph(figure=fig2)
        ])

    elif tab == 'tab-meddra':
        return html.Div([
            html.H2("Section MEDDRA_SE"),
            html.Div([
                html.H3("1. Nombre d'effets secondaires par médicament"),
                dcc.Graph(figure=fig_effect_dist)
            ]),
            html.Div([
                html.H3("2. Top 10 des effets secondaires les plus fréquents"),
                dcc.Graph(figure=fig_tp_eff)
            ]),
            html.Hr(),
            html.H2("Section MEDDRA_INDICATIONS"),
            html.Div([
                html.H3("3. Distribution du nombre d’indications thérapeutiques par médicament"),
                dcc.Graph(figure=fig_indications_count)
            ])
        ])

    elif tab == 'tab-drugbank':
        return html.Div([
            html.H2("Section DRUGBANK"),
            html.Div([
                html.H3("Nombre total de médicaments :"),
                html.H1(f"{total_drugs}", style={"color": "#2E86C1", "fontSize": "48px"})
            ], style={
                "border": "1px solid #ccc",
                "padding": "20px",
                "marginBottom": "20px",
                "borderRadius": "10px",
                "backgroundColor": "#f0f8ff",
                "textAlign": "center",
                "boxShadow": "2px 2px 8px rgba(0,0,0,0.1)"
            }),
            html.H3("Présence d'une indication thérapeutique"),
            dcc.Graph(figure=fig_indication),
            html.H3("Présence d'information sur les effets secondaires"),
            dcc.Graph(figure=fig_toxicity_presence),
        ])

    elif tab == 'tab-omim':
        return html.Div([
            html.H2("Section OMIM"),
            
            html.H3("2. Présence d'un synopsis clinique"),
            dcc.Graph(figure=fig_omim_cs),

            html.Div([
                html.H3("Nombre total de maladies référencées :"),
                html.H1(f"{len(omim_df)}", style={"color": "#2E8B57", "fontSize": "48px"})
            ])

            


        ])

if __name__ == "__main__":
    app.run(debug=True)
