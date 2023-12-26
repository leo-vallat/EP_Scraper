from geopy.geocoders import GeoNames
from geopy.exc import GeocoderTimedOut, GeocoderServiceError



class EliteProspectsGeolocator():

    coo_dic = {}  # Variable de classe contenant les pays et leur coo déjà récupérées

    def __init__(self):
        """
        Constructeur de la classe
        """
        self.geolocator = GeoNames(username = "leopold")
        self.coordinates = ()



    def scrap_coordinates(self, location, max_retries = 3):
        """
        Scrape les coordonnées de la location passées en paramètre.
        La location peut-être une ville ou un pays

        Args:
            location: Ville ou Pays dont on demande les coordonnées

            max_retries: Si une erreur "GeocoderTimedOut" survient on permet 3 tentatives
                        en faisant un appel récursif à cette même fonction
        """
        if location not in EliteProspectsGeolocator.coo_dic:
            coo = (None, None)
            try:
                geoloc_data = self.geolocator.geocode(location)
                if geoloc_data:  # Ajoute les coo du pays si elles existent
                    coo = (geoloc_data.latitude, geoloc_data.longitude)
                self.coordinates = coo
            except (GeocoderTimedOut, GeocoderServiceError) as e:
                print(f"Erreur : {e}")
                if max_retries > 0 :
                    self.scrap_coordinates(location, max_retries - 1)
                elif max_retries == 0:
                    coo = (None, None)
            EliteProspectsGeolocator.coo_dic[location] = coo
        else:
            self.coordinates = EliteProspectsGeolocator.coo_dic[location]
    


    def get_coordinates(self):
        """
        Retourne les coordonnées

        Returns:
            self.coordinates: tuple comprenant la latitude en première position
                            et la longitude en seconde position
        """
        return self.coordinates