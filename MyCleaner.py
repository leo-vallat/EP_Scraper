import re



class EliteProspectsDataCleaner():
    def __init__(self, for_team_data = False, for_player_data = False):
        """
        Constructeur du parser

        Args:
            player_data_list1 : Liste contenant la première partie des données 
            extraites sur le joueur (Nom, Taille, Poids ...)
            
            player_data_list2 : Liste contenant la seconde partie des données 
            extraites sur le joueur (stats sur la saison en cours)
        """
        # Attributs pour connaître la nature des données à nettoyer
        self.for_team_data = for_team_data
        self.for_player_data = for_player_data

        # Attributs pour nettoyer les données des joueurs
        self.player_data_list1 = []
        self.player_data_list2 = []
        self.is_field_player = True  # On part du principe que le joueur est un joueur de champs 
        self.is_goalie = False  # On part du principe que le joueur n'est pas un gardien
        self.is_NHL_prospect = False
        self.is_drafted = False
        self.has_NHL_rights = False
        self.has_NHL_contract = False

        # Attributs pour nettoyer les données d'une équipe 
        self.team_data_list = []
        


    def data_cleaner(self, team_data_list = [], player_data_list1 = [], player_data_list2 = []):
        """
        Opère un premier nettoyage sur les listes de données scrapées
        Les espaces vides sont supprimés
        Les valeurs manquantes sont remplacées par None

        Appelle la fonction de définition du profil de joueur
        Appelle les fonctions de nettoyage des données 
        """
        # Nettoyage des données d'une équipe
        if self.for_team_data:
            # Initialisation de l'attribut
            self.team_data_list = team_data_list

            # Suppression des espaces vides
            self.team_data_list = [item.strip() for item in self.team_data_list if item.strip()]

            # Remplacement des données Manquantes
            for i in range(len(self.team_data_list)):
                if '-' == self.team_data_list[i]:
                    self.team_data_list[i] = None

            # Formattage des données
            self.clean_team_data_list()


        # Nettoyage des données d'un joueur
        if self.for_player_data:
            # Initialisation des attributs
            self.player_data_list1 = player_data_list1
            self.player_data_list2 = player_data_list2

            # Suppression des espaces vides
            self.player_data_list1 = [item.strip() for item in self.player_data_list1 if item.strip()]  
            self.player_data_list2 = [item.strip() for item in self.player_data_list2 if item.strip()]  

            # Remplacement des données manquantes pas None
            for i in range(len(self.player_data_list1)):
                if '-' == self.player_data_list1[i] or '-/' in self.player_data_list1[i] or '- / -' in self.player_data_list1[i]:
                    self.player_data_list1[i] = None
            
            for i in range(len(self.player_data_list2)):
                if '-' == self.player_data_list2[i] or '-/' in self.player_data_list2[i] or '- / -' in self.player_data_list2[i]:
                    self.player_data_list2[i] = None


            # Définition des attributs du joueur
            self.define_type_player()

            # print(self.is_field_player)
            # print(self.is_goalie)  
            # print(self.is_drafted)
            # print(self.has_NHL_rights)
            # print(self.has_NHL_contract)


            # print(self.player_data_list1)
            # print(self.player_data_list2)


            # Formattage des deux parties des données
            self.clean_player_data_list1()
            self.clean_player_data_list2()

            self.set_attributes_default_values()  # On remet les attributs à leur valeur par défaut pour le joueur suivant



    def define_type_player(self):
        """
        Série de condition pour définir différentes caratéristiques du joueur dont
        on va nettoyer les données : Position, Draft, Contrat NHL, Droits NHL
        """
        # Cas où le joueur est un gardien
        if len(self.player_data_list2) == 4:
            self.is_goalie = True
            self.is_field_player = False

        # Cas où le joueur à été draté en NHL
        for element in self.player_data_list1:
            if element is not None:
                if 'overall by' in element:
                    self.is_drafted = True
        
        # Cas où le joueur à un contrat en NHL donc un salaire
        if 'Cap Hit' in self.player_data_list1:
            self.has_NHL_rights = True
            self.has_NHL_contract = True
        # Cas où le joueur n'a pas de contrat en NHL mais appartient quand même à une équipe NHL
        elif 'NHL Rights' in self.player_data_list1:
            self.has_NHL_rights = True

        # Cas où le joueur n'a aucun lien avec la NHL, le cas pas défaut
        else:
            pass



    def clean_team_data_list(self):
        """
        Met en forme les données propres à l'équipe
        """
        # Suppression du 5ème et du dernier éléments qui sont toujours nuls
        self.team_data_list.pop(4)
        self.team_data_list.pop(-1)

        # Inversion des positions la ville et du classement
        self.team_data_list[0], self.team_data_list[-1] = self.team_data_list[-1], self.team_data_list[0]

        # Déplacement du nombre de points en troisième position
        points = self.team_data_list.pop(8)
        self.team_data_list.insert(2, points)

        # Formattage de la ville du club
        if self.team_data_list[-1] is not None:
            self.team_data_list[-1] = self.team_data_list[-1].split(",")[0]

        # Converti les éléments voulu en entier
        for i in range(len(self.team_data_list[:-2])):
            self.team_data_list[i] = int(self.team_data_list[i])

        # Converti le nombre de points par match en flottant
        self.team_data_list[-2] = float(self.team_data_list[-2])



    def clean_player_data_list1(self):
        """
        Met en forme les caractéristiques du joueur
        """
        # Suppression de l'élément 'Agency' si il existe
        if self.player_data_list1[-1] == 'Agency':
            self.player_data_list1.pop(-1)

        # PREMIERE ETAPE : Avoir quelque soit le type de joueurs les mêmes éléments aux mêmes endroits
        # Cas joueur élégible au prochain draft NHL et classé parmis les meilleurs joueurs
        if self.player_data_list1[-1] != None:
            if re.search(r"#\d+ by", self.player_data_list1[-1]) and 'Ranked' in self.player_data_list1[-2]:
                self.player_data_list1 = self.player_data_list1[:-7]

        # Cas joueur éligible au prochain draft NHL
        if self.player_data_list1[-1] != None:
            if 'NHL Entry Draft' in self.player_data_list1[-1]:
                self.player_data_list1 = self.player_data_list1[:-3]  # Supprime les données du draft et le joueur est considéré sans draft, droits, contrat NHL

        # Cas joueur drafté avec des droits et un contrat NHL
        if self.is_drafted and self.has_NHL_rights and self.has_NHL_contract:
            self.player_data_list1 = self.player_data_list1[3:-3:2] + [self.player_data_list1[-1]] 

        # Cas joueur drafté qui a des droits en NHL mais pas de contrat NHL
        if self.is_drafted and self.has_NHL_rights and not self.has_NHL_contract:
            self.player_data_list1 = self.player_data_list1[3:-3:2] + [None] + [self.player_data_list1[-1]]  # Ajoute un None qui correspond au salaire

        # Cas joueur drafté sans droits en NHL et sans contrat en NHL
        if self.is_drafted and not self.has_NHL_rights and not self.has_NHL_contract:
            self.player_data_list1 = self.player_data_list1[3:-2:2] + [None] + [self.player_data_list1[-1]]  # Ajoute un None qui correspond au salaire

        # Cas joueur non drafté mais avec des droits et un contrat en NHL
        if not self.is_drafted and self.has_NHL_rights and self.has_NHL_contract:
            self.player_data_list1 = self.player_data_list1[3:-1:2] + [None]  # Ajoute un None qui correspond aux informations de draft

        # Cas joueur non drafté avec des droits NHL mais sans contrat
        if not self.is_drafted and self.has_NHL_rights and not self.has_NHL_contract:
            self.player_data_list1 = self.player_data_list1[3:-1:2] + [None] + [None] # Ajoute des None qui correspondent au salaire et aux informations de draft

        # Cas joueur non drafté sans droits ni contrat en NHL
        if not self.is_drafted and not self.has_NHL_rights and not self.has_NHL_contract:
            self.player_data_list1 = self.player_data_list1[3::2] + [None] + [None]  # Ajoute des None qui correspondent au salaire et aux informations de draft 
        

        # DEUXIEME ETAPE : Formater les éléments un par un
        #Formatage de la position (élément d'indice 0)
        if self.player_data_list1[0] not in [None,'G', 'D', 'F']:  #Si la position du joueur est C, LW, RW, C/LW ...
            self.player_data_list1[0] = 'F'  #Le joueur est alors simplement considéré comme un attaquant

        # Formatage de la taille
        if self.player_data_list1[2] is not None:  
            self.player_data_list1[2] = re.match(r'\d+', self.player_data_list1[2]).group(0)  # Garde uniquement la valeur numérique en cm de la taille

        # Formatage de la ville de naissance
        if self.player_data_list1[3] is not None:
            self.player_data_list1[3] = self.player_data_list1[3].split(',')[0]  #On ne garde que le nom de la ville

        # Formatage du poids
        if self.player_data_list1[4] is not None:  
            self.player_data_list1[4] = re.match(r'\d+', self.player_data_list1[4]).group(0)  # Garde uniquement la valeur numérique en kg du poids

        # Inversion du poid et de la ville de naissance si l'un des deux n'est pas nul (pour plus de cohérence)
        if self.player_data_list1[3] or self.player_data_list1[4] is not None:
            self.player_data_list1[3], self.player_data_list1[4] = self.player_data_list1[4], self.player_data_list1[3]

        # Inversion du shoot et du club formateur si l'un des deux n'est pas nul (pour plus de cohérence)
        if self.player_data_list1[6] or self.player_data_list1[7] is not None:
            self.player_data_list1[6], self.player_data_list1[7] = self.player_data_list1[7], self.player_data_list1[6]

        # Formatage de la donnée de draft
        if self.is_drafted:  # Si le joueur à été drafté
            draft = self.player_data_list1[-1]  #Récupère l'élément contenant les informations sur le draft
            match_draft = re.match(r"(\d{4}) round (\d+) #(\d+) overall by (.+)", draft)  #Expression régulière pour récupérer les infos utiles de draft
            self.player_data_list1.pop(-1)  #Supprime l'élément contenant les informations de draft avant de les ajoutées en dessous
            salaire = self.player_data_list1.pop(-1)  # Suppression du salaire pour le replacer après les données de draft
            self.player_data_list1.pop(-1)  # Suppression de la saison d'échéance du contrat actuel

            self.player_data_list1.append(match_draft.group(1)) #Année
            self.player_data_list1.append(match_draft.group(2))  #Numéro de ronde
            self.player_data_list1.append(match_draft.group(3))  #Numéro de choix
            self.player_data_list1.append(match_draft.group(4))  #Equipe

            self.player_data_list1.append(salaire)  # Repositionnement du salaire

        else:  # Si le joueur n'a pas été drafté
            salaire = self.player_data_list1.pop(-2)  # Le salaire se retrouve alors avant les données de draft
            
            if self.player_data_list1[-2] not in ['L', 'R']:  # Conditions vérifiant si l'avant dernier élément l'année d'échéance du contrat
                self.player_data_list1.pop(-2)  # Suppression de la saison d'échéance du contrat actuel

            self.player_data_list1.append(None)  # Ajoute 3 None à la place des valeurs de draft
            self.player_data_list1.append(None)  # Que 3 puisqu'on vait déjà mis un None plus haut
            self.player_data_list1.append(None)
            self.player_data_list1.append(salaire)  # Repositionnement du salaire

        # Formatage du salaire
        if self.has_NHL_contract:
            self.player_data_list1[-1] = self.player_data_list1[-1][1:]  # Retire le signe '$'
            self.player_data_list1[-1] = self.player_data_list1[-1].replace(',', '')  # Suppression des ,

        # Conversion des valeurs voulues en entier
        for i in [1,2,3,8,9,10,12]:
            if self.player_data_list1[i] is not None:
                self.player_data_list1[i] = int(self.player_data_list1[i])


    def clean_player_data_list2(self):
        """
        Met en forme les statisques de la saison du joueur
        """
        # Cas ou le joueur est un joueur de champs
        if self.is_field_player:
            self.player_data_list2 = self.player_data_list2 + [None, None] # Les None correspondent aux stats propres aux gardiens 

        # Cas ou le joueur est un gardien
        if self.is_goalie:
            self.player_data_list2 = [self.player_data_list2[0], None, None, None, None, None, self.player_data_list2[2], self.player_data_list2[3]]  # Les None correspondent aux stats propres aux joueurs 
        
        # Conversion des valeurs voulues en entier ou flottant
        for i in range(len(self.player_data_list2[:-2])):
            if self.player_data_list2[i] is not None:
                self.player_data_list2[i] = int(self.player_data_list2[i])
        for i in range(-1, -3, -1):
            if self.player_data_list2[i] is not None:
                self.player_data_list2[i] = float(self.player_data_list2[i])



    def set_attributes_default_values(self):
        """
        Modifie les attributs permettant de définir le type de joueur à qui les données appartiennent.
        Etant donné qu'on ne crée qu'une seule instance du Cleaner pour les joueurs il faut remettre
        ces attributs à leur valeur de défaut pour catégoriser les joueurs suivants.
        """
        self.is_field_player = True
        self.is_goalie = False  
        self.is_drafted = False
        self.has_NHL_rights = False
        self.has_NHL_contract = False



    def get_team_data(self):
        """
        Retourne la liste des données nettoyées de l'équipe

        Returns:
            self.team_data_list: Liste des données de l'équipe
        """
        return self.team_data_list



    def get_player_data(self):
         """
         Retourne les listes des données nettoyées des joueurs

         Returns:
            self.player_data_list1: Liste des caratéristiques du joueur (Age, Poids, Taille etc)

            self.player_data_list2: Liste des statistques de la saison en cours du joueur (Matchs joués, Buts, Assist etc)
         """
         return (self.player_data_list1, self.player_data_list2)