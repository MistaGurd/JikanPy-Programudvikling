from jikanpy import Jikan
jikan = Jikan()

anime = jikan.anime(1735)


def findENtitle(anime): # Funktion til at finde den engelske title
    for title in anime['data']['titles']: # Her graver vi i din data, som jikan.anime giver:
                                          # Først den overordnede data, derefter titles
                                          # Hvorefter vi leder efter typen English, da
                                          # Jikan kan udskrive for adskillige sprog.
        if title['type']=='English': # Hvis der findes en engelsk titel:
            return title['title'] # Gem titlen

print(findENtitle(anime)) # Udskriv titlen