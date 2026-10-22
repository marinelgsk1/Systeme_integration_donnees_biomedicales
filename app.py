from flask import Flask, request, render_template, jsonify
from DIsease_SE import *
import json
from OR_AND_disease import *
from find_treatment_drugs import *
from get_results import *
from flask import Flask, request, render_template
import json
from ia import *
from utils import _generate_pie_chart
from get_results import get_results 

app = Flask(__name__)

@app.route("/", methods=["GET"])
def index():
    """
    Displays the main interface.
    """
    return render_template("interface.html")

@app.route("/manual_results", methods=["POST"])
def manual_results():
    """
    Handles the submission of symptoms from the manual form.
    Processes the symptoms and operator, fetches results,
    generates charts and initializes the AI conversation.
    """
    operator = request.form.get("operator")
    
    symptoms_json = request.form.get("symptoms")
    symptoms = json.loads(symptoms_json) if symptoms_json else []

    if not symptoms:
        return render_template("interface.html", message="Please enter at least one symptom")
    
    # Main function to retrieve the data
    dico_drugs, dico_treamtent, dico_diseases, \
    sources_stat_drugs, sources_stat_treatment, sources_stat_diseases, hpo_matches = \
        get_results(symptoms, operator)

    # IA conversation initialization
    diseases = list(dico_diseases.keys())
    meds = list(dico_drugs.keys())
    treatments = list(dico_treamtent.keys())
    init_conversation(symptoms, diseases, meds, treatments)

    #Data vizualisation
    if sources_stat_diseases:
        _generate_pie_chart(['OMIM', 'ORPHA'], sources_stat_diseases, 'diseases.png')

    if sources_stat_drugs:
        _generate_pie_chart(['STITCH', 'DRUGBANK', 'STITCH + DRUGBANK'], sources_stat_drugs, 'drugs.png')

    if sources_stat_treatment:
        _generate_pie_chart(['STITCH', 'DRUGBANK', 'STITCH + DRUGBANK'], sources_stat_treatment, 'treatments.png')

    return render_template(
        "interface.html",
        symptom=symptom,
        symptoms=symptoms,
        operator=operator,
        results=hpo_matches,
        dico_drugs=dico_drugs,
        dico_treamtent=dico_treamtent,
        dico_diseases=dico_diseases,
        sources_stat_drugs=sources_stat_drugs,
        sources_stat_treatment=sources_stat_treatment,
        sources_stat_diseases=sources_stat_diseases
    )

@app.route("/ask_ai", methods=["POST"])
#interface with the AI
def ask_ai():
    data = request.get_json()
    message = data.get("message", "")
    response = ask_openai(message)
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True)