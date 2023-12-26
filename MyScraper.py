from MyScraperEngine import EliteProspectsScraperEngine
import time



def main():
    """
    Choix des paramètres de l'Elite Prospects Data Scraper
    1) Modes d'Exécutions :
        2 modes d'exécutions sont possibles :
            - 'Normal' = Scraping des données de tous les joueurs de la ligue choisie,
                ce mode crée 2 fichiers .csv :
                    - 'NomLigue_Teams.csv' contient le classement actuel de la ligue ainsi que des variables sur les équipes
                    - 'NomLigue_Players.csv' contient des données sur tous les joueurs de la ligue

            - 'Test' = Scraping des données d'un seul joueur d'une équipe et d'une ligue choisie,
                ce mode ne crée pas de fichier .csv, il se contente de d'afficher les données de l'équipe et les données du joueur choisi

    2) La ligue :
        On va renseigner un des numéros ci-dessous dans la variable (league_number)
        Ce numéro correspond à l'index de la ligue dans la liste de toutes les ligues scrapées

        Les ligues ci-dessous sont les ligues principales dans le monde
            0 : NHL (Ligue Majeure Nord Américaine, 32 équipes)
            1 : SHL (Ligue Majeure Suédoise, 14 équipes)
            46 : NL (Ligue Majeure Suisse, 14 équipes)
            68 : Ligue Magnus (Ligue Majeure Française, 12 équipes)
            84 : KHL (Ligue Majeure Russe, 23 équipes)

        
    3) Si jamais on veut faire tourner le Scraper en mode 'Test':
        3.1) Choix de l'équipe :
            De même que pour les ligues on va renseigner le numéro de l'équipe
            Ce numéro correspond à l'index de l'équipe dans la liste des équipes scrapées
            Les numéros vont de 0 à Nombre d'équipes-1 
            Le nombre d'équipe est rensigné juste au dessus en face de chaque ligue
            Assurez-vous de bien avoir choisi la bonne ligue !

            Pour la Ligue Magnus :
                0  : Amiens (23 joueurs)
                1  : Angers (26 joueurs)
                2  : Anglet (26 joueurs)
                3  : Bordeaux (32 joueurs)
                4  : Briançon (23 joueurs)
                5  : Cergy-Pontoise (25 joueurs)
                6  : Chamonix (22 joueurs)
                7  : Gap (26 joueurs)
                8  : Grenoble (29 joueurs)
                9  : Marseille (24 joueurs)
                10 : Nice (24 joueurs)
                11 : Rouen (24 joueurs)

                
        3.2) Choix du joueur :
            Encore une fois on va renseigner un numéro qui correspond à l'index dans la liste des joueurs scrapés
            Ces numéros vont de 0 jusqu'au Nombre de joueur-1  
            Le nombre de joueur est renseigné au dessus en face de chaque équipe
            Attention tout de même car ce nombre peut changer suivant les transferts au cours de la saison!
       
    Returns:
        scraper_mode: Le mode du scraper

        league_number; Le numéro de la ligue que l'on veut scraper

        team_number: Le numéro de l'équipe du joueur que l'on veut scraper (mode 'Test')

        player_number; Le numéro du joueur que l'on veut scraper (mode 'Test')
    """
    ###############################################################################################
    # Paramètres à modifier
    ###############################################################################################
    scraper_mode = 'Test'  # 'Normal' ou 'Test'

    league_number = 0  # 0 ou 1 ou 22 ou 46 ou 68 ou 84

    team_number = 5  # Ne sera pris en compte que si scraper_mode = 'Test'

    player_number = 0  # Ne sera pris en compte que si scraper_mode = 'Test'
    ###############################################################################################

    if league_number == 0:
        league_name = 'NHL'
    elif league_number == 1:
        league_name = 'SHL'
    elif league_number == 46:
        league_name = 'NL'
    elif league_number == 68:
        league_name = 'Ligue_Magnus'
    elif league_number == 84:
        league_name = 'KHL'


    return scraper_mode, league_number, team_number, player_number, league_name


if __name__ == '__main__':
    scraper_mode, league_number, team_number, player_number, league_name = main()


    # En mode Normal
    if scraper_mode == 'Normal':
        global_process_start = time.time()

        # Instanciation de l'Engine et récupération des dataframes
        engine = EliteProspectsScraperEngine()
        df_team, df_player = engine.process_scraping(league_number)

        # Exportation des dataframes sous forme de fichier .csv
        df_team.to_csv(f'{league_name}_Teams.csv', index=False, na_rep='None')
        df_player.to_csv(f'{league_name}_Players.csv', index=False, na_rep='None')  

        global_process_end = time.time()
        global_duration = (global_process_end - global_process_start) / 60
        print(f"Temps de process total : {global_duration:.4f} minutes")
    

    # En mode Test
    elif scraper_mode == 'Test':
        engine = EliteProspectsScraperEngine(
            in_test_mode=True, 
            team_to_test=team_number, 
            player_to_test=player_number
            )
        
        df_team, df_player = engine.process_scraping(league_number)
    
    else:
        print('Erreur : Mode du Scraper mal renseigné')