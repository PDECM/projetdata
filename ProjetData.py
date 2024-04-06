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
from sklearn.neighbors import NearestNeighbors

import pandas as pd
import requests
import numpy as np
from datetime import datetime, timedelta

LOGGER = get_logger(__name__)

def prerun(criteres_choisis,testing_offre,Top_actu_base):

    # Fonction pour obtenir le token
    def get_access_token():
        url = "https://entreprise.pole-emploi.fr/connexion/oauth2/access_token?realm=/partenaire"
        headers = {
            "Content-type": "application/x-www-form-urlencoded",
        }

        data = {
            "client_id": "PAR_projetdatapoleemploi_38ad66752ea11e10d1ebd7ee054368dd715a4bcedca1966a2cffb7c3706c97f9",
            "client_secret": "6e80708e1e1ab70c51b7bbe4a0575466d09c8382f06e29d4c5993f5b0abf1f36",
            "grant_type": "client_credentials",
            "scope": "api_offresdemploiv2 application_PAR_projetdatapoleemploi_38ad66752ea11e10d1ebd7ee054368dd715a4bcedca1966a2cffb7c3706c97f9 o2dsoffre",
        }

        try:
            response = requests.post(url, headers=headers, data=data)

            if response.status_code == 200 or response.status_code == 206:
                token_data = response.json()
                return token_data.get('access_token', '')
            else:
                print(f"Échec de la demande de token avec le code d'état : {response.status_code}")

        except Exception as e:
            print(f"Une erreur s'est produite lors de l'obtention du token : {str(e)}")
            return None


    # Fonction pour effectuer la requête GET
    def make_get_request(token, min_date, max_date):
        url = "https://api.emploi-store.fr/partenaire/offresdemploi/v2/offres/search"
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

        params = {
            "minCreationDate": min_date,
            "maxCreationDate": max_date,
            "range": "1-149",
        }

        try:
            response = requests.get(url, headers=headers, params=params)

            if response.status_code == 200 or response.status_code == 204 or response.status_code == 206:
                # Convertir la réponse JSON en DataFrame
                data = response.json().get('resultats', [])
                df = pd.json_normalize(data)
                df = df[['id', 'intitule','description','lieuTravail.latitude','lieuTravail.longitude','lieuTravail.codePostal','romeCode','appellationlibelle','entreprise.nom','typeContrat','experienceLibelle','salaire.libelle','dureeTravailLibelle','qualificationCode','codeNAF','origineOffre.urlOrigine']]
                return df

            else:
                print(f"Échec de la requête GET avec le code d'état : {response.status_code}")
                return pd.DataFrame()

        except Exception as e:
            print(f"Une erreur s'est produite lors de la requête GET : {str(e)}")
            return pd.DataFrame()
    if Top_actu_base == "Oui":
      # Obtenir le token
      access_token = get_access_token()

      # Initialiser le DataFrame en dehors de la boucle
      result_df = pd.DataFrame()

      # Boucle sur les dates
      start_date = datetime(2023, 10, 1)
      end_date = datetime(2024, 2, 7) ###to change

      while start_date <= end_date:
          # Convertir les dates en format ISO 8601
          min_date = start_date.isoformat() + "Z"
          next_date = start_date + timedelta(days=1)
          max_date = next_date.isoformat() + "Z"

          # Utiliser le token pour la requête GET et concaténer les résultats
          if access_token:
              df = make_get_request(access_token, min_date, max_date)
              result_df = pd.concat([result_df, df], ignore_index=True)

          # Mettre à jour la date de début pour la prochaine itération
          start_date = next_date
    else:
      result_df = pd.read_excel('result_df_excel.xlsx')

    #Data Analysis
    def calculate_code(row):
        rome_code = str(row['romeCode'])
        appellation_libelle = str(row['appellationlibelle'])

        left_part = ord(rome_code[0]) * 10**7
        middle_part = int(rome_code[-4:]) * 10**3
        right_part = ord(appellation_libelle[0])

        return left_part + middle_part + right_part

    # Appliquer la fonction à chaque ligne du DataFrame
    result_df['valnumcoderome'] = result_df.apply(calculate_code, axis=1)

    def calculate_val_num_code_naf(code_naf):
      try:
        parts = code_naf.split('.')
        left_part = int(parts[0]) * 10**4
        middle_part = int(parts[1][:2]) * 10**2
        right_part = ord(parts[1][2]) - ord('A') + 1
        return left_part + middle_part + right_part
      except Exception as e:
          return 0

    # Appliquer la fonction à la colonne 'codeNAF' et assigner le résultat à une nouvelle colonne 'ValNumCodeNaf'
    result_df['ValNumCodeNaf'] = result_df['codeNAF'].apply(calculate_val_num_code_naf)

    def numerisation_typeContrat(typeContrat):
      if typeContrat=='CDI':
        return(0)
      elif typeContrat=='CDD':
        return(1)
      elif typeContrat=='MIS':
        return(2)
      elif typeContrat=='DIN':
        return(3)

    # Appliquer la fonction à la colonne 'typeContrat' et assigner le résultat à une nouvelle colonne 'ValNumTypeContrat'
    result_df['ValNumTypeContrat'] = result_df['typeContrat'].apply(numerisation_typeContrat)

    def numerisation_exp(experienceLibelle):
      try:
        parts = experienceLibelle.split(' ')
        if parts[1] == 'mois':
          return(int(parts[0])/12)
        elif parts[1] == 'ans' or parts[1] == 'an':
          return(int(parts[0]))
        elif len(parts) > 4 and parts[4]== 'An(s)':
          return(int(parts[3]))
        else:
          return(0)
      except Exception as e:
        print(experienceLibelle)

    # Appliquer la fonction à la colonne 'experienceLibelle' et assigner le résultat à une nouvelle colonne 'ValNumExperienceLibelle'
    result_df['ValNumExp'] = result_df['experienceLibelle'].apply(numerisation_exp)

    def numerisation_salaire(salaire):
      try:
        if type(salaire) == float or salaire =='De' or salaire =='Annuel de' or salaire == 'Mensuel de':
          return 0
        else:
          salaire_max = 0
          duree = 12
          parts_duree = salaire.split(' sur ')
          if len(parts_duree)>1:
            duree = float(parts_duree[1].split(' ')[0])
          parts_intervalle_salaire = parts_duree[0].split(' à ')
          if len(parts_intervalle_salaire)> 1:
            salaire_max=int((parts_intervalle_salaire[1].split(' ')[0]).split(',')[0])
          salaire_min = int((parts_intervalle_salaire[0].split(' ')[2]).split(',')[0])
          salaire_moyen = (max(salaire_max,salaire_min) + salaire_min)/2
          if parts_intervalle_salaire[0].split(' ')[0] == 'Horaire':
            salaire = salaire_moyen * 7 * 25 * 12
          elif parts_intervalle_salaire[0].split(' ')[0] == 'Mensuel':
            salaire = salaire_moyen * duree
          elif parts_intervalle_salaire[0].split(' ')[0] == 'Annuel':
            salaire = salaire_moyen * duree / 12
          else:
            salaire = 0
          return(salaire)
      except Exception as e:
        salaire = salaire.replace(',','.')
        if salaire.split(' ')[0] == 'De' and float(salaire.split(' ')[1])<7000 and float(salaire.split(' ')[1])>100:
            if len(salaire.split(' ')) > 3:
              salaire = (float(salaire.split(' ')[1]) + float(salaire.split(' ')[4]) )*12/2
            else:
              salaire = float(salaire.split(' ')[1]) *12
        elif salaire.split(' ')[0] == 'De' and float(salaire.split(' ')[1])>10000:
            if len(salaire.split(' ')) > 3:
              salaire = (float(salaire.split(' ')[1]) + float(salaire.split(' ')[4]) )/2
            else:
              salaire = float(salaire.split(' ')[1])
        else:
          print('Erreur' + salaire)

    # Appliquer la fonction à la colonne 'salaire.libelle' et assigner le résultat à une nouvelle colonne 'ValNumSalaire'
    result_df['ValNumSalaire'] = result_df['salaire.libelle'].apply(numerisation_salaire)

    def calculate_dureetravailibelle(dureeTravailLibelle):
        if type(dureeTravailLibelle) != float:
            # Supprime les espaces avant et après la chaîne
            dureeTravailLibelle = dureeTravailLibelle.strip()
            dureeTravailLibelle = dureeTravailLibelle.replace(' ','')

            # Si la chaîne se termine par 'H' suivie de chiffres, c'est un format valide
            if dureeTravailLibelle.endswith('H') and dureeTravailLibelle[:-1].isdigit():
                heures = int(dureeTravailLibelle[:-1])
                return heures



            # Si la chaîne contient 'H' et des chiffres et des minutes après, c'est un format valide
            elif 'H' in dureeTravailLibelle and len(dureeTravailLibelle.split('H'))>1 :
                partie_heures, partie_minutes = dureeTravailLibelle.split('H')[0],dureeTravailLibelle.split('H')[1]
                if partie_heures.isdigit() and partie_minutes[:2].isdigit():
                    heures = int(partie_heures)
                    minutes = int(partie_minutes[:2])
                    return heures + minutes / 60
                elif partie_heures.isdigit():
                    heures = int(partie_heures)
                    return heures

                    # Si la chaîne contient 'H' et des chiffres avant, c'est un format valide
            elif 'H' in dureeTravailLibelle:
                partie_heures = dureeTravailLibelle.split('H')[0]
                if partie_heures.isdigit():
                    heures = int(partie_heures)
                    return heures


            if dureeTravailLibelle == 'Tempsplein':
              return 35
            if dureeTravailLibelle == 'Tempspartiel':
              return 24

            # Si aucun des formats ci-dessus n'est valide, la chaîne ne peut pas être convertie en un nombre d'heures
            return 0
        else:
          return 0

    # Appliquer la fonction à la colonne 'dureeTravailLibelle' et assigner le résultat à une nouvelle colonne 'ValNumDureeTravail'
    result_df['ValNumDureeTravail'] = result_df['dureeTravailLibelle'].apply(calculate_dureetravailibelle)

    train_df = result_df
    train_df['ValNumCodeNaf'] = train_df['ValNumCodeNaf'] * 10
    train_df['ValNumExp'] = train_df['ValNumExp']*10**6
    train_df['ValNumTypeContrat'] = train_df['ValNumTypeContrat']*10**6
    train_df['ValNumDureeTravail'] = train_df['ValNumDureeTravail']*10**5
    train_df['qualificationCode'].fillna(0, inplace=True)
    train_df['ValNumqualificationCode'] = train_df['qualificationCode']*10**6
    train_df['ValNumSalaire'] =train_df['ValNumSalaire'] * 10** 2

    Nb_voisins = 150      #  user_entry

    train_df = train_df.loc[:,criteres_choisis]
    train_df.fillna(0, inplace=True)

    nn_model = NearestNeighbors(n_neighbors= Nb_voisins, algorithm='auto', metric='euclidean')
    nn_model.fit(train_df)

    distances, indices_neighbors = nn_model.kneighbors(testing_offre)

    table_finale = result_df.iloc[indices_neighbors[0],:]
    table_finale['scoring'] = np.round((1-np.sqrt(distances[0]/np.linalg.norm(np.array(testing_offre))))*100 ,2)
    table_finale_export = table_finale[['intitule','description','lieuTravail.latitude','lieuTravail.longitude','entreprise.nom','typeContrat','origineOffre.urlOrigine','scoring']]
    table_finale_export = table_finale_export.reset_index(drop = True)
    #data_finale = table_finale_export.dropna(subset = ['lieuTravail.latitude', 'lieuTravail.longitude'], inplace=True)

    return table_finale_export

def run():
    
    def calculate_val_num_code_naf(code_naf):
      try:
        parts = code_naf.split('.')
        left_part = int(parts[0]) * 10**4
        middle_part = int(parts[1][:2]) * 10**2
        right_part = ord(parts[1][2]) - ord('A') + 1
        return left_part + middle_part + right_part
      except Exception as e:
          return 0

    def numerisation_typeContrat(typeContrat):
      if typeContrat=='CDI':
        return(0)
      elif typeContrat=='CDD':
        return(1)
      elif typeContrat=='MIS':
        return(2)
      elif typeContrat=='DIN':
        return(3)

    
    st.set_page_config(
        page_title="Bienvenue à la carte des offres ! (un 20/20 svp )",
        page_icon="👋",
    )

    st.write("# AuBoulot.fr")
    Top_actu_base = st.selectbox('Voudriez-vous actualiser la base de données ? ',["Oui","Non"])
    secteur_data = pd.read_excel('Correspondance_coderome.xlsx')
    secteur = st.selectbox('Intitulé du poste', np.array(secteur_data['RomeLib']).tolist())
    code_NAF = st.text_input('Code NAF (ex:49.32Z)')
    contrat = st.selectbox('Type de contrat', ["CDD","CDI","MIS","DIN"])
    experience = st.number_input('Expérience en année (ex: 2.5)')
    salaire = st.number_input('Salaire mensuel en euro (ex:2000)')
    horaires = st.number_input("Nombre d'heure par semaine (ex:35)")
    Qualification_code = st.number_input('Score qualification de 1 à 6 ( 1 peu qualifié ---- 6 hautement qualifié ',step = 1)

    if st.button('Valider'):
      # Création du dictionnaire des entrées
      criteres_choisis = []
      testing_offre = []

      correspondance_table = pd.read_excel('Correspondance_coderome.xlsx')
      rome_code = correspondance_table.loc[correspondance_table.RomeLib == secteur, 'Codes'].iloc[0] 
      criteres_choisis.append('valnumcoderome')
      testing_offre.append(rome_code)

      if code_NAF != "" :
        criteres_choisis.append('ValNumCodeNaf')
        testing_offre.append(calculate_val_num_code_naf(code_NAF)*10)


      criteres_choisis.append('ValNumTypeContrat')
      testing_offre.append(numerisation_typeContrat(contrat)*10**6)


      criteres_choisis.append('ValNumExp')
      testing_offre.append((experience)*10**6)

      if salaire != 0 :
        criteres_choisis.append('ValNumSalaire')
        testing_offre.append((salaire)*10**2)

      if horaires != 0 :
        criteres_choisis.append('ValNumDureeTravail')
        testing_offre.append(horaires*10**5)

      if Qualification_code !=0  :
        criteres_choisis.append('ValNumqualificationCode')
        testing_offre.append((Qualification_code)*10**6)

      testing_offre = np.array(testing_offre).reshape(1,-1)

      # Affichage du dictionnaire
      data2 = prerun(criteres_choisis,testing_offre,Top_actu_base)
      st.write(data2.head())
      #data2.to_json('test_table_js.json', orient='records')
      #st.write(data2[["intitule","entreprise.nom","typeContrat","origineOffre.urlOrigine","scoring"]])


if __name__ == "__main__":
    run()
