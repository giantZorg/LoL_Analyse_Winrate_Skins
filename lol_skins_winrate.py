# -*- coding: utf-8 -*-
"""
Created on Mon May  6 09:35:25 2019

@author: SUTY1
"""


# Pakete importieren
import os
import getpass

if getpass.getuser() == 'SUTY1':
    os.chdir('F:')

from selenium import webdriver
#from selenium.webdriver.chrome.options import Options
import lxml.html
from lxml.etree import tostring

#from itertools import chain, groupby
import re
import pandas as pd
import numpy as np
import pickle
from datetime import datetime

#import warnings
#import matplotlib.pyplot as plt


def modus(lst):
    return(max(set(lst), key=lst.count))


def stringZuMatrix(graphNurDaten):
    graphSplit = graphNurDaten.split('],[')
    graphSplit[0] = graphSplit[0][2:]
    graphSplit[-1] = graphSplit[-1][:-2]

    spalten = 2
    reihen = len(graphSplit)
    
    matrixOutput = np.zeros((reihen, spalten))
    
    for i in range(0, reihen):
        matrixOutput[i,:] = np.array(graphSplit[i].split(',')).astype(float)
        
    return(matrixOutput)
    

def htmlChampionsGeaendert(html, champListeAngepasst, patchNummer):
    # Championänderungen
    listeChampionsVeraendert = list()

    # Nach patch-champions
    elementIds = ["patch-champions", "patch-minor-changes-and-bugfixes", "patch-simple-champion-changes", "patch-fighters", "patch-mages-and-assassins", "patch-marksmen", "patch-supports", 
                  "patch-juggernauts", "patch-marksman-updates", "patch-major-mage-updates", "patch-minor-mage-updates", "patch-tank-updates", "patch-reksai-kindred-malzahar",
                  "patch-mid-lane-worlds-balance", "patch-top-lane", "patch-mid-lane", "patch-bot-lane", "patch-rammus", "patch-duskblade-champions",
                  "patch-simple-buffs", "patch-simple-nerfs", "patch-tanks", "patch-akali-and-pyke", "patch-kalista,-ornn-and-sejuani", "patch-simple-changes",
                  "patch-simple-buffs-and-nerfs"]
    
    for elementId in elementIds:
        try:
            if patchNummer == '6.18':
                htmlChampions = html.get_element_by_id(elementId)
            elif patchNummer == '8.9':
                htmlChampions = html.xpath("//h2[contains(@id, '" + elementId +"')]")[0].getparent()
            else:
                htmlChampions = html.get_element_by_id(elementId).getparent()
            
            
            while True:
                htmlChampions = htmlChampions.getnext()
                if htmlChampions.tag == 'p':
                    continue
                if htmlChampions.tag != 'div':
                    break
                
                for child in htmlChampions[0][0].getchildren():
                    if child.get("id") is not None:
                        listeChampionsVeraendert.append(child.get("id"))
        except:
            pass
    
    # Filtern
    pdChampionsVeraendert = pd.DataFrame({'Champions': [champ[6:].replace('wukong', 'monkeyking') for champ in listeChampionsVeraendert]})
    pdChampionsVeraendert = pdChampionsVeraendert.loc[pdChampionsVeraendert['Champions'].isin(champListeAngepasst)]

    if patchNummer == '6.9':    # Mage-Update
        mageZusatz = ['vladimir', 'malzahar', 'cassiopeia', 'zyra', 'brand', 'velkoz', 'anivia', 'annie', 'fiddlesticks', 'kennen', 'swain', 'syndra', 'veigar', 'viktor', 'xerath', 'ziggs']
        pdChampionsVeraendert = pdChampionsVeraendert.append(pd.DataFrame({'Champions': mageZusatz}))
    elif patchNummer == '6.21': # Assassin-Update
        assassinZusatz = ['talon', 'katarina', 'leblanc', 'rengar', 'fizz', 'khazix', 'akali', 'zed', 'ekko', 'shaco']
        pdChampionsVeraendert = pdChampionsVeraendert.append(pd.DataFrame({'Champions': assassinZusatz}))

    
    # Nach Skins suchen
    skinsHtml = html.xpath("//h4[contains(@class, 'skin-title')]")
    skinsListe = list()
    
    if len(skinsHtml):
        for skin in skinsHtml:  # skin = skinsHtml[0]
#            skinString = tostring(skin).decode('utf8')
#            skinsListe.append(re.search("href=\".*\"", skinString).group(0).split("\"")[1].split('/')[-1].split('_')[0])
            try:
                skinString = tostring(skin[0]).decode('utf8')
#                print(skinString)
                skinAuswahl = [champ for champ in champListe if champ.lower().replace('dr. mundo', 'mundo').replace('miss fortune', 'fortune') in re.search('>.*<', skinString).group(0).lower().replace('&#8217;', '\'')]
                if len(skinAuswahl) == 1:
                    skinsListe.append(skinAuswahl[0])
                elif len(skinAuswahl) > 1:
                    skinsListe.append(skinAuswahl[np.argmax([len(skinSel) for skinSel in skinAuswahl])])
            except:
                try:                 
                    skinAuswahl = [champ for champ in champListe if champ.lower().replace('dr. mundo', 'mundo').replace('miss fortune', 'fortune') in re.search('>.*$', skinString).group(0).lower().replace('&#8217;', '\'')]
                    if len(skinAuswahl) == 1:
                        skinsListe.append(skinAuswahl[0])
                    elif len(skinAuswahl) > 1:
                        skinsListe.append(skinAuswahl[np.argmax([len(skinSel) for skinSel in skinAuswahl])])
                except: 
                    pass
    
    # Ausnahmen hinzufügen
    if patchNummer == '5.4':
        skinsListe.append('Sona')
    elif patchNummer == '8.12':
        skinsListe.append('Rammus')        
    elif patchNummer == '8.14':
        skinsListe.append('Ezreal')        
        skinsListe.append('Gnar') 
        skinsListe.append('Rakan') 
        skinsListe.append('Taliyah') 
        skinsListe.append('Xayah') 
    elif patchNummer == '8.23':
        skinsListe.append('Soraka')        
        skinsListe.append('Miss Fortune') 
        skinsListe.append('Ezreal') 
        skinsListe.append('Lulu') 
        skinsListe.append('Lux') 
    elif patchNummer == '9.6':
        skinsListe.append('Yorick')     
    elif patchNummer == '9.8':
        skinsListe.append('Camille')        
        skinsListe.append('Fiora') 
        skinsListe.append('Irelia') 
        skinsListe.append('Kai\'sa') 
        skinsListe.append('Rakan') 
        skinsListe.append('LeBlanc') 
#    elif patchNummer == '5.14':
#        skinsListe.append('Miss Fortune')
        
    
    pdSkins = pd.DataFrame({'Skins': skinsListe}).drop_duplicates().reset_index(drop = True)
    if patchNummer == '6.15':
        pdSkins = pdSkins.drop(np.where(pdSkins['Skins'] == 'Lux')[0]).reset_index(drop = True)
        pdSkins = pdSkins.drop(np.where(pdSkins['Skins'] == 'LeBlanc')[0]).reset_index(drop = True)
    elif patchNummer == '6.19':
        pdSkins = pdSkins.drop(np.where(pdSkins['Skins'] == 'Fiora')[0]).reset_index(drop = True)
        pdSkins = pdSkins.drop(np.where(pdSkins['Skins'] == 'Teemo')[0]).reset_index(drop = True)
    elif patchNummer == '6.21':
        pdSkins = pdSkins.drop(np.where(pdSkins['Skins'] == 'Vladimir')[0]).reset_index(drop = True)
        pdSkins = pdSkins.drop(np.where(pdSkins['Skins'] == 'Sion')[0]).reset_index(drop = True)
    elif patchNummer == '6.22':
        pdSkins = pdSkins.drop(np.where(pdSkins['Skins'] == 'Twitch')[0]).reset_index(drop = True)
        pdSkins = pdSkins.drop(np.where(pdSkins['Skins'] == 'Maokai')[0]).reset_index(drop = True)
    elif patchNummer == '7.9':
        pdSkins = pdSkins.drop(np.where(pdSkins['Skins'] == 'Sejuani')[0]).reset_index(drop = True)
        pdSkins = pdSkins.drop(np.where(pdSkins['Skins'] == 'Maokai')[0]).reset_index(drop = True)
    elif patchNummer == '7.23':
        pdSkins = pdSkins.drop(np.where(pdSkins['Skins'] == 'Garen')[0]).reset_index(drop = True)
    elif patchNummer == '7.24':
        pdSkins = pdSkins.drop(np.where(pdSkins['Skins'] == 'Amumu')[0]).reset_index(drop = True)
    
    # Patch-Datum
    htmlStringAlles = tostring(html).decode('utf8')
    if patchNummer == '5.16':
        datum = '20.08.2015'
    else:
        datum = max([datetime.strptime(datum.split('.')[0].lstrip("0") + '.' + datum.split('.')[1].lstrip("0") + '.' + datum.split('.')[2], "%d.%m.%Y") for datum in re.findall('\d{1,2}[.]\d{1,2}[.]\d{4}', htmlStringAlles)]).strftime("%d.%m.%Y")    # Daten im Format %d.%m.%Y
    
#    datumHtml = html.xpath("//h3[contains(@class, change-title)]")
#    
#    datumHtml = html.xpath("//abbr[contains(@title, '')]")
#    datumAuswahl = list()
#    if len(datumHtml):
#        for datumElement in datumHtml:
#            datumAuswahl.append(re.search('title=".*,', tostring(datumElement).decode('utf8')).group(0).split('"')[1][:-1])
    
        # Als Datum das häufigste Element nehmen
#    datum = modus(datumAuswahl)
    
    # Dict mit den Resultaten
    datenGesammelt = {'Champions': pdChampionsVeraendert, 'Skins': pdSkins, 'Datum': datum, 'Patchnummer': patchNummer}

    return(datenGesammelt)


def ausgabePatch(patchInfo):    # patchInfo = patchDaten[0]
    print('Patch: ' + patchInfo['Patchnummer'])
    print('Datum: ' + patchInfo['Datum'])
    print('\nChampions:\n')
    for champ in patchInfo['Champions']['Champions'].tolist():
        print(champ)
    print('\nSkins:\n')
    for skin in patchInfo['Skins']['Skins'].tolist():
        print(skin)
    print('\n')
    return()
    

def patchZuPd(patchDaten):
    pdGesamt = list()
    for i in range(0, len(patchDaten)):
        patchNr = patchDaten[i]['Patchnummer']
        patchTag = patchDaten[i]['Datum']
        
        nChampions = patchDaten[i]['Champions'].shape[0]
        pdChamps = pd.DataFrame({'Patchnummer': np.repeat(patchNr, nChampions), 'Patchdatum': np.repeat(patchTag, nChampions), 'Typ': np.repeat('Champion', nChampions), 'Champion': patchDaten[i]['Champions']['Champions']})
        
        nSkins = patchDaten[i]['Skins'].shape[0]
        pdSkins = pd.DataFrame({'Patchnummer': np.repeat(patchNr, nSkins), 'Patchdatum': np.repeat(patchTag, nSkins), 'Typ': np.repeat('Skins', nSkins), 'Champion': patchDaten[i]['Skins']['Skins']})

        pdGesamt.append(pd.concat([pdChamps, pdSkins]))
        
    pdAlle = pd.concat(pdGesamt, ignore_index = True)
    for i in range(0, pdAlle.shape[0]):
        pdAlle.iloc[i,3] = pdAlle.iloc[i,3].lower().replace(' ', '').replace('\'', '').replace('.', '').replace('monkeyking', 'wukong')
        
    return(pdAlle)
    

def datenZuPd(beliebtheit, champListeAngepasst):
    pdAlleListe = list()
    for i in range(0, len(champListeAngepasst)):   # champ = champListeAngepasst[0]
        champ = champListeAngepasst[i].replace('monkeyking', 'wukong')
        
        pdNeu = pd.DataFrame(beliebtheit[i].copy())
        pdNeu.columns = ['Zeit', 'RatePrz']
        
        pdNeu['Zeit'] = pdNeu['Zeit'] / (1000*60*60*24)

        pdNeu['Champion'] = champ       
    
        pdAlleListe.append(pdNeu)

    return(pd.concat(pdAlleListe, ignore_index = True))
    

if __name__ == "__main__": 
    
    # Parameter
    leagueofgraphsGelesen = True
    
    ###
    # Champions-Liste
    champListe = ['Aatrox', 'Ahri', 'Akali', 'Alistar', 'Amumu', 'Anivia', 'Annie', 'Ashe', 'Aurelion Sol', 'Azir', 'Bard', 'Blitzcrank', 'Brand', 'Braum', 'Caitlyn', 'Camille', 'Cassiopeia', 'Cho\'Gath', 'Corki', 'Darius', 'Diana', 'Dr. Mundo', 'Draven', 'Ekko', 'Elise', 'Evelynn', 'Ezreal', 'Fiddlesticks', 'Fiora', 'Fizz', 'Galio', 'Gangplank', 'Garen', 'Gnar', 'Gragas', 'Graves', 'Hecarim', 'Heimerdinger', 'Illaoi', 'Irelia', 'Ivern', 'Janna', 'Jarvan IV', 'Jax', 'Jayce', 'Jhin', 'Jinx', 'Kai\'Sa', 'Kalista', 'Karma', 'Karthus', 'Kassadin', 'Katarina', 'Kayle', 'Kayn', 'Kennen', 'Kha\'Zix', 'Kindred', 'Kled', 'Kog\'Maw', 'LeBlanc', 'Lee Sin', 'Leona', 'Lissandra', 'Lucian', 'Lulu', 'Lux', 'Malphite', 'Malzahar', 'Maokai', 'Master Yi', 'Miss Fortune', 'Mordekaiser', 'Morgana', 'Nami', 'Nasus', 'Nautilus', 'Neeko', 'Nidalee', 'Nocturne', 'Nunu', 'Olaf', 'Orianna', 'Ornn', 'Pantheon', 'Poppy', 'Pyke', 'Quinn', 'Rakan', 'Rammus', 'Rek\'Sai', 'Renekton', 'Rengar', 'Riven', 'Rumble', 'Ryze', 'Sejuani', 'Shaco', 'Shen', 'Shyvana', 'Singed', 'Sion', 'Sivir', 'Skarner', 'Sona', 'Soraka', 'Swain', 'Sylas', 'Syndra', 'Tahm Kench', 'Taliyah', 'Talon', 'Taric', 'Teemo', 'Thresh', 'Tristana', 'Trundle', 'Tryndamere', 'Twisted Fate', 'Twitch', 'Udyr', 'Urgot', 'Varus', 'Vayne', 'Veigar', 'Vel\'Koz', 'Vi', 'Viktor', 'Vladimir', 'Volibear', 'Warwick', 'Wukong', 'Xayah', 'Xerath', 'Xin Zhao', 'Yasuo', 'Yorick', 'Zac', 'Zed', 'Ziggs', 'Zilean', 'Zoe', 'Zyra']
    champListeAngepasst = [champ.lower().replace(' ', '').replace('\'', '').replace('.', '').replace('wukong', 'monkeyking') for champ in champListe]

    urlLeagueOfGraphs = 'https://www.leagueofgraphs.com/de/champions/stats'
    
    # Browser
    browser = webdriver.Firefox()
    
    if leagueofgraphsGelesen:
        pickleSpeicher = open('datenLeagueofgraphsBeliebtheit.pkl', 'rb')
        beliebtheit = pickle.load(pickleSpeicher)
        pickleSpeicher.close()

        pickleSpeicher = open('datenLeagueofgraphsWinrate.pkl', 'rb')
        winrate = pickle.load(pickleSpeicher)
        pickleSpeicher.close()

        pickleSpeicher = open('datenLeagueofgraphsBannrate.pkl', 'rb')
        bannrate = pickle.load(pickleSpeicher)
        pickleSpeicher.close()

    else:
        beliebtheit = list()
        winrate = list()
        bannrate = list()
        
        for champ in champListeAngepasst:    # champ = champListe[0]
            browser.get(urlLeagueOfGraphs + '/' + champ)
            
            # Html abgreifen
            inneresHTML = browser.execute_script("return document.body.innerHTML")
            html = lxml.html.fromstring(inneresHTML)
    #        listenInhalt = html.get_element_by_id("graphDD5")
            htmlGraphen = html[1][1][2][0][1][1][0]   # [0]: Beliebtheit, [1]: Win-Rate, [2]: Bann-Rate
            
            # Graphen abgreifen
            for i in range(0,3):
                datenGraph = tostring(htmlGraphen[i]).decode('utf8')
                graphNurDaten = datenGraph.split('data:')[1].split(',\n')[0].strip()
            
                if i == 0:
                    beliebtheit.append(stringZuMatrix(graphNurDaten))   # plt.plot(beliebtheit[0][:,0], beliebtheit[0][:,1])
                elif i == 1:
                    winrate.append(stringZuMatrix(graphNurDaten))       # plt.plot(winrate[0][:,0], winrate[0][:,1])
                elif i == 2:
                    bannrate.append(stringZuMatrix(graphNurDaten))      # plt.plot(bannrate[0][:,0], bannrate[0][:,1])
        
        pickleSpeicher = open('datenLeagueofgraphsBeliebtheit.pkl', 'wb')
        pickle.dump(beliebtheit, pickleSpeicher)
        pickleSpeicher.close()

        pickleSpeicher = open('datenLeagueofgraphsWinrate.pkl', 'wb')
        pickle.dump(winrate, pickleSpeicher)
        pickleSpeicher.close()

        pickleSpeicher = open('datenLeagueofgraphsBannrate.pkl', 'wb')
        pickle.dump(bannrate, pickleSpeicher)
        pickleSpeicher.close()

#    browser.close()

    ###
    # Aktualisierungen herunterladen
    seasons = np.arange(4,10)    # Betrachtete Seasons
    patchMinimum = np.array([8,1,1,1,1,1])
    patchMaximum = np.array([21,24,24,24,24,9])
    patchBvorhanden = np.array([False, False, False, True, True, False])
    
    urlPatchAktualisierungen = 'https://euw.leagueoflegends.com/de/news/game-updates/patch/patchnotizen'
    urlPatchAktualisierungenUmgekehrt = 'https://euw.leagueoflegends.com/de/news/game-updates/patch'
    
    patchDaten = list()
    for i in range(0, len(seasons)):
#    for i in range(2, len(seasons)):
        for j in range(0, patchMaximum[i] - patchMinimum[i] + 1):
#        for j in range(17, patchMaximum[i] - patchMinimum[i] + 1):
            if str(seasons[i]) + str(patchMinimum[i] + j) == '516': # Patch 5.16 ist irgendwie komisch in der deutschen Variante
                browser.get(urlPatchAktualisierungenUmgekehrt + '/' + str(seasons[i]) + str(patchMinimum[i] + j) + '-patchnotizen')                
            else:
                browser.get(urlPatchAktualisierungen + '-' + str(seasons[i]) + str(patchMinimum[i] + j))
            
            try:
                inneresHTML = browser.execute_script("return document.body.innerHTML")
                html = lxml.html.fromstring(inneresHTML)

                patchDaten.append(htmlChampionsGeaendert(html, champListeAngepasst, str(seasons[i]) + '.' + str(patchMinimum[i] + j)))
            except:
                browser.refresh()
                
                inneresHTML = browser.execute_script("return document.body.innerHTML")
                html = lxml.html.fromstring(inneresHTML)

                patchDaten.append(htmlChampionsGeaendert(html, champListeAngepasst, str(seasons[i]) + '.' + str(patchMinimum[i] + j)))
                    
            
            leer = ausgabePatch(patchDaten[-1])

#            input("Press Enter to continue...") # Zu Testen
            
            # b-Patches
            if (j == patchMaximum[i] - patchMinimum[i]) & patchBvorhanden[i]:
                browser.get(urlPatchAktualisierungen + '-' + str(seasons[i]) + str(patchMinimum[i] + j) + 'b')
                
                try:
                    inneresHTML = browser.execute_script("return document.body.innerHTML")
                    html = lxml.html.fromstring(inneresHTML)
        
                    patchDaten.append(htmlChampionsGeaendert(html, champListeAngepasst, str(seasons[i]) + '.' + str(patchMinimum[i] + j) + 'b'))
                except:
                    browser.refresh()
                    
                    inneresHTML = browser.execute_script("return document.body.innerHTML")
                    html = lxml.html.fromstring(inneresHTML)
        
                    patchDaten.append(htmlChampionsGeaendert(html, champListeAngepasst, str(seasons[i]) + '.' + str(patchMinimum[i] + j) + 'b'))                        
                    
                leer = ausgabePatch(patchDaten[-1])
                
#                input("Press Enter to continue...") # Zum Testen

    browser.close()
    
    # Als csv abspeichern
    pdAlle = patchZuPd(patchDaten)
    pdAlle.to_csv('lol_patch_daten.csv', index = False)

    pdBeliebtheit = datenZuPd(beliebtheit, champListeAngepasst)
    pdWinrate = datenZuPd(winrate, champListeAngepasst)
    pdBannrate = datenZuPd(bannrate, champListeAngepasst)

    pdBeliebtheit.to_csv('lol_champions_beliebtheit.csv', index = False)
    pdWinrate.to_csv('lol_champions_winrate.csv', index = False)
    pdBannrate.to_csv('lol_champions_bannrate.csv', index = False)














