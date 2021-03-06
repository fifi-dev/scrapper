# import libraries

import requests
from bs4 import BeautifulSoup
import pandas as pd
import requests_cache
from pprint import pprint

requests_cache.install_cache('demo_cache')

# On demande à l'utilisateur de rentrer sa ville

#ville = input("Quel est votre ville ").strip()

userAgent = "Mozilla/5.0 (ventows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.74 Safari/537.36"
acceptLanguage = "en-US,en;q=0.5"


def get_weather_data(url):
    session = requests.Session()
    # Retourne le headers sous forme de dictionnaire
    session.headers['User-Agent'] = userAgent
    session.headers['Accept-Language'] = acceptLanguage
    session.headers['Content-Language'] = acceptLanguage
    html = session.get(url)
    # create a new soup
    soup = BeautifulSoup(html.text, "html.parser")

    # on recupere la météo du jour
    # stockage du résultat dans un dictionnaire
    result = {}
    # recuperation de la ville
    result['ville'] = soup.find("div", attrs={"id": "wob_loc"}).text
    # temperature actuelle
    result['temp'] = soup.find("span", attrs={"id": "wob_tm"}).text
    # jour et heure actuelle
    result['timestamp'] = soup.find("div", attrs={"id": "wob_dts"}).text
    # météo
    result['weather_now'] = soup.find("span", attrs={"id": "wob_dc"}).text
    #  % d'humidité
    result['humidity'] = soup.find("span", attrs={"id": "wob_hm"}).text
    # vent
    result['vent'] = soup.find("span", attrs={"id": "wob_ws"}).text
    # precipitation
    result['precipitation'] = soup.find("span", attrs={"id": "wob_pp"}).text

    # get next few days' weather
    jours_suivants = []
    jours = soup.find("div", attrs={"id": "wob_dp"})
    for jours in jours.findAll("div", attrs={"class": "wob_df"}):
        # extract the name of the day
        nom = jours.findAll("div")[0].attrs['aria-label']
        # get weather status for that day
        weather = jours.find("img").attrs["alt"]
        temp = jours.findAll("span", {"class": "wob_t"})

        # [0] Celsius, [1]ant fahrenheit
        tempMax = temp[0].text
        # [2] Celsius, [3] fahrenheit
        tempMin = temp[2].text

        jours_suivants.append(
            {"nom": nom, "weather": weather, "tempMin": tempMin, "tempMax": tempMax})
    # on ajoute cela au résultat
    result['jours_suivants'] = jours_suivants
    return result


if __name__ == "__main__":
    URL = "https://www.google.com/search?lr=lang_en&ie=UTF-8&q=weather"
    import argparse
    parser = argparse.ArgumentParser(
        description="Script permettant de voir la météo via Google Weather")
    parser.add_argument("ville", nargs="?", help="""Region de la météo que vous souhaitez consulter.
                                        la localisation par defaut est celle de votre adresse IP""", default="")
    # parse arguments
    args = parser.parse_args()
    ville = args.ville
    URL += ville
    # get data
    data = get_weather_data(URL)

 # Affichgage des données
    print("Ville:", data["ville"])
    print("Actuellement:", data["timestamp"])
    print(f"Temprature Actuelle: {data['temp']}°C")
    print("Description:", data['weather_now'])
    print("Precipitation:", data["precipitation"])
    print("Humidité:", data["humidity"])
    print("Vent:", data["vent"])
    print("Jours suivants:")
    for meteo in data["jours_suivants"]:
        print("="*20, meteo["nom"], "="*20)
        print("Description:", meteo["weather"])
        print(f" temperature Maximum: {meteo['tempMax']}°C")
        print(f" temperature Minimum: {meteo['tempMin']}°C")
