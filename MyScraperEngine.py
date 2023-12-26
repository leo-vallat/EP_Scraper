from MyParser import EliteProspectsParser
from MyCleaner import EliteProspectsDataCleaner
from MyGeolocator import EliteProspectsGeolocator
import pandas as pd
import time
import urllib.request
import warnings



# Ignorer l'avertissement spécifique lié à la concaténation de DataFrames
warnings.filterwarnings("ignore", category=FutureWarning, message="The behavior of DataFrame concatenation with empty or all-NA entries is deprecated.*")



class EliteProspectsScraperEngine():
    def __init__(self, in_test_mode=False, team_to_test=None, player_to_test=None):
        """
        Constructeur de la classe
        """
        self.url_EP = 'https://www.eliteprospects.com'
        self.url_leagues = self.url_EP + '/leagues'

        # Attributs si le Scraper Engine est en mode test
        self.in_test_mode = in_test_mode  # Par défaut l'attribut est False
        self.team_to_test = team_to_test  # Par défaut l'attribut est None
        self.player_to_test = player_to_test  # Par défaut l'attribut est None



    def HTTP_request(self,url):
        """
        Effectue la requête HTML de l'url voulu

        Args:
            url: Url du site sur lequel la requête sera effectuée
        
        Returns:
            response: La réponse à la requête 
        """
        req = urllib.request.Request(url, headers={'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/7046A194A'})
        html_response = urllib.request.urlopen(req)
        return html_response



    def html_shaping(self,html_response):
        """
        Met en forme une réponse HTML

        Args:
            html_reponse: réponse HTML issue d'une requête urllib.request.Request( )

        Returns:
            html_code_decoded: Le code html décodé
        """
        try :
            html_code_encoded = html_response.read()
        except OSError as e :
            print("Une erreur s'est produite :", e)
            pass

        html_code_decoded = html_code_encoded.decode('utf8')
        return html_code_decoded



    def scrap_leagues(self,html_code):
        """
        Extrait la listes des noms et des url des ligues de la page web Elite Prospects des ligues

        Args:
            html_code: code source de la page html décodé utf-8
        
        Returns:
            leagues: Liste de tuples contenant les noms et url des ligues
        """
        leagues_parser = EliteProspectsParser(leagues_webpage=True)
        leagues_parser.feed(html_code)
        leagues = leagues_parser.get_data()[0]
        return leagues



    def scrap_teams(self,html_code):
        """
        Extrait la listes des noms et des urls des équipes de la page web Elite Prospects de la ligue choisie 

        Args:
            html_data: source de la page html décodé utf-8
        
        Returns:
            les noms et les url des équipes de la ligue choisie
        """
        league_parser = EliteProspectsParser(league_webpage=True)
        league_parser.feed(html_code)
        teams = league_parser.get_data()[0]
        return teams



    def scrap_team_data(self,html_code):
        """
        Extrait la listes des noms et des urls des joueurs de la page web Elite Prospects de l'équipe choisie 

        Args:
            html_data: source de la page html décodé utf-8
        
        Returns:
            les noms et les url des équipes de la ligue choisie
        """
        players_parser = EliteProspectsParser(team_webpage=True)
        players_parser.feed(html_code)
        players = players_parser.get_data()[0]
        team_name = players_parser.get_data()[1][0]
        team_data = players_parser.get_data()[1][1:]
        return players, team_name, team_data



    def scrap_player_data(self,html_code, team):
        """
        Extrait la listes les infos de la page Elite Prospects choisi

        Args:
            html_data: source de la page html décodé utf-8
        
        Returns:
            les données concernant le joueur
        """
        player_data_parser = EliteProspectsParser(player_webpage=True)
        player_data_parser.give_team(team)
        player_data_parser.feed(html_code)
        player_data = (player_data_parser.get_data()[0], player_data_parser.get_data()[1])
        return player_data



    def scrap_coordinates(self,team_city = None, player_city = None, player_country = None):
        """
        Récupère les coordonées de la ville passée en paramètre

        Args:
            location: une chaine de caractère de la forme "Ville, Pays"
        
        Returns:
            coo: Liste contenant les coordonnées de la ville et celle du pays
            si on ne les a pas trouvées la liste contiendra des None
        """
        geolocator = EliteProspectsGeolocator()

        # Initialisation des tuples à retourner
        city_coo = (None, None)
        country_coo = (None, None)

        # Récupération des coordonnées de la ville d'une équipe
        if team_city is not None and player_city is None and player_country is None:
            if team_city == "Quinto":  # Cas particulier pour une ville introuvable
                team_city = "Quinto, Suisse"
            geolocator.scrap_coordinates(team_city)
            city_coo = geolocator.get_coordinates()

        # Récpuération des coordonnées de la ville et du pays d'une joueur
        if team_city is None and player_city is not None and player_country is not None:  # Si la ville n'est pas None et le pays n'est pas None
            city = player_city + ", " + player_country  # Met la ville sous la forme "Nom Ville, Nom Pays" pour obtenir des coo plus précises
            geolocator.scrap_coordinates(city)
            city_coo = geolocator.get_coordinates()

        if player_country is not None:  # Cas pays n'est pas None
            geolocator.scrap_coordinates(player_country)
            country_coo = geolocator.get_coordinates()

        return (city_coo, country_coo)



    def process_scraping(self,league_number):
        """
        Le Coeur du programme:
            1) Création des instances des EliteProscectsDataCleaner (équipe et joueur)
            Il mettront en forme les données récoltées par les EliteProspectParser 

            2) Création des dataframes pandas (équipes et joueurs)
            On commence par crée une instance de EliteProspectsDataCleaner 
            pour les données d'une équipe qui va mettre en forme les données
            Puis on définit la DataFrame Pandas et ses colonnes

            3) On scrape les ligues
            4) On scrape les équipes de la ligue choisie

            5.1) Si le Scraper Engine est de type test:
                - On procède au scraping des données du joueur choisi

            5.2) Sinon le Scraper Engine est de type normal:
                On entre dans une double boucle où:
                    - On scrape les joueurs des équipes
                    - On scrape les données des joueurs 
            
            Pour chaque étape de scraping un timer est déclenché
            Permettant d'obtenir le temps moyen de traitement d'une équipe (environ 2 minutes),
            Le temps moyen de traitement d'un joueur (environ 3,5 secondes),
            Le temps total de traitement pour la ligue choisie (de 15 à 45 minutes suivant le nombre d'équipes)

        Args:
            league_number: Indice de la ligue choisie dans la liste des url des ligues 

        Returns:
            df_teams: dataframe pandas avec les données des équipes (classement de la ligue)
            df_players: dataframe pandas avec les données des joueurs
        """
        ###########################################################################################
        # 1) Instanciation des EliteProspectsDataCleaner
        ###########################################################################################
        team_cleaner = EliteProspectsDataCleaner(for_team_data = True)
        player_cleaner = EliteProspectsDataCleaner(for_player_data = True)
        ###########################################################################################



        ###########################################################################################
        # 2) Création des dataframes pandas
        ###########################################################################################
        team_columns_names = ['Rang', 'Equipe', 'Match_Joue', 'Points', 'Victoire', 'Defaite', 
                            'Victoire_en_Prolongation', 'Défaite_en_Prolongation', 'Buts_Marques', 
                            'Buts_Encaisses', 'Point_par_Match', 'Ville', 'Latitude_Ville', 
                            'Longitude_Ville']
        df_teams_index = 0
        df_teams = pd.DataFrame(columns=team_columns_names)
        player_columns_names = ['Ligue', 'Equipe', 'Joueur', 'Position', 'Age', 'Taille', 
                        'Poids', 'Ville_de_Naissance', 'Pays_de_Naissance',
                        'Club_Formateur', 'Shoot', 'Annee_de_Draft', 'Ronde_de_Draft', 
                        'Position_de_Draft', 'Equipe_de_Draft', 'Salaire_NHL', 'Match_Joue', 'But', 
                        'Assist', 'Point', 'Penalites', 'Plus_Minus', 'GAA', 'SVP', 
                        'Latitude_Ville', 'Longitude_Ville', 'Latitude_Pays', 'Longitude_Pays']
        df_players_index = 0
        df_players = pd.DataFrame(columns=player_columns_names)
        ###########################################################################################



        ###########################################################################################
        # 3) Scraping des ligues
        ###########################################################################################
        leagues = self.scrap_leagues(self.html_shaping(self.HTTP_request(self.url_leagues)))  # Scraping de toutes les ligues du site
        url_leagues_list = [self.url_EP + league for a, b, league in leagues]  # Liste des url vers les pages web EP de toutes les ligues
        print('league : ', leagues[league_number][1])  # Print la ligue que l'on choisi
        ###########################################################################################



        ###########################################################################################
        # 4) Scraping des équipes
        ###########################################################################################
        teams = self.scrap_teams(self.html_shaping(self.HTTP_request(url_leagues_list[league_number])))  # Scraping des équipes de la ligue choisie
        url_teams_list = [self.url_EP + team for a, b, team in teams]  # Liste des url vers les pages web EP des équipes de la ligue choisie
        ###########################################################################################



        ###########################################################################################
        # 5.1) Scraper en mode test
        ###########################################################################################
        if self.in_test_mode:
            print('team : ', teams[self.team_to_test][1], '\n')  # Print l'équipe que l'on choisi

            team_data = self.scrap_team_data(self.html_shaping(self.HTTP_request(url_teams_list[self.team_to_test]))) # Scraping des joueurs de l'équipe choisie
            players = team_data[0]  # Récupère l'url du joueur
            team_name = team_data[1]  # Récupère le nom de son équipe
            team_data = team_data[2]  # Récupère le reste des données de l'équipe
            team_cleaner.data_cleaner(team_data_list=team_data)
            team_data = team_cleaner.get_team_data()
            coordinates_team = self.scrap_coordinates(team_city=team_data[-1])[0]
            team_data = [team_data[0]] + [teams[self.team_to_test][1]] + team_data[1:] + [coordinates_team[0], coordinates_team[1]]
            url_players_list = [self.url_EP + url_player for a,b,url_player in players] # Liste des url vers les pages web EP de tous les joueurs de l'équipe choisie

            for column_name, value in zip(team_columns_names, team_data):
                print(f"{column_name:>24} : {value}")  # Affichage des données de l'équipe
            print("\n")

            print('player : ', players[self.player_to_test][1], '\n')  # Print le joueur que l'on choisi

            player_data = self.scrap_player_data(self.html_shaping(self.HTTP_request(url_players_list[self.player_to_test])), team_name) #Scraping des données du joueur
            player_cleaner.data_cleaner(player_data_list1=player_data[0], player_data_list2=player_data[1])  # Clean des données scrapées
            data_pt1 = player_cleaner.get_player_data()[0]  # Stockage de la première partie des données
            data_pt2 = player_cleaner.get_player_data()[1]  # Stockage de la seconde partie des données
            coordinates = self.scrap_coordinates(player_city=data_pt1[4], player_country=data_pt1[5])  # Récupération des coordonnées de la ville et du pays d'origine du joueur
            
            player_data = (
                [leagues[league_number][1]] 
                + [teams[self.team_to_test][1]] 
                + [players[self.player_to_test][1]] 
                + data_pt1 
                + data_pt2 
                + [coordinates[0][0], coordinates[0][1], coordinates[1][0], coordinates[1][1]]
            )  # Liste des données du joueur

            for column_name, value in zip(player_columns_names, player_data):
                print(f"{column_name:>24} : {type(value).__name__:<8} : {value}")  # Affichage des données du joueur
            print("\n")
        ###########################################################################################



        ###########################################################################################
        # 5.2) Scraper en mode normal
        ###########################################################################################
        if not self.in_test_mode:
            # Listes pour stocker le temps d'execution du code pour chaque équipe et joueur 
            team_process_time_list = []
            player_process_time_list = []

            for j in range(len(url_teams_list)):  # Boucle sur les équipes choisies

                start_time_team = time.time()

                print(f'team {j+1}/{len(url_teams_list)} : {teams[j][1]}')  # Print l'équipe que l'on est entrain de scraper

                ###########################################################################################
                team_data = self.scrap_team_data(self.html_shaping(self.HTTP_request(url_teams_list[j]))) # Scraping des joueurs de l'équipe choisie
                players = team_data[0]  # Récupère l'url du joueur
                team_name = team_data[1]  # Récupère le nom de son équipe
                team_data = team_data[2]  # Récupère le reste des données de l'équipe
                team_cleaner.data_cleaner(team_data_list=team_data)  # Nettoyage des données
                team_data = team_cleaner.get_team_data()  # Récupération des données nettoyées
                coordinates_team = self.scrap_coordinates(team_city=team_data[-1])[0]  # Récupération des coordonnées de la ville de l'équipe
                team_data = [team_data[0]] + [teams[j][1]] + team_data[1:] + [coordinates_team[0], coordinates_team[1]]  # Création de la liste finale
                df_teams.loc[df_teams_index] = team_data  # Ajout des données de l'équipe à la dataframe df_teams
                df_teams_index += 1
                url_players_list = [self.url_EP + url_player for a, b, url_player in players] # Liste des url vers les pages web EP de tous les joueurs de l'équipe choisie
                ###########################################################################################


                for i in range(len(url_players_list)):  # Boucle sur les joueurs
                    
                    start_time_player = time.time()
                    
                    print(f'player {i+1}/{len(url_players_list)} : {players[i][1]}')  # Print le joueur que l'on est entrain de scraper

                    ###########################################################################################
                    player_data = self.scrap_player_data(self.html_shaping(self.HTTP_request(url_players_list[i])), team_name) #Scraping des données du joueur
                    player_cleaner.data_cleaner(player_data_list1=player_data[0], player_data_list2=player_data[1])  # Nettoyage des données scrapées
                    data_pt1 = player_cleaner.get_player_data()[0]  # Stockage de la première partie des données
                    data_pt2 = player_cleaner.get_player_data()[1]  # Stockage de la seconde partie des données
                    coordinates = self.scrap_coordinates(player_city=data_pt1[4], player_country=data_pt1[5])  # Récupération des coordonnées de la ville et du pays d'origine du joueur
                    
                    player_data = (
                        [leagues[league_number][1]] 
                        + [teams[j][1]] 
                        + [players[i][1]] 
                        + data_pt1 
                        + data_pt2 
                        + [coordinates[0][0], coordinates[0][1], coordinates[1][0], coordinates[1][1]]
                    ) # Liste finale des données du joueur

                    df_players.loc[df_players_index] = player_data  # Ajout des données du joueur à la dataframe df_players
                    df_players_index += 1
                    ###########################################################################################


                    end_time_player = time.time()
                    player_process_time_list.append(end_time_player - start_time_player)
                
                end_time_team = time.time()
                team_process_time_list.append((end_time_team - start_time_team) / 60)

            df_teams.sort_values(by='Points', inplace=True, ascending=False)  # Tri de la dataframe des équipes selon leur nombre de points pour obtenir un classement

            # Print des durées moyennes de traitement pour un joueur et une équipe
            print(f'Durée moyenne de process pour une équipe : {sum(team_process_time_list) / len(team_process_time_list):.4f} minutes')
            print(f'Durée moyenne de process pour un joueur : {sum(player_process_time_list) / len(player_process_time_list):.4f} secondes')
        ###########################################################################################

        

        return df_teams, df_players