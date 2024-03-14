# Copyright (c) Streamlit Inc. (2018-2022) Snowflake Inc. (2022)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import streamlit as st
from streamlit.logger import get_logger

LOGGER = get_logger(__name__)


def run():
    
    st.set_page_config(
        page_title="Hello",
        page_icon="👋",
    )

    st.write("# AuBoulot.fr")

    contrat = st.selectbox('Type de contrat', ["","CDD","CDI","Intérim","Stage","Apprentissage","Contrat pro","Indépendant"])

    experience = st.selectbox('Expérience', ["","Débutant", "1 an et plus", "3 ans et plus", "5 ans et plus"])
        
        #code_postal = st.text_input('Code Postal')
    
        #duree_publication = st.selectbox('Durée de publication', ["","Dernières 24h","Dernires 3j","Dernière semaine","Dernier mois"])
    
        #teletravail = st.selectbox('Télétravail', ["","Télétravail possible" ,"Téletravail partiel possible"])

    salaire = st.selectbox('Salaire', ["","1666,67+/mois","2083,33+/mois","2500,00+/mois","2916,67+/mois","3750,00+/mois"])

       # secteur = st.multiselect('Secteur', ["Ressources humaines et recrutement","Santé","Commerce de détail et de gros","Services aux particuliers",
       #                                      "Informatique","Gouvernement et administration publique","Enseignement et formation","Management et conseil aux entreprises",
       #                                      "ONG et associations à but non lucratif","Industrie manufacturière","Finance",
       #                                      "Services de construction, réparation et maintenance","Restauration","Énergie et exploitation des ressources naturelles",
       #                                      "Aérospatiale et défense","Assurance","Transport de biens et de personnes","Médias et communication","Télécommunications",
       #                                      "Immobilier","Hôtellerie et tourisme","Pharmaceutique et biotechnologie","Arts, divertissement et loisirs","Juridique",
       #                                      "Agriculture"])

    horaires = st.selectbox('Horaires', ["","Temps plein","Temps partiel","Week-end uniquement","Travail de nuit"])
    
    if st.button('Valider'):
            # Création du dictionnaire des entrées
            user_inputs = {
                'Type de contrat': contrat,
                'Expérience': experience,
                'Salaire': salaire,
        #        'Secteur': secteur,
                'Horaires': horaires
            }
            
            # Affichage du dictionnaire
            st.write(user_inputs)
            data = pd.read_json("BDD.json", lines=False)
            data2 = pd.DataFrame(data)
            df = data2[data2["typeContrat"]==user_inputs["Type de contrat"]]
            st.write(df)


if __name__ == "__main__":
    run()

