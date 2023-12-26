from html.parser import HTMLParser
import unicodedata



class EliteProspectsParser(HTMLParser):
    def __init__(self, leagues_webpage = False, league_webpage = False, team_webpage = False, player_webpage = False):
        """
        Constructeur du parser

        Args:
            leagues_webpage: Booléen valant True si le parser est destiné à Parser la page web contenant toutes les ligues

            league_webpage: Booléen valant True si le parser est destiné à Parser la page web d'une ligue

            team_webpage: Booléen valant True si le parser est destiné à Parser la page web d'une équipe

            player_webpage: Booléen valant True si le parser est destiné à Parser la page web d'un joueur
        """
        super().__init__()
        # Attributs pour connaitre la nature de la page à inspecter
        self.leagues_webpage = leagues_webpage
        self.league_webpage = league_webpage
        self.team_webpage = team_webpage
        self.player_webpage = player_webpage

        # Attribut pour éviter les doublons lors du scraping des ligues et s'assurer que la data que l'on récupère est bien une ligue
        self.anti_duplication_list = []
        self.is_league = False

        # Attributs pour assurer la pertinence des données lors du scraping des équipes d'une ligue
        self.in_target_div = False
        self.depth = 0
        self.is_team = False

        # Attributs pour assurer la pertinence des données lors du scraping des données de la page web d'une équipe
        # Pour scraper les joueurs
        self.is_player = False  
        # Pour scraper les données de l'équipe en générale 
        self.is_town = False
        self.in_h2 = False
        self.in_target_table = False
        self.is_team_data = False
        self.team_data_count = 0

        # Attributs pour assurer la pertinence des données lors du scraping des infos d'un joueur
        # Attributs du scraping des infos de la partie 1
        self.in_div = False
        self.in_a = False
        # Attributs du scraping des infos de la partie 2
        self.in_target_area = False
        self.in_target_tr = False
        self.len_max = 11  # Valeur qui permet de limiter le scraping des données à ce que l'on veut
        self.players_team = ''
        self.data_to_check = False
        self.scrap_data = False


        # Attribut qui contient la partie scpécifique du lien url vers une équipe ou un joueur que l'on a scrapé
        # il est nommé comme l'attribut de la balise html où l'on scrape les données
        self.href = ""

        # Listes contentant les ligues ou les équipes ou les joueurs ou la data des joueurs que l'on a scrapé
        # La deuxième liste sera utile pour le scraping des données d'un joueur
        self.data_list1 = []
        self.data_list2 = []

        # Attributs en plus, utiles lors du développement, notamment pour voir les doublons
        self.league_number = 0
        self.team_number = 0
        self.player_number = 0



    def handle_starttag(self, tag, attrs):
        """
        Analyse toutes les balises de départ du code html

        Args:
            tag: balise à analyser 

            attrs: attributs de la balise
        """
        if self.leagues_webpage:
            self.handle_starttag_leagues(tag, attrs)

        elif self.league_webpage:
            self.handle_starttag_league(tag, attrs)

        elif self.team_webpage:
            self.handle_starttag_team(tag, attrs)

        elif self.player_webpage:
            self.handle_starttag_player(tag, attrs)



    def handle_data(self, data):
        """
        Analyse les données à l'intérieur d'une balise

        Args:
            data: Données qui se trouve dans la balise
        """
        if self.leagues_webpage:
            self.handle_data_leagues(data)

        elif self.league_webpage:
            self.handle_data_league(data)

        elif self.team_webpage:
            self.handle_data_team(data)

        elif self.player_webpage:
            self.handle_data_player(data)



    def handle_endtag(self, tag):
        """
        Intercepte la balise de sortie du code html

        Args:
            tag: balise de sortie
        """
        if self.league_webpage:
            self.handle_endtag_league()

        if self.team_webpage:
            self.handle_endtag_team(tag)

        if self.player_webpage:
            self.handle_endtag_player(tag)



    # Méthodes d'analyse pour la page web contenant toutes les ligues
    def handle_starttag_leagues(self, tag, attrs):
        """
        Analyse des balises de départ spécifique à la page web contenant toutes les ligues

        Args:
            tag: balise à analyser 

            attrs: attributs de la balise      
        """
        if tag == 'a':
            for attr in attrs:
                if attr[0] == 'href' and '/league/' in attr[1] and attr[1] not in self.anti_duplication_list:
                        self.is_league = True
                        self.href = attr[1]
                        self.anti_duplication_list.append(self.href)

    def handle_data_leagues(self, data):
        """
        Analyse les données à l'intérieur d'une balise spécifique pour la page web contenant toutes les ligues

        Args:
            data: nom de la ligue
        """
        if self.is_league:
            self.league_number +=1
            self.data_list1.append((self.league_number, data, self.href))
            self.is_league = False

    def handle_endtag_league(self):
        """
        Intercepte les balises sortantes et modifie les attributs de tri lors du scraping des données d'une ligue

        Args:
            tag : la balise de sortie à analyser
        """
        if self.in_target_div:
            if self.depth > 0:
                self.depth -= 1
            else:
                self.in_target_div = False



    # Méthodes d'analyse pour la page web d'une ligue
    def handle_starttag_league(self, tag, attrs):
        """
        Analyse des balises de départ spécifique à la page web d'une ligue

        Args:
            tag: balise à analyser 

            attrs: attributs de la balise      
        """
        if tag == 'div' and ('id', 'league-team-rosters') in attrs:
            self.in_target_div = True
        elif self.in_target_div:
            self.depth +=1

        if tag == 'a' and self.in_target_div:
            for attr in attrs:
                if attr[0] == 'href' and '/team/' in attr[1]:
                    self.is_team = True
                    self.href = attr[1]

    def handle_data_league(self, data):
        """
        Analyse les données à l'intérieur d'une balise spécifique pour la page web d'une ligue

        Args:
            data: nom de l'équipe
        """
        if self.in_target_div and self.depth > 0 and self.is_team :
            self.team_number +=1
            self.data_list1.append((self.team_number, data, self.href))
            self.is_team = False



    # Méthodes de d'analyse pour la page web d'une équipe
    def handle_starttag_team(self, tag, attrs):
        """
        Analyse des balises de départ spécifique à la page web d'une équipe

        Args:
            tag: balise à analyser 

            attrs: attributs de la balise      
        """
        # Récupération du nom complet de l'équipe (servira pour scraper les données de jeu des joueurs)
        if tag == 'meta' and ('name', 'description') in attrs : 
            self.data_list2.append(attrs[1][1].split(' - ',1)[0])

        # Conditions pour scraper les noms des joueurs
        if tag == 'div' and ('class', 'Roster_player__9KrIs') in attrs:  #Condition pour vérifier qu'on est dans une balise div qui correspond
            self.is_player = True  #Alors on sait que le contenu de la balise a suivante est le nom et prénom du joueur
        if self.is_player and tag == 'a':   #Condition pour vérifier qu'on est dans une balise a qui correspond
            self.href = attrs[2][1]  #On récupère le lien vers la page web EP du joueur

        # Condition pour scraper le reste des données de l'équipe
        if tag == 'a':
            for attr in attrs:
                if '/search/team?town=' in attr[1]:  # Conditions pour la balise contenant la ville
                    self.is_town = True
        if tag == 'h2':  # Première condition pour repérer l'endroit du code contenant le reste des données
            self.in_h2 = True
        if self.in_target_table and tag == 'span':  # Condition pour trouver la balise contenant une data 
            self.is_team_data = True
        if self.in_target_table and self.team_data_count > 11:  # Condition pour arrêter la récolte de data
            self.in_target_table = False
        
    def handle_data_team(self, data):
        """
        Analyse les données à l'intérieur d'une balise spécifique pour la page web d'une équipe

        Args:
            data: nom du joueur
        """
        # Récupération du nom et prénom du joueur
        if self.is_player:  
            self.player_number += 1
            self.data_list1.append((self.player_number, data, self.href))  # On ajoute les données que l'on veut à la liste des joueurs
            self.is_player = False  # Puisqu'on sort de la balise juste après on passe l'attribut de condition à False

        # Récupération de la ville où joue l'équipe
        if self.is_town:
            self.data_list2.append(data)
        
        # Récupération des autres données de l'équipe
        if self.in_h2 and "History And Standings" in data:  # Seconde condition pour repérer l'endroit du code contenant le reste des données
            self.in_target_table = True

        if self.is_team_data and self.team_data_count <= 11:  # Condition pour récupérer les bonnes données
            self.data_list2.append(data)
            self.team_data_count +=1

    def handle_endtag_team(self, tag):
        """
        Intercepte les balises sortantes et modifie les attributs de tri lors du scraping des données d'une équipe

        Args:
            tag: balise de sortie à analyser
        """
        if tag == 'a' and self.is_town:
            self.is_town = False
        if tag == 'h2':
            self.in_h2 = False
        if tag == 'span' and self.is_team_data:
            self.is_team_data = False



    # Méthodes d'analyse pour la page web d'un joueur
    def handle_starttag_player(self, tag, attrs):
        """
        Analyse des balises de départ spécifique à la page web d'un joueur

        Args:
            tag: balise à analyser 

            attrs: attributs de la balise      
        """
        try:
            if tag == "div" and "class" in attrs[0][0] and "col-xs-12" in attrs[0][1]:  # Pour les données de la première partie
                self.in_div = True
        except IndexError:  #Dans le cas où la liste attrs est vide
            pass

        if self.in_div and tag == "a":  # Pour les données de la première partie
            self.in_a = True
        

        # Pour les données de la seconde partie
        try:
            if tag == 'tr' and 'class' in attrs[0][0] and 'player-stats stats-type-default' in attrs[0][1] and ('data-season','2023-2024') in attrs:  # Condition pour scraper les données de jeu de la bonne saison
                # print('in target tr')
                # print('/' + self.players_team + '/')
                self.in_target_tr = True

        except IndexError:  #Dans le cas où la liste attrs est vide
            pass
        try:
            #if self.in_target_tr and tag == 'a' and 'href' in attrs[0][0] and re.search(r"/.+" + re.escape(self.players_team) + r"/", attrs[0][1]):  # Condition pour scraper les données de jeu dans la bonne équipe
            if self.in_target_tr and tag == 'a' and 'href' in attrs[0][0] and '/' + self.players_team + '/' in attrs[0][1]:
                # print('scrap data')
                self.scrap_data = True
        except IndexError:
            pass
        try:
            if self.in_target_tr and self.scrap_data and tag == "td" and attrs[0][1] == 'regular gp':  # Condition pour scraper les bonnes données de jeu
                self.in_target_area = True
                # print('in target area')
        except IndexError:  #Dans le cas où la liste attrs est vide
            pass

    def handle_data_player(self, data):
        """
        Analyse les données à l'intérieur d'une balise spécifique pour la page web d'un joueur

        Args:
            data: données à l'intérieur des balises
        """
        #Condition pour savoir si le joueur est un gardien
        if len(self.data_list1) == 5 and 'G' == self.data_list1[4].strip():  
            self.len_max = 8  #Auquel cas on limite la longueur de self.data_list2

        # Scraping des données pour la première partie
        # Vérification qu'on est au bon endroit pour scraper les données
        if self.in_div or self.in_a:
            self.data_list1.append(data)
            if self.in_a:
                self.in_a = False    #Si on est dans une balise a elle même dans une balise div alors les balises a dans la balise div suivante ne seront pas prisent en compte
                self.in_div = False  #Utile dans le cas de double nationalité

        # Scraping des données pour la seconde partie
        # Vérification qu'on est au bon endroit pour scraper les données
        if self.in_target_tr and self.in_target_area and len(self.data_list2) < self.len_max:
            self.data_list2.append(data)

    def handle_endtag_player(self, tag):
        """
        Intercepte les balises sortantes et modifie les attributs de tri lors du scraping des données d'un joueur

        Args:
            tag : la balise de sortie à analyser
        """
        # Pour les données de la première partie
        if tag == "a" and self.in_a:
            self.in_a = False
        if tag == "div" and self.in_div:
            self.in_div = False

        # Pour les données de la seconde partie
        if tag == "tr" and self.in_target_area:
            self.in_target_tr = False
            self.in_target_area = False
            self.scrap_data = False



    # Autres Méthodes
    def give_team(self, team):
        """
        Récupère l'équipe dans laquelle joue le joueur
        et la formate tel qu'elle le serait dans une url
        Cette fonction est appelée uniquement si on parse la page EP d'un joueur

        On va se servir de l'équipe pour vérifier qu'au moment de scrape les données
        de la saison en cours du joueur, ces données soient bien celle de l'équipe dans laquelle il est 
        
        Si jamais un joueur à joué dans plusieurs équipes pendant la saison en cours
        
        Args:
            team: équipe du joueur
        """
        team = team.lower()  # Convertir en minuscules
        team = team.replace(" ", "-")  # Remplacer les espaces par des tirets
        team = ''.join(c for c in unicodedata.normalize('NFD', team) if unicodedata.category(c) != 'Mn')  # Supprimer les caractères accentués

        if team == 'rapperswil-jona':
            team = 'sc-rapperswil-jona-lakers'

        elif team == 'biel-bienne':
            team = 'ehc-biel-bienne'

        self.players_team = team

    def get_data(self):
        """
        Accesseur pour la liste des données parsées

        Returns:
            self.data_list1: la liste des données
        """
        return self.data_list1, self.data_list2